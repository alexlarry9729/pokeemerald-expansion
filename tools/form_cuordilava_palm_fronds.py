#!/usr/bin/env python3
"""Replace the existing ROUND Cuordilava shrubs with distinct palm silhouettes.

Each palm stays in its existing 16x16 scenery cell, uses the original palette
9 and original tile budget. The image is transparent around the thin leaves,
so the original rocks, bank and paving show through. No map placements,
graphics sheets, terrain attributes, NPCs or doorways change.
"""


def form_original_palm_fronds(pix, kind):
    if kind != "palm":
        return pix
    if len(pix) != 16 or any(len(row) != 16 for row in pix):
        raise ValueError("Cuordilava palms must remain exactly 16x16 pixels")
    art = [[0]*16 for _ in range(16)]
    def p(x,y,c):
        if 0 <= x < 16 and 0 <= y < 16:
            art[y][x] = c
    def stroke(x0,y0,x1,y1,c):
        dx,dy=abs(x1-x0),-abs(y1-y0)
        sx=1 if x0<x1 else -1
        sy=1 if y0<y1 else -1
        err=dx+dy
        while True:
            p(x0,y0,c)
            if (x0,y0)==(x1,y1):break
            twice=err*2
            if twice>=dy:err+=dy;x0+=sx
            if twice<=dx:err+=dx;y0+=sy
    # One natural offset tree crown, not a symmetric neon green circle.
    leaf_tips=((0,8),(1,5),(3,2),(5,0),(9,0),(12,2),
               (15,5),(15,8),(13,11),(2,11))
    for i,(ex,ey) in enumerate(leaf_tips):
        stroke(8,5,ex,ey,9)
        # Serrated leaf underside; the ends stay distinctly pointed.
        step=1 if ex>=8 else -1
        for ox,oy in ((ex-step,ey+1),(ex-2*step,ey+1),
                      (ex-3*step,ey+2)):
            p(ox,oy,10 if i%3 else 15)
    # Broad side fronds with light brown gaps, preserving outlines and
    # tropical fan geometry at the actual 3x preview magnification.
    for x,y in ((3,6),(4,5),(5,4),(6,3),(9,3),(10,4),
                (11,5),(12,6),(3,8),(4,9),(11,8),(12,9)):
        p(x,y,10)
        p(x+1,y,15)
    for x,y in ((4,4),(6,2),(8,2),(10,2),(12,4),
                (2,7),(5,7),(10,7),(13,7)):
        p(x,y,15)
    # A real narrow brown tree trunk, visible between front/back foliage.
    for y in range(7,15):
        p(7,y,12)
        p(8,y,13 if y%3 else 14)
    for x,y in ((6,13),(9,13),(5,14),(10,14),(6,15),(9,15)):
        p(x,y,9)
    # Orange autumn-flower beds planted along the existing tree root; they
    # remain decorative within the original impassable landscaping cell.
    for x,y in ((1,12),(3,13),(11,12),(13,13),(4,15),(10,15)):
        p(x,y,11)
        p(x+1,y,14)
        p(x,y-1,10)
    p(7,5,15)
    p(8,5,10)
    p(9,5,15)
    green=sum(c in (9,10,15) for row in art for c in row)
    flowers=sum(c in (11,14) for row in art for c in row)
    if green < 42 or flowers < 10:
        raise ValueError(f"Palm silhouette lost foliage/flowers {green}/{flowers}")
    if any(c<0 or c>15 for row in art for c in row):
        raise ValueError("Palm silhouette exceeds indexed palette")
    return art
