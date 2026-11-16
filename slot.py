import json, os, urllib.request, datetime, zoneinfo

# مسار ملف الـ JSON
JSON_PATH = os.path.join(os.path.dirname(__file__), "slots.json")

def load_offsets():
    if not os.path.exists(JSON_PATH):
        return {"Sunrise": 0, "Dhuhr": 0, "Asr": 0, "Isha": 30}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

OFFSETS = load_offsets()
tz = zoneinfo.ZoneInfo("Africa/Cairo")
now = datetime.datetime.now(tz)
url = "https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
T = json.load(urllib.request.urlopen(url, timeout=30))["data"]["timings"]
today = now.strftime("%Y-%m-%d")
slots = []

for k, off in OFFSETS.items():
    if k not in T:
        continue # لو فيه اسم مش موجود في الـ API يتخطاه بأمان
    h, m = map(int, T[k][:5].split(":"))
    t = now.replace(hour=h, minute=m, second=0, microsecond=0) + datetime.timedelta(minutes=off)
    slots.append((f"{today}-{k}", t))
    print(k, t.strftime("%H:%M"))

try:
    done = set(json.load(open("stats.json")).get("slots", []))
except Exception:
    done = set()

slot = ""
for sid, t in slots:
    if sid not in done and t <= now < t + datetime.timedelta(hours=3):
        slot = sid
        break

if os.environ.get("EVENT") == "workflow_dispatch" and not slot:
    slot = f"{today}-manual-{now:%H%M}"

print("now", now.strftime("%H:%M"), "->", slot or "no post")

# الشرط ده عشان يشتغل محلياً بدون أخطاء لو مفيش GITHUB_OUTPUT
if "GITHUB_OUTPUT" in os.environ:
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"slot={slot}\ngo={'true' if slot else 'false'}\n")
