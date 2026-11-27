import os, subprocess, requests
from bg import make_bg
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reciters import RECITERS

RECITER = "Yasser_Ad-Dussary_128kbps"
W, H = 1080, 1920
MAX_SECONDS = 45
WORK = "work"
font_path = "font.ttf"
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
RAQM = ImageFont.Layout.RAQM
AYAH_MAX, AYAH_MIN = 90, 36   # أكبر وأصغر حجم لخط الآية (بيصغّر لوحده للآيات الطويلة)
TEXT_MAXW = 800               # أقصى عرض للسطر
AVAIL_H = 1400                # أقصى ارتفاع لكتلة الآية
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

font_small = ImageFont.truetype(font_path, 50, layout_engine=RAQM)
font_logo = ImageFont.truetype(font_path, 35, layout_engine=RAQM)
_fonts = {}
def ayah_font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(font_path, size, layout_engine=RAQM)
    return _fonts[size]

def bbox(s, f, direction="rtl"):
    return f.getbbox(s, anchor="ls", direction=direction)

def wrap(tokens, f, maxw):
    lines, cur = [], ""
    for w in tokens:
        test = (cur + " " + w).strip()
        l, t, r, b = bbox(test, f)
        if cur and r - l > maxw:
            lines.append(cur); cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines

def put_centered(d, s, f, cx, cy, fill, direction="rtl"):
    l, t, r, b = bbox(s, f, direction)
    d.text((cx - (l + r) / 2, cy - (t + b) / 2), s, font=f, fill=fill,
           anchor="ls", direction=direction)

def put_line(d, segs, f, cx, base):
    gap = int(f.size * 0.25)
    boxes = [bbox(s, f) for s, _ in segs]
    total = sum(b[2] - b[0] for b in boxes) + gap * (len(segs) - 1)
    xr = cx + total / 2
    for (s, col), b in zip(segs, boxes):
        d.text((xr - b[2], base), s, font=f, fill=col, anchor="ls", direction="rtl")
        xr -= (b[2] - b[0]) + gap

def layout_ayah(text, ayah_num):
    # بيرجع أسطر الآية وخطها ومكانها، من غير ما يرسم حاجة
    marker = "﴿" + str(ayah_num).translate(AR_DIGITS) + "﴾"
    tokens = text.split()
    tokens[-1] = tokens[-1] + " " + marker
    for size in range(AYAH_MAX, AYAH_MIN - 1, -4):
        f = ayah_font(size)
        lines = wrap(tokens, f, TEXT_MAXW)
        pitch = int(size * 1.75)
        top = min(k * pitch + bbox(ln, f)[1] for k, ln in enumerate(lines))
        bot = max(k * pitch + bbox(ln, f)[3] for k, ln in enumerate(lines))
        if bot - top <= AVAIL_H:
            break
    shift = H / 2 - (top + bot) / 2   # توسيط رأسي حسب الحبر الفعلي
    return lines, f, pitch, shift, marker

def render_base(surah_name, base_img_path, out_path):
    # الخلفية لوحدها (هي اللي بتتعملها زوم)، وبيرجع png شفاف فيه الإطار الذهبي + اسم السورة + اللوجو (ثابت)
    img = ImageOps.fit(Image.open(base_img_path).convert("RGB"), (W, H)).convert("RGBA")
    img.convert("RGB").save(out_path)
    chrome = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(chrome)

    # الإطار الذهبي
    d.rectangle([40, 40, W-40, H-40], outline=GOLD, width=6)
    d.rectangle([65, 65, W-65, H-65], outline=GOLD, width=2)
    d.rectangle([85, 85, W-85, H-85], outline=GOLD, width=1)
    for x, y in [(65, 65), (W-65, 65), (65, H-65), (W-65, H-65)]:
        d.ellipse([x-20, y-20, x+20, y+20], outline=GOLD, width=3)
        d.ellipse([x-8, y-8, x+8, y+8], fill=GOLD)

    # اسم السورة جوه البيضاوي
    clean = surah_name.replace("سُورَةُ", "").replace("سورة", "").strip()
    s = f"سُورَةُ {clean}"
    l, t, r, b = bbox(s, font_small)
    ew, cy = (r - l) + 140, 160
    d.ellipse([W/2 - ew/2, cy - 55, W/2 + ew/2, cy + 55], outline=GOLD, width=3)
    put_centered(d, s, font_small, W/2, cy, GOLD, "rtl")

    put_centered(d, "Almushaf | المصحف", font_logo, W/2, H - 125, (160, 160, 160))
    chrome_path = out_path.replace(".png", "_chrome.png")
    chrome.save(chrome_path)
    return chrome_path

