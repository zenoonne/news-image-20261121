#!/usr/bin/env python3
"""render.py — draws the news-image-20261121 newspaper front page.

One 1024x1024 PNG summing up Saturday 21 November 2026: a masthead, a numbers strip,
3 big illustrated features, 10 medium illustrated stories, a 20-item list, a world map
with numbered pins, a DATE CHECK box and a footer. Everything is drawn with Pillow
primitives only — no external images and no network — so runs are byte-identical.
"""

import os
from PIL import Image, ImageDraw, ImageFont

import worldmap

W = H = 1024
M = 6  # page margin

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANSB = FONT_DIR + "DejaVuSans-Bold.ttf"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SERIFB = FONT_DIR + "DejaVuSerif-Bold.ttf"
MONOB = FONT_DIR + "DejaVuSansMono-Bold.ttf"

_fc = {}


def F(size, bold=False, serif=False, mono=False):
    key = (size, bold, serif, mono)
    if key not in _fc:
        if mono:
            path = MONOB
        elif serif:
            path = SERIFB if bold else SERIF
        else:
            path = SANSB if bold else SANS
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]


INK = (20, 18, 16)
PAPER = (252, 250, 244)
RED = (170, 26, 26)
GREY = (95, 92, 88)
LIGHT = (233, 228, 216)
RULE = (60, 56, 52)
BORDER = (170, 165, 155)

REGION = {
    "MIDDLE EAST": (176, 34, 34),
    "EUROPE": (28, 70, 162),
    "ASIA": (198, 108, 16),
    "AMERICAS": (24, 128, 68),
    "AFRICA": (128, 58, 148),
    "OCEANIA": (0, 128, 138),
    "SPACE": (62, 62, 92),
}
CONF = {
    "REPORTED": (24, 120, 60),
    "FORECAST": (28, 92, 170),
    "CLAIM": (196, 120, 8),
}

# --------------------------------------------------------------------------------------
# The 33 stories. Each: (n, region, confidence, place, headline, subline, scene_key)
# --------------------------------------------------------------------------------------

BIG = [
    (1, "MIDDLE EAST", "CLAIM", "GAZA",
     "Israeli fire kills four in Gaza",
     "Civil defence: three died in a drone strike on an aid truck; Israel says it hit operatives.",
     "gaza"),
    (2, "EUROPE", "REPORTED", "GULF OF FINLAND",
     "Drone strike sets Russian cargo ship ablaze",
     "Finland imposes airspace and sea restrictions after the ship is hit and catches fire.",
     "finland"),
    (3, "SPACE", "REPORTED", "MERCURY ORBIT",
     "BepiColombo arrives at Mercury",
     "The European Space Agency craft inserts itself into orbit after a decade in flight.",
     "mercury"),
]

MEDIUM = [
    (4, "MIDDLE EAST", "CLAIM", "BAHRAIN",
     "Iran says it hit US assets in Bahrain",
     "Tehran says it struck a US radar. — Al Jazeera", "bahrain"),
    (5, "EUROPE", "REPORTED", "TURKIYE",
     "COP31 climate talks deadlock",
     "Summit pushed deep into overtime. — Guardian", "cop31"),
    (6, "EUROPE", "REPORTED", "BRUSSELS",
     "EU and Indonesia sign trade deal",
     "Talks end after a decade. — Euronews", "euindo"),
    (7, "ASIA", "REPORTED", "INDIA",
     "Illicit alcohol kills 11 in Manipur",
     "About 180 poisoned; probe ordered. — Al Jazeera", "india"),
    (8, "MIDDLE EAST", "REPORTED", "IRAQ",
     "Fire at Basra power station kills four",
     "Thirty-five more injured. — Reuters", "iraq"),
    (9, "ASIA", "REPORTED", "INDONESIA",
     "Candy-factory fire; 36 missing",
     "Three killed near Jakarta. — The Guardian", "indonesia"),
    (10, "MIDDLE EAST", "CLAIM", "RIYADH",
     "Three Houthi missiles downed",
     "Coalition says it stopped the raid. — Al Jazeera", "houthi"),
    (11, "ASIA", "REPORTED", "BANGLADESH",
     "BNP and Awami League clash in Pabna",
     "Police fire rubber bullets. — UNB", "bangladesh"),
    (12, "AMERICAS", "REPORTED", "HAITI",
     "Salvadoran troops battle gangs",
     "Forces push into Port-au-Prince. — Guardian", "haiti"),
    (13, "EUROPE", "REPORTED", "EUROPE",
     "Gen Z protests sweep 25 countries",
     "Marches over wars and costs. — Al Jazeera", "genz"),
]

