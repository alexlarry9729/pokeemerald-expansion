#!/usr/bin/env python3
"""District-scale architectural pass using the SAME five 64x32 town murals.

Creates a coherent geothermal civic heart, a readable four-home basalt arcade,
and functional shop/clinic/forge frontages. Deliberately changes thousands of
4bpp source pixels, but only inside the 48 original private mural metatiles.
Does not touch the final map, primary underlay, collision, elevation, objects,
warp scripts, or GBA layer priorities. Run after rebuild_civic_massing().
"""

ROLES = {
    "POKEMON_CENTER_INDUSTRIAL_REACTOR": "clinic",
    "POKE_MART_TECHNICAL_FACADE": "market",
    "FLANNERY_GYM_MOLTEN_FORGE": "foundry",
    "HOUSING_MAGMA_TERRACES": "homes",
    "CENTRAL_VOLCANIC_PLAZA_CREST": "plaza",
}

def polish_street_facades(art, role):
    """Give each original 64x32 facade its own legible material and window rhythm.

    Alter ONLY existing building mural pixels. Retain roof crowns, identifiers,
    the central clinic cross / market cart / Gym crest, and every game tile.
    This is decoration, not new doors, collision or foreground geometry.
    """
    if role not in ("clinic", "market", "foundry", "homes"):
        return 0
    assert (art.w, art.h) == (64, 32)
    before = [row[:] for row in art.pix]

    def dot(x, y, color):
        assert 0 <= x < 64 and 13 <= y < 31 and 0 <= color < 16
        art.pixel(x, y, color)

    def horizontal(x0, x1, y, color):
        for x in range(x0, x1 + 1):
            dot(x, y, color)

    def window(left, top, width, height, glass, kind):
        right, bottom = left + width - 1, top + height - 1
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                on_edge = x in (left, right) or y in (top, bottom)
                inset = x in (left + 1, right - 1) or y in (top + 1, bottom - 1)
                if on_edge:
                    color = 5
                elif inset:
                    color = 6
                elif kind == "clinic" and x == left + width // 2:
                    color = 8
                elif kind == "market" and y == top + height // 2:
                    color = 8
                elif kind == "kiln" and (y - top) % 3 == 0:
                    color = 5
                elif kind == "home" and x == left + width // 2:
                    color = 8
                else:
                    color = glass if (x + 2 * y) % 7 else 13
                dot(x, y, color)
        horizontal(left - 1, right + 1, bottom + 1, 8)
        horizontal(left, right, bottom + 2, 6)

    if role == "clinic":
        # Diagnostic side bays, separate from the central medical cross.
        for left in (9, 44):
            horizontal(left, left + 11, 14, 5)
            horizontal(left + 1, left + 10, 15, 6)
            window(left + 2, 16, 8, 7, 10, "clinic")
            for x in (left, left + 11):
                for y in range(17, 26):
                    dot(x, y, 8 if y % 4 else 5)
            horizontal(left, left + 11, 26, 5)
            horizontal(left + 1, left + 10, 27, 13)
    elif role == "market":
        # Two cold-glass retail bays, outside the original cart/sign x20..44.
        window(12, 16, 8, 8, 10, "market")
        window(47, 16, 8, 8, 9, "market")
        for left, right in ((12, 19), (47, 54)):
            horizontal(left, right, 14, 5)
            horizontal(left + 1, right - 1, 15, 10)
            # The original uninterrupted cyan storefront canopy is at y=27.
            # Shade the footings BELOW it, never paint over the canopy.
            horizontal(left + 1, right - 1, 28, 6)
    elif role == "foundry":
        # Upright furnace vents, not duplicates of the clinic/market glass.
        for left in (10, 48):
            horizontal(left, left + 8, 14, 5)
            window(left + 1, 16, 7, 8, 12, "kiln")
            for x in (left + 2, left + 4, left + 6):
                for y in (18, 21):
                    dot(x, y, 14)
            horizontal(left - 1, left + 9, 27, 8)
            horizontal(left, left + 8, 28, 13)
    else:
        houses = (
            (7, 18, 12, "home"),
            (21, 32, 9, "market"),
            (34, 45, 14, "kiln"),
            (47, 58, 10, "clinic"),
        )
        for index, (left, right, glass, kind) in enumerate(houses):
            # Four readable residential bays with distinct glazing and stone.
            stone = (3, 2, 8, 3)[index]
            for y in range(15, 27):
                for x in range(left + 1, right):
                    dot(x, y, stone if (y + index) % 6 else 6)
            horizontal(left, right, 14, 5)
            horizontal(left + 1, right - 1, 15, 6)
            window(left + 2, 17, right - left - 3, 7, glass, kind)
            for x in (left, right):
                for y in range(16, 28):
                    dot(x, y, 8 if y % 4 else 5)
            # Four warm, continuous stone sills keep the houses visually
            # inhabited by night; each pair uses its own oxide tone.
            horizontal(left + 2, right - 2, 25, 13 if index % 2 == 0 else 11)
            horizontal(left, right, 28, 5)
            horizontal(left + 1, right - 1, 29, 13 if index % 2 == 0 else 11)

    if any(art.pix[y] != before[y] for y in range(13)):
        raise ValueError("Facade pass changed roof silhouettes or upper landmarks")
    safe_regions = {
        "clinic": ((9, 20), (44, 55)),
        "market": ((11, 20), (46, 55)),
        "foundry": ((9, 19), (47, 57)),
        "homes": ((7, 18), (21, 32), (34, 45), (47, 58)),
    }[role]
    changes = [(x, y) for y in range(32) for x in range(64)
               if art.pix[y][x] != before[y][x]]
    if any(y < 13 or not any(left <= x <= right for left, right in safe_regions)
           for x, y in changes):
        raise ValueError("Facade pass painted outside a private building wing")
    if len(changes) < 140:
        raise ValueError(f"{role} facade detailing too sparse: {len(changes)}")
    print(f"Cuordilava facade legibility: {role}, {len(changes)} safe pixels")
    return len(changes)