def render_lines(text, ayah_num, out_dir, tag):
    # كل سطر من الآية بيترسم لوحده على صورة شفافة (عشان يتعمله أنيميشن ظهور)
    lines, f, pitch, shift, marker = layout_ayah(text, ayah_num)
    paths = []
    for k, ln in enumerate(lines):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        base = k * pitch + shift
        if k == len(lines) - 1 and ln.endswith(marker):
            body = ln[:-len(marker)].rstrip()
            segs = ([(body, WHITE)] if body else []) + [(marker, GOLD)]
        else:
            segs = [(ln, WHITE)]
        put_line(d, segs, f, W/2, base)
        p = os.path.join(out_dir, f"line_{tag}_{k}.png")
        img.save(p)
        paths.append(p)
    return paths

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

STACK_TOP = 320          # أول سطر تحت اسم السورة
STACK_BOTTOM = H - 280   # فوق اللوجو

def layout_stack(texts, first_ayah):
    # كل آية بتتلف لوحدها (أسطرها ورا بعض، ما يتكسرش كلام آية جوه سطر آية تانية)،
    # والخط بيصغر لو التكديس طويل
    ayah_tokens = []
    for j, text in enumerate(texts):
        marker = "﴿" + str(first_ayah + j).translate(AR_DIGITS) + "﴾"
        tokens = text.split()
        tokens[-1] = tokens[-1] + " " + marker
        ayah_tokens.append(tokens)
    probe = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ ﴿١﴾"
    for size in range(AYAH_MAX, 20, -2):
        f = ayah_font(size)
        per_ayah_lines = [wrap(tokens, f, TEXT_MAXW) for tokens in ayah_tokens]
        nlines = sum(len(x) for x in per_ayah_lines)
        l, t, r, b = bbox(probe, f)
        pitch = int((b - t) * 1.30)
        if STACK_TOP + nlines * pitch <= STACK_BOTTOM:
            break
    return per_ayah_lines, f, pitch

def render_stack(texts, first_ayah, out_dir):
    # بيرسم كل سطر png شفاف، وبيرجع قائمة لكل آية بأسطرها (مترتبة)
    per_ayah_lines, f, pitch = layout_stack(texts, first_ayah)
    per_ayah, k = [[] for _ in texts], 0
    for j, lines in enumerate(per_ayah_lines):
        marker = "﴿" + str(first_ayah + j).translate(AR_DIGITS) + "﴾"
        for ln in lines:
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            l, t, r, b = bbox(ln, f)
            base = STACK_TOP + k * pitch - t
            if ln.endswith(marker):
                body = ln[:-len(marker)].rstrip()
                segs = ([(body, WHITE)] if body else []) + [(marker, GOLD)]
            else:
                segs = [(ln, WHITE)]
            put_line(d, segs, f, W / 2, base)
            p = os.path.join(out_dir, f"stk_{k}.png")
            img.save(p)
            per_ayah[j].append((p, len(ln)))
            k += 1
    return per_ayah

