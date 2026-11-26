import os

# 1. تعديل slot.py
slot_code = '''import json, os, datetime

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
        f.write(f"slot={slot}\\ngo={'true' if slot else 'false'}\\ntype={slot_type}\\n")
'''
with open("slot.py", "w", encoding="utf-8") as f:
    f.write(slot_code)

# 2. تعديل run.py (حقن كود البوست)
with open("run.py", "r", encoding="utf-8") as f:
    run_content = f.read()

header_code = '''
import sys
from islamic_content import get_facebook_post

slot_type = os.environ.get("SLOT_TYPE", "video")
if slot_type == "post":
    print("⏳ جاري تجهيز بوست فيسبوك...")
    pid = os.environ.get("FB_PAGE_ID")
    tok = os.environ.get("FB_PAGE_TOKEN")
    if pid and tok:
        msg = get_facebook_post()
        try:
            r = requests.post(f"https://graph.facebook.com/v23.0/{pid}/feed", data={"message": msg, "access_token": tok}, timeout=30)
            if r.status_code == 200:
                print("✅ Facebook Post OK")
            else:
                print(f"❌ فشل النشر: {r.text}")
        except Exception as e:
            print(f"❌ خطأ: {e}")
    try:
        st = json.load(open("stats.json"))
    except:
        st = {"log": []}
    st.setdefault("slots", []).append(os.environ.get("SLOT", ""))
    st["slots"] = st["slots"][-60:]
    json.dump(st, open("stats.json", "w"), ensure_ascii=False)
    sys.exit(0)
'''

if "from islamic_content import get_facebook_post" not in run_content:
    lines = run_content.split('\\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
    lines.insert(insert_idx, header_code)
    with open("run.py", "w", encoding="utf-8") as f:
        f.write('\\n'.join(lines))

# 3. تعديل post.yml
yml_path = ".github/workflows/post.yml"
if os.path.exists(yml_path):
    with open(yml_path, "r", encoding="utf-8") as f:
        yml_content = f.read()
    if "SLOT_TYPE:" not in yml_content:
        yml_content = yml_content.replace("SLOT: ${{ steps.slot.outputs.slot }}", "SLOT: ${{ steps.slot.outputs.slot }}\\n          SLOT_TYPE: ${{ steps.slot.outputs.type }}")
        with open(yml_path, "w", encoding="utf-8") as f:
            f.write(yml_content)

print("✅ تم تعديل كل الملفات (slot.py, run.py, post.yml) بنجاح!")
