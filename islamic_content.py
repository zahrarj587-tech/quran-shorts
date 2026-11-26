import requests
import random

def get_random_tafsir():
    surah = random.randint(1, 114)
    ayah = random.randint(1, 7) 
    # استخدام API التفسير الميسر من alquran.cloud
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar.muyassar"
    try:
        r = requests.get(url, timeout=10).json()
        if r.get("status") == "OK":
            text = r["data"]["text"]
            surah_name = r["data"]["surah"]["name"]
            return f"📖 تفسير الآية (سورة {surah_name}):\n\n{text}"
    except Exception:
        pass
    return "📖 تفسير الآية غير متاح حالياً."

def get_random_hadith():
    # استخدام API حديث بسيط وسريع
    url = "https://random-hadith-generator.vercel.app/bukhari/"
    try:
        r = requests.get(url, timeout=10).json()
        hadith_text = r["data"]["hadith_english"] # هنخليه انجليزي مؤقتاً لحد ما نلاقي API عربي مستقر
        return f"🕌 حديث نبوي:\n\n{hadith_text}\n\nالمصدر: صحيح البخاري"
    except Exception:
        return "🕌 حديث غير متاح حالياً."

def get_random_quiz():
    # كود تجريبي للسؤال والجواب
    return "❓ سؤال ديني:\n\nما هو الركن الأول من أركان الإسلام؟\n\n✅ الإجابة: شهادة أن لا إله إلا الله وأن محمداً رسول الله."

def get_facebook_post():
    choice = random.choice([get_random_tafsir, get_random_quiz]) # شلت الحديث مؤقتاً عشان الانجليزي
    return choice()

# للتجربة لما تشغل الملف لوحده
if __name__ == "__main__":
    print("--- تجربة جلب محتوى ---")
    print(get_facebook_post())
