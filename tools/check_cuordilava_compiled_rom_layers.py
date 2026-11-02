#!/usr/bin/env python3
"""Assert the COMPILED Pokemon Emerald ROM embeds the covered-BG2 town layers.

A source-side test could pass even if the ROM accidentally bundled old generated
assets. This gate confirms the actual 1024-byte secondary Cuordilava metatile
attributes table in the compiled GBA binary matches the generated assets and
that EVERY new walkable graphic passes the GBA layer-type audit. A successful
check is not a substitute for player-controlled movement in the emulator.
"""
import argparse
from pathlib import Path
import hashlib
import json
from validate_cuordilava_sprite_layers import audit

def check(root,rom):
    root=Path(root)
    rom=Path(rom)
    source=(root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin").read_bytes()
    content=rom.read_bytes()
    if len(content)<16*1024*1024 or len(source)!=1024:
        raise ValueError("Unexpected ROM size or original 512-metatile attribute count")
    offsets=[]
    begin=0
    while True:
        i=content.find(source,begin)
        if i<0:
            break
        offsets.append(i)
        begin=i+1
    if len(offsets)!=1:
        raise ValueError(
            f"Compiled ROM does not contain exactly one correct Cuordilava "
            f"attribute table (matches={len(offsets)}); refuse stale game download"
        )
    layers=audit(root)
    if layers.get("number_of_affected_map_cells")!=120:
        raise ValueError("Player layering guard lost one of 120 repaired walkable cells")
    return {
      "rom_sha256":hashlib.sha256(content).hexdigest(),
      "actual_compiled_rom_checked":True,
      "rom_attribute_table_offset":offsets[0],
      "compiled_attribute_bytes_identical_to_generated_source":True,
      "walkable_cuordilava_cells_with_bg2_player_visibility":120,
      "static_layer_test_not_an_ingame_walkthrough":True,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--rom",type=Path,default=Path("pokeemerald.gba"))
    p.add_argument("--output",type=Path,default=Path("cuordilava-rom-layer-audit.json"))
    args=p.parse_args()
    report=check(args.root,args.rom)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
