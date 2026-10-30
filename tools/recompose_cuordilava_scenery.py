#!/usr/bin/env python3
"""Strong, coherent scenery shapes on the 23 ORIGINAL Cuordilava scenic cells.

A new full 16x16 illustration is composed for palms, chimney, forge-lantern,
and mineral-water cascades. No extra pixels outside the existing four 8x8
sources per type. The exact old metatile attributes and event-safe 20x20 map
positions stay in dress_cuordilava_scenery.py.
"""


def recompose_scenery(kind, previous):
    if kind not in ("palm", "chimney", "lamp", "cascade"):
        raise ValueError(f"Unrecognized existing scenery {kind}")
    if len(previous) != 16 or any(len(row) != 16 for row in previous):
        raise ValueError(f"{kind}: existing scenic mural must remain 16x16")
    art = [[0] * 16 for _ in range(16)]

    def p(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            art[y][x] = c
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                p(x, y, c)
    def stroke(x0, y0, x1, y1, c):
        dx = abs(x1-x0)
        dy = -abs(y1-y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        while True:
            p(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            t = 2 * error
            if t >= dy:
                error += dy
                x0 += sx
            if t <= dx:
                error += dx
                y0 += sy

    if kind == "palm":
        # Broad orange-flowering green volcanic tropical plant. It occupies
        # the original ONE 16x16 palm cell, not a new two-block sprite.
        for y in range(1, 11):
            for x in range(1, 15):
                left = 3*(x-5)**2 + 2*(y-6)**2 < 51
                crown = 2*(x-8)**2 + 3*(y-4)**2 < 72
                right = 3*(x-11)**2 + 2*(y-7)**2 < 55
                if left or crown or right:
                    if (x*3 + y*7) % 13 == 0:
                        c = 0  # serrated canopy, not a square green blob
                    elif y < 4 and (x+y)%3:
                        c = 15  # bright new leaf tips
                    elif (x*5 + y*2)%7 in (0,1):
                        c = 9  # deep foliage cutout
                    else:
                        c = 10  # dominant natural mid-green
                    p(x, y, c)
        # Tapered branches grow through the canopy, clearly belonging to a
        # single organic plant and casting shadow across the lower ground.
        stroke(8, 6, 7, 15, 8)
        stroke(9, 7, 9, 15, 13)
        for y in range(10, 16):
            p(7, y, 8 if y % 3 else 5)
            p(8, y, 13 if y % 4 else 11)
            p(9, y, 8)
        for x, y in ((3, 5), (5, 3), (12, 5), (13, 7),
                     (2, 8), (5, 9), (11, 9), (10, 3)):
            p(x, y, 11)
            p(x+1, y, 14)
            p(x, y+1, 15)
        for x, y in ((1, 8), (3, 10), (13, 10), (14, 8),
                     (2, 7), (12, 3), (6, 1)):
            p(x, y, 15)
        for x in (6, 7, 9, 10):
            p(x, 15, 8)

    elif kind == "chimney":
        # Wide battered brick forging stack: shoulder, vent mouth and
        # continuous warm glass between basalt support posts.
        rect(5, 4, 11, 15, 8)
        rect(6, 5, 10, 14, 13)
        for y in range(5, 15):
            p(5, y, 5)
            p(11, y, 8)
            p(6, y, 11 if y % 4 else 14)
            p(10, y, 12 if y % 3 else 11)
            p(7, y, 12)
            p(8, y, 14 if y%3 == 0 else 12)
            p(9, y, 12)
            if y in (7, 11):
                stroke(4, y, 12, y, 5)
        rect(3, 2, 13, 4, 8)
        stroke(3, 2, 13, 2, 6)
        stroke(4, 3, 12, 3, 5)
        # Structural iron vent cap and two orange exhaust highlights.
        rect(5, 0, 11, 1, 8)
        stroke(5, 0, 11, 0, 5)
        for x in (6, 8, 10):
            p(x, 1, 11)
        for x, y in ((3, 1), (12, 1), (2, 3), (13, 4)):
            p(x, y, 13)
            p(x+1, y, 14)
        stroke(4, 15, 12, 15, 5)

    elif kind == "lamp":
        # Replace original lollipop with a recognisable enclosed copper
        # street lantern and a continuous iron post.
        rect(7, 8, 8, 15, 8)
        stroke(7, 9, 7, 15, 6)
        stroke(8, 10, 8, 14, 5)
        stroke(4, 15, 11, 15, 8)
        stroke(6, 14, 9, 14, 5)
        rect(4, 3, 11, 9, 8)
        rect(5, 4, 10, 8, 13)
        rect(6, 5, 9, 7, 12)
        p(7, 5, 14)
        p(8, 6, 11)
        stroke(4, 3, 11, 3, 5)
        stroke(5, 2, 10, 2, 6)
        stroke(6, 1, 9, 1, 8)
        p(7, 0, 14)
        stroke(5, 8, 10, 8, 5)
        stroke(4, 9, 11, 9, 6)
        for x, y in ((3, 5), (12, 5), (3, 8), (12, 8)):
            p(x, y, 13)
        p(6, 12, 15)
        p(9, 12, 10)

    elif kind == "cascade":
        # This 2x2 original cliff strip is OUTSIDE the original pool's
        # enclosing stone ring. Its old vertical turquoise/white streams
        # looked like the hot spring leaked down the outside of the rim.
        # Carve a NATURAL ROCK RETAINING BANK, not square gray grille panels.
        # Keep palette-8 water indices 1, 9 and 10 entirely absent.
        rocks = (
            (5, 3, 5, 4),   # (cx,cy,halfwidth,halfheight) large upper mass
            (11, 5, 4, 5),  # right steep cliff shoulder
            (5, 12, 5, 5),  # irregular lower basalt step
            (12, 13, 4, 3),
        )
        for y in range(16):
            for x in range(1, 15):
                # Indented boundary dissolves into the old original rock,
                # instead of creating a straight metallic rectangle.
                left_edge = 2 + (1 if y in (1, 8, 13) else 0)
                right_edge = 13 - (1 if y in (3, 10, 15) else 0)
                if not left_edge <= x <= right_edge:
                    continue
                mass = -1
                for i, (cx, cy, rx, ry) in enumerate(rocks):
                    if (x-cx)**2 * ry**2 + (y-cy)**2 * rx**2 < rx**2*ry**2:
                        mass = i
                        break
                if mass == -1:
                    # Deep gaps between large rough volcanic stones.
                    c = 8 if (x + 3*y) % 3 else 7
                else:
                    d = (x * 17 + y * 11 + mass * 7) % 17
                    if d in (0, 4):
                        c = 4  # lighter weathered basalt highlights
                    elif d in (5, 12):
                        c = 5
                    elif d in (1, 3, 9):
                        c = 6
                    else:
                        c = 7 if (x + y + mass) % 3 else 8
                p(x, y, c)

        # Two angled cracks, shallow stone plateaus and ash-filled crevices,
        # explicitly NOT horizontal/vertical metal grid-lines.
        for x0, y0, x1, y1 in (
            (4, 2, 7, 5), (7, 5, 5, 8),
            (10, 2, 12, 5), (12, 5, 10, 7),
            (3, 11, 6, 9), (6, 9, 9, 11),
            (10, 12, 12, 14),
        ):
            stroke(x0, y0, x1, y1, 8)
        for x0, y0, x1, y1 in (
            (3, 4, 6, 3), (9, 7, 12, 6),
            (3, 13, 7, 12), (9, 14, 12, 13),
        ):
            stroke(x0, y0, x1, y1, 5)
        # Sparse DRY yellow-ochre mineral veins (palette 8: ochre, not
        # teal); a few faint moss-coloured deposits live at the cliff base.
        for x, y, color in (
            (3, 2, 12), (4, 2, 13), (11, 3, 13),
            (9, 9, 12), (10, 9, 13), (4, 12, 13),
            (5, 13, 14), (12, 13, 14),
        ):
            p(x, y, color)

    if any(not 0 <= color <= 15 for row in art for color in row):
        raise ValueError(f"{kind}: new scenic graphic exceeds GBA 4bpp")
    change = sum(a != b for row0, row1 in zip(previous, art) for a, b in zip(row0, row1))
    minimum_change = 60 if kind in ("lamp", "cascade") else 80
    if change < minimum_change:
        raise ValueError(f"{kind}: expected a scenic silhouette redesign, got {change}")
    if kind == "palm":
        leaves = sum(v in (9,10,15) for row in art for v in row)
        flowers = sum(v == 11 for row in art for v in row)
        if leaves < 65 or flowers < 8:
            raise ValueError(f"New palm too sparse: {leaves=}, {flowers=}")
    if kind == "cascade":
        # This scene is now the OUTER ROCK WALL, not a waterfall outside the
        # hot spring. Never reintroduce any water or water-foam pixels here.
        wet = sum(v in (1, 9, 10) for row in art for v in row)
        stone = sum(v in (5, 6, 7, 8) for row in art for v in row)
        if wet or stone < 120 or any(row[0] or row[15] for row in art):
            raise ValueError(
                f"Thermal retaining bank is leaking/transparent: wet={wet}, stone={stone}"
            )
    return art
