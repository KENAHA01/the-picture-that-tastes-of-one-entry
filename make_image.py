# recorded build 2026-11-23
#!/usr/bin/env python3
"""Draw one delicious cheeseburger illustration, revision v2 (1024x1024 PNG).

Close-up, burger fills ~90% of the frame, with a BITE taken out of the
right side showing the juicy cross-section: bun crumb, melted cheese,
grilled patty, tomato, lettuce, all glossy and wet-looking. Rich
realistic shading, strong glossy highlight on the top-left of the bun,
sesame seeds with little shadows, cheese highlight streaks and glossy
round drips, patty grill marks and juice speckles, glossy tomato with
visible seeds, lettuce with leaf veins. Warm dark brown background with
a soft blurred light circle (bokeh) and a gentle vignette pulling the
eye to the burger. 3-4 thin semi-transparent steam wisps. No text.
Drawn at 2048 and downscaled to 1024 for smooth edges.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

S = 2048
random.seed(11)
OUT = "/home/hatch/workspace/makefun/the-picture-that-tastes-of-one-entry/entry.png"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(h - 1, 1)))
    return img


def masked_gradient(size, mask_draw_fn, top, bottom):
    mask = Image.new("L", size, 0)
    md = ImageDraw.Draw(mask)
    mask_draw_fn(md)
    grad = vgrad(size[0], size[1], top, bottom)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(grad, (0, 0))
    layer.putalpha(mask)
    return layer, mask


def clip_alpha(layer, mask):
    layer.putalpha(Image.composite(layer.split()[3], Image.new("L", layer.size, 0), mask))
    return layer


# ---------- background: dark warm gradient + warm glow + bokeh ----------
img = vgrad(S, S, (46, 25, 11), (16, 10, 4)).convert("RGBA")

glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([380, 380, 1680, 1800], fill=(165, 96, 36, 255))
glow = glow.filter(ImageFilter.GaussianBlur(280))
img.alpha_composite(glow)

bokeh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bd = ImageDraw.Draw(bokeh)
for (x, y, r, a) in [(300, 350, 90, 55), (1750, 300, 70, 45), (180, 900, 110, 40),
                     (1900, 1000, 95, 50), (250, 1600, 80, 42), (1820, 1650, 120, 48),
                     (1024, 180, 60, 38), (420, 1250, 65, 34)]:
    bd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 190, 110, a))
bokeh = bokeh.filter(ImageFilter.GaussianBlur(46))
img.alpha_composite(bokeh)

# ---------- soft shadow under the burger ----------
sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sd.ellipse([430, 1560, 1620, 1760], fill=(0, 0, 0, 160))
sh = sh.filter(ImageFilter.GaussianBlur(60))
img.alpha_composite(sh)

# ---------- burger silhouette mask (for the bite) ----------
sil = Image.new("L", (S, S), 0)
sm = ImageDraw.Draw(sil)
sm.pieslice([300, 330, 1750, 1280], start=180, end=360, fill=255)
sm.polygon([(300, 1010), (1750, 1010), (1750, 1130), (300, 1130)], fill=255)
sm.rounded_rectangle([310, 1120, 1740, 1210], radius=40, fill=255)
sm.rectangle([320, 1200, 1730, 1330], fill=255)
sm.rounded_rectangle([300, 1300, 1750, 1520], radius=70, fill=255)
sm.rounded_rectangle([370, 1500, 1680, 1780], radius=110, fill=255)

# ---------- bottom bun ----------
def bun_mask(md):
    md.rounded_rectangle([370, 1500, 1680, 1780], radius=110, fill=255)

layer, _ = masked_gradient((S, S), bun_mask, (232, 160, 74), (150, 90, 28))
img.alpha_composite(layer)
ov = Image.new("RGBA", (S, S), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
od.rounded_rectangle([370, 1660, 1680, 1780], radius=90, fill=(88, 46, 12, 120))
ov = ov.filter(ImageFilter.GaussianBlur(20))
img.alpha_composite(ov)
hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
hd = ImageDraw.Draw(hl)
hd.ellipse([430, 1480, 900, 1660], fill=(255, 228, 165, 80))
hl = hl.filter(ImageFilter.GaussianBlur(42))
img.alpha_composite(hl)

# ---------- patty: thick, grilled, juicy ----------
def patty_mask(md):
    md.rounded_rectangle([300, 1300, 1750, 1520], radius=70, fill=255)

layer, pmask = masked_gradient((S, S), patty_mask, (128, 70, 32), (62, 34, 15))
img.alpha_composite(layer)

gm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = ImageDraw.Draw(gm)
for x0 in range(360, 1720, 140):
    g.line([(x0, 1305), (x0 + 100, 1515)], fill=(28, 14, 6, 210), width=30)
img.alpha_composite(clip_alpha(gm, pmask))

dots = Image.new("RGBA", (S, S), (0, 0, 0, 0))
dd = ImageDraw.Draw(dots)
for _ in range(320):
    x = random.randint(330, 1720)
    y = random.randint(1320, 1500)
    r = random.randint(3, 10)
    c = (48, 26, 12, 130) if random.random() < 0.5 else (178, 108, 54, 120)
    dd.ellipse([x - r, y - r, x + r, y + r], fill=c)
img.alpha_composite(clip_alpha(dots, pmask))

sheen = Image.new("RGBA", (S, S), (0, 0, 0, 0))
shd = ImageDraw.Draw(sheen)
shd.ellipse([420, 1300, 1150, 1420], fill=(255, 190, 110, 46))
sheen = sheen.filter(ImageFilter.GaussianBlur(30))
img.alpha_composite(clip_alpha(sheen, pmask))

# ---------- cheese: bright cheddar with highlight streaks and glossy drips ----------
ch = Image.new("RGBA", (S, S), (0, 0, 0, 0))
cd = ImageDraw.Draw(ch)
cd.rectangle([320, 1200, 1730, 1330], fill=(247, 170, 34, 255))
cd.rectangle([320, 1200, 1730, 1245], fill=(252, 200, 82, 255))
cd.line([(320, 1330), (1730, 1330)], fill=(212, 126, 16, 255), width=6)
# bright highlight streaks across the band
for (x0, y0, x1, y1) in [(420, 1225, 900, 1215), (1050, 1230, 1500, 1220),
                         (500, 1290, 800, 1282), (1150, 1295, 1600, 1285)]:
    cd.line([(x0, y0), (x1, y1)], fill=(255, 226, 140, 200), width=14)
# rounded glossy drips of varying length
for (x, length) in [(400, 80), (510, 150), (620, 70), (730, 165), (850, 90),
                    (960, 150), (1080, 75), (1200, 160), (1320, 85), (1440, 140),
                    (1560, 70), (1660, 120)]:
    cd.rounded_rectangle([x - 30, 1310, x + 30, 1310 + length], radius=30,
                         fill=(247, 170, 34, 255))
    cd.ellipse([x - 12, 1310 + length - 18, x + 12, 1310 + length + 6],
               fill=(255, 225, 140, 220))
img.alpha_composite(ch)

# ---------- tomato: two glossy red slices with visible seeds ----------
tm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(tm)
td.rounded_rectangle([310, 1120, 1060, 1210], radius=45, fill=(208, 48, 36, 255))
td.rounded_rectangle([990, 1120, 1740, 1210], radius=45, fill=(208, 48, 36, 255))
td.ellipse([350, 1138, 1020, 1194], fill=(234, 86, 64, 255))
td.ellipse([1030, 1138, 1700, 1194], fill=(234, 86, 64, 255))
# seed pockets
for (x, y) in [(500, 1162), (700, 1166), (900, 1162), (1150, 1166), (1350, 1162), (1550, 1166)]:
    td.ellipse([x - 22, y - 10, x + 22, y + 10], fill=(245, 180, 150, 220))
    td.ellipse([x - 8, y - 4, x + 8, y + 4], fill=(250, 220, 190, 255))
# gloss streak on tomato
td.line([(380, 1150), (700, 1144)], fill=(255, 190, 170, 170), width=10)
td.line([(1080, 1150), (1400, 1144)], fill=(255, 190, 170, 170), width=10)
img.alpha_composite(tm)

# ---------- lettuce: wavy fresh green leaf with veins ----------
top_y = 1010
pts = [(x, top_y) for x in range(300, 1751, 20)]
for x in range(1750, 299, -20):
    wave = 1110 + int(26 * math.sin((x - 300) / 1750 * math.pi * 7))
    pts.append((x, wave))
lt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lt)
ld.polygon(pts, fill=(92, 166, 48, 255))
band = [(x, top_y + 36) for x in range(300, 1751, 20)]
for x in range(1750, 299, -20):
    wave = 1140 + int(26 * math.sin((x - 300) / 1750 * math.pi * 7))
    band.append((x, wave))
ld.polygon(band, fill=(58, 126, 32, 255))
# leaf veins
for x0 in range(380, 1700, 130):
    ld.line([(x0, 1030), (x0 + 40, 1105)], fill=(140, 205, 90, 160), width=7)
img.alpha_composite(lt)

# ---------- top bun: golden dome with rich shading ----------
def dome_mask(md):
    md.pieslice([300, 330, 1750, 1280], start=180, end=360, fill=255)

layer, dmask = masked_gradient((S, S), dome_mask, (242, 178, 88), (172, 102, 30))
img.alpha_composite(layer)

# radial warm glow centred upper-left of the dome
rg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
rd = ImageDraw.Draw(rg)
rd.ellipse([380, 300, 1250, 950], fill=(255, 226, 160, 110))
rg = rg.filter(ImageFilter.GaussianBlur(90))
img.alpha_composite(clip_alpha(rg, dmask))

# strong glossy highlight upper-left
hl2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
h2d = ImageDraw.Draw(hl2)
h2d.ellipse([430, 350, 980, 620], fill=(255, 238, 190, 130))
h2d.ellipse([520, 380, 820, 540], fill=(255, 246, 214, 120))
hl2 = hl2.filter(ImageFilter.GaussianBlur(46))
img.alpha_composite(clip_alpha(hl2, dmask))

# warm shadow at the dome base
band = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bd2 = ImageDraw.Draw(band)
bd2.pieslice([300, 520, 1750, 1430], start=180, end=360, fill=(108, 56, 14, 80))
band = clip_alpha(band, dmask).filter(ImageFilter.GaussianBlur(28))
img.alpha_composite(band)

# sesame seeds with little shadows
def seed(angle):
    t = Image.new("RGBA", (76, 46), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.ellipse([8, 10, 68, 42], fill=(150, 92, 30, 200))
    td.ellipse([6, 6, 66, 38], fill=(246, 222, 170, 255))
    td.ellipse([13, 10, 60, 30], fill=(253, 240, 202, 255))
    return t.rotate(angle, expand=True, resample=Image.BICUBIC)

positions = [
    (620, 500, 20), (880, 440, -15), (1140, 470, 35), (1380, 540, -25),
    (560, 640, -30), (820, 580, 10), (1080, 620, -20), (1330, 660, 25),
    (700, 760, 40), (980, 740, -35), (1240, 780, 15), (520, 560, 55),
    (1480, 700, -10), (900, 860, 30),
]
for (x, y, a) in positions:
    t = seed(a)
    img.alpha_composite(t, (x - t.width // 2, y - t.height // 2))

# ---------- BITE on the right side: juicy cross-section ----------
bite_circles = [(1520, 990, 165), (1660, 1060, 150), (1580, 1220, 160),
                (1450, 1150, 125), (1700, 1240, 110)]
bite = Image.new("L", (S, S), 0)
bdraw = ImageDraw.Draw(bite)
for (cx, cy, r) in bite_circles:
    bdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)

# crust rim: slightly larger circles, clipped to the burger silhouette
rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
rm = ImageDraw.Draw(rim)
for (cx, cy, r) in bite_circles:
    rm.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18],
               fill=(128, 68, 18, 255))
img.alpha_composite(clip_alpha(rim, sil))

# cross-section interior, clipped to bite AND silhouette
inter = Image.new("RGBA", (S, S), (0, 0, 0, 0))
idraw = ImageDraw.Draw(inter)
# bun crumb at the top of the bite
idraw.rectangle([1300, 800, 1800, 960], fill=(244, 208, 148, 255))
for _ in range(90):
    x = random.randint(1330, 1770)
    y = random.randint(820, 940)
    r = random.randint(3, 8)
    idraw.ellipse([x - r, y - r, x + r, y + r], fill=(226, 182, 120, 160))
# melted cheese
idraw.rectangle([1300, 960, 1800, 1030], fill=(250, 184, 46, 255))
idraw.line([(1340, 985), (1760, 978)], fill=(255, 230, 150, 220), width=12)
# patty
idraw.rectangle([1300, 1030, 1800, 1150], fill=(112, 62, 30, 255))
for _ in range(70):
    x = random.randint(1330, 1770)
    y = random.randint(1045, 1135)
    r = random.randint(3, 9)
    c = (60, 32, 14, 150) if random.random() < 0.5 else (186, 116, 60, 140)
    idraw.ellipse([x - r, y - r, x + r, y + r], fill=c)
# glossy juice sheen on the patty cut
idraw.ellipse([1400, 1040, 1700, 1090], fill=(255, 200, 120, 70))
# tomato
idraw.rectangle([1300, 1150, 1800, 1220], fill=(216, 52, 38, 255))
idraw.ellipse([1340, 1162, 1760, 1208], fill=(238, 92, 68, 255))
for (x, y) in [(1440, 1186), (1580, 1188), (1700, 1186)]:
    idraw.ellipse([x - 20, y - 9, x + 20, y + 9], fill=(248, 186, 156, 230))
# lettuce at the bottom of the bite
idraw.rectangle([1300, 1220, 1800, 1280], fill=(88, 162, 46, 255))
idraw.line([(1340, 1250), (1760, 1246)], fill=(150, 212, 100, 200), width=8)

bite_and_sil = Image.composite(bite, Image.new("L", (S, S), 0), sil)
img.alpha_composite(clip_alpha(inter, bite_and_sil))

# glossy wet highlights inside the bite
gl2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g2 = ImageDraw.Draw(gl2)
g2.ellipse([1420, 970, 1560, 1000], fill=(255, 240, 180, 150))
g2.ellipse([1500, 1050, 1620, 1080], fill=(255, 220, 140, 130))
g2.ellipse([1440, 1170, 1560, 1195], fill=(255, 200, 180, 140))
img.alpha_composite(clip_alpha(gl2, bite_and_sil))

# a cheese drip escaping from the bottom of the bite
dr = Image.new("RGBA", (S, S), (0, 0, 0, 0))
drd = ImageDraw.Draw(dr)
drd.rounded_rectangle([1560, 1240, 1620, 1400], radius=30, fill=(247, 170, 34, 255))
drd.ellipse([1568, 1380, 1612, 1404], fill=(255, 226, 140, 220))
img.alpha_composite(dr)

# ---------- thin steam rising above the bun ----------
st = Image.new("RGBA", (S, S), (0, 0, 0, 0))
std = ImageDraw.Draw(st)
for cx, amp, ph in [(700, 36, 0.0), (900, 46, 1.6), (1120, 32, 3.1), (1300, 40, 4.4)]:
    pts = [(cx + amp * math.sin(ph + (y - 200) / 70.0), y) for y in range(200, 380, 8)]
    std.line(pts, fill=(255, 255, 255, 72), width=18, joint="curve")
st = st.filter(ImageFilter.GaussianBlur(14))
img.alpha_composite(st)

# ---------- gentle vignette pulling the eye to the burger ----------
vg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
vd = ImageDraw.Draw(vg)
vd.rectangle([0, 0, S, S], fill=(0, 0, 0, 90))
hole = Image.new("L", (S, S), 0)
hd = ImageDraw.Draw(hole)
hd.ellipse([180, 140, 1870, 1900], fill=255)
hole = hole.filter(ImageFilter.GaussianBlur(180))
vg.putalpha(Image.composite(Image.new("L", (S, S), 0), vg.split()[3], hole))
img.alpha_composite(vg)

# ---------- tighten the frame so the burger fills ~90%, then downscale ----------
img = img.crop((180, 130, 1870, 1820)).convert("RGB").resize((1024, 1024), Image.LANCZOS)
img.save(OUT, optimize=True)
import os
print("saved", OUT, os.path.getsize(OUT), "bytes")
