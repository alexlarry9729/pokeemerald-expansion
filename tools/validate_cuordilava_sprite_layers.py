#!/usr/bin/env python3
"""Fail-closed regression test for the REAL GBA player-occlusion bug.

A normal (0) metatile sends its top four 8x8 graphics to BG1, ABOVE the
default-elevation-3 player. The former Cuordilava build accidentally gave
many opaque, walkable, new plaza/road/flower graphics this exact layer.

The correct covered (1) metatile draws both graphic quadrants on BG3/BG2,
BEHIND the player, without changing collision, event scripts or 20x20 map.
Reference: src/field_camera.c:DrawMetatile, global.fieldmap.h.
"""
from collections import Counter
from pathlib import Path
import json
import struct

from cuordilava_layers import COVERED_LAYER, validate_covered

# These are ORIGINAL open cells with newly added visual artwork. DO NOT force
# covered on the cliffs, tall canopies, bridges or other actual obstructions.
PAVEMENTS = set(range(400,412))   # 84 walkable original street cells
FLOWERS = {422,438}              # 12 walkable low basalt herb gardens
VENTS = {424}                    # 4 flush inlaid copper grilles
HOUSING_TERRACE = set(range(416,420)) # 4 original walkable roof-edge cells
# Entire architectural mural pieces whose ORIGINAL map collision is 0.
# Flannery ground approach, central plaza caldera, home roof approach.
WALKABLE_MURALS = set(range(457,461)) | set(range(465,473)) | set(range(477,481))
GROUPS = {"pavement": PAVEMENTS, "flowers":FLOWERS,
          "vents":VENTS,"walkable_murals":WALKABLE_MURALS,
          "housing_terrace":HOUSING_TERRACE}
EXPECTED_COUNTS = {"pavement":84, "flowers":12,
                   "vents":4,"walkable_murals":16,"housing_terrace":4}


def audit(root):
    root = Path(root)
    m=(root/"data/layouts/LavaridgeTown/map.bin").read_bytes()
    a=(root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin").read_bytes()
    p=(root/"data/tilesets/primary/general/metatile_attributes.bin").read_bytes()
    if (len(m),len(a),len(p)) != (800,1024,1024):
        raise ValueError("Cuordilava ROM dimensions or attribute banks changed")
    from sculpt_cuordilava_civic_paving import FLOOR_SOURCE, AVENUE_SOURCES
    counts=Counter()
    seen={group:set() for group in GROUPS}
    for pos in range(400):
        raw=struct.unpack_from("<H",m,pos*2)[0]
        mid=(raw&1023)-512
        if mid<0:
            continue
        # Catch ALL FUTURE town-specific 8x8 mural/roof/inlay artwork,
        # not just known groups. In the user's actual ROM four
        # y12 residential-roof cells escaped the previous enumerated test.
        # Any new walkable town private metatile on BG1 obscures sprites.
        if mid >= 400 and not ((raw>>10)&3):
            live_attr=struct.unpack_from("<H",a,mid*2)[0]
            if (live_attr>>12) != COVERED_LAYER:
                raise ValueError(
                    f"PLAYER HIDDEN BY UNREGISTERED TILE: cell {(pos%20,pos//20)} "
                    f"town metatile {mid}, layer {live_attr>>12}"
                )
        groups=[k for k,values in GROUPS.items() if mid in values]
        if not groups:
            continue
        if len(groups)!=1:
            raise ValueError(f"Decorated walkable {mid} matches multiple groups")
        group=groups[0]
        if (raw>>10)&3:
            raise ValueError(f"New ground graphic {group} at {pos%20,pos//20} has blocking collision")
        attr=struct.unpack_from("<H",a,mid*2)[0]
        if (attr>>12)!=COVERED_LAYER:
            raise ValueError(f"PLAYER HIDDEN: {group} at {(pos%20,pos//20)} "
                             f"metatile {mid} has layer={attr>>12} not COVERED/BG2")
        if group=="pavement":
            source=FLOOR_SOURCE if mid<406 else AVENUE_SOURCES[mid-406]
        elif group in ("flowers","vents"):
            source=FLOOR_SOURCE
        else:
            source=None
        if source is not None:
            original=struct.unpack_from("<H",p,2*source)[0]
            validate_covered(original,attr,
                             f"{group} metatile {mid} cell {(pos%20,pos//20)}")
        elif attr & 0x0FFF:
            raise ValueError(f"Walkable architectural image {mid} changed gameplay bits")
        counts[group]+=1
        seen[group].add(mid)
    if dict(counts)!=EXPECTED_COUNTS:
        raise ValueError(f"Ground layer audit map coverage changed: {dict(counts)} != {EXPECTED_COUNTS}")
    if any(seen[g]!=GROUPS[g] for g in GROUPS):
        raise ValueError(f"Private town floor tiles missing: {seen}")
    return {
       "player_above_all_redesigned_walkable_metatiles":True,
       "real_gba_layer_type":"COVERED (1), BG2 behind elevation-3 player",
       "metatile_attribute_layer_mask":"0xF000",
       "original_map_collision_and_elevation_preserved":True,
       "number_of_affected_map_cells":sum(counts.values()),
       "groups":dict(counts),
       "note":"Static source/metatile/BG layering audit; in-emulator walking still required",
    }


if __name__=="__main__":
    r=audit(Path(__file__).resolve().parents[1])
    print(json.dumps(r,indent=2))
