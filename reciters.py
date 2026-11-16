import json
import os
import requests

# مسار ملف الـ JSON
JSON_PATH = os.path.join(os.path.dirname(__file__), "reciters.json")

def load_reciters():
    if not os.path.exists(JSON_PATH):
        return {"Alafasy_128kbps": "مشاري العفاسي"} # fallback
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
    return a[n % len(a)]

if __name__ == "__main__":
    print("Total reciters loaded:", len(RECITERS))
