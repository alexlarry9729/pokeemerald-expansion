#!/usr/bin/env python3
"""Stitch ONLY the non-walkable rear Poké Mart roof to its authored facade.

The ORIGINAL x6..9,y1 corridor behind the mineral pool is *walkable elevated
hot-spring stair access* (elevation 3), NOT a Center roof. Earlier versions
incorrectly overpainted those four path cells with four private roof aliases.
Never touch those Center cells: restore_cuordilava_original_spring_steps.py
reinstates the original stone-step metatile in the final pipeline.

The four old Market roof cells at x14..17,y2 are not walkable and may reuse
the new Mart facade art through four private unused metatiles (390..393).
No shared source graphics, collision, elevation or town warps are changed.
"""
from pathlib import Path
import json
import struct

# NO CENTER_REAR: these were elevated walkable stone steps, never roof tiles.
CENTER_REAR = ()
MARKET_REAR = tuple((14+i, 2, mid, 390+i, 14+i, 3) for i,mid in
                    enumerate((590,587,588,591)))
EXTRA_METAS = frozenset(range(390,394))
DONOR_START = 441
PALETTE = 6


def word(buf,off):
    return struct.unpack_from('<H',buf,off)[0]


def paths(root):
    root=Path(root)
    return {
        "map":root/'data/layouts/LavaridgeTown/map.bin',
        "metas":root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        "attrs":root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        "events":root/'data/maps/LavaridgeTown/map.json',
        "primary":root/'data/tilesets/primary/general/metatiles.bin',
        "primary_attrs":root/'data/tilesets/primary/general/metatile_attributes.bin',
    }