LIST = [
    (14, "MIDDLE EAST", "Two tankers hit off the Strait of Hormuz, near Khasab, Oman."),
    (15, "ASIA", "Saudi Arabia to triple crude stored in Japan, to 24m barrels."),
    (16, "ASIA", "Garment factories in Savar and Ashulia declare holidays."),
    (17, "EUROPE", "Probe: a Russian firm tracked unknowing Swedes online."),
    (18, "EUROPE", "Miliband: rejoining the EU is 'on the table' for the UK."),
    (19, "EUROPE", "Rugby: England beat New Zealand 37-12 in the Nations Championship."),
    (20, "AMERICAS", "Formula 1: Max Verstappen wins the Las Vegas Grand Prix."),
    (21, "ASIA", "Motorcycle racing: Peter Hickman wins a fifth Macau Grand Prix."),
    (22, "EUROPE", "Football: Chelsea lose 1-4 to Leeds; Newcastle draw 2-2 with Arsenal."),
    (23, "AMERICAS", "NBA: Spurs beat the Pelicans 114-91; 76ers edge the Bucks 132-129."),
    (24, "AMERICAS", "US: ICE officers arrest two passengers boarding a flight in Seattle."),
    (25, "ASIA", "Honda and Toyota recall 1.6 million vehicles over Takata airbag risk."),
    (26, "ASIA", "A magnitude 6.8 earthquake strikes near Lospalos, Timor-Leste."),
    (27, "AMERICAS", "A magnitude 6.7 earthquake strikes near Carhuamayo, Peru."),
    (28, "EUROPE", "Italy: Bulgari chairman Paolo Bulgari dies aged 89."),
    (29, "EUROPE", "Germany: art collector Friedrich Christian Flick dies aged 82."),
    (30, "OCEANIA", "Australia: politician and minister Fred Nile dies aged 92."),
    (31, "OCEANIA", "Australia: Olympic swimming champion Jon Henricks dies aged 91."),
    (32, "AFRICA", "Guinea: former national footballer Petit Sory dies aged 81."),
    (33, "EUROPE", "UK: journalist and 'Lost Lives' author David McKittrick dies aged 77."),
]

EXCLUDED = [
    "Mexico arrests cartel boss 'El Chapo Isidro' - 20 Nov",
    "Costa Concordia captain Schettino freed - 20 Nov",
    "General strike across Italy - 20 Nov",
    "Nigeria: 24 die as boat capsizes in Bayelsa - 20 Nov",
    "Russian Kh-101 missile lands in Poland - 20 Nov",
    "Denmark expels Russian attaché over 'plot' - 20 Nov",
    "Vance declines to back Trump on Iran - 20 Nov",
    "'GTA VI' becomes biggest game launch - 19 Nov",
    "ICJ: Myanmar committed Rohingya genocide - 19 Nov",
    "Senegal enacts 2026 budget by decree - 19 Nov",
]

# Pins for the map: number -> (lon, lat). 3 (Mercury) is drawn off-map.
PINS = {
    1: (34.4, 31.5), 2: (26.0, 60.0), 4: (50.6, 26.2), 5: (30.7, 36.9),
    6: (4.4, 50.8), 7: (93.9, 24.8), 8: (47.8, 30.5), 9: (106.8, -6.2),
    10: (46.7, 24.7), 11: (89.2, 24.0), 12: (-72.3, 18.5), 13: (10.0, 50.0),
}


# --------------------------------------------------------------------------------------
# Small drawing helpers
# --------------------------------------------------------------------------------------

def wrap(d, text, fnt, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, xy, text, fnt, fill, maxw, lead=1.05, align="left"):
    x, y = xy
    lh = int(fnt.size * lead) + 1
    for i, ln in enumerate(wrap(d, text, fnt, maxw)):
        if align == "center":
            d.text((x, y + i * lh), ln, font=fnt, fill=fill, anchor="ma")
        else:
            d.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return y + len(wrap(d, text, fnt, maxw)) * lh


def tag(d, xy, text, fill, fg=(255, 255, 255), fnt=None, pad=3):
    fnt = fnt or F(8, bold=True)
    tw = d.textlength(text, font=fnt)
    x, y = xy
    d.rectangle([x, y, x + tw + 2 * pad, y + fnt.size + 2 * pad - 1], fill=fill)
    d.text((x + pad, y + pad - 1), text, font=fnt, fill=fg)


def figure(d, x, y, s, body, head=(60, 50, 45)):
    d.ellipse([x - s * 0.18, y - s * 0.95, x + s * 0.18, y - s * 0.62], fill=head)
    d.rectangle([x - s * 0.22, y - s * 0.66, x + s * 0.22, y], fill=body)


def flag(d, x, y, w, h, bands, emblem=None):
    """bands: list of (color, fraction) drawn as vertical stripes."""
    cx = x
    for color, frac in bands:
        ww = w * frac
        d.rectangle([cx, y, cx + ww, y + h], fill=color)
        cx += ww
    d.rectangle([x, y, x + w, y + h], outline=(40, 40, 40))
    if emblem:
        ex, ey, ew, eh, col = emblem
        d.rectangle([x + ex, y + ey, x + ex + ew, y + ey + eh], fill=col)


