import os
import random
import subprocess
import urllib.request
import json
import sys

def make_bg(theme, duration, out_path):
    api_key = os.environ.get("PIXABAY_API_KEY")
    
    if api_key:
        try:
            # كلمات بحث متنوعة عشان تجيب خلفيات طبيعية وإسلامية هادئة
            keywords = ["nature", "clouds", "sky", "stars", "islamic", "mosque", "water", "forest", "mountain", "light"]
            keyword = random.choice(keywords)
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={keyword}&orientation=vertical&video_type=film&per_page=20"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.load(response)
                
            if res.get("hits"):
                video = random.choice(res["hits"])
                video_url = video["videos"]["large"]["url"]
                
                temp_vid = f"/tmp/bg_temp_{random.randint(1000,9999)}.mp4"
                urllib.request.urlretrieve(video_url, temp_vid)
                
                # قص الفيديو 9:16 وتعتيمه عشان النص يبان
                cmd = [
                    "ffmpeg", "-y", "-stream_loop", "-1", "-i", temp_vid, 
                    "-t", str(duration), 
                    "-vf", "scale=-1:1920,crop=1080:1920,eq=brightness=-0.2:saturation=1.1",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", 
                    out_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(temp_vid):
                    os.remove(temp_vid)
                return out_path
        except Exception as e:
            print(f"Pixabay failed: {e}. Falling back to generated background.", file=sys.stderr)

    # الخطة البديلة: لو مفيش نت أو المفتاح ضاع، هيولّد خلفية لون هادئ مع حبيبات (عشان ميقفش)
    colors = {
        "emerald": "0x0f5132",
        "midnight": "0x0b132b",
        "gold": "0x5c4033",
        "royal": "0x1e3a8a",
        "onyx": "0x111827"
    }
    color_hex = colors.get(theme, "0x0f5132")
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color_hex}:s=1080x1920:d={duration}",
        "-vf", "noise=alls=20:allf=t",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path
