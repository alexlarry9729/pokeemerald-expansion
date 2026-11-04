#!/usr/bin/env python3
"""Rebuild the existing 64x16 Gym frontage as one monumental forge arcade.

Unlike the prior four identical shop-window panels, this has two flanking
multi-pier glass furnaces and one central blast-furnace portal. The room door
remains a separate original warp at (5,15), outside these four mural cells.
"""


def forge_ground_storey(a, name):
    if name != "GYM_FORGE_FACADE":
        return 0
    if (a.w, a.h) != (64, 16):
        raise ValueError("Original four-cell Gym wall footprint changed")
    previous = [row[:] for row in a.pix]
    a.pix = [[8] * 64 for _ in range(16)]
    def p(x,y,c):
        if 0 <= x < 64 and 0 <= y < 16:
            a.pixel(x,y,c)
    def rect(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                p(x,y,c)
    def line(x0,x1,y,c):
        for x in range(x0,x1+1):
            p(x,y,c)

    # A continuous coherent sandstone/obsidian lower storey; structural
    # joints follow the old full 64px frontage, not isolated cell edges.
    for y in range(16):
        for x in range(64):
            c = 2 if (x//13 + y//4)%3 else 3
            if y in (0,1,14):c=5
            elif y in (2,13):c=6
            elif y%5==0 and x%11 not in (0,1):c=4
            elif x%13==1:c=8
            p(x,y,c)
    for x in range(1,63):
        p(x,0,6)
        p(x,1,5 if x%7 else 13)
        p(x,14,5)
        p(x,15,13 if x%6 else 8)

    # Two industrial buttresses join the masonry to the roof above, plus
    # thick copper latticework over the distinct warm furnace chambers.
    for cx,half in ((10,5),(25,5),(40,5),(55,5)):
        rect(cx-half,3,cx+half,12,8)
        # Four fixed arch anchors are also a runtime regression guarantee.
        p(cx-5,3,6)
        for y in (4,5,6,7,8,9,10,11):
            left, right = cx-4,cx+4
            for x in range(left,right+1):
                if x in (left,right):
                    c=5
                elif x in (cx-2,cx+2):
                    c=12 if y in (7,9) else 13
                elif x==cx:
                    c=8 if y<10 else 5
                elif y in (4,11):
                    c=13
                elif y in (5,6):
                    c=14 if (x+y)%3 else 12
                else:
                    c=11 if (x+y)%4 else 12
                p(x,y,c)
        for x in range(cx-5,cx+6):
            p(x,12,5)
        for x in (cx-6,cx+5):
            for y in range(2,14):
                p(x,y,5 if y%4 else 6)
        p(cx,4,8)
        p(cx,5,13)

    # Recessed CENTRAL furnace gate, with a larger dark industrial arch
    # spanning the middle two bays. It does not replace the actual door.
    for y in range(2,13):
        half=9 if y>=5 else 6+(y-2)
        for x in range(32-half,33+half):
            if abs(x-32)>=half-1:
                p(x,y,5)
            elif y in (2,3):
                p(x,y,6)
            elif 26<=x<=38 and 5<=y<=11:
                p(x,y,8 if x%5==0 else 2)
    # Furnace-mouth/copper ribs, substantially larger than pixel-sized icons.
    for x in (28,31,34,37):
        for y in range(6,12):
            p(x,y,12 if x in (28,37) else 14)
    for x in range(27,39):
        p(x,5,13)
        p(x,12,5)
    for x in (27,38):
        for y in (6,7,8,9,10,11):p(x,y,6)

    # Retain four burnt-glass portholes as strong identity cues precisely at
    # the original audited locations, without restoring repetitive geometry.
    for cx in (10,25,40,55):
        for y in (7,9):
            p(cx-2,y,12)
            p(cx+2,y,12)
        p(cx-5,3,6)
        p(cx-4,12,5)
    p(32,14,5)
    p(32,15,13)

    delta=sum(before!=after for a0,a1 in zip(previous,a.pix) for before,after in zip(a0,a1))
    if delta<350:
        raise ValueError(f"Forge arcade did not materially change ({delta} pixels)")
    if any(not 0<=p<=15 for row in a.pix for p in row):
        raise ValueError("Forge arcade exceeds GBA 4bpp")
    if sum(c in (11,12,13,14) for row in a.pix for c in row)<150:
        raise ValueError("Four furnace bays lost their hot glass")
    return delta