def flames(d, x, y, s, n=5):
    for i in range(n):
        fx = x + i * s * 0.7
        d.polygon([(fx, y), (fx + s * 0.28, y - s * (1.0 + (i % 2) * 0.4)),
                   (fx + s * 0.56, y)], fill=(232, 120, 24))
        d.polygon([(fx + s * 0.12, y), (fx + s * 0.28, y - s * (0.6 + (i % 2) * 0.3)),
                   (fx + s * 0.44, y)], fill=(250, 206, 60))
    for i in range(n):
        fx = x + i * s * 0.7 + s * 0.2
        d.ellipse([fx, y - s * 2.0 - (i % 3) * 3, fx + s * 0.7, y - s * 1.2],
                  fill=(120, 118, 118))


def smoke(d, x, y, s, n=4, col=(120, 118, 118)):
    for i in range(n):
        r = s * (0.5 + i * 0.22)
        cx = x + i * s * 0.5
        cy = y - i * s * 0.7
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def star_field(d, bx, seed=7):
    x, y, w, h = bx
    for i in range(60):
        v = (i * 2654435761 + seed) & 0xFFFFFF
        px = x + v % w
        py = y + (v >> 8) % h
        d.point((px, py), fill=(255, 255, 255))


# --------------------------------------------------------------------------------------
# Scenes (Pillow primitives only)
# --------------------------------------------------------------------------------------

def scene_gaza(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(222, 205, 170))
    d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(200, 178, 140))
    # buildings
    for i, (bw, bh) in enumerate([(w * 0.16, h * 0.5), (w * 0.2, h * 0.62), (w * 0.14, h * 0.42)]):
        bxx = x + w * (0.04 + i * 0.22)
        d.rectangle([bxx, y + h * 0.72 - bh, bxx + bw, y + h * 0.74], fill=(178, 166, 150),
                    outline=(120, 110, 98))
        for r in range(3):
            d.rectangle([bxx + 3, y + h * 0.72 - bh + 4 + r * 6, bxx + 8,
                         y + h * 0.72 - bh + 7 + r * 6], fill=(90, 110, 130))
    # aid truck with red crescent
    tx, ty = x + w * 0.30, y + h * 0.68
    d.rectangle([tx, ty - h * 0.16, tx + w * 0.34, ty], fill=(245, 245, 240), outline=(60, 60, 60))
    d.rectangle([tx + w * 0.34, ty - h * 0.11, tx + w * 0.46, ty], fill=(235, 235, 232), outline=(60, 60, 60))
    d.ellipse([tx + 3, ty - h * 0.09, tx + 12, ty - h * 0.09 + 9], fill=(198, 40, 40))
    d.ellipse([tx + 6, ty - h * 0.105, tx + 17, ty - h * 0.105 + 11], fill=(198, 40, 40))
    d.rectangle([tx + 6, ty - h * 0.095, tx + 16, ty - h * 0.075], fill=(245, 245, 240))
    for wx in (tx + w * 0.08, tx + w * 0.4):
        d.ellipse([wx, ty - 3, wx + 10, ty + 7], fill=(40, 40, 40))
    # drone above (quadcopter)
    dx, dy = x + w * 0.62, y + h * 0.26
    d.line([dx - 16, dy - 6, dx + 16, dy + 6], fill=(60, 64, 70), width=2)
    d.line([dx - 16, dy + 6, dx + 16, dy - 6], fill=(60, 64, 70), width=2)
    for cx2, cy2 in [(dx - 16, dy - 6), (dx + 16, dy + 6), (dx - 16, dy + 6), (dx + 16, dy - 6)]:
        d.ellipse([cx2 - 5, cy2 - 3, cx2 + 5, cy2 + 3], fill=(120, 126, 134))
        d.ellipse([cx2 - 2, cy2 - 2, cx2 + 2, cy2 + 2], fill=(50, 54, 60))
    d.ellipse([dx - 6, dy - 4, dx + 6, dy + 4], fill=(80, 86, 94))
    # smoke / flames
    flames(d, tx + w * 0.02, ty - h * 0.16, 3, n=2)
    d.text((x + 4, y + 3), "GAZA CITY / JABALIA", font=F(8, bold=True), fill=(90, 30, 30))


def scene_finland(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h * 0.6], fill=(178, 196, 210))
    d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(52, 92, 128))
    for i in range(6):
        d.line([x, y + h * 0.62 + i * 6, x + w, y + h * 0.62 + i * 6 - 3], fill=(70, 112, 148))
    # cargo ship
    sx, sy = x + w * 0.24, y + h * 0.62
    d.polygon([(sx, sy), (sx + w * 0.5, sy), (sx + w * 0.46, sy + 12), (sx + w * 0.04, sy + 12)],
              fill=(70, 66, 62))
    d.rectangle([sx + w * 0.34, sy - h * 0.16, sx + w * 0.46, sy], fill=(210, 208, 202),
                outline=(60, 60, 60))
    for i, col in enumerate([(180, 60, 50), (60, 110, 170), (200, 150, 50)]):
        d.rectangle([sx + w * 0.04 + i * w * 0.09, sy - 10, sx + w * 0.11 + i * w * 0.09, sy - 1],
                    fill=col, outline=(50, 50, 50))
    flames(d, sx + w * 0.16, sy - 8, 4, n=3)
    # drone
    dx, dy = x + w * 0.7, y + h * 0.26
    d.line([dx - 12, dy, dx + 12, dy], fill=(40, 40, 40), width=2)
    d.line([dx, dy - 10, dx, dy + 10], fill=(40, 40, 40), width=2)
    for ex, ey in [(-12, 0), (12, 0), (0, -10), (0, 10)]:
        d.ellipse([dx + ex - 4, dy + ey - 3, dx + ex + 4, dy + ey + 3], fill=(60, 60, 60))
    # Finland flag
    flag(d, x + w - 34, y + 6, 28, 18, [((255, 255, 255), 1.0)],
         emblem=(9, 3, 5, 12, (28, 70, 162)))
    d.rectangle([x + w - 25, y + 2, x + w - 21, y + 6], fill=(120, 120, 120))
    d.text((x + 4, y + 3), "GULF OF FINLAND", font=F(8, bold=True), fill=(20, 40, 60))


