import os, subprocess, requests
from bg import make_bg
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

RECITER = "Alafasy_128kbps"
from reciters import RECITERS
W, H = 1080, 1920
MAX_SECONDS = 45
from PIL import features
print("raqm:", features.check("raqm"))
font = ImageFont.truetype("font.ttf", 80, layout_engine=ImageFont.Layout.RAQM)
WORK = "work"

def shape(t):
    return t

def wrap(text, maxw=900):
    lines, cur = [], ""
    for w in text.split():
        test = (cur + " " + w).strip()
        if font.getlength(shape(test)) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    lines.append(cur)
    return lines

def render(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lines = wrap(text)
    y = H // 2 - len(lines) * 70
    for l in lines:
        s = shape(l)
        d.text(((W - font.getlength(s)) / 2, y), s, font=font, fill="white")
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

def chunk_text(text, max_words=3):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

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
        
        chunks = chunk_text(text)
        n_chunks = len(chunks)
        chunk_dur = dur / n_chunks
        
        inputs = []
        filters = []
        
        # الخلفية (تأثير سينمائي)
        inputs.extend(["-loop", "1", "-framerate", "30", "-i", base_png])
        # صورة الغبار (شفافة حالياً، هنحولها لجزيئات متحركة)
        inputs.extend(["-loop", "1", "-framerate", "30", "-i", dust_png])
        
        # المقاطع النصية
        for idx, chunk in enumerate(chunks):
            png = f"{WORK}/{i}_{idx}.png"
            render(chunk, png)
            inputs.extend(["-loop", "1", "-framerate", "30", "-i", png])
            
            # تأخير ظهور النص بمقدار 0.3 ثانية عشان يسبق الصوت
            delay = 0.3 
            start = (idx * chunk_dur) + delay
            end = (idx + 1) * chunk_dur
            if end > dur: end = dur # تأمين عشان ميتعداش مدة الصوت
            
            fade_dur = min(0.4, chunk_dur / 2.0)
            fade_out_st = max(start, end - fade_dur)
            filters.append(f"[{2+idx}:v]format=rgba,fade=t=in:st={start}:d={fade_dur}:alpha=1,fade=t=out:st={fade_out_st}:d={fade_dur}:alpha=1[t{idx}]")
            
        # الصوت
        inputs.extend(["-i", mp3])
        audio_idx = 2 + n_chunks
        
        off = total
        # خلفية متحركة بزووم بطيء (Ken Burns) + إضاءة خفيفة
        filters.append(f"[0:v]scale=1400:2488,crop={W}:{H}:x='(iw-{W})/2+(iw-{W})/2*sin((t+{off})/25)':y='(ih-{H})/2+(ih-{H})/2*cos((t+{off})/30)',eq=brightness=-0.05:saturation=1.2,format=yuv420p[a]")
        # تحويل صورة الغبار الشفافة إلى جزيئات متحركة (Noise)
        filters.append(f"[1:v]format=rgba,noise=alls=12:allf=t+u,eq=brightness=0.1[d]")
        filters.append(f"[a][d]overlay=0:0[c]")
        
        # تركيب النص فوق الخلفية بالترتيب
        prev = "c"
        for idx in range(n_chunks):
            delay = 0.3
            start = (idx * chunk_dur) + delay
            end = (idx + 1) * chunk_dur
            if end > dur: end = dur
            next_label = f"v{idx}"
            filters.append(f"[{prev}][t{idx}]overlay=0:0:enable='between(t,{start},{end})'[{next_label}]")
            prev = next_label
            
        fc = ";".join(filters)
        out = f"{WORK}/{i}.mp4"
        
        # إضافة فلتر تطبيع الصوت (loudnorm) عشان الصوت يبقى عالي
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
            "-filter_complex", fc,
            "-map", f"[{prev}]", "-map", f"{audio_idx}:a", 
            "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
            "-shortest", "-r", "30",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", out], check=True)
            
        clips.append(out); total += dur; last = i; i += 1
        
    lst = f"{WORK}/list.txt"
    open(lst, "w").write("".join(f"file '{os.path.basename(c)}'\n" for c in clips))
    final = f"{WORK}/final.mp4"
    
    # إضافة Fade In في البداية و Fade Out في النهاية
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
        "-i", lst, 
        "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={total-0.5}:d=0.5",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "copy", final], check=True)
        
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
