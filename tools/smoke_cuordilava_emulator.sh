#!/usr/bin/env bash
# Real GBA emulator boot smoke test. This is NOT a Cuordilava walkthrough.
set -euo pipefail
if [[ "${1:-}" != "--inside-xvfb" ]]; then
    rom="$(realpath "${1:-pokeemerald.gba}")"
    out="$(realpath -m "${2:-build-emulator}")"
    mkdir -p "$out"
    exec xvfb-run -a -s "-screen 0 1024x768x24" bash "$0" --inside-xvfb "$rom" "$out"
fi
rom="$2"
out="$3"
export SDL_VIDEODRIVER=x11
export SDL_AUDIODRIVER=dummy
export SDL_RENDER_DRIVER=software
export LIBGL_ALWAYS_SOFTWARE=1
mkdir -p "$out"
test -s "$rom"

mgba -3 "$rom" >"$out/mgba.log" 2>&1 &
pid=$!
cleanup() {
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
}
trap cleanup EXIT

# mGBA SDL creates an X11 window. Require that it is actually live.
wid=""
for _ in $(seq 1 40); do
    if ! kill -0 "$pid" 2>/dev/null; then
        cat "$out/mgba.log"
        echo "mGBA exited before opening its game window" >&2
        exit 1
    fi
    wid="$(xdotool search --onlyvisible --pid "$pid" 2>/dev/null | head -n 1 || true)"
    if [[ -z "$wid" ]]; then
        wid="$(xdotool search --onlyvisible --name 'mGBA' 2>/dev/null | head -n 1 || true)"
    fi
    [[ -n "$wid" ]] && break
    sleep 0.5
done
if [[ -z "$wid" ]]; then
    echo "mGBA did not create a visible SDL game window" >&2
    cat "$out/mgba.log"
    exit 1
fi

xdotool windowactivate --sync "$wid"
# Allow the real emulated Game Boy Advance BIOS/title sequence to render.
sleep 13
kill -0 "$pid"
import -silent -window "$wid" "$out/emulator-boot.png"

# Start is the default Enter mapping of the real SDL mGBA frontend. This
# enters its title/menu flow without modifying memory, saves or ROM bytes.
xdotool windowactivate --sync "$wid"
xdotool key --clearmodifiers Return
sleep 6
kill -0 "$pid"
import -silent -window "$wid" "$out/emulator-after-start.png"

# Verify actual mGBA window pixels, not a static renderer/mock screenshot.
python3 - "$out" <<'PY'
from PIL import Image, ImageStat
from pathlib import Path
import json,sys
out=Path(sys.argv[1])
details={}
for stem in ('emulator-boot','emulator-after-start'):
    image=Image.open(out/(stem+'.png')).convert('RGB')
    w,h=image.size
    if w<240 or h<160:
        raise SystemExit(f'{stem}: too small for a real GBA framebuffer: {w}x{h}')
    reduced=image.resize((120,80))
    colors=reduced.getcolors(maxcolors=120*80)
    unique=len(colors) if colors else 120*80
    std=ImageStat.Stat(reduced).stddev
    vivid=sum(1 for r,g,b in reduced.getdata() if max(r,g,b)>35 and max(r,g,b)-min(r,g,b)>15)
    colored_pct=round(100*vivid/(120*80),2)
    details[stem]={'width':w,'height':h,'distinct_rgb_colors':unique,
                   'rgb_stddev':[round(x,2) for x in std],
                   'colored_pixel_percent':colored_pct}
    if unique<12 or max(std)<15 or colored_pct<1:
        raise SystemExit(f'{stem}: emulated display blank or stuck: {details[stem]}')
result={
    'emulator':'mGBA SDL',
    'source':'Actual ROM built for this commit in GitHub Actions',
    'real_emulator_boot_screenshots':True,
    'boot_and_start_screenshots':details,
    'does_not_prove_ingame_lavaridge_navigation':True,
    'does_not_prove_six_warp_gameplay':True,
    'human_emulator_walkthrough_still_required':True,
}
(out/'emulator-smoke-report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
PY
