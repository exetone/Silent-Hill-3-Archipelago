"""Read-only game observation; writes only the dedicated tracker UI mailbox."""
from __future__ import annotations
import json,os,struct
from pathlib import Path
from . import tracker_model as model
from .runtime_setup import atomic_write

# Native bundle tokens are delivery commands, not actual inventory items.
# Expand only the two catalogue-defined bundles; reject unrelated corrupt data.
_BUNDLE_HISTORY_RAWS = {
    model.ITEM_ID_TO_RAW[model.ITEM_NAME_TO_ID[bundle]]: frozenset(
        model.ITEM_ID_TO_RAW[model.ITEM_NAME_TO_ID[member]] for member in members
    )
    for bundle, members in model.BUNDLED_ITEMS.items()
}
_HISTORY_ALLOWED_RAWS = frozenset(item['raw'] for item in model.ICONS if item['raw'] >= 0)

def _normalise_history_raws(raws):
    expanded = set()
    for raw in raws:
        expanded.update(_BUNDLE_HISTORY_RAWS.get(raw, (raw,)))
    if not expanded <= _HISTORY_ALLOWED_RAWS:
        raise ValueError('Invalid tracker item history')
    return expanded

class History:
    def __init__(self,root:Path,cookie:bytes):
        self.cookie=cookie;self.ever=set();self.path=root/(cookie.hex()+'.json')
        if self.path.exists():
            value=json.loads(self.path.read_text(encoding='utf-8'))
            if value.get('schema')!=1 or value.get('cookie')!=cookie.hex():raise ValueError('Tracker history identity mismatch')
            stored=set(value['ever'])
            self.ever=_normalise_history_raws(stored)
            if self.ever!=stored:self._save(self.ever)
    def _save(self,ever):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        atomic_write(self.path,json.dumps(dict(schema=1,cookie=self.cookie.hex(),ever=sorted(ever))).encode())
    def add(self,held):
        combined=self.ever|_normalise_history_raws(held)
        if combined!=self.ever:
            self._save(combined)
            self.ever=combined

def sync(ctx,api,clear=False):
    if os.name!='nt':return
    pid,modules=api._runtime_discovery().get_modules();ui=modules.get('sh3ap_ui.asi',0)
    if not pid or not ui:
        ctx.tracker_cached_payload=None
        return
    k=api._kernel32();h=k.OpenProcess(0x438,False,pid)
    if not h:return
    try:
        base=ui+model.NATIVE_RVA
        head=api._read_process_memory(h,base,64)
        if not head or head[:16]!=model.SIGNATURE or head[16:32]!=model.SCHEMA_HASH:return
        travel=getattr(ctx,'travel_state',None)
        connected=(not clear and ctx.server is not None and ctx.slot is not None and ctx.team is not None
                   and ctx.location_catalogue_compatible and travel is not None
                   and travel.identity==[api.GAME_NAME,ctx.room_seed_name,ctx.team,ctx.slot,ctx.auth])
        if not connected:
            api._write_process_memory(h,base+36,bytes(4));ctx.tracker_cached_payload=None;return
        cookie=travel.cookie;bound=api._read_process_memory(h,ui+0x23040,32)
        if bound!=cookie*2:
            api._write_process_memory(h,base+36,bytes(4));return
        old_pid=getattr(ctx,'tracker_pid',None)
        if old_pid!=pid:
            ctx.tracker_pid=pid;ctx.tracker_cached_payload=None
        history=getattr(ctx,'tracker_history',None)
        if history is None or history.cookie!=cookie:
            api._write_process_memory(h,base+36,bytes(4))
            history=History(api.GAME_FOLDER/'scripts'/'SHAP_tracker',cookie);ctx.tracker_history=history
        # Tracker readiness is area-based, independent of popup startup/area gates.
        live_world=api._read_process_memory(h,0x70e66d8,1)
        live_manager=api._read_process_memory(h,0x711fca0,4)
        ready=(ctx.last_status.get('WORLD')=='1' and bool(live_world and live_world[0])
               and live_manager is not None and int.from_bytes(live_manager,'little') in model.AREA_MANAGERS
               and not (ctx.pending_new_game_start_checks and not ctx.new_game_cleanup_done)
               and not (ctx.runtime_entry_classification is None and ctx.receive_hold_deadline and api.time.monotonic()<ctx.receive_hold_deadline))
        manager=0;held=set();quantities={};flags=b'';room=None;stage=None
        if ready:
            inv=api._read_process_memory(h,0x712ca80,0x100)
            flags=api._read_process_memory(h,0x715d060,0x390)
            mgr=api._read_process_memory(h,0x711fca0,4)
            if inv is None or flags is None or mgr is None:ready=False
            else:
                held,quantities=model.read_inventory(inv,flags);manager=int.from_bytes(mgr,'little')
                room_bytes=api._read_process_memory(h,0x897e48,2)
                stage_bytes=api._read_process_memory(h,0x70e66d9,1)
                if room_bytes is not None and stage_bytes is not None:
                    room=int.from_bytes(room_bytes,'little');stage=stage_bytes[0]
        received=[int(i.item) for i in ctx.items_received]
        applied=min(len(received),max(0,int(ctx.last_status.get('AP_APPLIED_COUNT','0')))) if ready and ctx.session_bound_token==ctx.delivery_identity_token else 0
        applied_raw={api.ITEM_ID_TO_RAW[i] for i in received[:applied] if i in api.ITEM_ID_TO_RAW and api.ITEM_ID_TO_RAW[i]!=254}
        if ready:history.add(held|applied_raw)
        active=set(ctx.checked_locations)|set(ctx.missing_locations)
        payload=model.snapshot(cookie=cookie,connected=True,world=ready,manager=manager,
            world_flags=flags or b'',room=room,stage=stage,active_ids=active,checked=set(ctx.checked_locations),sent=set(ctx.locations_checked),
            received=received,applied_count=applied,held=held,quantities=quantities,ever=history.ever,disabled=model.disabled_items(getattr(ctx,'slot_data',{})),visited=(set(ctx.checked_locations) | set(getattr(ctx,'live_runtime_checks',())) | set(getattr(travel,'visited',()))))
        if len(payload)!=struct.unpack_from('<I',head,44)[0]:raise ValueError('Tracker payload layout mismatch')
        if ctx.tracker_cached_payload!=payload or not struct.unpack_from('<I',head,32)[0] or struct.unpack_from('<I',head,32)[0]&1:
            seq=(struct.unpack_from('<I',head,32)[0]+2)&0xfffffffe
            if not seq:seq=2
            # Revoke lease before a session switch and publish an even generation
            # only after every byte was written. Readers never trust a torn write.
            if not api._write_process_memory(h,base+32,struct.pack('<I',seq-1)):return
            if not api._write_process_memory(h,base+64,payload):return
            if not api._write_process_memory(h,base+32,struct.pack('<I',seq)):return
            ctx.tracker_cached_payload=payload
        api._write_process_memory(h,base+36,struct.pack('<I',int(k.GetTickCount())&0xffffffff or 1))
    finally:k.CloseHandle(h)
