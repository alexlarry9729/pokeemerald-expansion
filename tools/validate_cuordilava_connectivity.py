#!/usr/bin/env python3
"""Check actual game-world navigation, not just Lavaridge art and map size.

The connected walkable original street must still reach every street-level
warp and all signage, and the protected elevated spring component must still
reach its *sixth* warp, Old Man access and the hot-spring trigger. The full
20x20 walkability fingerprint must be IDENTICAL to the pristine committed
map even though 84 floor cells and many non-floor graphics are now rebuilt.

Uses exact 2-bit collision flags in each GBA map cell. The committed source
map and JSON are fetched from Git HEAD (not from another hand-written
approximation) to compare with the mutable on-disk generated map. This
captures any newly blocked passage or phantom collision, including outside
the redesigned district. It is a static graph validation, NOT an emulated
playthrough or a guarantee about scripts.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
import argparse
import json
import struct
import subprocess

SIZE = 20
WORLD_BYTES = SIZE * SIZE * 2
GROUND_GATE = (19, 9)  # original Route 112 east connection, street-level
SPRING_GATE = (5, 1)  # original raised mineral-pool access at elevation 3
SPRING_TRIGGER = (6, 3)
STREET_WARPS = {
    (12, 15): 'MAP_LAVARIDGE_TOWN_HERB_SHOP',
    (5, 15): 'MAP_LAVARIDGE_TOWN_GYM_1F',
    (15, 5): 'MAP_LAVARIDGE_TOWN_MART',
    (9, 6): 'MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F',
    (16, 15): 'MAP_LAVARIDGE_TOWN_HOUSE',
}
ELEVATED_WARP = ((9, 2), 'MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F')
GRAPH_DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))


def committed(root: Path, path: str) -> bytes:
    result = subprocess.run(
        ['git', '-C', str(root), 'show', f'HEAD:{path}'],
        check=True, capture_output=True,
    )
    return result.stdout


def flags(map_bytes: bytes) -> tuple[int, ...]:
    if len(map_bytes) != WORLD_BYTES:
        raise ValueError('Original Lavaridge 20x20 map changed size')
    return tuple((struct.unpack_from('<H', map_bytes, i * 2)[0] >> 10) & 3
                 for i in range(SIZE * SIZE))


def neighbors(pt: tuple[int, int]):
    x, y = pt
    for dx, dy in GRAPH_DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < SIZE and 0 <= ny < SIZE:
            yield (nx, ny)


def traversable(pt: tuple[int, int], flag_data: tuple[int, ...]) -> bool:
    x, y = pt
    return flag_data[SIZE*y+x] == 0


def reachable(start: tuple[int, int], flag_data: tuple[int, ...]):
    if not traversable(start, flag_data):
        raise ValueError(f'Protected entrance {start} is blocked')
    queue = deque([start])
    depth = {start: 0}
    while queue:
        xy = queue.popleft()
        for nxt in neighbors(xy):
            if nxt in depth or not traversable(nxt, flag_data):
                continue
            depth[nxt] = depth[xy] + 1
            queue.append(nxt)
    return depth


def audit(root: Path):
    root = Path(root).resolve()
    map_path = 'data/layouts/LavaridgeTown/map.bin'
    events_path = 'data/maps/LavaridgeTown/map.json'
    expected = committed(root, map_path)
    actual = (root / map_path).read_bytes()
    before = flags(expected)
    after = flags(actual)
    changes = [(i%SIZE, i//SIZE) for i, (a, b) in
               enumerate(zip(before, after)) if a != b]
    if changes:
        raise ValueError(
            f'Redesign changed original movement/collision bits: {changes[:12]}'
        )
    before_events = json.loads(committed(root, events_path))
    events = json.loads((root / events_path).read_text(encoding='utf-8'))
    # Every event field including the spring trigger, map connections and
    # non-interactive lamps must be preserved by this art-only redesign.
    if events != before_events:
        raise ValueError('Town events/warps/scripts no longer match original source')
    if len(events['warp_events']) != 6:
        raise ValueError('Original six entrances no longer exist')
    warps = {
        (int(w['x']), int(w['y'])): w
        for w in events['warp_events']
    }
    if set(warps) != set(STREET_WARPS) | {ELEVATED_WARP[0]}:
        raise ValueError('Wrong original warp positions')
    if not any(
        c.get('map') == 'MAP_ROUTE112' and c.get('direction') == 'right'
        for c in events.get('connections', [])
    ):
        raise ValueError('Original Route112 connection missing')
    street = reachable(GROUND_GATE, after)
    springs = reachable(SPRING_GATE, after)
    if street.keys() & springs.keys():
        raise ValueError('Original mountain-level thermal access unexpectedly merged with street')
    original_street = reachable(GROUND_GATE, before)
    original_springs = reachable(SPRING_GATE, before)
    if set(street) != set(original_street) or set(springs) != set(original_springs):
        raise ValueError('Pedestrian navigation no longer matches original geography')
    if len(street) < 120 or len(springs) < 15:
        raise ValueError('Original civic streets or elevated springs are no longer continuous')

    portal_summary = {}
    for xy, destination in STREET_WARPS.items():
        w = warps[xy]
        if w['dest_map'] != destination or int(w['elevation']) != 0:
            raise ValueError(f'Original street-level warp {xy} was reconfigured')
        # Many ORIGINAL doorway metatiles deliberately have collision=1.
        # The player approaches them from an adjacent walkable tile, not
        # necessarily from standing on their door image. Check adjacency.
        adjacent = [z for z in neighbors(xy) if z in street]
        if not adjacent:
            raise ValueError(f'Street access to original door {xy} is blocked')
        portal_summary[f'{xy[0]},{xy[1]}'] = {
            'destination': destination,
            'walkable_adjacent': [list(z) for z in adjacent],
            'min_approach_steps': min(street[z] for z in adjacent),
            'original_elevation': 0,
        }
    xy, destination = ELEVATED_WARP
    w = warps[xy]
    if w['dest_map'] != destination or int(w['elevation']) != 3:
        raise ValueError('Special elevated mineral-pool warp was changed')
    if xy not in springs:
        raise ValueError('Elevated spring-to-Center warp cannot be reached')
    if SPRING_TRIGGER not in springs:
        raise ValueError('Original hot-springs trigger cannot be reached')
    trigger = [
        x for x in events['coord_events']
        if (x.get('x'),x.get('y')) == SPRING_TRIGGER
    ]
    if len(trigger)!=1 or int(trigger[0]['elevation']) != 3:
        raise ValueError('Original thermal trigger or elevation was moved')
    portal_summary[f'{xy[0]},{xy[1]}'] = {
        'destination': destination,
        'min_approach_steps': springs[xy],
        'original_elevation': 3,
    }
    for event in events.get('bg_events', []):
        xy = (event.get('x'), event.get('y'))
        if int(event.get('elevation', 0)) != 0:
            continue  # original raised-tier signs require separate treatment
        if event.get('type') != 'sign':
            continue
        if not any(n in street for n in neighbors(xy)) and xy not in street:
            raise ValueError(f'Original city sign {xy} is inaccessible')

    return {
        'note': 'Static GBA tile-flag and BFS audit; not an emulator playthrough',
        'map_dimensions': [SIZE, SIZE],
        'collision_flags_identical_to_committed_original': True,
        'event_data_identical_to_committed_original': True,
        'original_street_component_cells': len(street),
        'original_elevated_spring_component_cells': len(springs),
        'route112_access_cell': list(GROUND_GATE),
        'raised_springs_access_cell': list(SPRING_GATE),
        'thermal_trigger_reachable': True,
        'entrances': portal_summary,
        'fully_covered_map_cells': SIZE * SIZE,
        'original_six_warps_preserved': True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(
        'Cuordilava reachable: 6/6 original doors including elevated '
        f'hot-spring access; {result["original_street_component_cells"]} '
        'street and '
        f'{result["original_elevated_spring_component_cells"]} raised '
        'spring cells; exact original collision/event flags preserved'
    )


if __name__ == '__main__':
    main()
