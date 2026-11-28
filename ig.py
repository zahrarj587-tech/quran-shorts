# ig.py - نشر الفيديو كـ Reel على انستجرام
import os
import subprocess
import time

import requests

IG_TOK = os.environ.get("IG_ACCESS_TOKEN", "").strip()
IG_ID = os.environ.get("IG_USER_ID", "").strip()
API = "https://graph.facebook.com/v27.0"


def _caption(desc):
    t = desc.replace("#shorts", "").strip()
    if len(t) <= 2200:
        return t
    cut = t[:2200]
    i = cut.rfind("\n")
    return cut[:i] if i > 0 else cut


def _faststart(path):
    out = path.replace(".mp4", "_ig.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", path,
         "-c", "copy", "-movflags", "+faststart", out],
        check=False,
    )
    return out if os.path.exists(out) else path


def _public_url(path):
    with open(path, "rb") as f:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=300,
        )
    link = r.text.strip()
    if r.status_code == 200 and link.startswith("http"):
        return link
    raise RuntimeError(f"catbox {r.status_code}: {link[:200]}")


def _ig_id():
    if IG_ID:
        return IG_ID
    r = requests.get(
        f"{API}/me/assigned_instagram_accounts",
        params={"fields": "id,username", "access_token": IG_TOK},
        timeout=30,
    ).json()
    data = r.get("data") or []
    if data:
        print("IG account:", data[0].get("username"), data[0].get("id"))
        return str(data[0]["id"])
    print("assigned_instagram_accounts empty, trying the page:", r)
    page = os.environ.get("FB_PAGE_ID", "").strip()
    if page:
        p = requests.get(
            f"{API}/{page}",
            params={"fields": "instagram_business_account{id,username}",
                    "access_token": IG_TOK},
            timeout=30,
        ).json()
        iba = p.get("instagram_business_account") or {}
        if iba.get("id"):
            print("IG account (from page):", iba.get("username"), iba["id"])
            return str(iba["id"])
        print("IG: no account linked to the page:", p)
    print("IG: could not find account id, set the secret IG_USER_ID")
    return ""


def publish_reel(video_path, description):
    if not IG_TOK:
        print("Instagram: no token, skipped")
        return None
    try:
        ig_id = _ig_id()
        if not ig_id:
            return None
        url = _public_url(_faststart(video_path))
        print("IG video URL:", url)
        c = requests.post(
            f"{API}/{ig_id}/media",
            data={
                "media_type": "REELS",
                "video_url": url,
                "caption": _caption(description),
                "access_token": IG_TOK,
            },
            timeout=60,
        ).json()
        cid = c.get("id")
        if not cid:
            print("IG container rejected:", c)
            return None
        for _ in range(40):
            time.sleep(15)
            s = requests.get(
                f"{API}/{cid}",
                params={"fields": "status_code", "access_token": IG_TOK},
                timeout=30,
            ).json()
            code = s.get("status_code")
            print("IG status:", code)
            if code == "FINISHED":
                break
            if code in ("ERROR", "EXPIRED"):
                print("IG processing failed:", s)
                return None
        else:
            print("IG processing took too long")
            return None
        p = requests.post(
            f"{API}/{ig_id}/media_publish",
            data={"creation_id": cid, "access_token": IG_TOK},
            timeout=60,
        ).json()
        if p.get("id"):
            print("Instagram OK:", p["id"])
            return p["id"]
        print("IG publish rejected:", p)
    except Exception as e:
        print("Instagram error:", e)
    return None
