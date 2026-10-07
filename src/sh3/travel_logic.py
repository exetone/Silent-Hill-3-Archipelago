"""Directional save-entry logic shared by generation and the native tracker.

The graph records verified directional travel. Missing reverse edges are intentional. Local pickup requirements are stored by stable check ID
in travel_routes.json, independently of display names and entry route.
"""
from functools import lru_cache
from importlib import resources
import json
from .data import (FAST_TRAVEL_MENU_LOCATIONS, ACTIVE_FAST_TRAVEL_ROWS,
                   ITEM_PROGRESSIVE_FAST_TRAVEL, BOSS_WEAPONS,
                   BOSS_WEAPON_COMBINATIONS, BOSS_EVENT_ITEMS, CHECK_CATALOGUE,
                   SILENCER_WEAPONS, LOCATION_NAME_TO_ID)

LOGIC_VERSION = 3
# Enable only with a verified fix for the reported train-interior return load.
PLATFORM_RETURN_VERIFIED = False
DESTINATIONS = (
    'mall', 'mall', 'mall_exit', 'ow_mall', 'ow_upper', 'ow_moths',
    'subway', 'train', 'platform_entry', 'underpass', 'sewer', 'construction',
    'office', 'office_lower', 'ow_office', 'ow_office', 'apartments', 'town',
    'hospital_lobby', 'hospital_store', 'ow_hospital', 'ow_hospital', 'ow_c4',
    'park', 'park_after_coaster', 'park_fortune', 'church_entry', 'church_entry', 'church')
COMBAT = 'A boss weapon or Heather Beam + Transform Costume'
PRE_LEONARD = 'Before Leonard closes the 1F stairs and elevator'
LEONARD = BOSS_EVENT_ITEMS['Leonard']
BOOKS = tuple(f'Shakespeare Anthology {i}' for i in range(1, 6))
VISIT_EVENT_ITEMS = {row: 'Visited save: ' + FAST_TRAVEL_MENU_LOCATIONS[row]
                     for row in ACTIVE_FAST_TRAVEL_ROWS}
EDGES = (
    ('mall', 'mall_elevator', ('Key Taken with Tongs', *BOOKS)),
    ('mall_elevator', 'ow_mall', ()),
    ('ow_mall', 'ow_upper', ('Hanger',)),
    ('ow_upper', 'ow_mall', ()),
    ('ow_upper', 'ow_east', ('Cooked Key',)),
    ('ow_east', 'ow_moths', ('Bleach', 'Detergent')),
    # Exhaustive Sports Shop return: Cafe, Bakery and 2F Supply Room only.
    ('ow_moths', 'ow_east', ()),
    ('ow_upper', 'ow_boss', ('Moonstone',)),
    ('ow_moths', 'ow_boss', ('Moonstone',)),
    ('ow_boss', 'mall_exit', (COMBAT,)),
    ('mall_exit', 'subway', ()),
    ('subway', 'train', ('Nutcracker',)),
    ('train', 'platform_entry', ()),
    ('platform_entry', 'underpass', ()),
    # Intended return is enabled only when the loading defect has been repaired.
    *((('underpass', 'platform_entry', ()),) if PLATFORM_RETURN_VERIFIED else ()),
    ('underpass', 'sewer', ('Oil-Filled Bottle',)),
    ('sewer', 'underpass', ()),
    ('sewer', 'construction', ('Dryer',)),
    ('construction', 'office', ()),
    ('office', 'office_lower', ('Rope', 'Jack')),
    ('office_lower', 'ow_office', ()),
    ('ow_office', 'ow_imports', ('Oxydol', 'Pork Liver', 'Matchbook')),
    ('ow_imports', 'ow_office', ()),
    ('ow_office', 'apartments', ('Life Insurance Key',)),
    ('apartments', 'apartment_after', ('House Key', COMBAT, BOSS_EVENT_ITEMS['Missionary'])),
    ('apartment_after', 'town', ()),
    ('town', 'town_checks', ()),
    ('town', 'hospital_lobby', ()),
    ('hospital_lobby', 'town', ()),
    ('hospital_lobby', 'hospital_lobby_checks', ()),
    # The sole normal-lobby route to the rest of Hospital is permanently closed
    # after Leonard. A Store Room unlock is a separate upper-floor entry.
    ('hospital_lobby', 'hospital_pre', (PRE_LEONARD,)),
    ('hospital_pre', 'hospital_lobby', ()),
    ('hospital_pre', 'hospital_upper', ('Stairwell Key',)),
    ('hospital_upper', 'hospital_store', ()),
    ('hospital_store', 'hospital_upper', ('Flashlight',)),
    ('hospital_upper', 'hospital_pre', ('Flashlight',)),
    ('hospital_upper', 'hospital_patient', ('Flashlight', 'Stairwell Key', 'Instant Camera')),
    ('hospital_patient', 'hospital_upper', ()),
    ('hospital_patient', 'ow_hospital', ()),
    ('ow_hospital', 'ow_patient', ('Cremated Key',)),
    ('ow_patient', 'ow_hospital', ()),
    ('ow_patient', 'ow_c4', ()),
    # C4 has no reverse edge. The normal-Hospital return is a different lobby.
    ('ow_c4', 'hospital_after', ('Plastic Bag (With Blood)', COMBAT, LEONARD)),
    ('hospital_after', 'hospital_lobby_checks', ()),
    ('hospital_after', 'town_checks', ()),
    ('hospital_after', 'park', ()),
    ('park', 'park_after_coaster', ('Roller Coaster Key',)),
    ('park_after_coaster', 'park_theatre', ()),
    ('park_theatre', 'park_fortune', ('Chain',)),
    ('park_fortune', 'park_carousel', ('Red Shoe', 'Doll Head')),
    ('park_carousel', 'church_entry', (COMBAT,)),
    # Belfry and Chapel share the early entry. Alessa's Room has access only to
    # BF and Library, not to the other earlier Chapel 1F checks.
    ('church_entry', 'church', ()),
)