def scene_mercury(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(16, 16, 34))
    star_field(d, bx)
    # sun
    d.ellipse([x + w - 34, y + 6, x + w - 6, y + 34], fill=(250, 214, 90))
    for a in range(8):
        import math
        ang = a * math.pi / 4
        d.line([x + w - 20 + 22 * math.cos(ang), y + 20 + 22 * math.sin(ang),
                x + w - 20 + 30 * math.cos(ang), y + 20 + 30 * math.sin(ang)],
               fill=(250, 214, 90), width=2)
    # Mercury
    cx, cy, r = x + w * 0.3, y + h * 0.58, min(w, h) * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 146, 140), outline=(90, 88, 84))
    for (ox, oy, orr) in [(-r * 0.3, -r * 0.2, r * 0.22), (r * 0.3, r * 0.1, r * 0.16),
                          (-r * 0.1, r * 0.4, r * 0.13), (r * 0.35, -r * 0.45, r * 0.12)]:
        d.ellipse([cx + ox - orr, cy + oy - orr, cx + ox + orr, cy + oy + orr],
                  fill=(126, 122, 116))
    # spacecraft
    px, py = x + w * 0.62, y + h * 0.44
    d.rectangle([px, py - 5, px + 30, py + 5], fill=(200, 204, 210), outline=(110, 112, 118))
    d.polygon([(px + 30, py - 5), (px + 38, py), (px + 30, py + 5)], fill=(160, 164, 170))
    d.rectangle([px + 2, py - 14, px + 12, py - 5], fill=(40, 90, 170))
    d.rectangle([px + 16, py + 5, px + 26, py + 14], fill=(40, 90, 170))
    d.text((x + 4, y + 3), "MERCURY", font=F(8, bold=True), fill=(210, 220, 240))


def scene_bahrain(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(232, 224, 200))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(214, 200, 168))
    # base building
    d.rectangle([x + 8, y + h * 0.36, x + 40, y + h * 0.76], fill=(196, 196, 190),
                outline=(110, 110, 106))
    d.rectangle([x + 12, y + h * 0.42, x + 22, y + h * 0.52], fill=(90, 110, 130))
    d.rectangle([x + 26, y + h * 0.42, x + 36, y + h * 0.52], fill=(90, 110, 130))
    # radar dish
    rx, ry = x + w * 0.62, y + h * 0.5
    d.rectangle([rx - 2, ry, rx + 2, y + h * 0.76], fill=(120, 120, 118))
    d.polygon([(rx - 14, ry - 10), (rx + 14, ry - 6), (rx + 14, ry + 6), (rx - 14, ry + 10)],
              fill=(180, 182, 178), outline=(90, 90, 90))
    # explosion burst
    import math
    for a in range(10):
        ang = a * math.pi / 5
        d.line([rx + 24 * math.cos(ang), ry - 18 + 24 * math.sin(ang),
                rx + 36 * math.cos(ang), ry - 18 + 36 * math.sin(ang)], fill=(240, 180, 40), width=2)
    d.ellipse([rx + 12, ry - 30, rx + 40, ry - 2], fill=(240, 150, 40))
    # Iran flag
    flag(d, x + 6, y + 4, 26, 16, [((35, 150, 70), 0.34), ((255, 255, 255), 0.32), ((198, 40, 40), 0.34)])
    d.text((x + 38, y + 5), "US BASE / BAHRAIN", font=F(8, bold=True), fill=(90, 40, 30))


def scene_cop31(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 226))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(200, 196, 176))
    d.text((x + 4, y + 2), "COP31", font=F(11, bold=True), fill=(20, 90, 60))
    # podium
    d.rectangle([x + w * 0.36, y + h * 0.5, x + w * 0.58, y + h * 0.8], fill=(120, 96, 70),
                outline=(70, 56, 40))
    figure(d, x + w * 0.47, y + h * 0.5, 12, (40, 70, 130))
    for i, col in enumerate([(230, 90, 60), (60, 130, 200), (240, 200, 70)]):
        d.polygon([(x + w * 0.66 + i * 9, y + h * 0.3), (x + w * 0.7 + i * 9, y + h * 0.64),
                   (x + w * 0.62 + i * 9, y + h * 0.64)], fill=col)
    # industry vs leaf
    d.rectangle([x + 10, y + h * 0.5, x + 24, y + h * 0.78], fill=(120, 120, 124))
    d.ellipse([x + 14, y + h * 0.46, x + 30, y + h * 0.54], fill=(150, 150, 154))
    d.polygon([(x + w - 26, y + h * 0.72), (x + w - 6, y + h * 0.5), (x + w - 4, y + h * 0.72)],
              fill=(60, 150, 90))


