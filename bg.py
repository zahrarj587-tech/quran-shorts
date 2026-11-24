import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    # ألوان فخمة (زمردي غامق مع ذهبي)
    bg_color = (8, 38, 34) # Deep Emerald
    gold_color = (212, 175, 55) # Golden
    
    img = Image.new("RGB", (1080, 1920), bg_color)
    draw = ImageDraw.Draw(img)
    
    # رسم زخرفة إسلامية هندسية في الخلفية (نجوم متداخلة)
    step = 200
    for x in range(-step, 1080 + step, step):
        for y in range(-step, 1920 + step, step):
            # نجمة ثمانية
            points = []
            for i in range(16):
                angle = i * math.pi / 8
                radius = 80 if i % 2 == 0 else 35
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, outline=(20, 60, 50), width=2)

    # تمويه خفيف جداً للخلفية عشان تبان زي "نقشة" مش خطوط حادة
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    
    # إضافة إضاءة دائرية (Vignette) عشان النص يبرز
    overlay = Image.new("L", (1080, 1920), 0)
    o_draw = ImageDraw.Draw(overlay)
    o_draw.ellipse([-200, 200, 1280, 1720], fill=100)
    overlay = overlay.filter(ImageFilter.GaussianBlur(150))
    
    # مزج الإضاءة مع الخلفية
    dark_bg = Image.new("RGB", (1080, 1920), (3, 15, 12))
    img = Image.composite(img, dark_bg, overlay)
    
    img.save(base_path)
    
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    
    return base_path, dust_path
