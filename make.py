import os, subprocess, requests
from bg import make_bg
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

RECITER = "Yasser_Ad-Dussary_128kbps"
from reciters import RECITERS
W, H = 1080, 1920
MAX_SECONDS = 45
font_path = "font.ttf"
font = ImageFont.truetype(font_path, 95, layout_engine=ImageFont.Layout.RAQM)
font_small = ImageFont.truetype(font_path, 55, layout_engine=ImageFont.Layout.RAQM)
font_logo = ImageFont.truetype(font_path, 40, layout_engine=ImageFont.Layout.RAQM)
WORK = "work"

def shape(t):
    return t

def wrap(text, maxw=850):
    lines, cur = [], ""
    for w in text.split():
        test = (cur + " " + w).strip()
        if font.getlength(shape(test)) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    lines.append(cur)
    return lines

def render_page(text, surah_name, ayah_num, path):
    img = Image.open(f"{WORK}/base.png").convert("RGBA")
    d = ImageDraw.Draw(img)
    
    # 1. الإطار الذهبي الفخم المزدوج
    gold = (212, 175, 55)
    d.rectangle([40, 40, W-40, H-40], outline=gold, width=8)
    d.rectangle([65, 65, W-65, H-65], outline=gold, width=2)
    d.rectangle([80, 80, W-80, H-80], outline=gold, width=1)
    
    # زخارف الأركان
    for x, y in [(65,65), (W-65,65), (65,H-65), (W-65,H-65)]:
        d.ellipse([x-25, y-25, x+25, y+25], outline=gold, width=4)
        d.ellipse([x-10, y-10, x+10, y+10], fill=gold)

    # 2. اسم السورة داخل شكل بيضاوي مزخرف
    clean_surah = surah_name.replace("سُورَةُ", "").replace("سورة", "").strip()
    surah_text = f"سُورَةُ {clean_surah}"
    surah_w = font_small.getlength(surah_text)
    surah_x = (W - surah_w) / 2
    d.ellipse([surah_x - 80, 100, surah_x + surah_w + 80, 200], outline=gold, width=3)
    d.text((surah_x, 115), surah_text, font=font_small, fill=gold)
    
    # 3. الآية في المنتصف بالضبط (بدون خلفية)
    lines = wrap(text)
    line_height = 140
    total_text_height = len(lines) * line_height
    y = (H - total_text_height) / 2
    
    for i, l in enumerate(lines):
        s = shape(l)
        line_w = font.getlength(s)
        x = (W - line_w) / 2
        
        # كتابة السطر
        d.text((x, y), s, font=font, fill=(255, 255, 255))
        
        # إضافة رقم الآية في نهاية آخر سطر (جوه زخرفة)
        if i == len(lines) - 1:
            marker = f" ۝{ayah_num} "
            marker_w = font.getlength(marker)
            # إزاحة بسيطة للرقم عشان ميتداخلش مع الكلام
            d.text((x - marker_w - 10, y), marker, font=font, fill=gold)
            
        y += line_height
        
    # 4. اللوجو / اسم القناة في الأسفل
    logo_text = "Almushaf | المصحف"
    logo_w = font_logo.getlength(logo_text)
    d.text(((W - logo_w) / 2, H - 160), logo_text, font=font_logo, fill=(180, 180, 180))
    
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
        
        png = f"{WORK}/{i}_page.png"
        render_page(text, name, i, png)
        
        out = f"{WORK}/{i}.mp4"
        
        # ثبات تام للصفحة (No animation inside, pure static text)
        fc = f"[0:v][1:v]overlay=0:0[v]"
        
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
