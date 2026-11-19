import os
import random
import requests
from PIL import Image, ImageEnhance, ImageDraw

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    api_key = os.environ.get("PIXABAY_API_KEY")
    img = None
    rng = random.Random(seed)

    # 1. محاولة جلب صورة من Pixabay بكلمات آمنة جداً
    if api_key:
        try:
            keywords = [
                "mountain", "desert", "ocean", "forest", "clouds", 
                "milky way", "night sky", "waterfall", "river", 
                "islamic architecture", "mosque interior", "islamic pattern", 
                "praying silhouette", "prostration", "digital art landscape"
            ]
            keyword = rng.choice(keywords)
            category = "nature" if "mosque" not in keyword and "islamic" not in keyword and "praying" not in keyword else "buildings"
            
            url = f"https://pixabay.com/api/?key={api_key}&q={keyword}&category={category}&orientation=vertical&image_type=photo&per_page=50"
            
            res = requests.get(url, timeout=10).json()
            if res.get("hits"):
                img_url = rng.choice(res["hits"])["largeImageURL"]
                img_data = requests.get(img_url, timeout=15).content
                with open(base_path, "wb") as f:
                    f.write(img_data)
                img = Image.open(base_path).convert("RGB")
        except Exception as e:
            print(f"Pixabay failed: {e}. Generating safe pattern...")

    # 2. الخطة البديلة الآمنة جداً: رسم زخرفة إسلامية هندسية (تم إزالة Picsum العشوائي)
    if img is None:
        img = Image.new("RGB", (1080, 1920), (15, 23, 42))
        draw = ImageDraw.Draw(img)
        color = rng.choice([(16, 185, 129), (59, 130, 246), (245, 158, 11), (212, 175, 55)])
        
        # رسم هندسي متداخل
        for x in range(-100, 1080, 120):
            for y in range(-100, 1920, 120):
                if (x//120 + y//120) % 2 == 0:
                    draw.ellipse([x, y, x+120, y+120], outline=color, width=4)
                else:
                    draw.rectangle([x, y, x+120, y+120], outline=color, width=2)
        print("Used generated Islamic pattern.")

    # قص الصورة 9:16 وتعتيمها عشان النص يبان
    w, h = img.size
    target_ratio = 1080 / 1920
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    
    img = img.resize((1080, 1920), Image.LANCZOS)
    img = ImageEnhance.Brightness(img).enhance(0.4)
    img.save(base_path)
    
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    return base_path, dust_path
