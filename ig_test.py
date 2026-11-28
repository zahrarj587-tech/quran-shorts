# ig_test.py - تجربة نشر انستجرام بس
import os

from make import make_chunk
from reciters import pick, RECITERS
from ig import publish_reel

SURAH, AYAH = 108, 1

rc = pick(7)
video, title, nxt = make_chunk(SURAH, AYAH, rc)
name = RECITERS.get(rc, rc)
desc = (
    f"{title}\n\n"
    f"🎙️ بصوت الشيخ: {name}\n\n"
    f"#قرآن #المصحف #{name.replace(' ', '_')}\n\n"
    f"(منشور تجربة)"
)
pid = publish_reel(video, desc)
print("RESULT:", pid if pid else "FAILED")
