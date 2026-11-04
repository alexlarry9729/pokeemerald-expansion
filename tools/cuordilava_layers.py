"""GBA metatile layer rules for the Cuordilava town-only redesign.

The player's default elevation is 3. The Emerald renderer puts the TOP
quadrants of METATILE_LAYER_TYPE_NORMAL (0) on BG1 (in front of the sprite).
Walking on newly inked paving, flowerbeds or plaza must instead draw the
visual overlay on BG2, behind the player, by using COVERED (1).
See src/field_camera.c:DrawMetatile and include/global.fieldmap.h.

Do not confuse 0x1000 METATILE ATTRIBUTE layer with the 0xF000
MAP BLOCK elevation: they are stored in two DIFFERENT binaries.
"""
NORMAL_LAYER = 0
COVERED_LAYER = 1
SPLIT_LAYER = 2
ATTR_LAYER_MASK = 0xF000
ATTR_GAMEPLAY_MASK = 0x0FFF


def player_above_walkable_art(original: int) -> int:
    """Keep behavior and all lower attribute bits; move overlay BG1 -> BG2."""
    if not 0 <= original <= 0xFFFF:
        raise ValueError("Not a packed Emerald metatile attribute")
    layer = original >> 12
    if layer not in (NORMAL_LAYER, COVERED_LAYER):
        raise ValueError(f"Unexpected GBA source layer {layer}; refuse unsafe change")
    return (original & ATTR_GAMEPLAY_MASK) | (COVERED_LAYER << 12)


def validate_covered(original: int, corrected: int, where: str) -> None:
    expected = player_above_walkable_art(original)
    if corrected != expected:
        raise ValueError(
            f"{where}: walkable 4bpp decoration will cover the player; "
            f"expected attribute {expected:#06x}, got {corrected:#06x}"
        )
