import os
import random
import requests
from PIL import Image, ImageEnhance, ImageFilter
from urllib.parse import quote

def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")
    
    rng = random.Random(seed)
    
    # قائمة أوصاف (Prompts) واقعية وآمنة تماماً - بدون أي بشر
    prompts = [
        "A realistic photograph of a clear night sky full of stars and a bright Milky Way galaxy, no people, no humans, serene atmosphere, high resolution, 8k",
        "A realistic photograph of soft white clouds in a blue sky during golden hour, warm sunlight, peaceful, no people, no humans, highly detailed",
        "A realistic photograph of majestic mountains covered in snow under a clear blue sky, breathtaking landscape, no people, no humans, 8k resolution",
        "A realistic photograph of a calm ocean at sunset, gentle waves, colorful sky, serene and peaceful, no people, no humans, photorealistic",
        "A realistic photograph of a green forest with sunlight filtering through the trees, misty morning atmosphere, no people, no humans, high quality",
        "A realistic photograph of a desert landscape with sand dunes at sunset, warm colors, clear sky, no people, no humans, cinematic lighting",
        "A realistic photograph of a beautiful mosque interior with intricate Islamic architecture, soft light, peaceful, no people, no humans, 8k"
    ]
    
    prompt = rng.choice(prompts)
    
    # استخدام Pollinations API لتوليد الصورة
    try:
        # ترميز الوصف ليناسب الرابط
        encoded_prompt = quote(prompt)
        # إضافة معلمات لضمان الجودة والخلو من العلامات المائية
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true&seed={seed}"
        
        print(f"Generating AI background with prompt: {prompt[:50]}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status() # التأكد من نجاح الطلب
        
        # حفظ الصورة التي تم توليدها
        with open(base_path, "wb") as f:
            f.write(response.content)
            
        img = Image.open(base_path).convert("RGB")
        
        # معالجة الصورة: قصها 9:16 وتعتيمها قليلاً لبروز النص
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
        # تعتيم خفيف (20%) للحفاظ على وضوح الصورة مع إبراز النص
        img = ImageEnhance.Brightness(img).enhance(0.8)
        img.save(base_path)
        
        print("AI background generated successfully.")
        
    except Exception as e:
        print(f"Failed to generate AI background: {e}")
        # في حال فشل التوليد، نستخدم خلفية احتياطية آمنة (لون داكن)
        img = Image.new("RGB", (1080, 1920), (15, 23, 42))
        img.save(base_path)
    
    # إنشاء صورة الغبار الشفافة (لا تزال مطلوبة للكود الحالي)
    dust = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dust.save(dust_path)
    
    return base_path, dust_path
