import os, subprocess, requests
from bg import make_bg
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

RECITER = "Alafasy_128kbps"
from reciters import RECITERS
W, H = 1080, 1920
MAX_SECONDS = 45
from PIL import features
font = ImageFont.truetype("font.ttf", 80, layout_engine=ImageFont.Layout.RAQM)
font_small = ImageFont.truetype("font.ttf", 40, layout_engine=ImageFont.Layout.RAQM)
WORK = "work"

def shape(t):
    return t

def wrap(text, maxw=800):
    lines, cur = [], ""
    for w in text.split():
        test = (cur + " " + w).strip()
        if font.getlength(shape(test)) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    lines.append(cur)
    return lines

def render_page(text, surah_name, path):
    img = Image.open(f"{WORK}/base.png").convert("RGBA")
    d = ImageDraw.Draw(img)
    
    # 1. رسم الإطار الذهبي المزخرف
    border_color = (180, 140, 50) # لون ذهبي
    border_width = 6
    # إطار خارجي
    d.rectangle([40, 40, W-40, H-40], outline=border_color, width=border_width)
    # إطار داخلي
    d.rectangle([60, 60, W-60, H-60], outline=border_color, width=2)
    
    # إضافة زخارف في الأركان (دوائر بسيطة)
    for x, y in [(60,60), (W-60,60), (60,H-60), (W-60,H-60)]:
        d.ellipse([x-15, y-15, x+15, y+15], outline=border_color, width=3)
        d.ellipse([x-8, y-8, x+8, y+8], fill=border_color)

    # 2. كتابة اسم السورة في الأعلى
    clean_surah = surah_name.replace("سُورَةُ", "").replace("سورة", "").strip()
    surah_text = f"سُورَةُ {clean_surah}"
    d.text(((W - font_small.getlength(surah_text)) / 2, 100), surah_text, font=font_small, fill=(120, 80, 20))
    
    # 3. كتابة الآية في النص
    lines = wrap(text)
    y = H // 2 - len(lines) * 70
    for l in lines:
        s = shape(l)
        # لون النص بني غامق عشان يبان على الورق
        d.text(((W - font.getlength(s)) / 2, y), s, font=font, fill=(20, 20, 20))
        y += 140
        
    img.save(path)

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
        
        # تركيب صفحة المصحف للآية
        png = f"{WORK}/{i}_page.png"
        render_page(text, name, png)
        
        out = f"{WORK}/{i}.mp4"
        
        # الفيديو: الخلفية (ثابتة) + الصفحة (تظهر مرة واحدة) + الصوت
        # إضافة Fade in/out بسيط للصفحة عشان تظهر بنعومة
        fc = f"[1:v]format=rgba,fade=t=in:st=0:d=0.5:alpha=1,fade=t=out:st={dur-0.5}:d=0.5:alpha=1[page];[0:v][page]overlay=0:0[v]"
        
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", base_png,
            "-loop", "1", "-framerate", "30", "-i", png,
            "-i", mp3, "-filter_complex", fc,
            "-map", "[v]", "-map", "2:a", "-shortest", "-r", "30",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
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
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 112
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print(make_chunk(s, a))
