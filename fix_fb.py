import sys

try:
    with open("run.py", "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = 'if pid and tok:'
    end_marker = '# 3. تحديث'

    if start_marker in content and end_marker in content:
        part1 = content.split(start_marker)[0]
        part2 = content.split(end_marker)[1]
        
        new_block = '''if pid and tok:
    try:
        print("⏳ جاري الرفع على فيسبوك...")
        g = f"https://graph.facebook.com/v23.0/{pid}/video_reels"
        
        s = requests.post(g, data={"upload_phase": "start", "access_token": tok}, timeout=30).json()
        
        if "upload_url" not in s:
            print(f"❌ فيسبوك رفض بدء الرفع: {s}")
        else:
            with open(video, "rb") as f_vid:
                data = f_vid.read()
            upload_res = requests.post(
                s["upload_url"], 
                data=data, 
                headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data))},
                timeout=300
            )
            
            if upload_res.status_code == 200:
                finish_res = requests.post(g, data={
                    "upload_phase": "finish", 
                    "video_id": s["video_id"], 
                    "video_state": "PUBLISHED", 
                    "description": description, 
                    "access_token": tok
                }, timeout=30).json()
                
                if "id" in finish_res or "success" in finish_res:
                    print("✅ Facebook OK")
                else:
                    print(f"❌ فيسبوك رفض إنهاء الرفع: {finish_res}")
            else:
                print(f"❌ فشل رفع الفيديو لفيسبوك: {upload_res.text}")
                
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء النشر على فيسبوك: {e}")

'''
        new_content = part1 + new_block + end_marker + part2
        
        with open("run.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ تم تعديل كود فيسبوك بنجاح! جاهز للرفع.")
    else:
        print("❌ لم أجد بداية أو نهاية الكود. تأكد من وجود 'if pid and tok:' و '# 3. تحديث'")
        
except Exception as e:
    print(f"❌ حدث خطأ: {e}")