ROUTES = json.loads(resources.files(__package__).joinpath('travel_routes.json')
                    .read_text(encoding='utf-8'))['checks']
FLASHLIGHT_CHECKS = frozenset(row['name'] for row in CHECK_CATALOGUE
                             if 'Flashlight' in row.get('requirements', ''))

def combat(owned):
    return (any(n in owned for n in BOSS_WEAPONS)
            or any(all(n in owned for n in pair) for pair in BOSS_WEAPON_COMBINATIONS))

def satisfied(requirement, owned):
    if requirement == COMBAT:
        return combat(owned)
    if requirement == 'Wall-breaking weapon':
        return any(n in owned for n in SILENCER_WEAPONS)
    if requirement == PRE_LEONARD:
        return LEONARD not in owned
    return requirement in owned

def target(name):
    try:
        row = ROUTES[str(LOCATION_NAME_TO_ID[name])]
    except KeyError as exc:
        raise ValueError('No verified travel route for ' + name) from exc
    return row['region'], tuple(row['requires'])

def starting_roots(starting_row=None):
    """None means the actual default Mall start, never an extra random-start root."""
    row = 0 if starting_row is None else starting_row
    if isinstance(row, bool) or row not in ACTIVE_FAST_TRAVEL_ROWS:
        raise ValueError('Invalid starting save row')
    return (DESTINATIONS[row],)

@lru_cache(maxsize=8192)
def reachable(owned, roots=('mall',)):
    reached = set(roots)
    reached.update(DESTINATIONS[row] for row in ACTIVE_FAST_TRAVEL_ROWS
                   if FAST_TRAVEL_MENU_LOCATIONS[row] in owned)
    reached.add('start')
    while True:
        before = len(reached)
        for source, dest, requirements in EDGES:
            if source in reached and all(satisfied(r, owned) for r in requirements):
                reached.add(dest)
        if len(reached) == before:
            return frozenset(reached)

def reachable_from_save(row, owned=(), *, include_other_unlocks=False):
    items = frozenset(owned)
    if not include_other_unlocks:
        items -= frozenset(FAST_TRAVEL_MENU_LOCATIONS)
    return reachable(items, starting_roots(row))

def can_access(name, owned, roots=('mall',)):
    region, requirements = target(name)
    return (region in reachable(frozenset(owned), tuple(roots))
            and all(satisfied(r, owned) for r in requirements))

def missing(name, owned, roots=('mall',)):
    region, requirements = target(name)
    if region not in reachable(frozenset(owned), tuple(roots)):
        return None
    return [r for r in requirements if not satisfied(r, owned)]

