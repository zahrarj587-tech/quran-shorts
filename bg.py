import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

THEMES = [
    ((22, 96, 72), (3, 24, 18)),
    ((26, 60, 112), (3, 9, 28)),
    ((18, 84, 94), (2, 20, 26)),
    ((70, 40, 96), (14, 6, 26)),
    ((96, 66, 30), (22, 13, 4)),
]
GOLD = (212, 175, 55)

def _star(d, cx, cy, r, color, w):
    d.rectangle([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    k = int(r * 1.414)
    pts = [(cx, cy - k), (cx + k, cy), (cx, cy + k), (cx - k, cy)]
    d.line(pts + [pts[0]], fill=color, width=w)

def make_bg(idx, work="work"):
    center, edge = THEMES[idx % len(THEMES)]
    rnd = random.Random(idx)
    BW, BH = 1300, 2300
    g = Image.radial_gradient("L").resize((BW, BH), Image.Resampling.BILINEAR)
    base = Image.composite(Image.new("RGB", (BW, BH), edge),
                           Image.new("RGB", (BW, BH), center), g)
    pat = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(pat)
    step = 170
    for y in range(0, BH + step, step):
        for x in range(0, BW + step, step):
            _star(d, x, y, 60, GOLD + (90,), 2)
    for y in range(step // 2, BH + step, step):
        for x in range(step // 2, BW + step, step):
            d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=GOLD + (70,), width=2)
    a = ImageChops.multiply(pat.getchannel("A"),
                            g.point(lambda v: min(255, int(v * 1.3))))
    pat.putalpha(a)
    base = Image.alpha_composite(base.convert("RGBA"), pat).convert("RGB")

    DW, DH = 1400, 2500
    dust = Image.new("RGBA", (DW, DH), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(140):
        x, y = rnd.randrange(DW), rnd.randrange(DH)
        r = rnd.choice([2, 3, 3, 4, 6])
        dd.ellipse([x - r, y - r, x + r, y + r],
                   fill=(255, 230, 150, rnd.randrange(50, 150)))
    dust = dust.filter(ImageFilter.GaussianBlur(2))

    bp, dp = f"{work}/bg_base.png", f"{work}/bg_dust.png"
    base.save(bp)
    dust.save(dp)
    return bp, dp