def build_clip(base_png, chrome_png, static_pngs, new_pngs, mp3, dur, zoom_off, out, new_weights=None):
    # خلفية بزوم بطيء مستمر عبر المقاطع + الإطار ثابت + الآيات السابقة ثابتة +
    # أسطر الآية الجديدة بتدخل سطر ورا سطر موزعة على مدة الآية بنسبة طول كل سطر
    inputs = ["-loop", "1", "-i", base_png, "-loop", "1", "-i", chrome_png]
    for p in static_pngs + new_pngs:
        inputs += ["-loop", "1", "-i", p]
    inputs += ["-i", mp3]
    ns, nn = len(static_pngs), len(new_pngs)
    zoom = (f"zoompan=z='min(1.08,1+0.0002*(on+{zoom_off}))':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920")
    fc = [f"[0:v]{zoom}[v0]", "[v0][1:v]overlay=0:0[v1]"]
    cur, idx = "v1", 2
    for k in range(ns):
        fc.append(f"[{cur}][{idx}:v]overlay=0:0[v{idx}]")
        cur, idx = f"v{idx}", idx + 1
    total_w = sum(new_weights) if new_weights else 0
    cum = 0
    for k in range(nn):
        if new_weights and total_w:
            st = dur * cum / total_w
            cum += new_weights[k]
        else:
            st = 0.25 + k * 0.35
        fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.45:alpha=1[l{k}]")
        fc.append(f"[{cur}][l{k}]overlay=0:y='14*(1-min(1,(t-{st:.2f})/0.45))':eval=frame[v{idx}]")
        cur, idx = f"v{idx}", idx + 1
    fc.append(f"[{cur}]null[vout]")
    subprocess.run(["ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(fc),
        "-map", "[vout]", "-map", f"{ns+nn+2}:a", "-shortest", "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
        "-c:a", "aac", out], check=True)

def get_ayahs(surah):
    data = requests.get(
        f"https://api.alquran.cloud/v1/surah/{surah}/quran-uthmani").json()["data"]
    return data["name"], data["ayahs"]

def build_title(surah_name, reciter, first, last):
    name = surah_name.replace("سُورَةُ", "").replace("سورة", "").strip()
    rng = f"({first}-{last})" if first != last else f"({first})"
    return f"سورة {name} {rng} | {RECITERS[reciter]}"

def make_chunk(surah, start_ayah, reciter=RECITER):
    os.makedirs(WORK, exist_ok=True)
    base_png, dust_png = make_bg(surah * 7 + start_ayah, WORK)
    name, ayahs = get_ayahs(surah)
    frame_png = os.path.join(WORK, "frame.png")
    chrome_png = render_base(name, base_png, frame_png)
    mp3s, durs, texts, total, i, last = [], [], [], 0.0, start_ayah, start_ayah
    while i <= len(ayahs):
        a = ayahs[i - 1]
        text = a["text"]
        if i == 1 and surah not in (1, 9):
            text = " ".join(text.split()[4:])
        mp3 = f"{WORK}/{i}.mp3"
        r = requests.get(f"https://everyayah.com/data/{reciter}/{surah:03d}{i:03d}.mp3")
        r.raise_for_status()
        open(mp3, "wb").write(r.content)
        dur = duration(mp3)
        if mp3s and total + dur > MAX_SECONDS:
            break
        mp3s.append(mp3); durs.append(dur); texts.append(text)
        total += dur; last = i; i += 1
    per_ayah = render_stack(texts, start_ayah, WORK)
    clips, zoom_off = [], 0
    for j, (mp3, dur) in enumerate(zip(mp3s, durs)):
        static_pngs = [p for aj in range(j) for p, _ in per_ayah[aj]]
        new_pngs = [p for p, _ in per_ayah[j]]
        new_weights = [w for _, w in per_ayah[j]]
        clip = f"{WORK}/{start_ayah + j}.mp4"
        build_clip(frame_png, chrome_png, static_pngs, new_pngs, mp3, dur, zoom_off, clip, new_weights)
        clips.append(clip)
        zoom_off += int(round((dur + 0.04) * 30))
    lst = f"{WORK}/list.txt"
    open(lst, "w").write("".join(f"file '{os.path.basename(c)}'\n" for c in clips))
    final = f"{WORK}/final.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
        "-i", lst, "-c", "copy", final], check=True)
    title = build_title(name, reciter, start_ayah, last)
    if last >= len(ayahs):
        nxt = {"surah": surah % 114 + 1, "ayah": 1}
    else:
        nxt = {"surah": surah, "ayah": last + 1}
    return final, title, nxt

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        os.makedirs(WORK, exist_ok=True)
        b, _ = make_bg(3, WORK)
        for n, (s, a) in enumerate([(112, 1), (2, 255), (2, 282)], 1):
            nm, ays = get_ayahs(s)
            frame = f"{WORK}/frame_preview.png"
            render_base(nm, b, frame)
            render_lines(ays[a - 1]["text"], a, WORK, f"preview{n}")
        print("preview ok")
    else:
        s = int(sys.argv[1]) if len(sys.argv) > 1 else 112
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(make_chunk(s, a))