# Room IDs at each destination were evaluated using the supplied EXE geometry;
# these are not guessed floor/area identifiers. See floor_follow_152/travel_cases.json.
SAVE_ROOMS = (3,12,18,22,29,41,54,62,71,85,93,99,116,109,134,146,149,
              156,160,176,192,201,196,212,217,229,240,250,262)
ROOM_ROOTS = {room: DESTINATIONS[row] for row, room in enumerate(SAVE_ROOMS)}
MANAGER_ROOTS = {
    0x7102f8:'mall', 0x70cf20:'ow_mall',
    0x70b260:'subway', 0x70a0bc:'subway', 0x708a98:'train',
    0x707c98:'underpass', 0x706478:'sewer', 0x704b2c:'construction',
    0x7035e0:'office_lower', 0x702a5c:'office', 0x7016c8:'office',
    0x700600:'ow_office', 0x6ff154:'ow_office', 0x6fe5f0:'ow_office',
    0x6fd914:'ow_office', 0x6fc784:'apartments',
    0x6fb378:'town', 0x6faa38:'town',
    0x6fa7c0:'hospital_lobby', 0x6f97d8:'hospital_pre',
    0x6f8834:'hospital_upper', 0x6f7804:'hospital_upper',
    0x6f3694:'ow_hospital', 0x6f2974:'ow_hospital',
    0x6eee40:'park', 0x6e1134:'church_entry', 0x6df100:'church',
}

def tracker_roots(manager, owned, world_flags=b'', room=None, stage=None):
    # A room override is accepted only for a coherent room/stage pair; a stale
    # pointer during loading must not promote another area's complete graph.
    if room is not None and stage is not None:
        from .poptracker_floor import coherent_room
        if coherent_room(stage, room) and room in ROOM_ROOTS:
            return (ROOM_ROOTS[room],)
    if manager == 0x70ed88:
        boss_transition = len(world_flags) > 206//8 and world_flags[206//8] & (1 << (206%8))
        return ('mall_exit',) if boss_transition else ('mall',)
    # Ambiguous shared stages (Sports Shop, C4, Fortuneteller, late Chapel 1F)
    # deliberately have no broad fallback. Actual save unlocks remain roots.
    root = MANAGER_ROOTS.get(manager)
    return (root,) if root else ()

RELEVANT_ITEMS = (frozenset(FAST_TRAVEL_MENU_LOCATIONS)
    | frozenset(r for _, _, req in EDGES for r in req if r not in (COMBAT, PRE_LEONARD))
    | frozenset(r for row in ROUTES.values() for r in row['requires']
                if r not in (COMBAT, PRE_LEONARD, 'Wall-breaking weapon'))
    | frozenset(BOSS_WEAPONS) | frozenset(n for pair in BOSS_WEAPON_COMBINATIONS for n in pair)
    | frozenset(SILENCER_WEAPONS) | frozenset(BOSS_EVENT_ITEMS.values()))

def state_owned(state, player):
    owned = {n for n in RELEVANT_ITEMS if state.has(n, player)}
    for row, event in VISIT_EVENT_ITEMS.items():
        if state.has(event, player):
            owned.add(FAST_TRAVEL_MENU_LOCATIONS[row])
    # Retain receipt/ID compatibility for older generated data.
    for index, row in enumerate(ACTIVE_FAST_TRAVEL_ROWS, 1):
        if state.has(ITEM_PROGRESSIVE_FAST_TRAVEL, player, index):
            owned.add(FAST_TRAVEL_MENU_LOCATIONS[row])
    return owned

def save_events_settled(state, player, roots):
    """Sweep available visit-unlock events before applying the permanent barrier.

    Visiting a save already unlocks it in the game; these addressless events do
    not grant its shuffled reward or complete a network check. This ordering
    prevents AP's event iteration order from throwing away a reachable return
    save when the Leonard event is swept in the same logical sphere.
    """
    owned = state_owned(state, player)
    return all(state.has(VISIT_EVENT_ITEMS[row], player)
               or not can_access(FAST_TRAVEL_MENU_LOCATIONS[row], owned, roots)
               for row in ACTIVE_FAST_TRAVEL_ROWS)
