import os
from PIL import Image, ImageDraw, ImageFilter

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    # 1. عمل خلفية ورقية (لون بيج فاخر)
    # لون الورق: (244, 235, 215)
    img = Image.new("RGB", (1080, 1920), (244, 235, 215))
    draw = ImageDraw.Draw(img)
    
    # إضافة إضاءة خفيفة في النص وتغميق الحواف (Vignette)
    for i in range(200):
        alpha = int(255 * (1 - i/200))
        draw.rectangle([i, i, 1080-i, 1920-i], outline=(220, 200, 170, alpha), width=2)
        
    # إضافة لمسة "نسيج الورق" (Noise خفيف جداً)
    noise = Image.effect_noise((1080, 1920), 15).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(1))
    img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.05)
    
    img.save(base_path)
    
    # صورة الغبار شفافة عشان الكود ميدربش
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    
    return base_path, dust_path
