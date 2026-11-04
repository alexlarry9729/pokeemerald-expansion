#!/usr/bin/env python3
"""Reinstate the ORIGINAL elevated hot-spring stairs, visibly and mechanically.

The walkable corridor from the hot springs to the rear Pokémon Center warp
is x6..9,y1 (map secondary metatile 174, elevation 3, collision 0). The earlier
roof-stitch pass confused it with a roof and overpainted the four stair panels.
The map already has the correct 4-cell connectivity: never alter its words.

The actual two original stair GRAPHIC characters (tiles 315 and 331) were
subsequently allocated to town murals. Do NOT point at those overwritten
characters. Instead, copy their EXACT indexed 8x8 pixels from the repository's
untouched vanilla secondary/lavaridge/tiles.png into characters 182 and 183
of the existing 512-character Cuordilava tileset. Both characters were only
used by the obsolete, now-retired scaffold on metatile 174 and must be
proven unreferenced by every other ACTIVE map cell before repurposing.

Original palette 8 and original base mountain graphics are retained.
No changes to world map, animation bands, 512-tile budget, elevation,
collision, six warps, scripts, thermal water or gameplay.
"""
from pathlib import Path
import json
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

STAIR_META = 174
STAIR_MAP_ID = 512+STAIR_META
STAIR_CELLS = {(6,1),(7,1),(8,1),(9,1)}
# Original secondary/Lavaridge source tile ID -> safe repurposed Cuordilava ID.
STEP_COPY = {315:182, 331:183}
assert not (set(STEP_COPY.values()) & (set(range(160,172)) | set(range(288,296))))
assert not (set(STEP_COPY.values()) & {168,169,180,181,184,185,200,201,202,203,392,393})
ORIGINAL_PIXELS_REFERENCES = (315,315,331,331)
ORIGINAL_STAIRS = (
    (10<<12)|82,(10<<12)|83,(10<<12)|98,(10<<12)|99,
    (8<<12)|(512+182),(8<<12)|(512+182),
    (8<<12)|(512+183),(8<<12)|(512+183),
)
OLD_SCAFFOLD = tuple((6<<12)|(512+t)
                     for t in (164,165,180,181,166,167,182,183))


def u16(buf, off):
    return struct.unpack_from('<H',buf,off)[0]


def paths(root):
    root=Path(root)
    return {
        'map':root/'data/layouts/LavaridgeTown/map.bin',
        'metas':root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        'attrs':root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'events':root/'data/maps/LavaridgeTown/map.json',
        'private_atlas':root/'data/tilesets/secondary/cuordilava/tiles.png',
        'vanilla_atlas':root/'data/tilesets/secondary/lavaridge/tiles.png',
    }


