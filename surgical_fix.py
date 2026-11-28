import re

with open("run.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. إزالة الكود المحقون بالغلط
content = re.sub(r'import sys\nfrom islamic_content import get_facebook_post.*?sys\.exit\(0\)\n', '', content, flags=re.DOTALL)

# 2. إصلاح السطر المقطوع بتاع التفسير
content = content.replace('tafsir_section = f"', 'tafsir_section = f"\\n📝 {tafsir_source}:\\n{tafsir_text}\\n"')

# 3. إضافة كود البوستات في بداية الملف (عشان لو بوست ينفذ ويقفل، ولو فيديو يكمل عادي)
post_logic = '''import sys
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

# ندور على أول سطر فيه import عشان نحط الكود بعده
lines = content.split('\n')
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith('import ') or line.startswith('from '):
        insert_idx = i + 1
        
lines.insert(insert_idx, post_logic)
content = '\n'.join(lines)

with open("run.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ تم إصلاح الملف بنجاح وجاهز للرفع!")