def scene_euindo(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(222, 230, 240))
    flag(d, x + 6, y + h * 0.16, 34, 22, [((28, 70, 162), 1.0)])
    import math
    for i in range(12):
        ang = i * math.pi / 6
        d.ellipse([x + 6 + 17 + 10 * math.cos(ang) - 1.5, y + h * 0.16 + 11 + 8 * math.sin(ang) - 1.5,
                   x + 6 + 17 + 10 * math.cos(ang) + 1.5, y + h * 0.16 + 11 + 8 * math.sin(ang) + 1.5],
                  fill=(250, 220, 70))
    flag(d, x + w - 40, y + h * 0.16, 34, 22, [((210, 40, 40), 0.5), ((255, 255, 255), 0.5)])
    # handshake
    d.line([x + w * 0.28, y + h * 0.62, x + w * 0.5, y + h * 0.52], fill=(60, 60, 60), width=6)
    d.line([x + w * 0.72, y + h * 0.62, x + w * 0.5, y + h * 0.52], fill=(60, 60, 60), width=6)
    d.ellipse([x + w * 0.46, y + h * 0.44, x + w * 0.54, y + h * 0.58], fill=(240, 210, 170),
              outline=(60, 60, 60))
    # container
    d.rectangle([x + w * 0.42, y + h * 0.78, x + w * 0.6, y + h * 0.92], fill=(200, 120, 60),
                outline=(90, 60, 30))


def scene_india(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 214))
    # warning triangle
    d.polygon([(x + w * 0.5, y + 4), (x + w * 0.86, y + h - 6), (x + w * 0.14, y + h - 6)],
              fill=(240, 196, 40), outline=(120, 90, 10))
    d.text((x + w * 0.5 - 2, y + h * 0.4), "!", font=F(14, bold=True), fill=(40, 30, 10))
    # bottle with skull
    bx2 = x + w * 0.12
    d.rectangle([bx2, y + h * 0.34, bx2 + 16, y + h * 0.86], fill=(120, 170, 120),
                outline=(40, 80, 40))
    d.rectangle([bx2 + 4, y + h * 0.26, bx2 + 12, y + h * 0.36], fill=(90, 140, 90))
    d.ellipse([bx2 + 3, y + h * 0.5, bx2 + 13, y + h * 0.6], fill=(240, 240, 240))
    d.ellipse([bx2 + 5, y + h * 0.53, bx2 + 7, y + h * 0.56], fill=(30, 30, 30))
    d.ellipse([bx2 + 9, y + h * 0.53, bx2 + 11, y + h * 0.56], fill=(30, 30, 30))
    # glass
    gx = x + w * 0.74
    d.polygon([(gx, y + h * 0.44), (gx + 16, y + h * 0.44), (gx + 12, y + h * 0.74),
               (gx + 4, y + h * 0.74)], fill=(210, 220, 235), outline=(90, 90, 90))
    d.rectangle([gx + 4, y + h * 0.56, gx + 12, y + h * 0.74], fill=(200, 180, 120))


def scene_iraq(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(224, 198, 150))
    d.rectangle([x, y + h * 0.8, x + w, y + h], fill=(206, 178, 132))
    for cx in (x + w * 0.18, x + w * 0.56):
        d.polygon([(cx, y + h * 0.24), (cx + 26, y + h * 0.8), (cx - 26, y + h * 0.8)],
                  fill=(178, 172, 164), outline=(110, 106, 100))
        d.rectangle([cx - 6, y + h * 0.24, cx + 6, y + h * 0.3], fill=(140, 136, 130))
    flames(d, x + w * 0.12, y + h * 0.62, 5, n=4)
    smoke(d, x + w * 0.2, y + h * 0.34, 5, n=3)
    # pylon
    d.line([x + w * 0.88, y + h * 0.3, x + w * 0.88, y + h * 0.82], fill=(80, 80, 84), width=2)
    d.line([x + w * 0.82, y + h * 0.4, x + w * 0.94, y + h * 0.4], fill=(80, 80, 84), width=2)


