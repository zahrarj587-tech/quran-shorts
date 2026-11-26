import os, subprocess, requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from reciters import RECITERS
import arabic_reshaper
from bidi.algorithm import get_display

W, H = 1080, 1920
WORK = "work"
font_path = "font.ttf"
font = ImageFont.truetype(font_path, 85, layout_engine=ImageFont.Layout.RAQM)
font_small = ImageFont.truetype(font_path, 45, layout_engine=ImageFont.Layout.RAQM)

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

def render_special_page(text, ayah_num, path, base_path):
    # فتح الصورة وتعتميها
    img = Image.open(base_path).convert("RGBA")
    # قص الصورة عشان تناسب مقاس 9:16
    w, h = img.size
    target_ratio = W / H
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    img = img.resize((W, H), Image.LANCZOS)
    
    # تعتيم الصورة عشان النص يبان
    img = ImageEnhance.Brightness(img).enhance(0.35)
    d = ImageDraw.Draw(img)
    
    # إطار أبيض بسيط للحادث
    d.rectangle([40, 40, W-40, H-40], outline=(200, 200, 200), width=4)
    
    # كتابة الآية
    lines = wrap(text)
    line_height = 130
    total_text_height = len(lines) * line_height
    y = (H - total_text_height) / 2 
    
    for i, l in enumerate(lines):
        s = shape(l)
        line_w = font.getlength(s)
        x = (W - line_w) / 2
        
        # ظل للنص عشان يبان على الخلفية الغامقة
        d.text((x+2, y+2), s, font=font, fill=(0,0,0))
        d.text((x, y), s, font=font, fill=(255, 255, 255))
        
        if i == len(lines) - 1:
            marker = f"﴿{ayah_num}﴾"
            d.text((x - 100, y), marker, font=font, fill=(255, 200, 200))
            
        y += line_height
        
    img.convert("RGB").save(path)

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def get_ayahs(surah):
    data = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/quran-uthmani").json()["data"]
    return data["name"], data["ayahs"]

# الإعدادات للفيديو الخاص
surah = 2
reciter = "Abdul_Basit_Mujawwad_128kbps" # صوت مجوّد وخاشع جداً
start_ayah = 156
end_ayah = 157

name, ayahs = get_ayahs(surah)
base_path = f"{WORK}/fire_bg.jpg"
clips = []

for i in range(start_ayah, end_ayah + 1):
    text = ayahs[i - 1]["text"]
    mp3 = f"{WORK}/fire_{i}.mp3"
    r = requests.get(f"https://everyayah.com/data/{reciter}/{surah:03d}{i:03d}.mp3")
    r.raise_for_status()
    open(mp3, "wb").write(r.content)
    dur = duration(mp3)
    
    png = f"{WORK}/fire_{i}.png"
    render_special_page(text, i, png, base_path)
    
    out = f"{WORK}/fire_{i}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-framerate", "30", "-i", png,
        "-i", mp3, "-map", "0:v", "-map", "1:a", "-shortest", "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-c:a", "aac", out], check=True)
    clips.append(out)

lst = f"{WORK}/list_fire.txt"
open(lst, "w").write("".join(f"file '{os.path.basename(c)}'\n" for c in clips))
final = f"{WORK}/fire_final.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-i", lst, "-c", "copy", final], check=True)
print("DONE:", final)
