"""Editable tracker catalogue and conservative check reachability.

No item placement or completion is inferred from a reward icon. Only implemented checks are shown; only the connected server's location set
is counted.
"""
from __future__ import annotations
import hashlib,json,struct,unicodedata
from .travel_logic import can_access as travel_access, missing as travel_missing, FLASHLIGHT_CHECKS, tracker_roots
from importlib import resources
from .data import (ITEM_NAME_TO_ID, ITEM_ID_TO_RAW, BOSS_WEAPONS, MAP_RAW_TO_FLAG,
                   SUPPORTED_BOSS_LOCATIONS, active_locations, BOSS_GOAL_LOCATION_IDS,
                   ACTIVE_FAST_TRAVEL_ROWS, FAST_TRAVEL_MENU_LOCATIONS, ITEM_PROGRESSIVE_FAST_TRAVEL,
                   SAVE_ID_TO_LOCATION_ID, SAVE_ID_TO_MENU_ROW, BUNDLED_ITEMS, BOSS_EVENT_ITEMS)

ROOT=resources.files(__package__).joinpath('tracker')
CATALOGUE=json.loads(ROOT.joinpath('catalogue.json').read_text(encoding='utf-8'))
ITEMS=json.loads(ROOT.joinpath('items.json').read_text(encoding='utf-8'))
SCHEMA_HASH=hashlib.sha256((json.dumps(CATALOGUE,sort_keys=True)+json.dumps(ITEMS,sort_keys=True)).encode()).digest()[:16]
CHECKS=CATALOGUE['checks']; ICONS=ITEMS['items']; AREA_MANAGERS={int(k,0):v for k,v in json.loads(ROOT.joinpath('areas.json').read_text(encoding='utf-8'))['manager_to_area'].items()}
SIGNATURE=b'SHAP_TRACKER_V1\0'; NATIVE_RVA=0x30000
PENDING,COLLECTED,READY,BLOCKED,UNVERIFIED,DISABLED,SENT=range(7)
ID_TO_NAME={v:k for k,v in ITEM_NAME_TO_ID.items()}

def evaluate(name,owned,roots=()):
    # No legacy OR fallback: tracker and generator share all route/local gates.
    if name in FLASHLIGHT_CHECKS and 'Flashlight' not in owned:
        return ['Flashlight'],True
    if travel_access(name,owned,roots):return [],True
    local=travel_missing(name,owned,roots)
    if local is not None:return local,True
    return ['a reachable route or Fast Travel unlock'],True


