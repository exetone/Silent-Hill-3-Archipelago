"""Read-only equivalent of SH3's map selector at 0x4997b0.
Derived from the supported executable and verified room/stage data.
No native function calls or writes are made to the game process.
"""
from bisect import bisect_right
import math

ROOM_BOUNDS = (0, 1, 11, 20, 29, 42, 46, 53, 62, 71, 87, 99, 106, 110, 118, 126, 130, 136, 142, 148, 149, 155, 156, 157, 158, 159, 166, 172, 181, 186, 190, 197, 200, 209, 216, 232, 240, 241, 253, 266, 267)
STAGE_GROUPS = (0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 6, 6, 7, 7, 7, 7, 8, 9, 10, 11, 12, 13, 14, 14, 14, 14, 15, 16, 16, 16, 17, 17, 17, 18, 19, 19, 20)
MAP_RULES = ((0, 0, 45), (0, 0, 62), (0, 0, 63), (0, 0, 64), (0, 0, 65), (0, 0, 66), (0, 0, 67), (0, 0, 68), (0, 0, 69), (0, 0, 70), (0, 0, 208), (1, 0, 18), (1, 0, 19), (2, 0, 20), (8, 0, 49), (8, 0, 54), (9, 0, 50), (9, 0, 51), (10, 0, 52), (10, 0, 53), (10, 0, 55), (10, 0, 56), (23, 0, 183), (26, 0, 253), (1, 1, 0), (2, 2, 0), (4, 3, 0), (5, 4, 0), (6, 5, 0), (7, 6, 0), (11, 7, 0), (12, 9, 0), (13, 10, 0), (14, 12, 0), (15, 13, 0), (16, 14, 0), (17, 15, 0), (17, 16, 0), (18, 17, 0), (19, 18, 0), (21, 22, 0), (21, 23, 0), (21, 24, 0), (22, 25, 0), (23, 26, 0), (23, 27, 0), (22, 28, 0), (24, 30, 0), (25, 31, 0), (25, 32, 0), (26, 36, 0), (26, 37, 0), (27, 38, 0))

MAP_PAGES = {
 1: ('Mall','1F'), 2: ('Mall','2F'), 3: ('OW Mall','3F'),
 4: ('OW Mall','1F'), 5: ('OW Mall','2F'), 6: ('OW Mall','3F'),
 7: ('Subway','B1'), 8: ('Subway','B2'), 9: ('Subway','B3'),
 10: ('Subway','B4'), 11: ('Subway','B5'),
 12: ('Underpass','Underpass'), 13: ('Underpass','Sewers'),
 14: ('Hilltop','1F / 2F'), 15: ('Hilltop','3F / 4F'), 16: ('Hilltop','5F / 6F'),
 17: ('OW Hilltop','1F / 2F'), 18: ('OW Hilltop','3F / 4F'), 19: ('OW Hilltop','5F / 6F'),
 20: ('Silent Hill','Map'), 21: ('Silent Hill','Map'),
 22: ('Hospital','1F / BF'), 23: ('Hospital','2F / 3F / RF'),
 24: ('OW Hospital','1F / B3'), 25: ('OW Hospital','2F / 3F / RF'),
 26: ('Chapel','1F'), 27: ('Chapel','BF'),
}

def room_stage(room):
    if not 0 < room < ROOM_BOUNDS[-1]: return None
    return bisect_right(ROOM_BOUNDS, room)-1

def coherent_room(stage, room):
    rs = room_stage(room)
    return rs is not None and 0 < stage < len(STAGE_GROUPS) and STAGE_GROUPS[rs] == STAGE_GROUPS[stage]

def native_map(stage, room, position, flags):
    """Mirror native precedence, height boundaries and elevator bits exactly."""
    x,y,z = position
    if not all(math.isfinite(v) for v in position): return None
    f90,fa4,fb4 = flags
    result = next((m for m,s,r in MAP_RULES if s == stage or r == room), 0)
    if room == 9 and y < -1209.0: result = 2
    elif room == 14 and y > -2790.0: result = 1
    elif room == 34 and y < -5000.0: result = 6
    elif room == 118:
        floor = 6
        for i,h in enumerate((-1255.0,-3655.0,-6056.0,-8458.0,-10855.0), 1):
            if y > h+2 or (y > h-2 and x < -20000.0):
                floor = i
                break
        result = 14 if floor <= 2 else 15 if floor <= 4 else 16
    elif room == 137: result = 19 if y < -1200.0 else 18
    elif room == 147: result = 17 if f90 & 0xc0 else 18 if f90 & 0x100 else 19
    elif room == 184:
        floor = 4
        for i,h in enumerate((-1000.0,-3000.0,-5000.0), 1):
            if y > h+2 or (y > h-2 and z > -100000.0):
                floor = i
                break
        result = 22 if floor == 1 else 23
    elif room == 185: result = 22 if fa4 & 0x100 else 23
    elif room == 206: result = 0 if fb4 & 0x10000000 else 24 if fb4 & 0x20000000 else 25
    elif room == 254: result = 26 if y < -2750.0 else 27
    return result

def page_for_location(stage, room, position, flags):
    if not coherent_room(stage, room): return None
    map_id = native_map(stage, room, position, flags)
    if map_id is None: return None
    # Room 196 is the verified C4 destination. The OW Hospital stage group
    # contains both floors, so a coherent-but-stale 31/32 selector used to win.
    if room == 196 and stage in (30, 31, 32):
        map_id = 24
    page = MAP_PAGES.get(map_id)
    # These custom pack pages cover areas without an in-game map.
    if page is None:
        if stage in (33,34,35): page = ('Amusement Park','Map')
        elif stage == 11: page = ('Hilltop','3F / 4F')  # Construction Site
        elif stage in (19,20): page = ('Hilltop','1F / 2F')  # Outside Hilltop / Daisy Villa Apartments
        elif stage in (21,22,23,24): page = ('Silent Hill','Map')
    return (map_id, page)
