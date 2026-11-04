#!/usr/bin/env python3
"""Add a complete kiln-glass ground-floor strip below Flannery's Gym facade.

Five private secondary metatiles contain original collision and base graphics
plus reused 4bpp house glass patterns. Distinct ordering differentiates the
forge's kiln windows. Does not touch the Gym entrance at (5,15), sprites,
effects, warp data, world light engine, tile counts, or outdoor access paths.
"""
from pathlib import Path
import struct
import json
from construct_cuordilava_lower_facade import ART_TILES

GYM_Y = 14
GYM_XS = (2, 3, 4, 5, 6)
OLD_IDS = (448, 449, 450, 453, 451)
NEW_IDS = (425, 426, 427, 428, 429)
# Source panels 0..6, used in a nonconsecutive order for a technical furnace.
PANELS = (4, 1, 6, 2, 5)


def u16(raw, off):
    return struct.unpack_from('<H', raw, off)[0]


def sources(root):
    root=Path(root)
    return {
        'map': root/'data/layouts/LavaridgeTown/map.bin',
        'metas': root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        'attrs': root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'primary': root/'data/tilesets/primary/general/metatiles.bin',
        'priattr': root/'data/tilesets/primary/general/metatile_attributes.bin',
        'events': root/'data/maps/LavaridgeTown/map.json',
    }


def validate_built(root):
    p=sources(root)
    town=p['map'].read_bytes()
    meta=p['metas'].read_bytes()
    attrs=p['attrs'].read_bytes()
    pri=p['primary'].read_bytes()
    pattr=p['priattr'].read_bytes()
    if (len(town),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('Volcanic map dimensions/metatile budget changed')
    for x,old,mid,panel in zip(GYM_XS,OLD_IDS,NEW_IDS,PANELS):
        addr=GYM_Y*20+x
        value=u16(town,addr*2)
        if (value&1023)!=512+mid:
            raise ValueError('Kiln frontage metatile missing')
        if u16(attrs,mid*2)!=u16(pattr,old*2):
            raise ValueError('Original Gym wall behavior is not preserved')
        if meta[mid*16:mid*16+8]!=pri[old*16:old*16+8]:
            raise ValueError('Gym original underlay was changed')
        for q in range(4):
            encoded=u16(meta,mid*16+8+q*2)
            expected=(6<<12)|(512+ART_TILES[panel*4+q])
            if encoded!=expected:
                raise ValueError('Unexpected kiln window tile/palette')
        occurrences=[i for i in range(400)
                     if (u16(town,i*2)&1023)==512+mid]
        if occurrences != [addr]:
            raise ValueError('Kiln facade has leaked outside its room wall')


def run(root):
    p=sources(root)
    mapbuf=bytearray(p['map'].read_bytes())
    meta=bytearray(p['metas'].read_bytes())
    attrs=bytearray(p['attrs'].read_bytes())
    pri=p['primary'].read_bytes()
    pattr=p['priattr'].read_bytes()
    if (len(mapbuf),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('Run Gym art AFTER new housing wall and spa passes')
    ev=json.loads(p['events'].read_text())
    reserved={(int(o['x']),int(o['y']))
              for category in ('object_events','warp_events','coord_events','bg_events')
              for o in ev.get(category,[]) if 'x' in o and 'y' in o}
    if reserved.intersection((x,GYM_Y) for x in GYM_XS):
        raise ValueError('Cannot decorate Gym over an NPC, sign, or warp')
    already={u16(mapbuf,i*2)&1023 for i in range(400)}
    if any(512+mid in already for mid in NEW_IDS):
        raise ValueError('One of the selected private Gym metatiles is active')
    before_map=bytes(mapbuf)
    before_meta=bytes(meta)
    before_attr=bytes(attrs)
    for x,old,mid,panel in zip(GYM_XS,OLD_IDS,NEW_IDS,PANELS):
        address=(GYM_Y*20+x)*2
        prior=u16(mapbuf,address)
        if prior&1023!=old:
            raise ValueError(f'Gym base facade moved at {x},{GYM_Y}: {prior&1023}')
        # The source base/collision is retained byte-for-byte.
        new=bytearray(pri[old*16:old*16+8])
        if len(new)!=8:
            raise ValueError('Gym source underlay missing')
        for q in range(4):
            new+=struct.pack('<H',(6<<12)|(512+ART_TILES[panel*4+q]))
        meta[mid*16:mid*16+16]=new
        attrs[mid*2:mid*2+2]=pattr[old*2:old*2+2]
        struct.pack_into('<H',mapbuf,address,(prior&~1023)|(512+mid))
    for i in range(400):
        old,new=u16(before_map,i*2),u16(mapbuf,i*2)
        if (old>>10)!=(new>>10) or ((i%20,i//20) not in {(x,GYM_Y) for x in GYM_XS} and old!=new):
            raise ValueError('Unintended world geometry/collision changes')
    if any(meta[i*16:i*16+16]!=before_meta[i*16:i*16+16]
           for i in range(512) if i not in NEW_IDS):
        raise ValueError('Unintended neighboring metatile modification')
    if any(attrs[i*2:i*2+2]!=before_attr[i*2:i*2+2]
           for i in range(512) if i not in NEW_IDS):
        raise ValueError('Unintended collision modification')
    p['map'].write_bytes(mapbuf)
    p['metas'].write_bytes(meta)
    p['attrs'].write_bytes(attrs)
    validate_built(root)
    print('Flannery Gym: five additional connected furnace-glass frontage cells; '
          'original warp, scripts, illumination, metatile total and collision retained')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
