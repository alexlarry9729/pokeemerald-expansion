#!/usr/bin/env python3
"""Richer flowering palm fronds and detailed thermal-furnace street scenery.

Operate exclusively on the four existing 16x16 Cuordilava scenery motifs.
No new sprites, metatiles, atlas dimensions, town map cells, or palettes.
"""

def polish_scenery(pix, kind):
    def p(x,y,c):
        if 0<=x<16 and 0<=y<16: pix[y][x]=c
    def ln(x0,y0,x1,y1,c):
        dx=abs(x1-x0);dy=-abs(y1-y0)
        sx=1 if x0<x1 else -1
        sy=1 if y0<y1 else -1
        err=dx+dy
        while True:
            p(x0,y0,c)
            if x0==x1 and y0==y1:break
            e=2*err
            if e>=dy:err+=dy;x0+=sx
            if e<=dx:err+=dx;y0+=sy
    if kind=='palm':
        # Flowering tropical fronds: layered shadow, jade and bright green.
        for x,y in ((1,8),(2,4),(5,1),(10,1),(14,4),(14,9),(3,11),(12,11)):
            ln(8,6,x,y,9)
        for x,y in ((1,7),(3,4),(5,2),(10,2),(13,4),(14,8),(3,10),(12,10)):
            ln(8,5,x,y,15)
        for x,y in ((2,6),(4,3),(6,1),(11,2),(14,5),(13,9),(3,10),(12,10)):
            p(x,y,10)
        for x,y in ((1,10),(2,11),(13,12),(14,11),(4,12),(11,13)):
            p(x,y,11);p(x+1,y,14)
        for y in range(7,15):
            p(7,y,12)
            p(8,y,14 if y%3 else 13)
        for x in (5,6,9,10):p(x,15,12)
        for x,y in ((7,5),(8,5),(9,5),(7,6),(8,6),(9,6)):
            p(x,y,15)
        # Dense serrated fronds and scattered volcanic-orange blossoms.
        for x,y in ((2,5),(3,6),(4,2),(5,3),(10,3),(11,2),
                    (13,6),(12,7),(3,9),(4,10),(11,10),(12,9)):
            p(x,y,15)
            p(x+1,y,10)
        for x,y in ((2,11),(13,11),(4,13),(11,14),(1,9),(14,9)):
            p(x,y,11)
            p(x+1,y,14)
    elif kind=='chimney':
        # Reddish steam exhaust and copper-lit industrial risers.
        for x,y in ((6,1),(7,0),(8,2),(11,0),(12,1),(5,3),(13,3)):
            p(x,y,5)
        for x,y in ((6,0),(9,1),(10,0),(12,2)):p(x,y,3)
        for x in (5,10):
            ln(x,4,x,15,6)
            p(x,10,13)
        for x in (7,8,9):
            for y in (5,8,11,14):p(x,y,14 if y%2 else 12)
        for x in (4,12):
            p(x,3,11);p(x,4,13)
    elif kind=='lamp':
        # A caged hot-glass lamp with a tiny copper halo and bolted base.
        for x in range(5,11):p(x,3,5)
        p(7,1,14);p(8,1,11);p(7,2,12)
        for y in (4,5,6):
            p(5,y,6);p(10,y,6)
        for x in range(6,10):
            p(x,4,14)
            p(x,5,12 if x%2 else 11)
            p(x,6,14)
        for y in range(8,15):
            p(7,y,8);p(8,y,5)
        for x,y in ((3,3),(12,3),(2,6),(13,6),(4,1),(11,1)):
            p(x,y,13)
        for x in range(5,11):p(x,14,5)
        for x in (5,10):p(x,15,8)
    elif kind=='cascade':
        # Narrow turquoise waterfall: alternating white mineral foam, shadowed
        # central current and irregular rock splashes. Side pixels stay clear.
        for y in range(1,15):
            for x in range(4,12):
                phase=(x*7+y*11)%13
                if phase in (1,4):
                    p(x,y,1)
                elif phase in (0,3,6,9):
                    p(x,y,10)
                else:
                    p(x,y,9)
            if y in (3,8,13):
                for x in (5,7,10):
                    p(x,y,1)
        for y in (1,6,11,14):
            p(3,y,6)
            p(12,y,6)
    return pix
