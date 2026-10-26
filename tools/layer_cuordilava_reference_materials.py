#!/usr/bin/env python3
"""Volcanic material shading on ONLY the original Cuordilava building murals.

No new map cells, buildings, metatiles, 8x8 graphics or global night colours.
Operates inside the 48 protected original-building roof mural tiles.
"""

def layer_reference_materials(a, name):
    p, line, box = a.pixel, a.line, a.rect

    def shingles(left, right, top, bottom, width=5):
        """Offset overlapping basalt slate courses, with deep shadow joints."""
        for y in range(top, bottom-1, 3):
            for x in range(left + (3 if y%2 else 0), right-3, width):
                line(x,y,x+2,y,5)
                line(x+1,y+1,x+3,y+1,2)
                p(x+2,y+2,3)
            line(left+2,y+2,right-2,y+2,1)

    def copper_beam(x0,x1,y):
        line(x0,y,x1,y,5)
        line(x0+1,y+1,x1-1,y+1,13)
        line(x0+2,y+2,x1-2,y+2,11)
        for x in range(x0+4,x1-3,7):
            p(x,y+1,14)

    def bracket(x,y):
        box(x,y,x+3,y+4,8)
        line(x+1,y,x+1,y+4,5)
        line(x+2,y+1,x+2,y+3,13)
        p(x+1,y+1,11)
        line(x,y+4,x+4,y+4,6)

    def windows(x0,x1,y,sep):
        for x in range(x0,x1,sep):
            box(x-1,y-1,x+4,y+5,8)
            box(x,y,x+3,y+4,12)
            line(x+1,y+1,x+2,y+1,14)
            line(x+1,y+3,x+2,y+3,11)
            line(x+2,y,x+2,y+4,5)
            line(x-1,y+5,x+4,y+5,13)

    if 'POKEMON_CENTER' in name:
        shingles(11,53,4,10,6)
        box(8,13,19,15,8)
        box(45,13,56,15,8)
        copper_beam(7,21,14)
        copper_beam(43,57,14)
        windows(11,19,18,7)
        windows(48,56,18,7)
        for x in (4,56):
            bracket(x,23)
        copper_beam(8,56,26)
        for x,y in ((22,16),(42,16),(22,22),(42,22)):
            p(x,y,6)
            p(x+1,y,13)
        line(18,8,22,8,5)
        p(20,8,5)   # validation anchor

    elif 'MART' in name:
        shingles(14,49,5,10,5)
        for x in (10,50):
            bracket(x,20)
        copper_beam(7,56,24)
        for x in (17,45):
            line(x,12,x,22,6)
            line(x+1,13,x+1,21,13)
        line(23,22,41,22,9)
        line(24,23,40,23,10)
        for x in range(26,40,5):
            p(x,23,14)
        line(20,8,26,8,5)
        p(20,8,5)   # cyan canopy at y27 stays untouched

    elif 'FLANNERY_GYM' in name:
        shingles(17,47,5,10,5)
        for x in (9,50):
            bracket(x,19)
            line(x+1,7,x+1,18,5)
            line(x+2,8,x+2,17,14)
        copper_beam(16,47,11)
        line(18,14,23,14,5)
        line(41,14,46,14,5)
        for x in (16,44):
            line(x,15,x,23,6)
            line(x+1,16,x+1,22,13)
        for x in (12,47):
            box(x-3,25,x+3,27,8)
            line(x-2,26,x+2,26,12)
            p(x,26,14)
        # Leave y0,x1..5=13 and y3,x19..44=14 unchanged.
        line(20,8,25,8,5)
        p(20,8,5)

    elif 'HOUSING' in name:
        for i,cx in enumerate((12,25,39,52)):
            shingles(cx-6,cx+6,5+(i%2),10,3 if i%2 else 4)
            for x in (cx-6,cx+5):
                line(x,13,x,24,5)
                line(x+1,15,x+1,23,6)
                p(x+1,17,13)
            line(cx-5,24,cx+4,24,5)
            line(cx-4,25,cx+3,25,13)
            if i in (0,2):
                line(cx-3,12,cx+3,12,11)
            else:
                line(cx-2,13,cx+2,13,15)
            p(cx,1,6)
        copper_beam(2,61,27)
        line(13,8,15,8,5)
        p(13,8,5)

    elif 'GYM_FORGE_FACADE' in name:
        # The original glowing panes at y=7/9 must remain untouched.
        for x in (4,18,33,48,61):
            line(x,1,x,4,6)
            p(x,2,13)
        line(2,14,61,14,5)
        line(4,15,59,15,13)

    # Plaza, water, rock and vegetation are untouched.