def scene_indonesia(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(226, 220, 214))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(198, 190, 182))
    d.rectangle([x + w * 0.16, y + h * 0.34, x + w * 0.72, y + h * 0.78], fill=(205, 200, 194),
                outline=(110, 106, 100))
    for i in range(3):
        d.rectangle([x + w * 0.22 + i * w * 0.16, y + h * 0.46, x + w * 0.3 + i * w * 0.16,
                     y + h * 0.56], fill=(90, 110, 130))
    flames(d, x + w * 0.24, y + h * 0.4, 5, n=4)
    smoke(d, x + w * 0.34, y + h * 0.16, 5, n=3)
    # sweets
    for i, col in enumerate([(220, 80, 90), (250, 200, 70), (100, 170, 220)]):
        sx = x + w * 0.78
        sy = y + h * 0.5 + i * 10
        d.ellipse([sx, sy, sx + 14, sy + 8], fill=col, outline=(90, 60, 60))
        d.polygon([(sx - 4, sy + 4), (sx, sy), (sx, sy + 8)], fill=col)
        d.polygon([(sx + 18, sy + 4), (sx + 14, sy), (sx + 14, sy + 8)], fill=col)


def scene_houthi(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(210, 224, 238))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(196, 206, 214))
    for i, bh in enumerate([0.30, 0.44, 0.24, 0.5, 0.34, 0.4, 0.28]):
        bxx = x + 6 + i * (w - 12) / 7
        d.rectangle([bxx, y + h * 0.78 - h * bh, bxx + (w - 12) / 7 - 3, y + h * 0.8],
                    fill=(150, 156, 166), outline=(100, 104, 112))
    # incoming missiles
    for i in range(3):
        mx = x + w * 0.24 + i * w * 0.22
        d.line([mx, y + 6, mx - 6, y + h * 0.42], fill=(120, 120, 120), width=2)
        d.polygon([(mx - 8, y + 6), (mx + 2, y + 16), (mx + 2, y + 4)], fill=(120, 40, 40))
        d.line([mx - 6, y + h * 0.42, mx + 14, y + h * 0.5], fill=(120, 120, 120))
    # interceptor bursts
    import math
    for bx2 in (x + w * 0.34, x + w * 0.62):
        for a in range(8):
            ang = a * math.pi / 4
            d.line([bx2, y + h * 0.46, bx2 + 8 * math.cos(ang), y + h * 0.46 + 8 * math.sin(ang)],
                   fill=(240, 200, 60), width=2)


def scene_bangladesh(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 200))
    d.rectangle([x, y + h * 0.74, x + w, y + h], fill=(190, 206, 178))
    for i in range(4):
        figure(d, x + 14 + i * 14, y + h * 0.78, 16, (40, 110, 60))
    for i in range(4):
        figure(d, x + w - 14 - i * 14, y + h * 0.78, 16, (40, 60, 120))
    flag(d, x + w * 0.44, y + h * 0.2, 26, 16, [((20, 120, 60), 1.0)], emblem=(9, 3, 8, 10, (210, 40, 40)))
    # tear gas puffs
    for i in range(3):
        d.ellipse([x + w * 0.5 - 6 + i * 8, y + h * 0.5 - 4, x + w * 0.5 + 4 + i * 8, y + h * 0.5 + 6],
                  fill=(220, 220, 210))


def scene_haiti(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(206, 226, 236))
    d.rectangle([x, y + h * 0.76, x + w, y + h], fill=(190, 210, 180))
    for px in (x + 24, x + w - 30):
        d.line([px, y + h * 0.2, px, y + h * 0.78], fill=(120, 90, 60), width=3)
        for a in (-1, 1):
            d.line([px, y + h * 0.2, px + a * 18, y + h * 0.12], fill=(50, 130, 70), width=4)
            d.line([px, y + h * 0.22, px + a * 16, y + h * 0.18], fill=(50, 130, 70), width=4)
    for i in range(3):
        figure(d, x + w * 0.34 + i * 18, y + h * 0.8, 18, (70, 80, 60), head=(60, 70, 50))
        d.ellipse([x + w * 0.34 + i * 18 - 7, y + h * 0.8 - 17, x + w * 0.34 + i * 18 + 7,
                   y + h * 0.8 - 9], fill=(60, 70, 50))
    flag(d, x + w * 0.42, y + h * 0.16, 26, 16, [((30, 60, 150), 0.5), ((200, 40, 40), 0.5)])


def scene_genz(d, bx):
    x, y, w, h = bx
    d.rectangle([x, y, x + w, y + h], fill=(224, 228, 238))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(206, 210, 220))
    for i in range(7):
        col = [(210, 70, 70), (60, 120, 200), (240, 200, 70)][i % 3]
        figure(d, x + 12 + i * 15, y + h * 0.82, 18, col)
    # placards
    for i in range(3):
        px = x + 20 + i * 34
        d.line([px, y + h * 0.6, px, y + h * 0.82], fill=(90, 80, 70), width=2)
        d.rectangle([px - 8, y + h * 0.4, px + 12, y + h * 0.6], fill=(250, 250, 245),
                    outline=(90, 90, 90))
    flag(d, x + w - 40, y + 6, 30, 18, [((28, 70, 162), 1.0)])
    import math
    for i in range(8):
        ang = i * math.pi / 4
        d.ellipse([x + w - 25 + 9 * math.cos(ang) - 1.4, y + 15 + 7 * math.sin(ang) - 1.4,
                   x + w - 25 + 9 * math.cos(ang) + 1.4, y + 15 + 7 * math.sin(ang) + 1.4],
                  fill=(250, 220, 70))


