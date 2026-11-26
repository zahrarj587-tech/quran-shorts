import json, os, datetime

now = datetime.datetime.utcnow() + datetime.timedelta(hours=2) # توقيت مصر
today = now.strftime("%Y-%m-%d")

slots = []
try:
    with open("slots.json", "r") as f:
        data = json.load(f)
        for item in data:
            time_str = item["time"]
            stype = item.get("type", "video")
            h, m = map(int, time_str.split(":"))
            t = now.replace(hour=h, minute=m, second=0, microsecond=0)
            sid = f"{today}-{time_str}"
            slots.append((sid, t, stype))
except Exception as e:
    print("Error parsing slots.json:", e)

try:
    done = set(json.load(open("stats.json")).get("slots", []))
except Exception:
    done = set()

slot = ""
slot_type = ""
for sid, t, stype in slots:
    if sid not in done and t <= now < t + datetime.timedelta(hours=3):
        slot = sid
        slot_type = stype
        break

if os.environ.get("FORCE") == "true" and not slot:
    slot = f"{today}-manual-{now:%H%M}"
    slot_type = "video"

print("now", now.strftime("%H:%M"), "->", slot or "no post", "| type:", slot_type)

if "GITHUB_OUTPUT" in os.environ:
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"slot={slot}\ngo={'true' if slot else 'false'}\ntype={slot_type}\n")
