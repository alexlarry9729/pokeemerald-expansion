#!/usr/bin/env python3
"""Replace flat roof textures with coherent inhabited volumes in Cuordilava.

This is intentionally a single composition pass over the EXISTING four
architectural murals. It changes no tile allocation, layout, map position,
warp, sign, event, palette, shared asset or day/night light setting. Its
safe-coordinate guards preserve exact landmarks expected by gameplay and
visual regression checks; existing 64x32 murals remain 64x32.
"""


def compose_existing_volumes(a, name):
    if not any(n in name for n in
               ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")):
        return

    before = [row[:] for row in a.pix]
    protected = set()
    if "POKEMON_CENTER" in name:
        protected.update((x, 11) for x in range(7, 57))
        protected.update(((31,1), (20,8), (31,18), (31,16), (10,16)))
        protected.update((x,y) for x in range(24,41) for y in range(14,25))
    elif "POKE_MART" in name:
        protected.update((x,11) for x in range(11,53))
        protected.update((x,27) for x in range(16,48))
        protected.update(((20,8), (32,20), (9,16)))
        protected.update((x,y) for x in range(20,45) for y in range(15,25))
    elif "FLANNERY_GYM" in name:
        protected.update((x,11) for x in range(12,52))
        protected.update((x,0) for x in range(1,6))
        protected.update((x,3) for x in range(19,45))
        protected.update(((20,8), (32,19)))
        protected.update((x,y) for x in range(19,46) for y in range(14,26))
    else:
        protected.update((x,1) for x in (12,25,39,52))
        protected.update(((13,8),))
        protected.update((x,12) for x in (12,25,39,52))

    def p(x,y,c):
        if 0<=x<a.w and 0<=y<a.h and (x,y) not in protected:
            a.pixel(x,y,c)

    def hline(x0,x1,y,c):
        for x in range(x0,x1+1): p(x,y,c)

    def vline(x,y0,y1,c):
        for y in range(y0,y1+1): p(x,y,c)

    def box(x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            hline(x0,x1,y,c)

    def roof_panel(left,right,top,bottom,course,accent):
        """Full-length hipped basalt plane with offset slate roofing.

        Contrast comes from contiguous plate masses and deep joints, not
        random emissive specks. Slope is within the existing 64px mural.
        """
        center=(left+right)//2
        for x in range(left,right+1):
            top_y=min(bottom-2,top+abs(center-x)//10)
            for y in range(top_y,bottom+1):
                col=8 if y%4!=0 else 2
                p(x,y,col)
            p(x,top_y,5 if x<center else 6)
            if top_y+1<=bottom:p(x,top_y+1,3)
        for y in range(top+3,bottom,3):
            offset=(y//3)%2*(course//2)
            for x in range(left+3+offset,right-3,course):
                hline(x,x+course-2,y,5)
                hline(x+1,x+course-3,y+1,2)
                p(x+2,y+2,3)
        hline(left+1,right-1,bottom,5)
        hline(left+2,right-2,bottom+1,accent)
        for x in range(left+5,right-3,9):
            p(x,bottom+1,11)

    def deep_window(cx, y, width, height, glass=12):
        """Wide cast-iron window with actual inset heat-glass area."""
        l,r=cx-width//2,cx+width//2
        box(l-2,y-2,r+2,y+height+1,8)
        hline(l-1,r+1,y-1,5)
        hline(l,r,y,13)
        box(l,y+1,r,y+height-1,glass)
        for yy in range(y+2,y+height-1):
            hline(l+1,r-1,yy,14 if yy%3 else 11)
        vline(cx,y+1,y+height-1,5)
        hline(l-1,r+1,y+height,5)
        hline(l,r,y+height+1,13)
        p(l+1,y+2,11)

    def column(x,y0,y1,style):
        box(x,y0,x+4,y1,8)
        vline(x,y0,y1,5)
        vline(x+1,y0+1,y1-1,6)
        vline(x+3,y0+1,y1-1,13 if style%2 else 11)
        for yy in range(y0+3,y1,5):
            hline(x,x+4,yy,5)
            p(x+2,yy,14)

    def truss(x0,y0,dx,dy):
        """Roof struts line up to real supporting columns beneath eaves."""
        for k in range(max(abs(dx),abs(dy))+1):
            x=x0+round(dx*k/max(1,max(abs(dx),abs(dy))))
            y=y0+round(dy*k/max(1,max(abs(dx),abs(dy))))
            p(x,y,5)
            p(x+1,y,13)

    if "POKEMON_CENTER" in name:
        # A single broad clinic roof, with independently mounted thermal
        # radiators left and right of the distinctive central cross.
        roof_panel(8,55,3,9,7,13)
        for cx in (15,49):
            box(cx-5,12,cx+5,14,8)
            hline(cx-4,cx+4,12,6)
            hline(cx-4,cx+4,13,13)
            deep_window(cx,17,7,5)
        for x in (5,56):
            column(x,13,25,1)
            truss(x+3,13,5,3)
        # Black volcanic plinth and glowing radiator vents across both wings.
        for x0,x1 in ((8,22),(42,56)):
            hline(x0,x1,25,5)
            hline(x0+1,x1-1,26,13)
            for x in range(x0+3,x1-2,5):
                hline(x,x+2,28,12)
                hline(x+1,x+2,29,14)
        # Keep center red cross, roof identity and the original six warps.

    elif "POKE_MART" in name:
        # Lower industrial roof and conspicuous cyan commercial frontage.
        roof_panel(12,51,4,9,6,9)
        for cx in (13,50):
            column(cx-5,13,24,0)
            deep_window(cx,16,7,6)
        for x in (11,53):
            truss(x,12,5 if x<32 else -5,5)
        # Refrigerant manifold above the original blue shop canopy.
        for x0,x1 in ((7,18),(46,58)):
            hline(x0,x1,24,5)
            hline(x0+1,x1-1,25,10)
        for x in (7,56):
            vline(x,9,22,9)
            p(x,11,10); p(x,18,15)
        # Cyan store sign, original cart panel, and canopy are protected.

    elif "FLANNERY_GYM" in name:
        # A full furnace roof with flank chimneys instead of clinic-style
        # storefront detailing. One sacred central flame is left uncovered.
        roof_panel(12,51,4,9,5,13)
        for x in (3,56):
            column(x,7,25,1)
            box(x+1,10,x+3,22,12)
            for yy in (11,15,19,22):
                hline(x+1,x+3,yy,5)
                p(x+2,yy+1,14)
            truss(x+2,12,5 if x<32 else -5,5)
        for cx in (12,52):
            deep_window(cx,18,5,5)
        hline(7,18,27,5); hline(46,57,27,5)
        hline(8,17,28,13);hline(47,56,28,13)
        # Landmark flame shield and original copper galleried roof intact.

    elif "HOUSING" in name:
        # Each of the four current roofs now has its own slate pitch,
        # dormer shape and inhabited facade. No added house or doorway.
        for i,cx in enumerate((12,25,39,52)):
            width=(6,5,6,5)[i]
            roof_panel(cx-width,cx+width,3+(i%2),9,
                       (3,4,5,3)[i],13 if i%2 else 6)
            column(cx-width,14,23,i)
            if i in (0,3):
                deep_window(cx,16,5,6)
            elif i==1:
                deep_window(cx-2,16,5,6)
                vline(cx+4,16,22,10)
                p(cx+4,18,15)
            else:
                deep_window(cx+1,16,5,6)
                hline(cx-3,cx+4,23,5)
            # Mixed wood and stone balcony shadows, unique to each dwelling.
            hline(cx-5,cx+5,24,5)
            hline(cx-4,cx+4,25,13 if i in (0,2) else 11)
            p(cx-3,26,14)
            p(cx+3,26,11)
        # The four raised gable-tip identity pixels remain protected.

    changed=sum(pix!=old for row,orig in zip(a.pix,before)
                for pix,old in zip(row,orig))
    if changed<90:
        raise ValueError(f"New inhabited architectural volumes are too sparse "
                         f"for {name}: {changed} changed mural pixels")
    if any(a.pix[y][x]!=before[y][x] for x,y in protected):
        raise ValueError("An original roof emblem, store sign, or structural "
                         "identity anchor was accidentally modified")
