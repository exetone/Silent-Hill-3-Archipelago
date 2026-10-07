"""AP DeathLink protocol and leased, seed-bound native requests."""
from __future__ import annotations
import os,struct,time,math
from dataclasses import dataclass,field
SIGNATURE=b'SHAP_DEATH_V1\0'
NATIVE_RVA=0x3b000

@dataclass
class State:
    binding: tuple|None=None
    count: int|None=None
    sequence: int=0
    pending: bool=False
    ready: bool=False
    active: bool=False
    can_queue: bool=False
    last_time: float=0.0
    seen: set=field(default_factory=set)

    def receive(self,data):
        if not self.active or not self.can_queue:return False
        try:
            stamp=float(data['time']);source=str(data['source'])
        except (KeyError,TypeError,ValueError):return False
        token=(stamp,source)
        if not math.isfinite(stamp) or token in self.seen:return False
        # Ignore delayed packets older than the activation/reconnection boundary.
        if stamp < self.last_time-1:return False
        self.seen.add(token)
        if len(self.seen)>256:self.seen={token}
        self.pending=True
        return True

    def reset(self):
        self.binding=None;self.count=None;self.pending=False
        self.ready=False;self.active=False;self.can_queue=False;self.seen.clear();self.last_time=time.time()

def exchange(ctx,api,clear=False):
    """Return supported/current local counter/status. Never write game state."""
    if os.name!='nt':return None
    pid,mods=api._runtime_discovery().get_modules();ui=mods.get('sh3ap_ui.asi',0)
    if not pid or not ui:return None
    k=api._kernel32();h=k.OpenProcess(0x438,False,pid)
    if not h:return None
    try:
        base=ui+NATIVE_RVA;head=api._read_process_memory(h,base,64)
        if head is None or head[:len(SIGNATURE)]!=SIGNATURE:return None
        travel=getattr(ctx,'travel_state',None)
        enabled=(not clear and ctx.server is not None and ctx.slot is not None
                 and ctx.location_catalogue_compatible and bool(ctx.slot_data.get('death_link',False))
                 and travel is not None and travel.identity==[api.GAME_NAME,ctx.room_seed_name,ctx.team,ctx.slot,ctx.auth])
        if not enabled:
            api._write_process_memory(h,base+16,bytes(8));return None
        cookie=travel.cookie
        if api._read_process_memory(h,ui+0x23040,32)!=cookie*2:
            api._write_process_memory(h,base+16,bytes(8));return None
        state=ctx.deathlink_state;binding=(pid,ui,cookie)
        request,ack,count,ready,status=struct.unpack_from('<5I',head,40)
        if state.binding!=binding:
            state.reset();state.binding=binding;state.count=count;state.sequence=request
            # Stop publishing before replacing identity. The native reader also
            # requires both existing save/travel cookies to match.
            if not api._write_process_memory(h,base+16,bytes(8)):return None
            if not api._write_process_memory(h,base+24,cookie):return None
        state.ready=bool(ready)
        state.can_queue=status in (2,5)
        if status in (0,1,3,4):state.pending=False
        if state.pending and ready and request==ack:
            state.sequence=(request+1)&0xffffffff or 1
            if api._write_process_memory(h,base+40,struct.pack('<I',state.sequence)):
                state.pending=False
        if not api._write_process_memory(h,base+20,struct.pack('<I',1)):return None
        if not api._write_process_memory(h,base+16,struct.pack('<I',int(k.GetTickCount())&0xffffffff or 1)):return None
        return count,status
    finally:k.CloseHandle(h)

async def sync(ctx,api):
    state=ctx.deathlink_state
    result=await api.asyncio.to_thread(exchange,ctx,api)
    active=result is not None and result[1] not in (0,1,4)
    if active!=state.active:
        state.active=active;state.last_time=time.time()
    await ctx.update_death_link(active)
    if result is None:
        state.reset();return
    count,status=result
    if status==4 and not getattr(ctx,'deathlink_warning',False):
        api.bridge_logger.warning('DeathLink paused: runtime player/code validation failed.')
        ctx.deathlink_warning=True
    if state.count is None:state.count=count
    elif count!=state.count:
        state.count=count
        if status in (1,2,3,5):
            await ctx.send_death(f'{ctx.player_names.get(ctx.slot,"Heather")} died in Silent Hill 3.')
