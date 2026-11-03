#!/usr/bin/env python3
"""Heavy, town-private architectural redraw for Cuordilava's four civic murals.

A 64x32 mural is a fixed 4x2 arrangement of original 16x16 map cells.
Carve coherent roof profiles, occupied volumes, arcades, columns, awnings,
glazing and foundations directly into those SAME pixels. In particular, no
new map footprint, objects, tile allocations, warps or foreground layers are
introduced. This is the last mural pass, after organize_districts().
"""

ROLES = {
    "POKEMON_CENTER_INDUSTRIAL_REACTOR": "center",
    "POKE_MART_TECHNICAL_FACADE": "mart",
    "FLANNERY_GYM_MOLTEN_FORGE": "gym",
    "HOUSING_MAGMA_TERRACES": "homes",
}

def carve_architecture(art, name):
    role = ROLES.get(name)
    if role is None:
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError("The existing 4x2 landmark must remain exactly 64x32")
    original = [r[:] for r in art.pix]
    locked = set()

    # All structural eaves, recognisable identifiers and exact validator
    # anchors remain IMMUTABLE. The CENTER, MART and GYM inner emblem bays
    # are left completely intact, including their gameplay-facing symbols.
    if role == "center":
        locked |= {(x, 11) for x in range(7, 57)}
        locked |= {(x, y) for x in range(23, 42)
                   for y in range(13, 25)}
        locked |= {(31, 1), (20, 8), (31, 18), (10, 16)}
    elif role == "mart":
        locked |= {(x, 11) for x in range(11, 53)}
        locked |= {(x, 27) for x in range(16, 48)}
        locked |= {(x, y) for x in range(20, 45)
                   for y in range(14, 26)}
        locked |= {(20, 8), (32, 20), (9, 16)}
    elif role == "gym":
        locked |= {(x, 0) for x in range(1, 6)}
        locked |= {(x, 3) for x in range(19, 45)}
        locked |= {(x, 11) for x in range(12, 52)}
        locked |= {(x, y) for x in range(19, 46)
                   for y in range(13, 26)}
        locked |= {(20, 8), (32, 19)}
    else:
        locked |= {(x, 1) for x in (12, 25, 39, 52)}
        locked |= {(x, 12) for x in (12, 25, 39, 52)}
        locked |= {(13, 8)}

    def p(x, y, c):
        if 0 <= x < 64 and 0 <= y < 32 and (x, y) not in locked:
            art.pixel(x, y, c)

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                p(x, y, c)

    def hline(x0, x1, y, c):
        for x in range(x0, x1+1):
            p(x, y, c)

    def vline(x, y0, y1, c):
        for y in range(y0, y1+1):
            p(x, y, c)

    def slope_roof(left, right, crest, pitch, material, accent):
        """Carve a true sloped roof plane with separate lip and underside."""
        cx = (left + right)//2
        for x in range(left, right+1):
            roofline = min(9, crest + abs(x-cx)//pitch)
            for y in range(roofline, 11):
                if y == roofline:
                    c = 5
                elif y == roofline+1:
                    c = 6
                elif y == 10:
                    c = 8
                elif y == 9:
                    c = accent if (x//5)%5 else 5
                else:
                    c = material if (x//6 + y//3)%5 else 3
                p(x, y, c)
        hline(left-1, right+1, 10, 5)

    def window(cx, top, half, glass, pane="vertical"):
        """Recessed 3-dimensional window instead of painted-on neon squares."""
        left, right = cx-half, cx+half
        rect(left-2, top-1, right+2, top+10, 8)  # deep structural cavity
        hline(left-2, right+2, top-1, 5)
        hline(left-1, right+1, top, 6)
        vline(left-1, top+1, top+9, 5)
        vline(right+1, top+1, top+9, 5)
        for y in range(top+1, top+9):
            for x in range(left, right+1):
                edge = x in (left,right) or y in (top+1,top+8)
                if edge:
                    c = 6
                elif pane == "vertical" and x == cx:
                    c = 8
                elif pane == "horizontal" and y == top+5:
                    c = 8
                elif pane == "kiln" and y%3 == 0:
                    c = 5
                else:
                    c = glass if (x+y)%7 else 14
                p(x, y, c)
        hline(left-2, right+2, top+10, 5)
        hline(left-1, right+1, top+11, 13)

    def masonry_bay(left, right, top, floor, base, warm):
        """One continuous stone-faced building *volume*, not loose lamps."""
        for y in range(top, floor+1):
            for x in range(left, right+1):
                if x in (left,right):
                    c = 8
                elif x in (left+1,right-1):
                    c = 5
                elif y in (top,floor):
                    c = 5
                elif y in (top+1,floor-1):
                    c = 6
                elif (y-top)%7 == 0:
                    c = 4
                else:
                    c = base if (x//8+y//5)%6 else 3
                p(x,y,c)
        # Coloured architectural footing: heat lives inside the building.
        hline(left+2, right-2, floor-2, warm)
        hline(left, right, floor+1, 8)

    def buttress(x, ytop, ybottom, cap):
        """Projecting 3px load-bearing pier with shadow and raised stone cap."""
        rect(x-1, ytop, x+1, ybottom, 8)
        vline(x-1, ytop+2, ybottom-1, 5)
        vline(x, ytop+3, ybottom-2, 3)
        hline(x-2, x+2, ytop+1, 5)
        p(x, ytop, cap)
        hline(x-2, x+2, ybottom, 6)

    def crown(cx, top, half, lit):
        """Actual small upper storey with stone crenellations and inset glass."""
        for y in range(top, 11):
            for x in range(cx-half, cx+half+1):
                edge = x in (cx-half,cx+half) or y in (top,10)
                if edge:
                    c = 5
                elif y == top+1:
                    c = 6
                elif abs(x-cx) <= 2 and top+3<=y<=8:
                    c = lit if x!=cx else 8
                else:
                    c = 3
                p(x,y,c)
        hline(cx-half-1, cx+half+1, top, 6)
        for x in (cx-half, cx+half):
            p(x, top-1, 5)

    if role == "center":
        # Healthcare: monumental central cross tower, flanking sloped clinic
        # wings and an inhabited medical ground floor. Ruby is prominent.
        slope_roof(5, 24, 1, 4, 3, 13)
        slope_roof(40, 59, 2, 4, 3, 13)
        crown(32, 2, 7, 12)
        for cx in (14, 51):
            crown(cx, 4, 4, 12)
        for left, right in ((5,22),(42,59)):
            masonry_bay(left,right,13,29,3,13)
        for cx in (14, 51):
            window(cx,16,4,12)
        for x in (5,22,42,59):
            buttress(x,13,30,14)
        # Low long hospital emergency ribbon connects the two wings without
        # covering the protected red cross or any warp.
        for y in (26,27,28):
            for x in list(range(8,22))+list(range(43,57)):
                if y==26 or (x+y)%8:
                    p(x,y,12 if y==27 else 13)
        hline(9,55,30,5)

    elif role == "mart":
        # Mart: angular stepped warehouse, long cyan cold-glass clerestory,
        # physical loading bays and substantial supply-depot columns.
        for left,right,top in ((5,20,2),(20,36,0),(36,58,3)):
            slope_roof(left,right,top,5,4,9)
        for cx in (13, 49):
            crown(cx,3,5,10)
        for left,right in ((6,19),(45,58)):
            masonry_bay(left,right,13,28,2,11)
        for cx in (13, 51):
            window(cx,15,4,10,"horizontal")
        for x in (6,19,45,58):
            buttress(x,13,29,10)
        # A rigid two-tone loading arcade ends at (but never erases) the
        # existing blue canopy on y=27 x16..47.
        for left,right in ((7,19),(45,57)):
            hline(left,right,26,5)
            hline(left+1,right-1,27,9)
            hline(left+2,right-2,28,10)
        hline(7,57,30,5)

    elif role == "gym":
        # Gym: giant stepped furnace hall, tall unequal smelter chimneys and
        # deep orange blast doors. Its unique central flame crest stays.
        for left,right,top in ((6,22,3),(21,48,1),(48,60,4)):
            slope_roof(left,right,top,5,8,13)
        for cx,top,half in ((10,0,5),(54,1,4)):
            crown(cx,top,half,12)
            for y in (top+3,top+6):
                hline(cx-2,cx+2,y,14)
        # Huge hot forge roof over central crest, with the mandatory
        # copper row y3 x19..44 retained exactly.
        for y in range(5,11):
            for x in range(22,43):
                if y in (5,10) or x in (22,42):
                    p(x,y,5)
                elif y in (7,8) and x%6 in (2,3):
                    p(x,y,14)
                else:
                    p(x,y,8)
        for left,right in ((5,18),(47,59)):
            masonry_bay(left,right,13,29,8,13)
        for cx in (12,52):
            window(cx,15,4,12,"kiln")
        for x in (5,18,47,59):
            buttress(x,13,30,14)
        # Lower kiln mouth and heavy hot rolled-steel footing.
        for left,right in ((9,17),(48,56)):
            rect(left,26,right,28,12)
            hline(left,right,26,14)
            hline(left-1,right+1,29,5)
        hline(7,57,30,13)

    else:  # Four separate houses rather than a single long conveyor belt.
        homes = (
            (6,18,12,1,3,12,0),   # copper-gabled inn, tall dormer
            (19,32,25,3,8,9,1),  # slate terrace, low industrial dormer
            (33,45,39,0,3,14,2), # forge worker's steep chimney house
            (46,59,52,2,4,10,3), # gray basalt observatory house
        )
        for left,right,cx,top,stone,glass,index in homes:
            slope_roof(left,right,top,3 if index%2==0 else 5,stone,
                       13 if index in (0,2) else 6)
            if index == 2:
                # Tall isolated hearth stack, distinctive among the homes.
                rect(left+1,1,left+3,9,8)
                vline(left+1,2,8,5)
                hline(left, left+4, 2, 13)
            elif index == 3:
                crown(cx,3,3,10)
            else:
                crown(cx,4 if index==0 else 5,3,glass)
            masonry_bay(left,right,14,28,stone,13)
            window(cx,17 if index!=1 else 16,3,glass,
                   "horizontal" if index==1 else "vertical")
            buttress(left,14,29,13)
            buttress(right,14,29,6)
            hline(left+1,right-1,29,13 if index in (0,2) else 6)
            hline(left,right,30,5)
        # Independent black stepped firebreaks divide, rather than visually
        # merging, the four private housing facades.
        for x in (19,33,46):
            vline(x,14,29,8)
            vline(x+1,15,28,5)

    for x,y in locked:
        if art.pix[y][x] != original[y][x]:
            raise ValueError(f"{role}: protected architectural identity at {x,y} moved")
    if (art.w,art.h)!=(64,32) or any(not 0<=v<16 for row in art.pix for v in row):
        raise ValueError("Heavy architecture exceeded GBA 4bpp/fixed mural budget")
    changed = sum(a!=b for row_a,row_b in zip(original,art.pix)
                  for a,b in zip(row_a,row_b))
    if changed < (420 if role == "homes" else 330):
        raise ValueError(f"{role}: architectural redraw is too superficial: {changed}")
    print(f"Cuordilava heavy architectural redesign {role}: {changed} pixels, "
          "new roof masses/columns/windows; original portals and town safe")
    return changed
