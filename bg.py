import os
import random
import requests
from PIL import Image, ImageEnhance, ImageDraw

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    api_key = os.environ.get("PIXABAY_API_KEY")

    # 1. محاولة جلب صورة من Pixabay
    if api_key:
        try:
            keywords = ["nature", "clouds", "sky", "stars", "islamic", "mosque", "water", "forest", "mountain", "light", "sunset", "night"]
            rng = random.Random(seed)
            keyword = rng.choice(keywords)
            url = f"https://pixabay.com/api/?key={api_key}&q={keyword}&orientation=vertical&image_type=photo&per_page=50"
            
            res = requests.get(url, timeout=15).json()
            if res.get("hits"):
                img_url = rng.choice(res["hits"])["largeImageURL"]
                img_data = requests.get(img_url, timeout=20).content
                
                with open(base_path, "wb") as f:
                    f.write(img_data)
                    
                # معالجة الصورة: قصها 9:16 وتعتيمها
                img = Image.open(base_path).convert("RGB")
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
                img = ImageEnhance.Brightness(img).enhance(0.35) # تعتيم عشان النص يبان
                img.save(base_path)
                
                # صورة شفافة للغبار عشان الكود ميدربش
                dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                dust.save(dust_path)
                return base_path, dust_path
        except Exception as e:
            print(f"Pixabay image failed: {e}. Falling back.")

    # 2. الخطة البديلة: خلفية لونية متدرجة (لو مفيش نت أو المفتاح ضاع)
    themes = [
        ((10, 50, 30), (20, 80, 50)),
        ((10, 15, 40), (25, 30, 70)),
        ((60, 40, 20), (100, 70, 30)),
        ((20, 20, 20), (50, 50, 50))
    ]
    rng = random.Random(seed)
    top_c, bot_c = rng.choice(themes)
    
    base = Image.new("RGB", (1080, 1920), top_c)
    draw = ImageDraw.Draw(base)
    for y in range(1920):
        r = int(top_c[0] + (bot_c[0] - top_c[0]) * y / 1920)
        g = int(top_c[1] + (bot_c[1] - top_c[1]) * y / 1920)
        b = int(top_c[2] + (bot_c[2] - top_c[2]) * y / 1920)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))
        
    base.save(base_path)
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    return base_path, dust_path
