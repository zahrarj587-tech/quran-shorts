import json
import os
import requests
import random

JSON_PATH = os.path.join(os.path.dirname(__file__), "reciters.json")

# تم تحديث القائمة لتشمل أصوات الخشوع والإبداع فقط
KHUSHOO_KEYS = [
    "Yasser_Ad-Dussary_128kbps",
    "Idrees_Abkar_128kbps",
    "Fares_Abbad_64kbps",
    "Muhammad_Al_Luhaidan_128kbps",
    "Khalid_Al_Jalil_128kbps",
    "Abdullaah_3awwaad_Al-Juhaynee_128kbps",
    "Mohammad_al_Tablaway_128kbps",
    "Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net",
    "Nasser_Alqatami_128kbps",
    "Muhammad_Abdulkareem_128kbps",
    "Abdul_Basit_Mujawwad_128kbps"
]

def load_reciters():
    if not os.path.exists(JSON_PATH):
        return {"Alafasy_128kbps": "مشاري العفاسي"}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

RECITERS = load_reciters()
_ok = None

def available():
    global _ok
    if _ok is None:
        _ok = []
        for k in RECITERS:
            try:
                r = requests.get(f"https://everyayah.com/data/{k}/001001.mp3", stream=True, timeout=20)
                if r.status_code == 200:
                    _ok.append(k)
                r.close()
            except Exception:
                pass
        if not _ok:
            _ok = ["Yasser_Ad-Dussary_128kbps"]
    return _ok

def pick(n):
    a = available()
    avail_khushoo = [k for k in a if k in KHUSHOO_KEYS]
    avail_tarteel = [k for k in a if k not in KHUSHOO_KEYS]

    if not avail_khushoo:
        return random.Random(n).choice(avail_tarteel)
    if not avail_tarteel:
        return random.Random(n).choice(avail_khushoo)

    # التبديل: فيديو خشوع قوي، وبعده ترتيل هاديء
    if n % 2 == 0:
        return random.Random(n).choice(avail_khushoo)
    else:
        return random.Random(n).choice(avail_tarteel)
