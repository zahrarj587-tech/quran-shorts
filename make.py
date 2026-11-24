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
        if cur and (r - l) > maxw:
            lines.append(cur); cur = w
        else:
            cur = test
    lines.append(cur)
    return lines

def put_centered(d, s, f, cx, cy, fill, direction=None):
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

def render_page(text, surah_name, ayah_num, path, base_path):
    img = ImageOps.fit(Image.open(base_path).convert("RGB"), (W, H)).convert("RGBA")
    d = ImageDraw.Draw(img)

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

    # الآية + رقمها جوه الأقواس (آخر كلمة + الرقم بيتلفوا مع بعض)
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
    for k, ln in enumerate(lines):
        base = k * pitch + shift
        if k == len(lines) - 1 and ln.endswith(marker):
            body = ln[:-len(marker)].rstrip()
            segs = ([(body, WHITE)] if body else []) + [(marker, GOLD)]
        else:
            segs = [(ln, WHITE)]
        put_line(d, segs, f, W/2, base)

    put_centered(d, "Almushaf | المصحف", font_logo, W/2, H - 125, (160, 160, 160))
    img.convert("RGB").save(path)

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

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
    clips, total, i = [], 0.0, start_ayah
    last = start_ayah
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
        if clips and total + dur > MAX_SECONDS:
            break
        png = f"{WORK}/{i}_page.png"
        render_page(text, name, i, png, base_png)
        out = f"{WORK}/{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", png,
            "-i", mp3, "-map", "0:v", "-map", "1:a", "-shortest", "-r", "30",
            "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
            "-c:a", "aac", out], check=True)
        clips.append(out); total += dur; last = i; i += 1
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
            render_page(ays[a - 1]["text"], nm, a, f"{WORK}/preview{n}.png", b)
        print("preview ok")
    else:
        s = int(sys.argv[1]) if len(sys.argv) > 1 else 112
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(make_chunk(s, a))
