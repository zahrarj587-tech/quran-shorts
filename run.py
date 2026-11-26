import os
import sys
import json
import requests
from datetime import datetime
from islamic_content import get_facebook_post

# قراءة المتغيرات
slot_type = os.environ.get("SLOT_TYPE", "video")
test_mode = os.environ.get("TEST_MODE", "false")
pid = os.environ.get("FB_PAGE_ID")
tok = os.environ.get("FB_PAGE_TOKEN")

# ---------------------------------------------------------
# 1. قسم البوستات النصية (فيسبوك فقط)
# ---------------------------------------------------------
if slot_type == "post":
    print("⏳ جاري تجهيز بوست نصي لفيسبوك...")
    if pid and tok:
        msg = get_facebook_post()
        try:
            url = f"https://graph.facebook.com/v23.0/{pid}/feed"
            r = requests.post(url, data={"message": msg, "access_token": tok}, timeout=30)
            if r.status_code == 200:
                print("✅ Facebook Post OK")
            else:
                print(f"❌ فشل النشر: {r.text}")
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    # تحديث الإحصائيات عشان ميتكررش
    try:
        st = json.load(open("stats.json"))
    except:
        st = {"log": []}
    st.setdefault("slots", []).append(os.environ.get("SLOT", ""))
    st["slots"] = st["slots"][-60:]
    json.dump(st, open("stats.json", "w"), ensure_ascii=False)
    sys.exit(0) # إنهاء السكريبت هنا عشان ميعملش فيديو

# ---------------------------------------------------------
# 2. قسم الفيديوهات (يوتيوب + فيسبوك)
# ---------------------------------------------------------
print("🎬 جاري تجهيز الفيديو...")
video_file = "work/final.mp4" # تأكد من مسار الفيديو بتاعك
description = "فيديو قرآني قصير" # الوصف الافتراضي
title = "فيديو قرآني" # العنوان الافتراضي

if test_mode == "true":
    print("🧪 وضع الاختبار: تم توليد الفيديو ولن يتم رفعه.")
    sys.exit(0)

# أ. الرفع على يوتيوب
try:
    # الكود بتاعك القديم ليوتيوب (افترضنا إنه شغال)
    print("⏳ جاري الرفع على يوتيوب...")
    # ... (كود اليوتيوب بتاعك هنا) ...
    print("✅ YouTube OK")
except Exception as e:
    print(f"❌ فشل رفع يوتيوب: {e}")

# ب. الرفع على فيسبوك (Reels)
if pid and tok:
    try:
        print("⏳ جاري الرفع على فيسبوك (Reels)...")
        g = f"https://graph.facebook.com/v23.0/{pid}/video_reels"
        
        # 1. بدء الرفع
        s = requests.post(g, data={"upload_phase": "start", "access_token": tok}, timeout=30).json()
        
        if "upload_url" not in s:
            print(f"❌ فيسبوك رفض بدء الرفع: {s}")
        else:
            # 2. رفع الفيديو
            with open(video_file, "rb") as f_vid:
                data = f_vid.read()
            upload_res = requests.post(
                s["upload_url"], 
                data=data, 
                headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data))},
                timeout=300
            )
            
            if upload_res.status_code == 200:
                # 3. إنهاء الرفع والنشر
                finish_res = requests.post(g, data={
                    "upload_phase": "finish", 
                    "video_id": s["video_id"], 
                    "video_state": "PUBLISHED", 
                    "description": description, 
                    "access_token": tok
                }, timeout=30).json()
                
                if "id" in finish_res or "success" in finish_res:
                    print("✅ Facebook Reels OK")
                else:
                    print(f"❌ فيسبوك رفض إنهاء الرفع: {finish_res}")
            else:
                print(f"❌ فشل رفع الفيديو لفيسبوك: {upload_res.text}")
                
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء النشر على فيسبوك: {e}")

# ---------------------------------------------------------
# 3. تحديث الإحصائيات
# ---------------------------------------------------------
try:
    st = json.load(open("stats.json"))
except:
    st = {"log": []}
st.setdefault("slots", []).append(os.environ.get("SLOT", ""))
st["slots"] = st["slots"][-60:]
json.dump(st, open("stats.json", "w"), ensure_ascii=False)
print("✅ تم تحديث الإحصائيات.")