def inspect_access(m,attrs,events):
    if (len(m),len(attrs))!=(800,1024):
        raise ValueError('Original 20x20 world or original collision budget changed')
    found={(i%20,i//20) for i in range(400)
           if (u16(m,2*i)&1023)==STAIR_MAP_ID}
    if found!=STAIR_CELLS:
        raise ValueError(f'Original raised spa steps replaced by roof cells: {found}')
    for x,y in STAIR_CELLS:
        word=u16(m,2*(20*y+x))
        if (word&1023)!=STAIR_MAP_ID or ((word>>10)&3)!=0 or word>>12 != 3:
            raise ValueError(f'Hot-spring walkway no longer walkable at {(x,y)}')
    if u16(attrs,2*STAIR_META)!=0x1000:
        raise ValueError('Original elevated spa step behaviour was changed')
    warps=events['warp_events']
    if len(warps)!=6 or not any(
        w.get('x')==9 and w.get('y')==2
        and w.get('dest_map')=='MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F'
        and int(w.get('elevation',-1))==3
        for w in warps
    ):
        raise ValueError('The hot-spring staircase no longer reaches the rear Center warp')
    if not any(
        e.get('x')==6 and e.get('y')==3 and int(e.get('elevation',-1))==3
        for e in events.get('coord_events',[])
    ):
        raise ValueError('Original hot-spring trigger no longer exists')


def verify_exact_step_pixels(root):
    p=paths(root)
    src_w,src_h,src=png_indexed(p['vanilla_atlas'])
    dst_w,dst_h,dst=png_indexed(p['private_atlas'])
    if (src_w,src_h)!=(128,232) or (dst_w,dst_h)!=(128,256):
        raise ValueError('Step repair changed the original secondary atlas geometry')
    for original,local in STEP_COPY.items():
        ox,oy=(original%16)*8,(original//16)*8
        dx,dy=(local%16)*8,(local//16)*8
        a=[tuple(src[oy+y][ox:ox+8]) for y in range(8)]
        b=[tuple(dst[dy+y][dx:dx+8]) for y in range(8)]
        if a!=b:
            raise ValueError(f'Original 8x8 stair graphic {original} was not restored at {local}')


def validate_built(root):
    p=paths(root)
    m,meta,attrs=(p[key].read_bytes() for key in ('map','metas','attrs'))
    if len(meta)!=8192:
        raise ValueError('Original 512 GBA character registrations were changed')
    events=json.loads(p['events'].read_text(encoding='utf-8'))
    inspect_access(m,attrs,events)
    if struct.unpack_from('<8H',meta,STAIR_META*16)!=ORIGINAL_STAIRS:
        raise ValueError('The raised step panels no longer point to restored vanilla art')
    # The two source characters are private to the four restored elevated
    # cells; original nearby art, animated lava and all other tiles are safe.
    for pos in range(400):
        mid=u16(m,2*pos)&1023
        bank=meta if mid>=512 else None
        if bank is None:
            continue
        idx=mid-512
        for slot in range(8):
            value=u16(bank,idx*16+slot*2)
            if (value&1023)-512 in STEP_COPY.values() and mid!=STAIR_MAP_ID:
                raise ValueError(f'Restored stair graphic is shared at map cell {pos}')
    verify_exact_step_pixels(root)
    return True


def run(root):
    root=Path(root)
    p=paths(root)
    m,meta,attrs=(p[key].read_bytes() for key in ('map','metas','attrs'))
    events=p['events'].read_bytes()
    if len(meta)!=8192:
        raise ValueError('Stair fix requires assembled fixed-capacity Cuordilava art')
    inspect_access(m,attrs,json.loads(events))
    if struct.unpack_from('<8H',meta,STAIR_META*16)!=OLD_SCAFFOLD:
        raise ValueError('Old (incorrect) stair scaffold changed; refusing stale edit')
    # Check no other ACTIVE metatile on the town references 182 or 183.
    old_chars=set(STEP_COPY.values())
    for pos in range(400):
        mid=u16(m,2*pos)&1023
        if mid<512 or mid==STAIR_MAP_ID:
            continue
        idx=mid-512
        for slot in range(8):
            t=u16(meta,idx*16+slot*2)&1023
            if t>=512 and t-512 in old_chars:
                raise ValueError(f'Cannot safely reuse original stair art slot at cell {pos}')
    w,h,dst=png_indexed(p['private_atlas'])
    sw,sh,src=png_indexed(p['vanilla_atlas'])
    if (w,h)!=(128,256) or (sw,sh)!=(128,232):
        raise ValueError('Unexpected changed GBA tileset dimensions')
    source_png=p['private_atlas'].read_bytes()
    colour_table=source_png[source_png.index(b'PLTE')+4:
                            source_png.index(b'PLTE')+52]
    if len(colour_table)!=48:
        raise ValueError('Private 4bpp palette changed unexpectedly')
    for original,local in STEP_COPY.items():
        sx,sy=(original%16)*8,(original//16)*8
        dx,dy=(local%16)*8,(local//16)*8
        for y in range(8):
            for x in range(8):
                dst[dy+y][dx+x]=src[sy+y][sx+x]
    newmeta=bytearray(meta)
    struct.pack_into('<8H',newmeta,STAIR_META*16,*ORIGINAL_STAIRS)
    for mid in range(512):
        if mid!=STAIR_META and (
            newmeta[16*mid:16*mid+16]!=meta[16*mid:16*mid+16]
        ):
            raise ValueError('The stair restoration altered unrelated GBA metatiles')
    write_png(p['private_atlas'],128,256,dst,colour_table)
    p['metas'].write_bytes(newmeta)
    validate_built(root)
    if p['map'].read_bytes()!=m or p['attrs'].read_bytes()!=attrs or \
       p['events'].read_bytes()!=events:
        raise ValueError('Restoring the staircase altered the world geometry')
    print('Cuordilava REAL original stair graphics restored: 4 raised access '
          'cells at x6..9,y1, 2 exact original 8x8 graphic characters '
          'copied to previously occupied but now retired slots 182/183; '
          '0 new slots, 6 original warps, collision and elevation unchanged')


if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
