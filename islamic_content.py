import requests
import json
import os

# دالة تحويل الأرقام لعربية (عشان رقم الآية يبقى زي المصحف)
def to_arabic_num(number):
    arabic_nums = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩'}
    return ''.join(arabic_nums.get(d, d) for d in str(number))

# 1. دالة التفسير (بشكل دوري بالترتيب)
def get_sequential_tafsir():
    state_file = "tafsir_state.json"
    
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"surah": 1, "ayah": 1} 
        
    surah = state["surah"]
    ayah = state["ayah"]
    
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,ar.muyassar"
    
    try:
        r = requests.get(url, timeout=10).json()
        
        if r.get("status") != "OK":
            surah += 1
            ayah = 1
            if surah > 114:
                surah = 1
            
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-uthmani,ar.muyassar"
            r = requests.get(url, timeout=10).json()
            
            if r.get("status") != "OK":
                return "📖 التفسير غير متاح حالياً."
                
        ayah_text = r["data"][0]["text"]
        tafsir_text = r["data"][1]["text"]
        surah_name = r["data"][0]["surah"]["name"]
        ayah_num = r["data"][0]["numberInSurah"]
        
        # تحويل الرقم لعربي
        ayah_num_ar = to_arabic_num(ayah_num)
        
        # تحديث الحالة للآية اللي بعدها
        next_state = {"surah": surah, "ayah": ayah + 1}
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(next_state, f, ensure_ascii=False)
            
        # التنسيق الجديد (السورة فوق والآية بين الأقواس المزخرفة)
        post_text = f"({surah_name})\n\n﴿ {ayah_text} ﴾ ﴿{ayah_num_ar}﴾\n\n📝 التفسير الميسر:\n{tafsir_text}"
        return post_text
        
    except Exception as e:
        print(f"Error: {e}")
        return "📖 التفسير غير متاح حالياً."

# 2. دالة التوجيه (البوستات كلها هتكون آيات)
def get_facebook_post():
    print("🔄 جاري جلب الآية التالية من القرآن...")
    return get_sequential_tafsir()

if __name__ == "__main__":
    print(get_facebook_post())
