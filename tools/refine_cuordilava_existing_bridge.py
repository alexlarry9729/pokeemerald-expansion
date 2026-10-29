#!/usr/bin/env python3
"""Rustic copperwood walkway over Cuordilava's already existing hot-spring rail.

Pure 64x16 town-private 4bpp mural polish. The rail occupies the same four
decorative metatiles, on exactly the same original 20x20 map cells. Water,
passability, entry points, steaming spring effects and events do not change.
"""


def refine_existing_thermal_bridge(art, name):
    if "THERMAL_BASIN_BRIDGE_RAIL" not in name:
        return
    if (art.w, art.h) != (64, 16):
        raise ValueError("Original four-cell Cuordilava spring railing moved")
    original = [row[:] for row in art.pix]
    def p(x, y, c):
        if 0 <= x < 64 and 0 <= y < 16:
            art.pixel(x, y, c)
    def horiz(x0, x1, y, c):
        for x in range(x0, x1 + 1):
            p(x, y, c)
    # Open space above y=8 deliberately retains the animated spring beneath.
    # A continuous copperwood bridge deck and two backlit wrought-iron rails.
    for y, tone in ((9,5),(10,13),(11,11),(12,12),(13,8),(14,6)):
        horiz(1, 62, y, tone)
    for x in range(3, 62, 7):
        # Dark staggered gaps between wooden planks, not a neon wall.
        for y in (10, 11, 12):
            p(x, y, 8)
        horiz(x+1, x+4, 11, 13)
        p(x+2, 12, 14)
    # Keep the same stone post locations originally drawn by the renderer.
    for x in (1,13,26,39,51,62):
        for y in range(5,15):
            p(x, y, 5)
            if x+1 < 64:
                p(x+1, y, 6)
        for y in (6,10):
            p(x, y, 13)
            p(x+1, y, 11)
        p(x,4,14)
        p(x+1,4,13)
        p(x,15,8)
    # Light from the thermal pools peeks through the top bar and lower joints.
    for x in range(6, 61, 9):
        horiz(x, x+3, 7, 5)
        p(x+1,8,9)
        p(x+2,8,10)
        p(x+2,13,5)
    # The feet and both sides remain open to the water rather than extending
    # the bridge's impassable footprint by a new metatile.
    if any(art.pix[y][x] != original[y][x] for y in range(0,3)
           for x in range(64)):
        raise ValueError("Transparent spring water above the bridge changed")
    changed=sum(a!=b for before,after in zip(original,art.pix)
                for a,b in zip(before,after))
    if changed<100:
        raise ValueError(f"Thermal railing not sufficiently transformed: {changed}")
    if any(not 0<=c<=15 for row in art.pix for c in row):
        raise ValueError("Cuordilava thermal railing is no longer indexed 4bpp")
