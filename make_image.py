#!/usr/bin/env python3
"""Draw one delicious cheeseburger illustration, 1024x1024 PNG.

Clean illustration style: warm dark background, one big cheeseburger
filling the frame, glossy toasted top bun with sesame, melting cheddar
dripping over a thick grilled patty, fresh lettuce and tomato, soft warm
light from the upper left, a whisper of steam. No text in the image.
Drawn at 2x and downscaled for smooth edges.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

S = 2048  # working size, downscaled to 1024
OUT = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(7)


def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return img.resize((w, h))


def ellipse_arc_points(cx, cy, rx, ry, a0, a1, n=120):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def wave_edge(x0, x1, y_base, amp, waves, n=120, phase=0.0):
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = y_base + amp * math.sin(2 * math.pi * waves * i / n + phase)
        pts.append((x, y))
    return pts


def apply_mask(base, mask, fill):
    """Paste fill (RGB tuple or RGB image) through an L mask."""
    if isinstance(fill, tuple):
        layer = Image.new("RGB", base.size, fill)
    else:
        layer = fill
    base.paste(layer, (0, 0), mask)


def main():
    img = Image.new("RGB", (S, S))
    # --- background: warm dark vertical gradient ---
    img.paste(vgrad(S, S, (26, 15, 10), (52, 30, 17)), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # warm glow behind the burger
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((260, 260, 1788, 1900), fill=(122, 62, 22, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # --- soft shadow under the burger ---
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((330, 1700, 1718, 1860), fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(60))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))

    # ================= BOTTOM BUN =================
    bun_mask = Image.new("L", (S, S), 0)
    bd = ImageDraw.Draw(bun_mask)
    bd.rounded_rectangle((330, 1390, 1718, 1780), radius=170, fill=255)
    apply_mask(img, bun_mask, vgrad(S, S, (216, 143, 58), (158, 96, 28)))
    d = ImageDraw.Draw(img, "RGBA")
    # toasted top rim of bottom bun
    d.rounded_rectangle((330, 1390, 1718, 1460), radius=60, fill=(232, 164, 74, 255))
    # soft bottom shade
    d.rounded_rectangle((330, 1680, 1718, 1780), radius=80, fill=(120, 70, 20, 90))

    # ================= PATTY =================
    patty_mask = Image.new("L", (S, S), 0)
    pd = ImageDraw.Draw(patty_mask)
    top = wave_edge(300, 1748, 1150, 14, 3)
    bot = wave_edge(300, 1748, 1445, 14, 3, phase=1.2)
    pd.polygon(top + list(reversed(bot)), fill=255)
    apply_mask(img, patty_mask, vgrad(S, S, (122, 68, 32), (82, 44, 20)))
    # patty texture: speckles + grill marks, clipped by patty mask
    tex = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tex)
    for _ in range(300):
        x = random.randint(310, 1738)
        y = random.randint(1160, 1435)
        r = random.randint(3, 8)
        td.ellipse((x - r, y - r, x + r, y + r),
                   fill=(48, 24, 10, random.randint(40, 100)))
    for i in range(7):
        x = 420 + i * 190
        td.line((x, 1160, x - 90, 1440), fill=(40, 20, 8, 90), width=14)
    # glossy top edge of patty
    td.rectangle((300, 1145, 1748, 1175), fill=(150, 84, 38, 120))
    tex.putalpha(Image.composite(tex.split()[3], Image.new("L", (S, S), 0), patty_mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), tex).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================= TOMATO (peeks out at the sides) =================
    for (x0, x1) in ((255, 700), (1350, 1795)):
        d.rounded_rectangle((x0, 1045, x1, 1175), radius=55, fill=(214, 48, 39, 255))
        d.rounded_rectangle((x0 + 26, 1068, x1 - 26, 1152), radius=40,
                            fill=(232, 84, 66, 255))

    # ================= CHEESE (melting, dripping over the patty) =================
    cheese_mask = Image.new("L", (S, S), 0)
    cd = ImageDraw.Draw(cheese_mask)
    top = wave_edge(305, 1743, 960, 10, 2)
    bot = wave_edge(305, 1743, 1105, 26, 4, phase=0.6)
    cd.polygon(top + list(reversed(bot)), fill=255)
    # drips hanging below the wavy edge
    for (cx, length, w) in ((480, 120, 95), (830, 165, 105), (1180, 135, 95),
                            (1520, 150, 100)):
        cd.rounded_rectangle((cx - w // 2, 1080, cx + w // 2, 1080 + length),
                             radius=w // 2, fill=255)
        cd.ellipse((cx - w // 2, 1080 + length - w // 2,
                    cx + w // 2, 1080 + length + w // 2), fill=255)
    apply_mask(img, cheese_mask, vgrad(S, S, (255, 176, 46), (240, 138, 18)))
    d = ImageDraw.Draw(img, "RGBA")
    # cheese top sheen
    d.polygon(wave_edge(305, 1743, 985, 8, 2) +
              list(reversed(wave_edge(305, 1743, 1030, 8, 2, phase=0.6))),
              fill=(255, 205, 92, 255))

    # ================= LETTUCE (fresh, wavy, sticks out past the bun) =================
    let_mask = Image.new("L", (S, S), 0)
    ld = ImageDraw.Draw(let_mask)
    top = wave_edge(215, 1833, 860, 34, 5)
    bot = wave_edge(215, 1833, 985, 30, 5, phase=0.9)
    ld.polygon(top + list(reversed(bot)), fill=255)
    apply_mask(img, let_mask, vgrad(S, S, (110, 190, 74), (62, 138, 44)))
    d = ImageDraw.Draw(img, "RGBA")
    # lighter ruffled top edge
    d.polygon(wave_edge(215, 1833, 872, 34, 5) +
              list(reversed(wave_edge(215, 1833, 920, 30, 5, phase=0.9))),
              fill=(140, 208, 96, 255))
    # a few darker leaf folds
    for x in (420, 760, 1120, 1480):
        d.arc((x - 90, 830, x + 90, 1000), start=200, end=340,
              fill=(46, 110, 34, 160), width=14)

    # ================= TOP BUN DOME =================
    dome_mask = Image.new("L", (S, S), 0)
    dd = ImageDraw.Draw(dome_mask)
    arc = ellipse_arc_points(1024, 900, 752, 640, 180, 360)
    dd.polygon(arc + [(1776, 900), (272, 900)], fill=255)
    apply_mask(img, dome_mask, vgrad(S, S, (238, 176, 92), (176, 106, 38)))
    # warm highlight, top-left of the dome, clipped to the dome
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.ellipse((430, 300, 1080, 640), fill=(255, 226, 170, 110))
    hl = hl.filter(ImageFilter.GaussianBlur(90))
    hl.putalpha(Image.composite(hl.split()[3], Image.new("L", (S, S), 0), dome_mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), hl).convert("RGB"), (0, 0))
    # darker rim along the dome's bottom edge (thin band, clipped to dome)
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rectangle((272, 845, 1776, 905), fill=(140, 82, 26, 130))
    rim.putalpha(Image.composite(rim.split()[3], Image.new("L", (S, S), 0), dome_mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), rim).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # sesame seeds
    seeds = [(560, 470), (700, 400), (880, 360), (1080, 350), (1280, 380),
             (1440, 450), (1520, 560), (480, 580), (640, 560), (820, 470),
             (1000, 470), (1180, 500), (1360, 580), (900, 600), (1100, 620),
             (760, 680), (1300, 700), (620, 700)]
    for (x, y) in seeds:
        d.ellipse((x - 26, y - 13, x + 26, y + 13), fill=(247, 223, 168, 255),
                  outline=(200, 160, 90, 255), width=3)
        d.ellipse((x - 26, y - 13, x + 26, y + 2), fill=(255, 240, 200, 255))

    # ================= STEAM (thin wisps above the bun) =================
    steam = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for (x0, amp, phase) in ((760, 46, 0.0), (1024, 56, 1.4), (1290, 42, 2.6)):
        pts = []
        for i in range(41):
            y = 300 - i * 5
            x = x0 + amp * math.sin(i / 40 * 2.4 * math.pi + phase) * (1 - i / 60)
            pts.append((x, y))
        sd.line(pts, fill=(255, 244, 230, 70), width=16, joint="curve")
    steam = steam.filter(ImageFilter.GaussianBlur(12))
    img.paste(Image.alpha_composite(img.convert("RGBA"), steam).convert("RGB"), (0, 0))

    # ================= WARM LIGHT from upper left =================
    light = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(light)
    ld2.ellipse((-500, -500, 1100, 900), fill=(255, 214, 150, 46))
    light = light.filter(ImageFilter.GaussianBlur(160))
    img.paste(Image.alpha_composite(img.convert("RGBA"), light).convert("RGB"), (0, 0))

    # downscale to 1024x1024 and save
    out = img.resize((OUT, OUT), Image.LANCZOS)
    path = os.path.join(HERE, "entry.png")
    out.save(path, "PNG", optimize=True)
    print("wrote", path, out.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
