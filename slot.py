import json, os, urllib.request, datetime, zoneinfo
OFFSETS = {"Sunrise": 0, "Dhuhr": 0, "Asr": 0, "Isha": 30}
tz = zoneinfo.ZoneInfo("Africa/Cairo")
now = datetime.datetime.now(tz)
url = "https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
T = json.load(urllib.request.urlopen(url, timeout=30))["data"]["timings"]
today = now.strftime("%Y-%m-%d")
slots = []
for k, off in OFFSETS.items():
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
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"slot={slot}\ngo={'true' if slot else 'false'}\n")
