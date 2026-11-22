"""worldmap.py — simplified public-style continent polygons for the news page.

Everything here is hand-written coordinate data (a coarse, recognisable world) drawn with
Pillow primitives. No external images, no network. Longitude/latitude are projected with a
simple equirectangular projection onto the given box.
"""

# Each continent/country blob is a list of (lon, lat) points, closed by the renderer.
LAND = {
    "greenland": [(-45, 60), (-30, 68), (-20, 74), (-22, 82), (-40, 84), (-58, 80),
                  (-55, 68), (-48, 62), (-45, 60)],
    "north_america": [(-168, 65), (-165, 71), (-150, 71), (-133, 70), (-115, 70), (-95, 70),
                      (-80, 73), (-64, 60), (-53, 52), (-60, 47), (-70, 45), (-72, 40),
                      (-76, 35), (-81, 25), (-85, 30), (-90, 29), (-97, 26), (-105, 22),
                      (-114, 30), (-124, 40), (-124, 48), (-132, 55), (-140, 60), (-152, 59),
                      (-165, 55), (-168, 65)],
    "central_america": [(-97, 26), (-92, 18), (-87, 15), (-83, 9), (-77, 8), (-79, 15),
                        (-84, 17), (-88, 21), (-97, 26)],
    "caribbean": [(-85, 23), (-74, 20), (-66, 18), (-61, 18), (-70, 18), (-80, 22), (-85, 23)],
    "south_america": [(-81, 10), (-70, 12), (-60, 10), (-50, 0), (-35, -6), (-38, -15),
                      (-48, -25), (-58, -35), (-62, -40), (-66, -55), (-72, -52), (-75, -45),
                      (-71, -30), (-70, -18), (-78, -5), (-81, 10)],
    "europe": [(-9, 37), (-9, 43), (-2, 43), (3, 43), (8, 44), (13, 45), (16, 42), (19, 40),
               (24, 40), (28, 41), (31, 45), (38, 46), (45, 48), (45, 55), (40, 60), (30, 63),
               (30, 70), (20, 70), (10, 64), (5, 58), (8, 54), (3, 52), (-2, 49), (-5, 44),
               (-9, 43), (-9, 37)],
    "uk": [(-6, 50), (-6, 54), (-5, 58), (-2, 58), (0, 54), (1, 51), (-5, 50), (-6, 50)],
    "africa": [(-17, 15), (-16, 20), (-10, 27), (0, 32), (10, 34), (20, 32), (32, 31),
               (35, 24), (39, 15), (43, 11), (51, 12), (48, 2), (41, -5), (40, -15),
               (32, -28), (25, -34), (18, -34), (12, -18), (9, -1), (9, 4), (3, 6),
               (-8, 5), (-13, 9), (-17, 15)],
    "madagascar": [(43, -12), (50, -15), (50, -25), (45, -25), (43, -12)],
    "asia": [(30, 45), (45, 48), (60, 45), (72, 45), (85, 45), (98, 50), (110, 50),
             (122, 53), (132, 45), (142, 50), (152, 60), (162, 66), (172, 68), (178, 68),
             (178, 62), (162, 58), (142, 52), (135, 45), (128, 39), (122, 32), (115, 22),
             (108, 18), (102, 10), (97, 8), (92, 20), (88, 22), (80, 15), (77, 8),
             (72, 20), (68, 24), (62, 25), (57, 22), (50, 28), (43, 30), (35, 29),
             (35, 36), (28, 41), (30, 45)],
    "japan": [(129, 32), (135, 34), (141, 36), (142, 40), (145, 44), (141, 42), (137, 36),
              (132, 34), (129, 32)],
    "indonesia": [(95, 5), (103, -1), (110, -7), (118, -9), (124, -9), (131, -8), (141, -8),
                  (141, -3), (128, -1), (118, 1), (110, 3), (100, 6), (95, 5)],
    "philippines": [(120, 18), (124, 14), (126, 9), (122, 6), (120, 12), (120, 18)],
    "australia": [(114, -22), (113, -26), (115, -34), (123, -34), (129, -32), (135, -35),
                  (140, -38), (148, -38), (153, -28), (146, -19), (142, -11), (136, -12),
                  (130, -11), (125, -14), (122, -18), (114, -22)],
    "new_zealand": [(172, -34), (178, -38), (174, -42), (168, -47), (166, -45), (171, -40),
                    (172, -34)],
}

# Equirectangular window used for the drawing (crop Antarctica, keep the inhabited band).
LON_MIN, LON_MAX = -180.0, 180.0
LAT_TOP, LAT_BOTTOM = 75.0, -52.0


def project(lon, lat, box):
    """Project (lon, lat) degrees into the pixel box (x, y, w, h)."""
    x0, y0, w, h = box
    fx = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    fy = (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM)
    return (x0 + fx * w, y0 + fy * h)


def draw_world(draw, box, ocean=(223, 232, 240), land=(232, 222, 200),
               outline=(150, 140, 120), graticule=(205, 216, 226), grid=True):
    """Draw the simplified world into `box` = (x, y, w, h). Returns `project` for pins."""
    x0, y0, w, h = box
    draw.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=ocean, outline=outline)

    if grid:
        for lon in range(-150, 180, 30):
            px, _ = project(lon, 0, box)
            draw.line([px, y0, px, y0 + h - 1], fill=graticule)
        for lat in range(-40, 74, 20):
            _, py = project(0, lat, box)
            draw.line([x0, py, x0 + w - 1, py], fill=graticule)

    for points in LAND.values():
        poly = [project(lo, la, box) for (lo, la) in points]
        draw.polygon(poly, fill=land, outline=outline)

    return lambda lon, lat: project(lon, lat, box)
