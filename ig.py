# ig.py - نشر الفيديو كـ Reel على انستجرام
import os
import subprocess
import time

import requests

IG_TOK = os.environ.get("IG_ACCESS_TOKEN", "").strip()
IG_ID = os.environ.get("IG_USER_ID", "").strip()
API = "https://graph.facebook.com/v27.0"
UPLOAD = "https://rupload.facebook.com/ig-api-upload/v27.0"


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


def _container_upload(ig_id, path, caption):
    try:
        c = requests.post(
            f"{API}/{ig_id}/media",
            data={"media_type": "REELS", "upload_type": "resumable",
                  "caption": caption, "access_token": IG_TOK},
            timeout=60,
        ).json()
        cid = c.get("id")
        if not cid:
            print("direct upload not available:", c)
            return None
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            data = f.read()
        up = requests.post(
            f"{UPLOAD}/{cid}",
            headers={"Authorization": f"OAuth {IG_TOK}", "offset": "0",
                     "file_size": str(size)},
            data=data,
            timeout=600,
        )
        if up.status_code != 200:
            print("direct upload failed:", up.status_code, up.text[:300])
            return None
        print("direct upload OK:", size, "bytes")
        return cid
    except Exception as e:
        print("direct upload error:", e)
        return None


def _public_url(path):
    name = os.path.basename(path)
    try:
        with open(path, "rb") as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload",
                              files={"file": (name, f, "video/mp4")},
                              timeout=300)
        j = r.json()
        url = ((j.get("data") or {}).get("url") or "").strip()
        if url:
            direct = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
            print("public link (tmpfiles):", direct)
            return direct
        print("tmpfiles returned:", r.status_code, r.text[:200])
    except Exception as e:
        print("tmpfiles error:", e)
    try:
        with open(path, "rb") as f:
            r = requests.post("https://0x0.st", files={"file": f},
                              headers={"User-Agent": "quran-shorts-bot/1.0"},
                              timeout=300)
        url = r.text.strip()
        if r.status_code == 200 and url.startswith("http"):
            print("public link (0x0):", url)
            return url
        print("0x0 returned:", r.status_code, url[:200])
    except Exception as e:
        print("0x0 error:", e)
    return ""


def _container_url(ig_id, url, caption):
    c = requests.post(
        f"{API}/{ig_id}/media",
        data={"media_type": "REELS", "video_url": url,
              "caption": caption, "access_token": IG_TOK},
        timeout=60,
    ).json()
    if c.get("id"):
        return c["id"]
    print("IG container rejected:", c)
    return None


def publish_reel(video_path, description):
    if not IG_TOK:
        print("Instagram: no token, skipped")
        return None
    try:
        ig_id = _ig_id()
        if not ig_id:
            return None
        path = _faststart(video_path)
        cap = _caption(description)
        cid = _container_upload(ig_id, path, cap)
        if not cid:
            url = _public_url(path)
            if not url:
                print("IG: no public link")
                return None
            cid = _container_url(ig_id, url, cap)
            if not cid:
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
