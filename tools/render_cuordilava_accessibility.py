#!/usr/bin/env python3
"""Real city day/night previews with collision-safe connected route overlays.

Diagnostic only; this tool never modifies ROM art, scripts or map data.
Blue dots indicate original walkable Route112/street network, lilac dots the
isolated elevated hot spring component, amber rings the five street-level
doors, and a purple ring the special elevated Center access. Dots never
invent new paths; they are computed from the generated map's GBA collision
bits, cross-checked against the committed original map.
"""
from pathlib import Path
import argparse
import json
from render_cuordilava_detail_sheet import rgb_png
from render_cuordilava_preview import pack_png
from validate_cuordilava_connectivity import (
    SIZE, GROUND_GATE, SPRING_GATE, STREET_WARPS,
    ELEVATED_WARP, audit, flags, reachable,
)

CELL = 48
DAY_STREET = (93, 190, 223)
DAY_SPRING = (201, 141, 232)
NIGHT_STREET = (131, 200, 245)
NIGHT_SPRING = (196, 148, 237)
DOOR = (255, 177, 80)
SPECIAL_DOOR = (214, 140, 247)


def mark(rgb: bytearray, x: int, y: int, color, radius=4, hollow=False):
    width = SIZE * CELL
    for dy in range(-radius-1, radius+2):
        for dx in range(-radius-1, radius+2):
            xx, yy = x+dx, y+dy
            if not 0 <= xx < width or not 0 <= yy < width:
                continue
            d = dx*dx+dy*dy
            if (radius-2)**2 <= d <= (radius+1)**2 if hollow else d <= radius*radius:
                off = (yy*width+xx)*3
                # Composite network nodes over real image, retaining detail.
                if hollow:
                    rgb[off:off+3] = bytes(color)
                else:
                    prev=rgb[off:off+3]
                    rgb[off:off+3] = bytes(
                        (prev[i]+2*color[i])//3 for i in range(3)
                    )


def render(root: Path, preview: Path, out: Path):
    root = Path(root)
    result = audit(root)
    raw=(root/'data/layouts/LavaridgeTown/map.bin').read_bytes()
    f=flags(raw)
    road=reachable(GROUND_GATE,f)
    spring=reachable(SPRING_GATE,f)
    out.mkdir(parents=True,exist_ok=True)
    generated={}
    for mode in ('day','night'):
        width,height,rgb=rgb_png(preview/f'cuordilava-{mode}.png')
        if (width,height)!=(SIZE*CELL,SIZE*CELL):
            raise ValueError('Cuordilava accessibility audit requires real 960px preview')
        street_col=DAY_STREET if mode=='day' else NIGHT_STREET
        spring_col=DAY_SPRING if mode=='day' else NIGHT_SPRING
        for x,y in road:
            mark(rgb,x*CELL+CELL//2,y*CELL+CELL//2,street_col,3)
        for x,y in spring:
            mark(rgb,x*CELL+CELL//2,y*CELL+CELL//2,spring_col,3)
        for x,y in STREET_WARPS:
            mark(rgb,x*CELL+CELL//2,y*CELL+CELL//2,DOOR,10,True)
        x,y=ELEVATED_WARP[0]
        mark(rgb,x*CELL+CELL//2,y*CELL+CELL//2,SPECIAL_DOOR,10,True)
        target=out/f'cuordilava-accessibility-{mode}.png'
        pack_png(target,width,height,rgb)
        generated[mode]={'image':target.name,'size_bytes':target.stat().st_size}
    manifest={
        **result,
        'overlay_diagnostic_only':True,
        'legend': {
            'small_cyan_dots':'Street-level walkable ground connected to Route112',
            'small_lilac_dots':'Elevated hot-spring walkable component',
            'orange_door_rings':'Five original street-accessible warp positions',
            'lilac_door_ring':'Original elevated hot-spring Center warp',
            'visual_elements_are_not_in_the_ROM':True,
        },
        'images':generated,
    }
    (out/'cuordilava-accessibility.json').write_text(
        json.dumps(manifest,indent=2)+'\n',encoding='utf-8'
    )
    print(f'Cuordilava map accessibility: {len(road)} street nodes, '
          f'{len(spring)} spring nodes, 6 original doorways; '
          'diagnostic day/night images generated')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--input-dir',type=Path,default=Path('build-preview'))
    p.add_argument('--output-dir',type=Path,default=Path('build-preview'))
    args=p.parse_args()
    render(args.root,args.input_dir,args.output_dir)
