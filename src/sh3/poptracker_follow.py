"""Read-only location observer and slot-scoped PopTracker map broadcasts.
No game-memory writes, teleport requests, item grants or check submissions.
"""
from __future__ import annotations
import asyncio
import os
import time
import uuid
import struct
from .poptracker_floor import page_for_location
from .tracker_model import AREA_MANAGERS

AREA_TABS = {1:'Mall',2:'OW Mall',3:'Subway',4:'Underpass',5:'Underpass',
             6:'Hilltop',7:'Hilltop',8:'OW Hilltop',9:'Hilltop',10:'Silent Hill',
             11:'Hospital',12:'OW Hospital',13:'Amusement Park',14:'Chapel'}
# Read-only signatures for the room getter and the native map/position routines.
SIGNATURES = {
    0x464950: bytes.fromhex('a1487e8900c3'),
    0x472fe0: bytes.fromhex('a100c112078b108b4c24048911'),
    0x4997b0: bytes.fromhex('83ec205657e8d62d17000fb6f0'),
}

def observe(api):
    if os.name != 'nt': return None
    pid, modules = api._runtime_discovery().get_modules()
    if not pid: return None
    kernel = api._kernel32()
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle: return None
    try:
        def read(address, size):
            data = api._read_process_memory(handle, address, size)
            return data if data is not None and len(data) == size else None
        def travel_busy():
            ui = modules.get('sh3ap_ui.asi', 0)
            return ui and any(read(ui+offset, 1) != b'\0' for offset in (0xa06c,0xa0f8))
        context = read(0x70e66d8, 6)
        manager = read(0x711fca0, 4)
        room_data = read(0x897e48, 4)
        actor_data = read(0x712c100, 4)
        if (not context or not context[0] or not context[5] or
                manager is None or room_data is None or actor_data is None or travel_busy()):
            return None
        for address, expected in SIGNATURES.items():
            actual = read(address, len(expected))
            if actual is None: return None
            if actual != expected:
                raise RuntimeError('SH3 executable map-reader signature differs; floor following paused')
        actor = int.from_bytes(actor_data,'little')
        if actor < 0x10000 or actor > 0x7fffffef: return None
        room = int.from_bytes(room_data,'little')
        stage = context[1]
        def snapshot():
            position = read(actor, 12)
            flags = [read(a,4) for a in (0x715d090,0x715d0a4,0x715d0b4)]
            if position is None or any(f is None for f in flags): return None
            return page_for_location(stage,room,struct.unpack('<3f',position),
                                     tuple(int.from_bytes(f,'little') for f in flags))
        resolved = snapshot()
        if resolved is None: return None
        # Reject torn transitions, including a new arrival within the same area.
        if (travel_busy() or read(0x70e66d8,6) != context or
                read(0x711fca0,4) != manager or read(0x897e48,4) != room_data or
                read(0x712c100,4) != actor_data or snapshot() != resolved): return None
        map_id, page = resolved
        value = int.from_bytes(manager,'little')
        if page is None:
            area_id = 12 if value == 0x6f3694 else AREA_MANAGERS.get(value)
            area = AREA_TABS.get(area_id)
            if area is None: return None
            page = (area,None)  # Native no-map room; do not invent a floor.
        return (pid,value,context[1:3].hex(),*page,room,map_id)
    finally:
        kernel.CloseHandle(handle)

class FollowState:
    def __init__(self):
        self.identity = None
        self.candidate = None
        self.since = 0.0
        self.stable = None
        self.sequence = 0
        self.session = uuid.uuid4().hex
        self.sent_at = -1e30

    def update(self, identity, observation, now):
        if self.identity != identity:
            self.__init__()
            self.identity = identity
        if observation is None:
            self.candidate = None
            self.stable = None
            return None
        if observation != self.candidate:
            self.candidate, self.since = observation, now
            return None
        if now-self.since < 0.75: return None
        if observation != self.stable:
            self.stable = observation
            self.sequence += 1
            self.sent_at = -1e30
        if now-self.sent_at < 2.0: return None
        _, manager, context, area, floor, room, map_id = observation
        return dict(protocol=1, session=self.session, sequence=self.sequence,
                    area=area, floor=floor or '', manager=hex(manager), context=context, room=room, map_id=map_id)

async def sync(ctx, api):
    identity = (ctx.room_seed_name, ctx.team, ctx.slot)
    server = ctx.server
    if server is None or not identity[0] or identity[1] is None or identity[2] is None:
        ctx.poptracker_follow_state = None
        return
    state = getattr(ctx, 'poptracker_follow_state', None)
    if state is None:
        state = FollowState()
        ctx.poptracker_follow_state = state
    observation = await asyncio.to_thread(observe, api)
    if ctx.server is not server or (ctx.room_seed_name,ctx.team,ctx.slot) != identity: return
    now = time.monotonic()
    payload = state.update(identity, observation, now)
    if payload is None: return
    payload.update(seed=identity[0], team=identity[1], slot=identity[2])
    await ctx.send_msgs([{'cmd':'Bounce','slots':[ctx.slot],
                          'data':{'sh3_map_follow':payload}}])
    if state.sent_at < 0:
        api.bridge_logger.info('PopTracker location: %s / %s (manager=%s context=%s room=%s native_map=%s)',
                               payload['area'],payload['floor'] or 'floor unverified',
                               payload['manager'],payload['context'],payload['room'],payload['map_id'])
    state.sent_at = now