SCENES = {
    "gaza": scene_gaza, "finland": scene_finland, "mercury": scene_mercury,
    "bahrain": scene_bahrain, "cop31": scene_cop31, "euindo": scene_euindo,
    "india": scene_india, "iraq": scene_iraq, "indonesia": scene_indonesia,
    "houthi": scene_houthi, "bangladesh": scene_bangladesh, "haiti": scene_haiti,
    "genz": scene_genz,
}


# --------------------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------------------

def draw_masthead(d):
    d.rectangle([0, 0, W, H], fill=PAPER)
    d.text((M + 2, 6), "33 STORIES · FULLY ILLUSTRATED", font=F(11, bold=True), fill=GREY)
    d.text((W - M - 2, 6), "ONE PAGE · SAT 21 NOV 2026", font=F(11, bold=True), fill=GREY, anchor="ra")
    d.text((W / 2, 18), "THE WORLD TODAY", font=F(15, bold=True, serif=True), fill=INK, anchor="ma")
    d.text((W / 2, 32), "SATURDAY 21 NOVEMBER 2026", font=F(44, bold=True, serif=True), fill=RED, anchor="ma")
    d.line([M, 92, W - M, 92], fill=RULE, width=2)


def draw_numbers(d):
    d.text((W / 2, 98),
           "33 STORIES    MIDDLE EAST 5 · EUROPE 11 · ASIA 8 · AMERICAS 5 · OCEANIA 2 · AFRICA 1 · SPACE 1",
           font=F(11, bold=True), fill=INK, anchor="ma")
    d.text((W / 2, 114),
           "4 KILLED IN GAZA  ·  98.5% EU TARIFFS CUT  ·  24m bbl SAUDI OIL TO JAPAN  ·  "
           "1.6m VEHICLES RECALLED  ·  11 DEAD, 180 POISONED IN INDIA",
           font=F(11, bold=True), fill=RED, anchor="ma")
    d.text((W / 2, 130),
           "HOW SURE ARE WE? 33 stories, each checked against a primary outlet for its EVENT date; "
           "10 other-day stories left out (see DATE CHECK).",
           font=F(10), fill=GREY, anchor="ma")
    d.line([M, 144, W - M, 144], fill=RULE, width=1)


def draw_big(d):
    y0 = 150
    h = 212
    gap = 6
    cw = (W - 2 * M - 2 * gap) / 3
    for i, (n, region, conf, place, head, sub, key) in enumerate(BIG):
        x = M + i * (cw + gap)
        d.rectangle([x, y0, x + cw, y0 + h], fill=(255, 255, 255), outline=BORDER)
        # number badge
        d.ellipse([x + 6, y0 + 6, x + 28, y0 + 28], fill=RED)
        d.text((x + 17, y0 + 17), str(n), font=F(14, bold=True), fill=(255, 255, 255), anchor="mm")
        # illustration
        ib = (x + 3, y0 + 3, cw - 6, 116)
        SCENES[key](d, ib)
        d.rectangle([ib[0], ib[1], ib[0] + ib[2], ib[1] + ib[3]], outline=BORDER)
        # tags
        ty = y0 + 124
        tag(d, (x + 4, ty), region, REGION[region], fnt=F(9, bold=True))
        tw = d.textlength(conf, font=F(9, bold=True)) + 6
        tag(d, (x + cw - 4 - tw, ty), conf, CONF[conf], fnt=F(9, bold=True))
        # headline
        yy = ty + 16
        for ln in wrap(d, head, F(17, bold=True), cw - 10)[:2]:
            d.text((x + 5, yy), ln, font=F(17, bold=True), fill=INK)
            yy += 19
        d.text((x + 5, yy + 1), place, font=F(9, bold=True), fill=GREY)
        block(d, (x + 5, yy + 13), sub, F(10), (70, 68, 64), cw - 10, lead=1.0)
    return y0 + h + 6


def draw_medium(d, y0):
    rows, cols = 2, 5
    gap = 4
    cw = (W - 2 * M - (cols - 1) * gap) / cols
    ch = 95
    idx = 0
    for r in range(rows):
        for c in range(cols):
            n, region, conf, place, head, sub, key = MEDIUM[idx]
            idx += 1
            x = M + c * (cw + gap)
            y = y0 + r * (ch + gap)
            d.rectangle([x, y, x + cw, y + ch], fill=(255, 255, 255), outline=BORDER)
            d.rectangle([x, y + 1, x + 3, y + ch - 1], fill=REGION[region])
            ib = (x + 5, y + 3, cw - 10, 34)
            SCENES[key](d, ib)
            d.rectangle([ib[0], ib[1], ib[0] + ib[2], ib[1] + ib[3]], outline=BORDER)
            d.ellipse([x + cw - 19, y + 2, x + cw - 5, y + 16], fill=RED)
            d.text((x + cw - 12, y + 9), str(n), font=F(9, bold=True), fill=(255, 255, 255), anchor="mm")
            ty = y + 40
            tag(d, (x + 5, ty), region, REGION[region], fnt=F(7, bold=True), pad=2)
            pw = d.textlength(place, font=F(7, bold=True))
            d.text((x + 5 + d.textlength(region, font=F(7, bold=True)) + 8, ty + 2), place,
                   font=F(7, bold=True), fill=GREY)
            tw = d.textlength(conf, font=F(7, bold=True)) + 4
            tag(d, (x + cw - 5 - tw, ty), conf, CONF[conf], fnt=F(7, bold=True), pad=2)
            yy = y + 52
            for ln in wrap(d, head, F(11, bold=True), cw - 10)[:2]:
                d.text((x + 5, yy), ln, font=F(11, bold=True), fill=INK)
                yy += 12
            block(d, (x + 5, yy), sub, F(8), (84, 82, 78), cw - 10, lead=1.0)
    return y0 + rows * ch + (rows - 1) * gap + 6


