#!/usr/bin/env python3
"""Dense, layered 4bpp architecture for Cuordilava's existing 20x20 footprint.

Paints onto the *48 already allocated* town-private civic landmark murals.
No new metatiles, events, collision attributes, global palettes or map cells.
Each colour index refers to the Cuordilava secondary palette 06 (night 15).
"""

def polish_monument(a, name):
    """Layer iron roof ridges, furnace architecture and recessed neon signage."""
    W,H=a.w,a.h
    def p(x,y,c): a.pixel(x,y,c)
    def ln(x,y,x1,y1,c): a.line(x,y,x1,y1,c)
    def box(x,y,x1,y1,c,fill=True): a.rect(x,y,x1,y1,c,fill)

    if any(k in name for k in ('POKEMON_CENTER','POKE_MART','FLANNERY_GYM','HOUSING')):
        # Stepped roofline and deep overhang; palette-0 stays transparent.
        for x in range(3,W-3):
            bevel=max(0,10-min(x,W-1-x))//2
            for y in range(min(bevel,H-2)):
                p(x,y,0)
            y=4+bevel
            p(x,y,3)
            if x%11:p(x,y+1,5)
            if x%7 in (2,3):p(x,8,2)
        # Copper gutters and projecting bolted beams.
        for x in range(4,W-4):
            if x%8 not in (1,2):p(x,H-5,11)
            p(x,H-4,13)
            if x%5==0:p(x,H-3,14)
        ln(4,H-2,W-5,H-2,5)
        for bx in range(6,W-5,9):
            p(bx,H-6,3);p(bx+1,H-6,8);p(bx,H-3,12)
            if bx//9%2==0:p(bx+3,11,11)
        for bx in (7,W-10):
            box(bx-2,H-11,bx+2,H-7,5)
            box(bx-1,H-11,bx+1,H-9,7)
            p(bx,H-10,15)
        for bx in range(10,W-10,15):
            ln(bx,2,bx+5,7,6)
            ln(bx+1,2,bx+6,7,2)

    if 'POKEMON_CENTER' in name:
        # Glowing thermal coils flanking the central red-cross reactor.
        for x in (15,47):
            box(x-4,12,x+3,22,8)
            box(x-3,13,x+2,20,6,False)
            for yy in (14,17,20):
                ln(x-2,yy,x+1,yy,11);p(x-1,yy,14)
            box(x-3,23,x+2,25,5)
        for x in (5,55):
            box(x-1,3,x+1,12,8)
            ln(x,4,x,12,13)
            p(x,5,14);p(x,7,15)
        ln(24,5,40,5,11)
        for x in (28,36):p(x,4,14)
        for x,y in ((32,2),(20,16),(44,16),(32,29)):
            p(x,y,5);p(x+1,y,14)

    elif 'MART' in name:
        # Cyan shopping fascia; orange service risers; magenta side banners.
        for x in range(16,49):
            p(x,7,10 if x%5 else 9)
            if x%4 in (0,1):p(x,8,9)
        for x in (12,49):
            box(x-3,11,x+1,23,5)
            box(x-2,11,x,23,8)
            ln(x-1,12,x-1,22,12)
            for y in (12,17,22):p(x,y,14)
        for x in (24,39):p(x,23,13);p(x+1,23,11)
        for x in (4,53):
            box(x,9,x+5,26,8)
            box(x+1,10,x+4,25,15,False)
            for y in (12,16,20,24):
                p(x+2,y,10);p(x+3,y+1,15)

    elif 'FLANNERY_GYM' in name:
        # Three-dimensional blast furnace with asymmetric copper buttresses.
        for x in (14,42):
            box(x,1,x+8,7,8)
            ln(x,1,x+8,1,6)
            ln(x+1,2,x+1,6,5)
            ln(x+7,2,x+7,6,5)
            for ix in (x+3,x+5):ln(ix,2,ix,6,11)
        for x in (2,54):
            box(x,9,x+7,24,8)
            ln(x+1,10,x+1,23,5)
            ln(x+4,10,x+4,23,13)
            ln(x+5,10,x+5,23,14)
            for y in (13,18,23):ln(x,y,x+7,y,6)
        for x in range(17,47):
            if x in (17,18,45,46):ln(x,8,x,24,5)
            if x%5==0:p(x,27,12)
        ln(19,5,45,5,13)
        ln(19,6,45,6,11)
        for x in (19,44):p(x,4,15)

    elif 'HOUSING' in name:
        # A whole row of coherent tileable warm-window industrial houses.
        for center in (12,25,39,52):
            for dx in (-6,-5,-4,-3,3,4,5,6):
                x=center+dx
                if 0<=x<W:
                    p(x,6,2);p(x,7,5)
            ln(center-7,9,center+7,9,6)
            ln(center-6,10,center+6,10,13)
            box(center-4,13,center+4,21,8)
            box(center-3,14,center+3,20,6,False)
            box(center-2,15,center+2,19,12)
            ln(center,15,center,19,5)
            p(center-1,17,14);p(center+1,18,11)
            for x in (center-6,center+6):
                ln(x,12,x,24,8);p(x,16,15)
        for x in range(3,W-3):
            if x%8 in (2,3):p(x,28,11)

    elif 'GYM_FORGE_FACADE' in name:
        # The lower facade must be furnace WINDOWS, not a second gym roof.
        box(0,0,W-1,H-1,8)
        ln(1,0,W-2,0,6)
        for x in range(2,W-2):
            p(x,2,5);p(x,14,6)
            if x%7<2:p(x,1,3)
        for cx in (10,25,40,55):
            box(cx-5,3,cx+5,13,5)
            box(cx-4,4,cx+4,12,8)
            box(cx-3,5,cx+3,11,12)
            ln(cx-2,5,cx+2,5,11)
            for dx in (-2,0,2):
                for y in (6,8,10):p(cx+dx,y,14 if (dx+y)%3==0 else 11)
            ln(cx,4,cx,12,5)
            for x in (cx-5,cx+5):ln(x,2,x,14,6)
        for x in (1,62):
            ln(x,0,x,14,13);p(x,3,15)
        ln(3,15,60,15,14)

    elif 'PLAZA' in name:
        # Lava crest inset into irregular cobblestones, not a flat road sticker.
        for y in range(1,H-1):
            for x in range(1,W-1):
                if (x*17+y*7)%23==0:p(x,y,3)
                elif (x*11+y*5)%31==0:p(x,y,5)
                elif y%5==0 and x%8 in (1,2,3,4):p(x,y,1)
        for r,c in ((15,6),(13,11),(10,13)):a.ring(31,16,r,c,1)
        for dx,dy in ((-14,0),(14,0),(0,-14),(0,14)):
            x,y=31+dx,16+dy
            p(x,y,14)
            if x+1<W and y+1<H:p(x+1,y+1,11)
        ln(31,7,31,25,12)

    elif 'THERMAL_BASIN' in name:
        # Open iron guardrails: the water texture remains transparent below.
        for x in range(4,W-4,8):
            for y in (9,13):p(x,y,13)
            p(x+1,10,11)
        for x in (1,61):
            p(x,4,14);p(x+1,5,15)
