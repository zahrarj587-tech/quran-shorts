import json, os, datetime, requests, sys
from make import make_chunk
from reciters import pick, RECITERS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
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




p = json.load(open("progress.json"))
n = p.get("n", 0)
rc = pick(n)
video, title, nxt = make_chunk(p["surah"], p["ayah"], rc)
print("Made:", title)

# --- وضع التجربة والتحميل المباشر ---
if os.environ.get("TEST_MODE") == "true":
    print("🚧 TEST MODE: Uploading video for quick download...")
    try:
        url = "https://catbox.moe/user/api.php"
        data = {"reqtype": "fileupload"}
        with open(video, "rb") as f:
            files = {"fileToUpload": f}
            response = requests.post(url, data=data, files=files, timeout=60)
        if response.status_code == 200 and response.text.startswith("https://"):
            video_url = response.text.strip()
            print(f"Video URL: {video_url}")
            json.dump({"url": video_url, "time": datetime.datetime.now().isoformat()}, open("test_video.json", "w"))
        else:
            print(f"Upload failed. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error uploading to catbox: {e}")
    sys.exit(0)
# ------------------------------------

# جلب اسم القارئ وعمل هاشتاج منه
reciter_name = RECITERS.get(rc, rc)
reciter_hashtag = "#" + reciter_name.replace(" ", "_")

# جلب التفسير (تفسير الميسر)
tafsir_section = ""
try:
    tafsir_url = f"https://api.alquran.cloud/v1/ayah/{p['surah']}:{p['ayah']}/ar.muyassar"
    tafsir_data = requests.get(tafsir_url, timeout=10).json()["data"]
    tafsir_text = tafsir_data["text"]
    tafsir_source = tafsir_data["edition"]["name"]
    tafsir_section = f"\n📖 تفسير الآية ({tafsir_source}):\n{tafsir_text}"
except Exception as e:
    print("Tafsir fetch failed:", e)

# تجهيز الوصف المفصل
description = (
    f"{title}\n\n"
    f"🎙️ بصوت الشيخ: {reciter_name}\n"
    f"{tafsir_section}\n\n"
    f"#قرآن #shorts #المصحف {reciter_hashtag}"
)

# 1. يوتيوب
creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YT_CLIENT_ID"],
    client_secret=os.environ["YT_CLIENT_SECRET"])
yt = build("youtube", "v3", credentials=creds)
r = yt.videos().insert(part="snippet,status",
    body={"snippet": {"title": title + " #Shorts",
                      "description": description,
                      "categoryId": "22"},
          "status": {"privacyStatus": "public",
                     "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload(video, resumable=True)).execute()
print("YouTube OK:", r["id"])

# 2. فيسبوك (لو المفاتيح موجودة)
pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
if pid and tok:
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

# 3. تحديث التقدم
nxt["n"] = n + 1
json.dump(nxt, open("progress.json", "w"))

try:
    st = json.load(open("stats.json"))
except Exception:
    st = {"log": []}
st["log"].append({"t": datetime.datetime.utcnow().isoformat() + "Z",
    "title": title, "reciter": reciter_name, "yt": r["id"]})
st["next"] = {"surah": nxt["surah"], "ayah": nxt["ayah"]}
st["slots"] = (st.get("slots", []) + [os.environ.get("SLOT", "")])[-60:]
json.dump(st, open("stats.json", "w"), ensure_ascii=False)
