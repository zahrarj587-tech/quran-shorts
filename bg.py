import os
import math
from PIL import Image, ImageDraw, ImageFilter

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    # لون خلفية كحلي ملكي غامق جداً (فخم)
    bg_color = (11, 19, 43) 
    
    img = Image.new("RGB", (1080, 1920), bg_color)
    draw = ImageDraw.Draw(img)
    
    # رسم زخرفة إسلامية هندسية دقيقة جداً في الخلفية (لون كحلي أفتح شوية)
    step = 150
    for x in range(-step, 1080 + step, step):
        for y in range(-step, 1920 + step, step):
            points = []
            for i in range(16):
                angle = i * math.pi / 8
                radius = 50 if i % 2 == 0 else 20
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, outline=(23, 37, 84), width=2)

    # تمويه خفيف عشان الزخرفة تبان كأنها نقش في الخلفية مش خطوط حادة
    img = img.filter(ImageFilter.GaussianBlur(1))
    
    img.save(base_path)
    
    # صورة الغبار شفافة (عشان الكود ميدربش)
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    
    return base_path, dust_path
