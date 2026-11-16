import json, os, requests
from make import make_chunk
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

p = json.load(open("progress.json"))
from reciters import pick
n = p.get("n", 0)
video, title, nxt = make_chunk(p["surah"], p["ayah"], pick(n))
nxt["n"] = n + 1
print("Made:", title)

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

pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
if pid and tok:
    g = f"https://graph.facebook.com/v21.0/{pid}/video_reels"
    s = requests.post(g, data={"upload_phase": "start", "access_token": tok}).json()
    data = open(video, "rb").read()
    requests.post(s["upload_url"], data=data, headers={
        "Authorization": f"OAuth {tok}", "offset": "0",
        "file_size": str(len(data))})
    requests.post(g, data={"upload_phase": "finish", "video_id": s["video_id"],
        "video_state": "PUBLISHED", "description": title + "\n\n#قرآن",
        "access_token": tok})
    print("Facebook OK")

json.dump(nxt, open("progress.json", "w"))
