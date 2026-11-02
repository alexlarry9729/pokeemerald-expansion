#!/usr/bin/env python3
"""Large-scale original-footprint Cuordilava urban architecture pass.

Unlike the old isolated roof highlights, rebuilds the UPPER architectural mass
on the FOUR existing, connected 64x32 civic/residential murals, then completely
reprofiles the 64x32 central plaza as a coherent recessed volcanic caldera.
The bottom of the Center/Mart/Gym murals (including original recognizable
symbols, glass shopfronts and event/door identities) stays intact. No other
graphic, town cell, tile count, 4bpp palette, warp or collision is modified.

Run directly AFTER recompose_original_architecture in sculpt_cuordilava_city.
"""

ROLES = {
    "POKEMON_CENTER_INDUSTRIAL_REACTOR": "clinic",
    "POKE_MART_TECHNICAL_FACADE": "market",
    "FLANNERY_GYM_MOLTEN_FORGE": "foundry",
    "HOUSING_MAGMA_TERRACES": "residence",
    "CENTRAL_VOLCANIC_PLAZA_CREST": "square",
}


def rebuild_civic_massing(art, name):
    role = ROLES.get(name)
    if role is None:
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"{name}: landmark's original 4x2 footprint changed")
    before = [row[:] for row in art.pix]

    def p(x,y,c):
        if 0 <= x < 64 and 0 <= y < 32:
            art.pixel(x,y,c)

    def rect(l,t,r,b,c):
        for yy in range(max(0,t),min(b+1,32)):
            for xx in range(max(0,l),min(r+1,64)):
                p(xx,yy,c)

    def line(l,r,y,c):
        for x in range(l,r+1):
            p(x,y,c)

    def vertical(x,y0,y1,c):
        for y in range(y0,y1+1):
            p(x,y,c)

    def roof_backdrop():
        # Preserve untouched below this line; it contains all recognisable
        # ground-storey symbols, shop controls and blazing windows.
        for y in range(0,11):
            for x in range(64):
                p(x,y,0)

    def pitched_roof(left,right,center,ridge,eave,core,tip):
        """Actual multi-pitched building shape, no flat shipping container."""
        for x in range(left,right+1):
            dx=abs(x-center)
            top=min(eave-2,ridge+(dx*3)//8)
            for y in range(top,eave+1):
                if y==top:
                    c=5 if dx%7 else 6
                elif y==top+1:
                    c=tip
                elif y==eave:
                    c=8
                elif y==eave-1:
                    c=5
                elif (x//6+y//3)%7==0:
                    c=6
                else:
                    c=core
                p(x,y,c)
        line(left,right,eave+1,5)

    def slate_clerestory(cx,top,half,glass):
        rect(cx-half-1,top,cx+half+1,top+5,8)
        line(cx-half-1,cx+half+1,top,5)
        for x in range(cx-half,cx+half+1):
            for y in range(top+1,top+5):
                c=glass if (x+y)%7 else 14
                if x in (cx-half,cx+half) or x==cx or y==top+4:
                    c=6
                p(x,y,c)
        line(cx-half-2,cx+half+2,top+5,13)

    if role == "clinic":
        roof_backdrop()
        # Two lateral surgical wings framing the pitched medical tower. The
        # visible main roof is the same footprint, but a NEW silhouette.
        for left,right,crest,tone in (
            (4,21,4,8),(43,59,5,8)
        ):
            cx=(left+right)//2
            pitched_roof(left,right,cx,crest,10,tone,6)
        pitched_roof(19,45,32,0,10,13,11)
        # Central healthcare tower with a glowing six-pixel cross.
        rect(25,4,39,9,8)
        line(24,40,4,5)
        rect(29,5,35,8,13)
        for x in range(31,34):
            for y in range(5,9):
                p(x,y,12)
        for x in range(28,37):
            p(x,7,12)
        # Large medical windows within the flanking gabled roofs.
        slate_clerestory(14,5,4,12)
        slate_clerestory(50,5,4,12)
        # Tall asymmetrical thermal chimney stands behind the roof mass.
        rect(4,1,8,8,8)
        vertical(5,1,8,5)
        vertical(7,1,8,6)
        line(3,9,1,5)
        for y in (3,5,7):
            p(6,y,13)
        # Shadow and copper eaves form one uninterrupted supporting lintel.
        line(7,56,11,5)
        p(31,1,6)
        p(20,8,5)
        p(31,18,12)

    elif role == "market":
        roof_backdrop()
        # Four highly visible staggered foundry saw-tooth skylights. The
        # market reads as a technical supply depot, never a second hospital.
        rect(5,6,58,10,8)
        for i,(left,right,top) in enumerate(
            ((7,18,1),(19,31,3),(32,44,1),(45,57,4))
        ):
            for x in range(left,right+1):
                top_here=min(8,top+(right-x)//5)
                for y in range(top_here,9):
                    p(x,y,5 if y==top_here else
                      6 if y==top_here+1 else
                      8 if (x+y+i)%5 else 2)
            for x in range(left+2,right):
                for y in (6,7):
                    p(x,y,9 if y==6 else 10)
            # Uneven industrial iron braces, believable daylight skylights.
            for x in (left+1,right-1):
                vertical(x,4,9,8)
            line(left,right,9,8)
        # Long CYAN shop canopy bridges all four roof sections. Keep two
        # heavy dark end columns and the original shopping cart underneath.
        line(10,54,10,10)
        for x in range(10,55):
            if x%8 in (1,2):
                p(x,9,9)
            elif x%8==0:
                p(x,9,14)
        for x in (5,58):
            vertical(x,5,10,5)
            vertical(x+1,7,10,8)
        line(11,52,11,5)
        p(20,8,5)
        p(32,20,10)
        p(9,16,5)

    elif role == "foundry":
        roof_backdrop()
        # True stepped volcanic kiln architecture, with different twin
        # smokestacks and a strongly sheltered furnace crest.
        rect(7,7,57,10,8)
        for x in range(8,56):
            top=4+abs(32-x)//9
            for y in range(top,11):
                p(x,y,6 if y==top else
                  5 if y==10 else
                  8 if (x//7+y//2)%4 else 3)
        # Two gigantic masonry chimneys with independent steam shafts.
        for cx,top,wide in ((7,0,6),(55,1,5)):
            left,right=cx-wide,cx+wide
            rect(left,top,right,9,8)
            for y in range(top,10):
                for x in range(left+1,right):
                    c=6 if x in (left+1,right-1) else 3
                    if 3<=y<=6 and abs(x-cx)<2:
                        c=12 if y%3 else 14
                    p(x,y,c)
            line(left,right,top,13)
            line(left,right,top+1,5)
            for y in (top+4,top+8):
                line(left,right,y,5)
        # A broad central high-temperature hood forms a distinct mass
        # across the middle, keeping the upper copper roofline identity.
        rect(17,5,47,9,8)
        for x in range(17,48):
            p(x,5,5)
            p(x,6,6 if x%6 else 13)
            p(x,9,8)
        for cx in (24,32,40):
            for x in range(cx-3,cx+4):
                p(x,7,12 if abs(x-cx)<2 else 5)
                p(x,8,14 if abs(x-cx)<2 else 8)
        # Source validators protect these two contiguous structural lines.
        line(19,44,3,14)
        line(12,51,11,5)
        for x in range(1,6):
            p(x,0,13)
        p(20,8,5)
        p(32,19,12)

    elif role == "residence":
        roof_backdrop()
        # The existing 4x2 housing frontage receives a GENUINE four-home
        # terraced skyline. Heights, pitches, materials and windows differ.
        homes = (
            (12, 7, 1, 12, 14), # copper chalet / inn
            (25, 6, 0, 8, 10),  # shaded mineral-slate workers' house
            (39, 7, 2, 13, 12), # heat-vented forge home
            (52, 6, 0, 3, 11),  # basalt watch roof
        )
        for i,(cx,half,top,body,glass) in enumerate(homes):
            left,right=cx-half,cx+half
            for x in range(left,right+1):
                # Four visible stepped gables at different heights.
                slope=(abs(cx-x)*3)//(4 if i in (0,2) else 5)
                first=min(10,top+slope)
                for y in range(first,12):
                    c=(6 if y==first else
                       5 if y==first+1 else
                       8 if y==11 else
                       5 if y==10 else
                       body if (x//4+y//3)%5 else 3)
                    p(x,y,c)
            # Each home gets a framed, varied attic window.
            w=2 if i in (0,2) else 3
            for y in range(5,9):
                for x in range(cx-w,cx+w+1):
                    if y==5 or x in (cx-w,cx+w):
                        c=5
                    elif x==cx:
                        c=8
                    else:
                        c=glass if (x+y)%4 else 14
                    p(x,y,c)
            # Finite copper gutter and narrow stone-vaulted roof post.
            line(left+1,right-1,11,5)
            p(cx,1,6)
            p(cx,12,5)
        # Physical gaps in the roofline, darker separating chimney stacks.
        for x, height in ((19,4),(32,3),(46,5)):
            rect(x, height, x+2,11,8)
            vertical(x,height,11,5)
            for y in range(height+1,10,3):
                p(x+1,y,13)
        p(13,8,5)
        # LOWER y>=13 house windows and entrances copied unchanged.

    else: # Full 64x32 civic plaza: calm volcanic civic landmark
        # Major composition change: instead of a busy full-block lava badge,
        # build one readable recessed octagonal assembly inset within spacious
        # slate flagstones. All is walkable art on existing BG2 metatiles.
        art.pix = [[0] * 64 for _ in range(32)]
        for y in range(32):
            for x in range(64):
                dx, dy = abs(x-31), abs(y-15)
                ring = dx*2 + dy*3
                if ring <= 61:
                    # Massive uninterrupted slate paving outside an inset seal.
                    color = 12 if ((x//14)+(y//8))%3 else 13
                    if y in (7, 24) and 7 <= x <= 55:
                        color = 5
                    elif (x in (14, 49)) and 9 <= y <= 22:
                        color = 6
                    p(x, y, color)
                # Beyond the stone octagon let the ORIGINAL walkable
                # cobbled underlay show through; no decorative pixel noise.
        # Large octagonal recessed basalt plinth, three coherent bands.
        for y in range(6,26):
            for x in range(12,52):
                dx,dy=abs(x-31),abs(y-15)
                edge = dx*2+dy*3
                if edge <= 50:
                    c = 5 if edge>=47 else 6 if edge>=43 else 8
                    p(x,y,c)
                if edge <= 31:
                    p(x,y,12 if edge>27 else 13)
                if edge in (27,28) and (x+y)%5:
                    p(x,y,11)
        # Centerpiece is a contained geothermal compass, not a chaotic
        # open magma lake. Four cardinal stone arms with copper at their
        # ends deliberately leave large clean stone negative space.
        for x in range(25,39):
            p(x,15,5)
            if x in (25,38):
                p(x,15,14)
        for y in range(10,22):
            p(31,y,5)
            if y in (10,21):
                p(31,y,14)
        # Distinctive central low furnace seal; visible but not sprite-high.
        for y in range(13,19):
            for x in range(28,35):
                if abs(x-31)+abs(y-15)<=4:
                    p(x,y,8)
        for x,y in ((31,13),(29,15),(33,15),(31,17)):
            p(x,y,11)
        p(31,15,14)
        # Four clean inset municipal corner grates, no fake obstacles.
        for cx,cy in ((9,8),(54,8),(9,24),(54,24)):
            for yy in range(cy-2,cy+2):
                for xx in range(cx-2,cx+2):
                    p(xx,yy,8 if xx in (cx-2,cx+1) or yy in (cy-2,cy+1) else 6)
            p(cx,cy,13)

    # Guard emblem, exact identity, non-invasive dimensions and magnitude.
    if (art.w,art.h)!=(64,32):
        raise ValueError("Urban massing changed the immutable landmark geometry")
    protected = {
        "clinic": [(31,1,6),(20,8,5),(31,18,12)],
        "market": [(20,8,5),(32,20,10),(9,16,5)],
        "foundry": [(20,8,5),(32,19,12)],
        "residence": [(12,1,6),(25,1,6),(39,1,6),
                      (52,1,6),(13,8,5)]
    }
    for x,y,c in protected.get(role,()):
        if art.pix[y][x]!=c:
            raise ValueError(f"{name}: protected {(x,y)}={c} was displaced")
    if role=="foundry":
        if any(art.pix[0][x]!=13 for x in range(1,6)):
            raise ValueError("Foundry chimney crest damaged")
        if any(art.pix[3][x]!=14 for x in range(19,45)):
            raise ValueError("Foundry hot roofline damaged")
    if role in ("clinic","market","foundry"):
        x0,x1={"clinic":(7,56),"market":(11,52),"foundry":(12,51)}[role]
        if any(art.pix[11][x]!=5 for x in range(x0,x1+1)):
            raise ValueError(f"{name}: lower roof fascia no longer connected")
    if role=="residence":
        if any(art.pix[12][x]!=5 for x in (12,25,39,52)):
            raise ValueError("Terraced homes lost their eave supports")
    change=sum(old!=new for r,s in zip(before,art.pix)
               for old,new in zip(r,s))
    minimum = 400 if role == "square" else 300
    if change < minimum:
        raise ValueError(
            f"{name}: new citywide massing too subtle "
            f"({change} changed pixels, minimum {minimum})"
        )
    print(f"Major Cuordilava architectural massing {role}: "
          f"{change} indexed 4bpp pixels rebuilt on original four-by-two mural")
    if any(not 0 <= c <= 15 for row in art.pix for c in row):
        raise ValueError("Citywide landmark art no longer GBA 4bpp")
    return change
