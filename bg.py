import os
import math
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageStat

W, H = 1080, 1920

# خلفيات متأكدين منها صورة صورة: مساجد ومناظر طبيعية ليلية، من غير أشخاص ولا حيوانات
# المصدر Pexels (صور مجانية الاستخدام) - من غير بحث عشوائي عشان ميجيبش صور مش مناسبة
BACKGROUNDS = [
    # مسجد من جوه - محراب
    "https://images.pexels.com/photos/34219158/pexels-photo-34219158.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # المسجد الأزرق من جوه - قبوات
    "https://images.pexels.com/photos/17186766/pexels-photo-17186766.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # مسجد من جوه - فيروزي
    "https://images.pexels.com/photos/33881860/pexels-photo-33881860.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # قبة مسجد من جوه
    "https://images.pexels.com/photos/22613910/pexels-photo-22613910.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # مئذنة مسجد وقت الغروب مع هلال
    "https://images.pexels.com/photos/31316303/pexels-photo-31316303.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # صحراء تحت النجوم
    "https://images.pexels.com/photos/35548672/pexels-photo-35548672.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # رمال صحراء بالليل
    "https://images.pexels.com/photos/13620627/pexels-photo-13620627.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # سماء صحراء مليانة نجوم
    "https://images.pexels.com/photos/5955002/pexels-photo-5955002.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # درب التبانة فوق جبال
    "https://images.pexels.com/photos/28146402/pexels-photo-28146402.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # درب التبانة فوق جبال ٢
    "https://images.pexels.com/photos/3213577/pexels-photo-3213577.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # درب التبانة فوق جبل ثلجي
    "https://images.pexels.com/photos/5707111/pexels-photo-5707111.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
    # بحر غامق وقت الغروب
    "https://images.pexels.com/photos/32635228/pexels-photo-32635228.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop",
]


def _fallback_bg(base_path):
    # الخلفية القديمة (كحلي بزخرفة) - بنستخدمها لو النت وقع أو التحميل فشل
    bg_color = (11, 19, 43)
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    step = 150
    for x in range(-step, W + step, step):
        for y in range(-step, H + step, step):
            points = []
            for i in range(16):
                angle = i * math.pi / 8
                radius = 50 if i % 2 == 0 else 20
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, outline=(23, 37, 84), width=2)
    img = img.filter(ImageFilter.GaussianBlur(1))
    img.save(base_path)


def _load_photo(seed, out_dir):
    # بيختار صورة من القائمة بالتناوب حسب رقم الآية، وبينزّلها مرة واحدة في فولدر الشغل
    url = BACKGROUNDS[seed % len(BACKGROUNDS)]
    photo_id = url.split("/")[4]
    path = os.path.join(out_dir, f"bg_{photo_id}.jpg")
    if not os.path.exists(path):
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return Image.open(path).convert("RGB")


def _darken(img):
    # بيقص الصورة على مقاس الفيديو، يعمل تمويه خفيف، ويغمّقها عشان الكلام يبان
    img = ImageOps.fit(img, (W, H))
    img = img.filter(ImageFilter.GaussianBlur(2))
    lum = ImageStat.Stat(img.convert("L")).mean[0]
    factor = 0.15 if lum <= 65 else min(0.85, 1 - 65 / lum)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(img, black, factor)


def make_bg(seed, out_dir):
    base_path = os.path.join(out_dir, "base.png")
    dust_path = os.path.join(out_dir, "dust.png")

    try:
        img = _darken(_load_photo(seed, out_dir))
        img.save(base_path)
    except Exception as e:
        print("تعذر تحميل صورة الخلفية، هنستخدم الزخرفة الافتراضية:", e)
        _fallback_bg(base_path)

    # صورة الغبار شفافة (عشان الكود ميدربش)
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dust.save(dust_path)

    return base_path, dust_path
