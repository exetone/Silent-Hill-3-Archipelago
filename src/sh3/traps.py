"""Filler traps and a durable, seed-bound, at-most-once effect queue."""
from __future__ import annotations
import json, os, struct, tempfile
from pathlib import Path
from .data import TRAP_ITEM_IDS, TRAP_NAMES, ITEM_CLASSIFICATION
from .supplies import AMMO, HEALING

SIGNATURE = b'SHAP_TRAPS_V1\0'
NATIVE_RVA = 0x3c000

def replace_filler_with_traps(pool, percentage, selected, rng):
    result = list(pool)
    names = sorted(set(selected))
    if not 0 <= percentage <= 100 or not set(names) <= set(TRAP_NAMES):
        raise ValueError('Invalid trap options')
    if not percentage or not names:
        return result
    slots = [i for i,n in enumerate(result) if n in AMMO | HEALING | {'Beef Jerky'}
             and ITEM_CLASSIFICATION[n] == 'filler']
    for i in rng.sample(slots, len(slots)*percentage//100):
        result[i] = rng.choice(names) + ' Trap'
    return result

class State:
    def __init__(self, travel):
        self.identity = travel.identity
        self.cookie = travel.cookie
        self.path = travel.path.with_name(travel.path.stem + '.traps.json')
        self.entries = {}
        if self.path.exists():
            obj = json.loads(self.path.read_text(encoding='utf-8'))
            if obj.get('version') != 1 or obj.get('identity') != self.identity:
                raise ValueError('Trap journal identity/version mismatch')
            self.entries = {int(i): list(v) for i,v in obj['entries'].items()}
            if any(i < 0 or len(v) != 2 or v[0] not in TRAP_ITEM_IDS or type(v[1]) is not bool
                   for i,v in self.entries.items()):
                raise ValueError('Invalid trap journal; delivery paused')
    def commit(self, entries):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=self.path.name + '.', dir=self.path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                json.dump(dict(version=1,identity=self.identity,entries=entries),f,sort_keys=True)
                f.flush();os.fsync(f.fileno())
            os.replace(tmp,self.path)
            self.entries = entries
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def enqueue(self, index, item):
        if item not in TRAP_ITEM_IDS or index < 0:raise ValueError('Invalid trap receipt')
        old = self.entries.get(index)
        if old is not None:
            if old[0] != item:raise ValueError('AP stream changed at a recorded trap index')
            return
        self.commit({**self.entries,index:[item,False]})
    def consume(self,index):
        self.commit({**self.entries,index:[self.entries[index][0],True]})

def ensure_state(ctx):
    travel = getattr(ctx,'travel_state',None)
    if travel is None:raise ValueError('Trap identity is not bound')
    state = getattr(ctx,'trap_state',None)
    if state is None or state.identity != travel.identity:
        state = ctx.trap_state = State(travel)
    return state

def enqueue(ctx,index,item):
    ensure_state(ctx).enqueue(index,item)

def exchange(ctx,api,clear=False):
    if os.name != 'nt':return
    pid,mods = api._runtime_discovery().get_modules();ui = mods.get('sh3ap_ui.asi',0)
    if not pid or not ui:return
    k = api._kernel32();h = k.OpenProcess(0x438,False,pid)
    if not h:return
    try:
        base = ui + NATIVE_RVA
        head = api._read_process_memory(h,base,80)
        if head is None or head[:len(SIGNATURE)] != SIGNATURE:return
        def write(offset,data):
            if not api._write_process_memory(h,base+offset,data):raise OSError('Trap mailbox write failed')
        travel = getattr(ctx,'travel_state',None)
        valid = (not clear and ctx.server is not None and ctx.slot is not None
                 and ctx.location_catalogue_compatible and ctx.slot_data.get('trap_protocol') == 1
                 and travel is not None and travel.identity == [api.GAME_NAME,ctx.room_seed_name,ctx.team,ctx.slot,ctx.auth])
        if not valid:
            write(16,bytes(8));return
        state = ensure_state(ctx)
        if api._read_process_memory(h,ui+0x23040,32) != state.cookie*2:
            write(16,bytes(8));return
        req,kind,intensity,ack,status,remaining = struct.unpack_from('<6I',head,40)
        tick = int(k.GetTickCount()) & 0xffffffff or 1
        if head[24:40] != state.cookie or struct.unpack_from('<I',head,20)[0] != 1:
            write(16,bytes(8));write(24,state.cookie);write(40,bytes(24))
            write(20,struct.pack('<I',1));write(16,struct.pack('<I',tick));return
        if status == 5 and req == ack and not remaining:
            # Require the ordinary receipt stream to have acknowledged this
            # virtual item. Native traps never block later inventory items.
            applied = int(getattr(ctx,'last_status',{}).get('AP_APPLIED_COUNT','0'))
            pending = [(i,v) for i,v in sorted(state.entries.items()) if not v[1] and i < applied]
            if pending:
                index,(item,_) = pending[0]
                if index >= len(ctx.items_received) or ctx.items_received[index].item != item:
                    raise ValueError('Trap queue does not match authoritative AP receipts')
                # Stop the lease before publishing. Commit before arming so a
                # reconnect/save rollback cannot repeat the trap. A process
                # crash between commit and arming can lose this one effect.
                write(16,bytes(4))
                write(40,struct.pack('<3I',index+1,list(TRAP_ITEM_IDS).index(item)+1,
                                     max(0,min(2,int(ctx.slot_data.get('trap_intensity',1))))))
                state.consume(index)
        write(16,struct.pack('<I',tick))
    finally:k.CloseHandle(h)
