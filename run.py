import json, os, datetime, requests
from make import make_chunk
from reciters import pick, RECITERS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

p = json.load(open("progress.json"))
n = p.get("n", 0)
rc = pick(n)
video, title, nxt = make_chunk(p["surah"], p["ayah"], rc)
print("Made:", title)

# 1. يوتيوب
creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YT_CLIENT_ID"],
    client_secret=os.environ["YT_CLIENT_SECRET"])
yt = build("youtube", "v3", credentials=creds)
r = yt.videos().insert(part="snippet,status",
    body={"snippet": {"title": title + " #Shorts",
                      "description": title + "\n\n#قرآن #shorts",
                      "categoryId": "22"},
          "status": {"privacyStatus": "public",
                     "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload(video, resumable=True)).execute()
print("YouTube OK:", r["id"])

# 2. فيسبوك (لو المفاتيح موجودة)
pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
if pid and tok:
    g = f"https://graph.facebook.com/v21.0/{pid}/video_reels"
    s = requests.post(g, data={"upload_phase": "start", "access_token": tok}).json()
    data = open(video, "rb").read()
    requests.post(s["upload_url"], data=data, headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data))})
    requests.post(g, data={"upload_phase": "finish", "video_id": s["video_id"], "video_state": "PUBLISHED", "description": title + "\n\n#قرآن", "access_token": tok})
    print("Facebook OK")

# 3. تحديث التقدم
nxt["n"] = n + 1
json.dump(nxt, open("progress.json", "w"))

try:
    st = json.load(open("stats.json"))
except Exception:
    st = {"log": []}
st["log"].append({"t": datetime.datetime.utcnow().isoformat() + "Z",
    "title": title, "reciter": RECITERS.get(rc, rc), "yt": r["id"]})
st["next"] = {"surah": nxt["surah"], "ayah": nxt["ayah"]}
st["slots"] = (st.get("slots", []) + [os.environ.get("SLOT", "")])[-60:]
json.dump(st, open("stats.json", "w"), ensure_ascii=False)