def read_inventory(inventory: bytes,world_flags:bytes):
    """Valid raw IDs only; bytes after owned flags contain quantities."""
    held=set();quantities={}
    if len(inventory)<0x100:return held,quantities
    for item in ICONS:
        raw=item['raw']
        if 0<raw<108 and inventory[raw//8]&(1<<(raw%8)):held.add(raw)
        elif raw in MAP_RAW_TO_FLAG:
            flag=MAP_RAW_TO_FLAG[raw]
            if len(world_flags)>flag//8 and world_flags[flag//8]&(1<<(flag%8)):held.add(raw)
        if 9<=raw<=21:quantities[raw]=struct.unpack_from('<H',inventory,14+raw*2)[0]
    return held,quantities


def wire_text(s,length=88):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore')[:length-1]
    return s+b'\0'*(length-len(s))


def disabled_items(slot_data):
    options = {
        'include_unlimited_submachine_gun': 'Unlimited Submachine Gun',
        'include_beam_saber': 'Beam Saber',
        'include_flamethrower': 'Flamethrower',
        'include_gold_pipe': 'Gold Pipe',
        'include_silver_pipe': 'Silver Pipe',
        'include_heather_beam': 'Heather Beam',
    }
    excluded={name for key,name in options.items() if key in slot_data and slot_data[key] in (False,0)}
    if 'add_costumes_to_item_pool' in slot_data and slot_data['add_costumes_to_item_pool'] in (False,0):
        excluded.update(item['name'] for item in ICONS if item['category']==3)
    return excluded


def snapshot(*,cookie:bytes,connected:bool,world:bool,manager:int,active_ids:set[int],checked:set[int],sent:set[int],received:list[int],applied_count:int,held:set[int],quantities:dict[int,int],ever:set[int],disabled:set[str]=frozenset(),visited:set[int]=frozenset(),world_flags:bytes=b'',room:int|None=None,stage:int|None=None):
    if len(cookie)!=16:raise ValueError('Tracker cookie must be 16 bytes')
    owned={ID_TO_NAME[i] for i in received[:applied_count] if i in ID_TO_NAME}
    for bundle, members in BUNDLED_ITEMS.items():
        if bundle in owned:owned.update(members)
    owned.update(item['name'] for item in ICONS if item['raw'] in held|ever)
    owned.update(FAST_TRAVEL_MENU_LOCATIONS[SAVE_ID_TO_MENU_ROW[native]]
                 for native, location in SAVE_ID_TO_LOCATION_ID.items() if location in visited)
    progressive=sum(ID_TO_NAME.get(i)==ITEM_PROGRESSIVE_FAST_TRAVEL for i in received[:applied_count])
    owned.update(FAST_TRAVEL_MENU_LOCATIONS[row] for row in ACTIVE_FAST_TRAVEL_ROWS[:progressive])
    roots=tracker_roots(manager,owned,world_flags,room=room,stage=stage)
    for boss in SUPPORTED_BOSS_LOCATIONS:
        if BOSS_GOAL_LOCATION_IDS[boss] in (visited | checked | sent):
            owned.add(BOSS_EVENT_ITEMS[boss])
    # Native Leonard completion is flag 657 in the verified scripted catalogue.
    # It stays authoritative for the physical stair/elevator closure even when
    # loading an already-progressed save before its check has been reported.
    if len(world_flags) > 657//8 and world_flags[657//8] & (1 << (657%8)):
        owned.add(BOSS_EVENT_ITEMS['Leonard'])
    done=len(checked&active_ids)
    data=bytearray(struct.pack('<5I16s',int(connected),AREA_MANAGERS.get(manager,0xffffffff),int(world),done,len(active_ids),cookie))
    for entry in CHECKS:
        loc=entry['id'];active=bool(loc and loc in active_ids)
        if not entry['implemented']:state=DISABLED;detail='Excluded from AP checks.' if loc else 'Starting inventory; not a separate AP check.'
        elif not connected:state=PENDING;detail='Connect to AP to see check status.'
        elif not active:state=DISABLED;detail='This location is not active in this seed.'
        elif loc in checked:state=COLLECTED;detail='Archipelago confirmed this location for this seed.'
        elif loc in sent:state=SENT;detail='Live check reported; waiting for server confirmation.'
        elif not world:state=UNVERIFIED;detail='Not yet possible'
        else:
            missing,verified=evaluate(entry['name'],owned,roots)
            if missing:state=BLOCKED;detail='Need: '+', '.join(dict.fromkeys('Shakespeare Anthology' if item.startswith('Shakespeare Anthology ') else item for item in missing))
            elif verified:state=READY;detail='Obtainable'
            else:state=UNVERIFIED;detail='Requirements unavailable for this location.'
        data.extend(struct.pack('<II88s',state,int(active),wire_text(detail)))
    for item in ICONS:
        raw=item['raw'];receipts=sum(ID_TO_NAME.get(i)==item['name'] for i in received)
        delivered=sum(ID_TO_NAME.get(i)==item['name'] for i in received[:applied_count])
        delivered += sum(ID_TO_NAME.get(i) in BUNDLED_ITEMS and item['name'] in BUNDLED_ITEMS[ID_TO_NAME[i]] for i in received[:applied_count])
        receipts += sum(ID_TO_NAME.get(i) in BUNDLED_ITEMS and item['name'] in BUNDLED_ITEMS[ID_TO_NAME[i]] for i in received)
        obtained=(BOSS_GOAL_LOCATION_IDS[item['name']] in visited) if item['category']==4 else (raw in held|ever or bool(delivered))
        # A key consumed after delivery is "previously obtained", never pending.
        pending=receipts>delivered
        flags=(int(item['name'] in disabled)<<4)|int(obtained)|(int(pending)<<1)|(int(9<=raw<=21)<<2)|(int(raw in held)<<3)
        data.extend(struct.pack('<4I',flags,quantities.get(raw,0),receipts,0))
    return bytes(data)