def spots(map_bytes, mid):
    return {(i%20,i//20) for i in range(400)
            if (word(map_bytes,2*i)&1023)==mid}


def donor_overlay(map_bytes, metas, x, y):
    mid=word(map_bytes,2*(20*y+x))&1023
    if not (512+DONOR_START<=mid<512+DONOR_START+16):
        raise ValueError(f"Roof donor at {(x,y)} is no longer part of the authored civic murals: {mid}")
    art=metas[(mid-512)*16+8:(mid-512)*16+16]
    if len(art)!=8:
        raise ValueError("Incomplete roof art quadrant")
    for q in range(4):
        tile=word(art,2*q)
        if (tile>>12)!=PALETTE or (tile&1023)<512 or (tile&0x0c00):
            raise ValueError(f"Old/back roof cannot borrow nonprivate 4bpp art: {tile:#06x}")
    return art


def check_event_safety(path_map):
    data=json.loads(path_map.read_text(encoding="utf-8"))
    reserved={(int(e['x']),int(e['y'])) for group in
              ('object_events','warp_events','coord_events','bg_events')
              for e in data.get(group,[]) if 'x' in e and 'y' in e}
    selected={(x,y) for x,y,*_ in CENTER_REAR} | {
        (x,y) for x,y,*_ in MARKET_REAR}
    if selected&reserved:
        raise ValueError(f"Rear-roof repair overlaps an existing game event: {selected&reserved}")
    # The elevated Center warp is NOT one of our four rooftop cells;
    # it sits directly BELOW them at (9,2) and must never move.
    entrances={(w['x'],w['y']) for w in data['warp_events']}
    if (9,2) not in entrances or (15,5) not in entrances or len(entrances)!=6:
        raise ValueError("Original Center/Mart entrances were displaced")


def validate_built(root):
    p=paths(root)
    m,meta,attrs=[p[k].read_bytes() for k in ('map','metas','attrs')]
    if (len(m),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError("Rear roof must retain original map and 512-metatile footprint")
    check_event_safety(p['events'])
    for x,y,old,new,donor_x,donor_y in CENTER_REAR:
        if spots(m,512+new)!={(x,y)} or (word(m,2*(y*20+x))&1023)!=512+new:
            raise ValueError(f"Disconnected Center roof panel at {(x,y)}")
        if meta[16*new+8:16*new+16] != donor_overlay(m,meta,donor_x,donor_y):
            raise ValueError(f"Center rear roof lost continuous donor art {(x,y)}")
        if word(attrs,2*new)!=word(attrs,2*(old-512)):
            raise ValueError("Elevated Center rear roofing changed collision/behavior")
    for x,y,old,new,donor_x,donor_y in MARKET_REAR:
        if spots(m,512+new)!={(x,y)}:
            raise ValueError(f"Market rear roof alias lost correct location at {(x,y)}")
        off=new*16
        if meta[off+8:off+16]!=donor_overlay(m,meta,donor_x,donor_y):
            raise ValueError(f"Market rear roof lost registered donor art at {(x,y)}")
        if word(attrs,2*new)!=word(attrs,2*(old-512)):
            raise ValueError("Market roof changed original terrain behavior")
    return True


def run(root):
    p=paths(root)
    m=bytearray(p['map'].read_bytes())
    meta=bytearray(p['metas'].read_bytes())
    attrs=bytearray(p['attrs'].read_bytes())
    if (len(m),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError("Rear roof pass requires completed 20x20 town and private GBA tiles")
    check_event_safety(p['events'])
    before_map,before_meta,before_attrs=bytes(m),bytes(meta),bytes(attrs)
    used={word(m,2*i)&1023 for i in range(400)}
    if any(512+mid in used for mid in EXTRA_METAS):
        raise ValueError("Rear roof metatile alias conflicts with existing city art")
    if any(spots(m,old)!={(x,y)} for x,y,old,*_ in MARKET_REAR):
        raise ValueError("Old Market roof graphics are shared with another map cell")
    if spots(m,686)!={(6,1),(7,1),(8,1),(9,1)}:
        raise ValueError("Center upper annex no longer has four original roof panels")
    # Do not adjust the original old upper roof base layers: their actual
    # source geometry and terrain elevation remain exactly as they were.
    for x,y,old,new,donor_x,donor_y in CENTER_REAR:
        oldidx=old-512
        background=meta[oldidx*16:oldidx*16+8]
        roof=donor_overlay(m,meta,donor_x,donor_y)
        meta[new*16:new*16+16]=background+roof
        struct.pack_into('<H',attrs,new*2,word(before_attrs,oldidx*2))
        at=2*(20*y+x)
        original=word(m,at)
        if original&1023!=old:
            raise ValueError("Center old roof source unexpectedly moved")
        struct.pack_into('<H',m,at,(original&~1023)|(512+new))
    # Keep protected original Market source definitions pristine. Use four
    # separately registered local aliases that keep exact terrain semantics.
    for x,y,old,new,donor_x,donor_y in MARKET_REAR:
        old_idx=old-512
        background=meta[old_idx*16:old_idx*16+8]
        roof=donor_overlay(m,meta,donor_x,donor_y)
        meta[new*16:new*16+16]=background+roof
        struct.pack_into('<H',attrs,new*2,word(before_attrs,old_idx*2))
        at=2*(20*y+x)
        raw=word(m,at)
        if raw&1023!=old:
            raise ValueError("Original Market rooftop source shifted unexpectedly")
        struct.pack_into('<H',m,at,(raw&~1023)|(512+new))
    for i in range(400):
        a,b=word(before_map,i*2),word(m,i*2)
        if a>>10!=b>>10 or (
            (i%20,i//20) not in (
                {(x,y) for x,y,*_ in CENTER_REAR} |
                {(x,y) for x,y,*_ in MARKET_REAR}
            ) and a!=b
        ):
            raise ValueError("Rear rooftop art altered original game geometry")
    for mid in range(512):
        if mid not in EXTRA_METAS and (
            meta[mid*16:mid*16+16]!=before_meta[mid*16:mid*16+16]
            or attrs[mid*2:mid*2+2]!=before_attrs[mid*2:mid*2+2]
        ):
            raise ValueError(f"Rear roof pass leaked outside protected metatile {mid}")
    p['map'].write_bytes(m)
    p['metas'].write_bytes(meta)
    p['attrs'].write_bytes(attrs)
    validate_built(root)
    print("Cuordilava: registered only four non-walkable Mart rear roof cells; "
          "the four ORIGINAL elevated Center-to-hot-spring stair cells were "
          "left untouched; no collision/elevation or warp changes")


if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
