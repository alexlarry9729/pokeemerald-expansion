#!/usr/bin/env python3
"""Cross-check completed city collision, entrance and visual audits.

Checks independently produced diagnostics refer to one valid 20x20 Cuordilava
preview, and exports a release-readiness JSON. Does NOT claim emulator testing.
"""
import argparse
import json
from pathlib import Path
from render_cuordilava_detail_sheet import rgb_png

DOORS={"12,15","5,15","15,5","9,6","16,15","9,2"}
POOL_ZERO=("exterior_turquoise_pixels","exterior_white_foam_pixels",
           "upper_lower_shoulder_turquoise_pixels",
           "upper_lower_shoulder_yellow_pixels")

def check(directory):
    d=Path(directory)
    nav=json.loads((d/"cuordilava-navigation.json").read_text())
    visual=json.loads((d/"cuordilava-accessibility.json").read_text())
    pool=json.loads((d/"cuordilava-thermal-perimeter.json").read_text())
    for k,v in nav.items():
        if visual.get(k)!=v:
            raise ValueError(f"Two generated navigation reports disagree on {k}")
    if nav.get("map_dimensions")!=[20,20] or set(nav.get("entrances",{}))!=DOORS:
        raise ValueError("Original 20x20 layout or six doors changed")
    for key in ("collision_flags_identical_to_committed_original",
                "event_data_identical_to_committed_original",
                "original_six_warps_preserved","thermal_trigger_reachable"):
        if nav.get(key) is not True:
            raise ValueError(f"Original playable map regression: {key}")
    if nav.get("original_street_component_cells",0)<100 or nav.get(
            "original_elevated_spring_component_cells",0)<10:
        raise ValueError("Original street/raised hot-spring connectivity lost")
    if any(door.get("min_approach_steps",-1)<0
           for door in nav["entrances"].values()):
        raise ValueError("Original town door has no reachable approach")
    containment=pool.get("water_containment",{})
    for key in POOL_ZERO:
        if containment.get(key)!=0:
            raise ValueError(f"Thermal pool left-bank visual regression: {key}")
    for mode in ("day","night"):
        for prefix in ("cuordilava-","cuordilava-accessibility-"):
            w,h,_=rgb_png(d/f"{prefix}{mode}.png")
            if (w,h)!=(960,960):
                raise ValueError(f"{mode} real original-map preview is not 960x960")
        for prefix in ("cuordilava-thermal-perimeter-",):
            path=d/f"{prefix}{mode}.png"
            if not path.is_file() or path.stat().st_size<1000:
                raise ValueError("Missing actual annotated spa image: "+str(path))
    return {
        "evidence_passed":True,
        "scope":"Source collision/event data + rendered 960px day/night city",
        "not_an_emulator_playthrough":True,
        "city_dimensions":nav["map_dimensions"],
        "doors_verified":len(DOORS),
        "street_component":nav["original_street_component_cells"],
        "raised_spring_component":nav["original_elevated_spring_component_cells"],
        "left_cliff_water_or_yellow_pixels":{k:containment[k] for k in POOL_ZERO},
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,default=Path("build-preview"))
    args=parser.parse_args()
    result=check(args.input_dir)
    (args.input_dir/"cuordilava-release-evidence.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Cuordilava release evidence: 6 doors, both path components, "
          "dry left spa cliff, complete day/night renders; source-only audit")