def organize_districts(art, name):
    role=ROLES.get(name)
    if role is None:
        return 0
    if (art.w,art.h)!=(64,32):
        raise ValueError("District reprofile cannot alter four-by-two original footprint")
    before=[row[:] for row in art.pix]

    def p(x,y,c):
        if 0 <= x < 64 and 0 <= y < 32:
            art.pixel(x,y,c)

    def rect(l,t,r,b,c):
        for y in range(max(0,t),min(32,b+1)):
            for x in range(max(0,l),min(64,r+1)):
                p(x,y,c)

    def line(l,r,y,c):
        for x in range(l,r+1):
            p(x,y,c)

    def tower(cx,top,half,glass):
        # Narrow arched lantern tower grows out of a larger gabled mass:
        # a roof ornament, not a new game object or blocking building.
        for y in range(top,top+7):
            width=half if y>top+1 else half-1
            for x in range(cx-width,cx+width+1):
                if y in (top,top+6) or x in (cx-width,cx+width):
                    p(x,y,5 if y!=top+6 else 8)
                elif x==cx:
                    p(x,y,8)
                else:
                    p(x,y,glass if (x+y)%3 else 13)
        line(cx-half-1,cx+half+1,top+7,6)

    if role=="plaza":
        # A broad geothermally carved diamond amphitheatre replaces a tiny
        # isolated badge. Multiple tonal stages make the district legible
        # at 3x GBA preview and 1x gameplay scale: outer flagstone ring,
        # matte basalt approach, protective copper rim, warm central oculus.
        # No teal/water pixels: this is solid decorative walkable inlay.
        art.pix=[[0]*64 for _ in range(32)]
        for y in range(32):
            for x in range(64):
                dx=abs(x-31)
                dy=abs(y-15)
                d=3*dx+5*dy
                if d>92:
                    continue
                if d>=88:
                    c=5
                elif d>=84:
                    c=6
                elif d>=72:
                    c=3 if (x//9+y//6)%4 else 4
                elif d>=67:
                    c=5
                elif d>=61:
                    c=13 if (x//7+y//5)%3 else 6
                elif d>=51:
                    c=2
                elif d>=46:
                    c=5
                elif d>=38:
                    c=13 if (x+y)%3 else 11
                else:
                    c=8 if (x//7+y//4)%4 else 3
                p(x,y,c)
        # Exterior stone landing-bays point to three town approaches, rather
        # than uniform neon squares. Embedded pads are NOT collision blocks.
        for y in (5,24):
            for x in range(18,46):
                if (x+y)%4!=0:
                    p(x,y,5)
        for left,right in ((5,17),(45,59)):
            for y in (12,20):
                line(left,right,y,5)
                line(left+2,right-2,y+1,6)
        # Large iris seal with six pointed basalt fins surrounding a central
        # warm mineral eye. Its outline is exactly registered to our diamond.
        for x0,y0,x1,y1 in (
            (31,8,23,15),(23,15,31,23),(31,23,40,15),(40,15,31,8),
            (24,15,39,15),(31,8,31,23)
        ):
            art.line(x0,y0,x1,y1,13)
        for x0,y0,x1,y1 in (
            (31,10,26,16),(26,16,31,21),(31,21,36,16),(36,16,31,10)
        ):
            art.line(x0,y0,x1,y1,11)
        for y in range(12,21):
            for x in range(28,36):
                d=2*abs(x-31)+3*abs(y-16)
                if d<=12:
                    p(x,y,12 if d<8 else 14)
                if d==13:
                    p(x,y,13)
        for x,y in ((31,12),(28,16),(34,16),(31,20)):
            p(x,y,14)
        # Bottom/border remains translucent over the original plaza ground.
        if sum(v != 0 for row in art.pix for v in row)<980:
            raise ValueError("The new geothermal town square became a sparse emblem")

    elif role=="homes":
        # The y>=13 facade previously looked like one continuous electronic
        # conveyor belt despite the four roof gables. Give four homes their
        # own mineral stonewall, arched windows, attics and base terraces.
        # The row y<=12 remains preserved for the existing roof stitch,
        # iconic roof peaks and private house-marquee validators.
        for y in range(13,31):
            for x in range(4,61):
                district = 0 if x<19 else 1 if x<33 else 2 if x<46 else 3
                face=(3,2,8,3)[district]
                c=face
                if y in (13,28,30):
                    c=5
                elif y in (14,29):
                    c=6
                elif (y-15)%6==0 and (x+district*3)%8 not in (0,1):
                    c=5
                elif x in (5,18,19,32,33,45,46,59):
                    c=8
                elif (x+2*y+district)%23==0:
                    c=4
                p(x,y,c)
        # Arches are recessed residential windows (not additional warps).
        # Material/glazing schemes are intentionally different per house.
        for idx,(cx,half,top,glass) in enumerate(
            ((12,5,17,12),(25,4,16,11),(39,5,17,14),(52,4,15,12))
        ):
            left,right=cx-half,cx+half
            for y in range(top,27):
                for x in range(left,right+1):
                    dist=abs(x-cx)
                    if y==top and dist>=half-1:
                        continue
                    if y==top+1 and dist==half:
                        c=8
                    elif y==top or y==26 or dist==half:
                        c=5
                    elif y in (top+5,23):
                        c=6
                    elif x==cx:
                        c=8
                    elif idx==1 and y>=23:
                        c=3
                    else:
                        c=glass if (x+y+idx)%8 else 13
                    p(x,y,c)
            line(left-1,right+1,27,6)
            line(left,right,28,13)
            # The street arcade has dark structural feet aligned with the
            # four separate homes, rather than columns floating in windows.
            for x in (left-2,right+2):
                for y in range(16,28):
                    p(x,y,5 if y%5!=0 else 6)
            for x in range(left,right+1,3):
                p(x,30,13)
        # Shadowed home separators, gently warm shared base.
        for x in (19,33,46):
            for y in range(13,30):
                p(x,y,8 if y%6!=0 else 5)
                p(x+1,y,5 if y%4 else 6)
        line(6,58,30,5)

    elif role=="clinic":
        # Restore a little of the volcanic village identity to the currently
        # giant electronic Center. Unify the lower masonry and add its own
        # paired diagnostic wing arches without touching core cross or doors.
        for left,right in ((6,21),(43,57)):
            for y in range(14,24):
                for x in range(left,right+1):
                    if y in (14,23) or x in (left,right):
                        c=5
                    elif y in (15,22) or x in (left+1,right-1):
                        c=6
                    elif x in ((left+right)//2,):
                        c=8
                    else:
                        c=12 if (x+y)%5 else 14
                    p(x,y,c)
            line(left-1,right+1,24,13)
        # Volcanic ash stone at roof side-bays, consistent eave profile.
        for x in range(8,57):
            if x in range(27,40):
                continue # keep the iconic red medical cross
            if x%7 not in (0,1) and 12<=x<=53:
                p(x,13,5)
        for cx in (14,50):
            tower(cx,1,3,12)
        p(20,8,5)
        p(31,1,6)
        p(31,18,12)

    elif role=="market":
        # Two distinct massive east and west shop arcades beneath the cyan
        # technical canopy. Center panel and existing shopping display kept.
        for left,right,glass in ((11,25,11),(39,54,12)):
            for y in range(13,25):
                for x in range(left,right+1):
                    if y in (13,24) or x in (left,right):
                        c=5
                    elif y==14 and x in (left+1,right-1):
                        c=8
                    elif y in (19,22):
                        c=6
                    elif x==(left+right)//2:
                        c=8
                    else:
                        c=glass if (x+y)%6 else 13
                    p(x,y,c)
            line(left-1,right+1,25,5)
        for x in (9,32,56):
            for y in range(12,26):
                if x !=32:
                    p(x,y,8)
                    if y in (12,18,24):
                        p(x,y,13)
        p(20,8,5)
        p(32,20,10)
        p(9,16,5)

    else:  # foundry
        # High-temperature workshop on the Gym's lower upper-wall mural:
        # two recognizable kiln vaults and a broad black basalt lintel,
        # distinct from the Center's medical and Market's shop windows.
        for left,right,glass in ((10,26,12),(39,55,11)):
            mid=(left+right)//2
            for y in range(13,24):
                for x in range(left,right+1):
                    dx=abs(x-mid)
                    if y==13 and dx>5:
                        continue
                    if y==13 or x in (left,right) or y==23:
                        c=5
                    elif x==mid or y==19:
                        c=8
                    elif y==14 and dx>6:
                        c=6
                    else:
                        c=glass if (x+y)%6 else 14
                    p(x,y,c)
            line(left-1,right+1,24,5)
            for x in range(left+1,right,4):
                p(x,22,13)
        # Keep elevated central forge crest intact at y19,x32.
        for x in (7,58):
            for y in range(13,27):
                p(x,y,5 if y%4 else 6)
        p(20,8,5)
        p(32,19,12)

    # Final graphic-only pass makes original civic frontages distinct.
    polish_street_facades(art, role)

    # Reject partial/minimal passes. This redraw is substantially larger
    # than a couple of decorative roof pixels, but adds ZERO world geometry.
    changed=sum(before[y][x]!=art.pix[y][x]
                for y in range(32) for x in range(64))
    threshold={"clinic":140,"market":140,"foundry":140,
               "homes":550,"plaza":900}[role]
    if changed<threshold:
        raise ValueError(
            f"District {role} is too superficial: {changed} changed source pixels"
        )
    if any(c not in range(16) for row in art.pix for c in row):
        raise ValueError("Cuordilava district art exceeds 4-bit GBA indexed palette")
    print(f"Cuordilava zoning pass: {role}, {changed} source pixels recomposed")
    return changed
