import json
import os
import requests
import random

JSON_PATH = os.path.join(os.path.dirname(__file__), "reciters.json")

# قائمة القراء اللي صوتهم خشوع ومؤثر جداً
KHUSHOO_KEYS = [
    "Abdul_Basit_Mujawwad_128kbps",
    "Minshawy_Mujawwad_192kbps",
    "Husary_128kbps_Mujawwad",
    "Mustafa_Ismail_48kbps",
    "Mahmoud_Ali_Al_Banna_32kbps",
    "Fares_Abbad_64kbps",
    "Muhammad_Abdulkareem_128kbps",
    "Yasser_Ad-Dussary_128kbps",
    "Nasser_Alqatami_128kbps",
    "Idrees_Abkar_128kbps",
    "Salah_Al_Budair_128kbps",
    "Abdullah_Matroud_128kbps"
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
            _ok = ["Alafasy_128kbps"]
    return _ok

def pick(n):
    a = available()
    
    # نفصل القراء المتاحين (اللي شغالين) لنوعين
    avail_khushoo = [k for k in a if k in KHUSHOO_KEYS]
    avail_tarteel = [k for k in a if k not in KHUSHOO_KEYS]

    # لو إنت حذفت كل قراء الخشوع من الداشبورد، هيختار ترتيل
    if not avail_khushoo:
        return random.Random(n).choice(avail_tarteel)
    # لو إنت حذفت كل قراء الترتيل، هيختار خشوع
    if not avail_tarteel:
        return random.Random(n).choice(avail_khushoo)

    # التبديل: لو رقم الفيديو زوجي (0, 2, 4) نختار خشوع، لو فردي (1, 3, 5) نختار ترتيل
    if n % 2 == 0:
        return random.Random(n).choice(avail_khushoo)
    else:
        return random.Random(n).choice(avail_tarteel)
