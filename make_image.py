# recorded build 2026-11-23
#!/usr/bin/env python3
"""Draw one delicious cheeseburger illustration (1024x1024 PNG).

Close-up of a single big cheeseburger on a warm dark background:
glossy toasted top bun with sesame, melting cheddar dripping over a
thick grilled patty, fresh lettuce, red tomato, soft steam, warm light
from the top-left. Clean illustration style, no text anywhere.
Drawn at 2048 and downscaled to 1024 for smooth edges.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

S = 2048
random.seed(7)
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
    """Vertical gradient clipped to the shape drawn by mask_draw_fn."""
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


# ---------- background: dark warm gradient + glow behind the burger ----------
img = vgrad(S, S, (43, 23, 10), (18, 11, 5)).convert("RGBA")

glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([380, 420, 1670, 1780], fill=(150, 88, 34, 255))
glow = glow.filter(ImageFilter.GaussianBlur(260))
img.alpha_composite(glow)

# ---------- soft shadow under the burger ----------
sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sd.ellipse([500, 1530, 1550, 1710], fill=(0, 0, 0, 150))
sh = sh.filter(ImageFilter.GaussianBlur(55))
img.alpha_composite(sh)

# ---------- bottom bun ----------
def bun_mask(md):
    md.rounded_rectangle([640, 1240, 1410, 1530], radius=110, fill=255)

layer, _ = masked_gradient((S, S), bun_mask, (226, 154, 69), (158, 96, 30))
img.alpha_composite(layer)
ov = Image.new("RGBA", (S, S), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
od.rounded_rectangle([640, 1420, 1410, 1530], radius=90, fill=(90, 48, 12, 110))
ov = ov.filter(ImageFilter.GaussianBlur(18))
img.alpha_composite(ov)
hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
hd = ImageDraw.Draw(hl)
hd.ellipse([700, 1220, 1150, 1400], fill=(255, 225, 160, 70))
hl = hl.filter(ImageFilter.GaussianBlur(40))
img.alpha_composite(hl)

# ---------- patty: thick, grilled ----------
def patty_mask(md):
    md.rounded_rectangle([590, 1075, 1460, 1275], radius=70, fill=255)

layer, pmask = masked_gradient((S, S), patty_mask, (122, 66, 30), (66, 36, 16))
img.alpha_composite(layer)

gm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = ImageDraw.Draw(gm)
for x0 in range(650, 1450, 130):
    g.line([(x0, 1080), (x0 + 90, 1270)], fill=(30, 16, 6, 200), width=26)
img.alpha_composite(clip_alpha(gm, pmask))

dots = Image.new("RGBA", (S, S), (0, 0, 0, 0))
dd = ImageDraw.Draw(dots)
for _ in range(260):
    x = random.randint(620, 1430)
    y = random.randint(1095, 1255)
    r = random.randint(3, 9)
    c = (52, 28, 12, 120) if random.random() < 0.5 else (170, 104, 52, 110)
    dd.ellipse([x - r, y - r, x + r, y + r], fill=c)
img.alpha_composite(clip_alpha(dots, pmask))

# ---------- cheese: bright cheddar draped over the patty, dripping ----------
ch = Image.new("RGBA", (S, S), (0, 0, 0, 0))
cd = ImageDraw.Draw(ch)
cd.rectangle([610, 1005, 1440, 1120], fill=(246, 168, 33, 255))
cd.rectangle([610, 1005, 1440, 1045], fill=(250, 196, 77, 255))
cd.line([(610, 1120), (1440, 1120)], fill=(214, 128, 18, 255), width=6)
# rounded drips of varying length hanging below the band
for (x, length) in [(660, 70), (760, 130), (850, 60), (950, 150), (1040, 80),
                    (1130, 140), (1220, 65), (1310, 120), (1400, 75)]:
    cd.rounded_rectangle([x - 26, 1100, x + 26, 1100 + length], radius=26,
                         fill=(246, 168, 33, 255))
img.alpha_composite(ch)

# ---------- tomato: two red slices peeking out ----------
tm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(tm)
td.rounded_rectangle([600, 945, 1060, 1035], radius=45, fill=(207, 47, 36, 255))
td.rounded_rectangle([990, 945, 1450, 1035], radius=45, fill=(207, 47, 36, 255))
td.ellipse([640, 962, 1020, 1018], fill=(232, 84, 63, 255))
td.ellipse([1030, 962, 1410, 1018], fill=(232, 84, 63, 255))
img.alpha_composite(tm)

# ---------- lettuce: wavy fresh green leaf ----------
top_y = 830
pts = [(x, top_y) for x in range(580, 1471, 20)]
for x in range(1470, 579, -20):
    wave = 930 + int(26 * math.sin((x - 580) / 1470 * math.pi * 7))
    pts.append((x, wave))
lt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lt)
ld.polygon(pts, fill=(88, 160, 44, 255))
band = [(x, top_y + 34) for x in range(580, 1471, 20)]
for x in range(1470, 579, -20):
    wave = 960 + int(26 * math.sin((x - 580) / 1470 * math.pi * 7))
    band.append((x, wave))
ld.polygon(band, fill=(56, 122, 30, 255))
img.alpha_composite(lt)

# ---------- top bun: golden dome ----------
def dome_mask(md):
    md.pieslice([545, 400, 1505, 1300], start=180, end=360, fill=255)

layer, dmask = masked_gradient((S, S), dome_mask, (238, 172, 84), (176, 106, 32))
img.alpha_composite(layer)

band = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
bd.pieslice([545, 560, 1505, 1460], start=180, end=360, fill=(110, 58, 14, 70))
band = clip_alpha(band, dmask).filter(ImageFilter.GaussianBlur(25))
img.alpha_composite(band)

hl2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
h2d = ImageDraw.Draw(hl2)
h2d.ellipse([640, 380, 1120, 640], fill=(255, 232, 170, 90))
hl2 = hl2.filter(ImageFilter.GaussianBlur(60))
img.alpha_composite(clip_alpha(hl2, dmask))

# sesame seeds
def seed(angle):
    t = Image.new("RGBA", (72, 44), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.ellipse([6, 6, 66, 38], fill=(244, 220, 168, 255))
    td.ellipse([12, 10, 60, 30], fill=(252, 238, 200, 255))
    return t.rotate(angle, expand=True, resample=Image.BICUBIC)

positions = [
    (760, 520, 20), (980, 470, -15), (1180, 500, 35), (700, 660, -30),
    (900, 600, 10), (1120, 640, -20), (1300, 620, 25), (820, 740, 40),
    (1050, 760, -35), (1260, 760, 15), (700, 560, 55), (1400, 700, -10),
]
for (x, y, a) in positions:
    t = seed(a)
    img.alpha_composite(t, (x - t.width // 2, y - t.height // 2))

# ---------- thin steam rising above the bun ----------
st = Image.new("RGBA", (S, S), (0, 0, 0, 0))
std = ImageDraw.Draw(st)
for cx, amp, ph in [(850, 34, 0.0), (1024, 44, 1.6), (1200, 30, 3.1)]:
    pts = [(cx + amp * math.sin(ph + (y - 240) / 70.0), y) for y in range(240, 430, 8)]
    std.line(pts, fill=(255, 255, 255, 70), width=18, joint="curve")
st = st.filter(ImageFilter.GaussianBlur(14))
img.alpha_composite(st)

# ---------- tighten the frame so the burger fills it, then downscale ----------
img = img.crop((300, 200, 1750, 1650)).convert("RGB").resize((1024, 1024), Image.LANCZOS)
img.save(OUT, optimize=True)
import os
print("saved", OUT, os.path.getsize(OUT), "bytes")