def draw_list(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=BORDER)
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    d.text((x + 5, y + 3), "ALSO ON SATURDAY 21 NOVEMBER", font=F(11, bold=True), fill=(255, 255, 255))
    yy = y + 20
    for n, region, text in LIST:
        d.text((x + 5, yy), str(n), font=F(9, bold=True), fill=REGION[region], anchor="la")
        lines = wrap(d, text, F(9), w - 26)[:2]
        for j, ln in enumerate(lines):
            d.text((x + 22, yy + j * 10), ln, font=F(9), fill=INK)
        yy += 10 * len(lines) + 3


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=BORDER)
    d.rectangle([x, y, x + w, y + 16], fill=(40, 70, 120))
    d.text((x + 5, y + 3), "WHERE IT HAPPENED — NUMBERED PINS MATCH THE FEATURES", font=F(10, bold=True),
           fill=(255, 255, 255))
    box = (x + 5, y + 20, w - 10, h - 46)
    proj = worldmap.draw_world(d, box)
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(220, 40, 40), outline=(255, 255, 255))
        d.text((px, py), str(n), font=F(8, bold=True), fill=(255, 255, 255), anchor="mm")
    # off-map Mercury pin
    mx, my = x + w - 30, y + 26
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(220, 40, 40), outline=(255, 255, 255))
    d.text((mx, my), "3", font=F(8, bold=True), fill=(255, 255, 255), anchor="mm")
    d.text((mx, my + 10), "Mercury", font=F(7, bold=True), fill=GREY, anchor="ma")
    # legend
    ly = y + h - 22
    lx = x + 6
    for name, col in REGION.items():
        d.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=col)
        d.text((lx + 11, ly), name, font=F(8, bold=True), fill=INK)
        lx += 14 + d.textlength(name, font=F(8, bold=True))
        if lx > x + w - 70:
            lx = x + 6
            ly += 12
    d.text((x + w - 6, y + h - 11), "Pins 1-2, 4-13 = places on the map.", font=F(7), fill=GREY, anchor="ra")


def draw_datecheck(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 249, 236), outline=RED)
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    d.text((x + 5, y + 3), "DATE CHECK", font=F(11, bold=True), fill=(255, 255, 255))
    d.text((x + 5, y + 20),
           "Every story on this page happened, or was first reported, on Saturday 21 November 2026.",
           font=F(9), fill=INK)
    d.text((x + 5, y + 32), "LEFT OUT AS OTHER DAYS' NEWS:", font=F(9, bold=True), fill=RED)
    ncol = 3
    colw = (w - 10 - (ncol - 1) * 8) / ncol
    for i, txt in enumerate(EXCLUDED):
        cx = x + 5 + (i % ncol) * (colw + 8)
        cy = y + 46 + (i // ncol) * 13
        d.text((cx, cy), "• " + txt, font=F(9), fill=INK)
    d.text((x + w - 6, y + h - 12),
           "Every figure and place on this page is checked against a primary outlet (see SOURCES.md).",
           font=F(8), fill=GREY, anchor="ra")


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_numbers(d)
    y = draw_big(d)
    y = draw_medium(d, y)
    # bottom band: map + numbered list on top, full-width DATE CHECK below
    by = y
    bottom_h = H - by - M - 14
    list_w = 382
    map_w = W - 2 * M - list_w - 6
    upper_h = 284
    draw_map(d, M, by, map_w, upper_h)
    draw_list(d, M + map_w + 6, by, list_w, upper_h)
    draw_datecheck(d, M, by + upper_h + 4, W - 2 * M, bottom_h - upper_h - 4)
    d.line([M, H - 13, W - M, H - 13], fill=RULE, width=1)
    d.text((W / 2, H - 11),
           "Every story is an event of Saturday 21 November 2026.  Sources: AFP, Reuters, Al Jazeera, Euronews, "
           "The Guardian, BBC, AP, ESA, USGS, The Japan Times, UNB, TBS, The Daily Star, New York Post.",
           font=F(7), fill=GREY, anchor="ma")
    img.save(path)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render(out)
    print("wrote", out)
