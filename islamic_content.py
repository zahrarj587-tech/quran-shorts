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
    MAX_AYAHS = 3      # أقصى عدد آيات في البوست
    MAX_CHARS = 700    # أقصى طول (آية + تفسير) في البوست

    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"surah": 2, "ayah": 1}

    surah = state["surah"]
    ayah = state["ayah"]

    # تخطي سورة الفاتحة
    if surah == 1:
        surah, ayah = 2, 1

    def fetch(s, a):
        url = f"https://api.alquran.cloud/v1/ayah/{s}:{a}/editions/quran-uthmani,ar.muyassar"
        r = requests.get(url, timeout=10).json()
        if r.get("status") != "OK":
            return None
        return r["data"]

    try:
        data = fetch(surah, ayah)
        if data is None:
            # خلصت السورة: ننتقل للسورة اللي بعدها
            surah += 1
            ayah = 1
            if surah > 114:
                surah = 2
            data = fetch(surah, ayah)
            if data is None:
                return "📖 التفسير غير متاح حالياً."

        surah_name = data[0]["surah"]["name"]
        ayat = [(data[0]["numberInSurah"], data[0]["text"], data[1]["text"])]
        total = len(data[0]["text"]) + len(data[1]["text"])
        next_ayah = ayat[0][0] + 1

        # تجميع الآيات القصيرة
        while len(ayat) < MAX_AYAHS:
            nxt = fetch(surah, next_ayah)
            if nxt is None:
                break
            add = len(nxt[0]["text"]) + len(nxt[1]["text"])
            if total + add > MAX_CHARS:
                break
            ayat.append((nxt[0]["numberInSurah"], nxt[0]["text"], nxt[1]["text"]))
            total += add
            next_ayah += 1

        # تحديث الحالة للآية التالية
        next_state = {"surah": surah, "ayah": next_ayah}
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(next_state, f, ensure_ascii=False)

        # التنسيق
        ayah_part = " ".join(f"{t} ﴿{to_arabic_num(n)}﴾" for n, t, _ in ayat)
        if len(ayat) == 1:
            tafsir_part = ayat[0][2]
        else:
            tafsir_part = "\n".join(f"({to_arabic_num(n)}) {tf}" for n, _, tf in ayat)

        post_text = f"({surah_name})\n\n{ayah_part}\n\n📝 التفسير الميسر:\n{tafsir_part}"
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
