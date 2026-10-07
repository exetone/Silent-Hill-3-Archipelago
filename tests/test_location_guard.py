"""Client regression tests with real file I/O; game/server/Win32 calls are mocked.

Pass the unpacked sh3 directory. The selected client definitions are executed
unchanged via AST so no Archipelago GUI/Windows runtime is required on Linux.
"""
import ast
import asyncio
import ctypes
from ctypes import wintypes
import importlib.util
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import Mock, patch

ROOT=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'src/sh3'
spec=importlib.util.spec_from_file_location('sh3_data',ROOT/'data.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
NAMES={'_read_live_bridge_events','_read_new_runtime_trace','_trace_fields',
       '_observe_new_game_trace','_sync_locations','PipeBridge'}
ns=dict(vars(d),asyncio=asyncio,ctypes=ctypes,wintypes=wintypes,os=os,Path=Path,
        time=time,threading=threading,sys=sys,__name__='test_sh3_client',
        LIVE_BRIDGE_STALE_SECONDS=5.0,bridge_logger=logging.getLogger('test'))
tree=ast.parse((ROOT/'client.py').read_text())
selected=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+
                    [n for n in tree.body if getattr(n,'name',None) in NAMES],type_ignores=[])
exec(compile(ast.fix_missing_locations(selected),str(ROOT/'client.py'),'exec'),ns)

class GuardTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.events=Path(self.temp.name)/'events.txt';self.trace=Path(self.temp.name)/'trace.txt'
        self.now=time.time_ns();self.started=self.now-1_000_000_000
        self.identity=(42,self.started)
        ns['_live_bridge_event_path']=lambda:self.events
        ns['_live_check_trace_path']=lambda:self.trace
        ns['_acquire_start_arm_lock']=Mock();ns['_release_start_arm_lock']=Mock()
        ns['_new_game_inventory_initialized']=Mock(return_value=True)
        ns['_clear_unlock_all_new_game_inventory']=Mock(return_value=(True,set(),set()))
        async def bind(ctx,status):return status
        ns['_bind_receive_session']=bind
        sys.modules['test_sh3_client']=types.ModuleType('test_sh3_client')
        feature=types.ModuleType('test_sh3_client.features_runtime');feature.sync_random_start=lambda *a:None
        self.patcher=patch.dict(sys.modules,{'test_sh3_client.features_runtime':feature})
        self.patcher.start();self.addCleanup(self.patcher.stop)
        ns['__package__']='test_sh3_client'
        ns['__spec__']=None
        self.ctx=types.SimpleNamespace(
            server=object(),slot=1,location_catalogue_compatible=True,
            bridge=types.SimpleNamespace(event_process_identity=lambda:self.identity),
            location_source_warning=None,location_process_identity=None,
            live_check_trace_offset=None,bridge_last_completed=set(),bridge_completed_baseline=set(),
            new_game_candidate_ids=set(),last_location_diag=None,missing_locations=set(d.LOCATION_NAME_TO_ID.values()),
            checked_locations=set(),location_names=types.SimpleNamespace(lookup_in_game=lambda x,g:str(x)))
        self.submitted=[]
        async def check_locations(locs):
            new=set(locs)-self.ctx.checked_locations
            self.ctx.checked_locations.update(locs);self.submitted.extend(sorted(new));return new
        self.ctx.check_locations=check_locations
        names=['Mall 1F Boutique - Handgun Bullets 1','Mall 1F Boutique - Handgun Bullets 2',
               'Mall 2F Supply Room - Beef Jerky','Mall 2F Storeroom - Health Drink 1',
               'Mall 2F Storeroom - Health Drink 2','Mall 2F Storeroom - Handgun Bullets',
               'Mall 2F Bookstore - Handgun Bullets','Otherworld Mall 1F First Aid Room - Health Drink 1',
               'Otherworld Mall 1F First Aid Room - Health Drink 2','Otherworld Mall 1F First Aid Room - Ampoule']
        self.ids={d.LOCATION_NAME_TO_ID[n] for n in names}
        self.flags=[f for f,l in d.PERSIST_FLAG_TO_LOCATION_ID.items() if l in self.ids]
        assert len(self.flags)==10
        self.start='=== SH3AP 0.1.23 SESSION START ===\n'
        self.newgame='CATALOG_CONTEXT_CHANGE KEY=E4:0000/D9:01 D8=21 DA=01 +00:00->21 +01:00->01\n'
        self.raw13='ALT_ITEM_GRANT RAW_ITEM_ID=13 OWNED_BEFORE=0 OWNED_AFTER=1 QTY_BEFORE=0 QTY_AFTER=32 KEY=E4:0000/D9:01\n'
        self.pickups=''.join(f'GROUND_PICKUP_DIRECT PERSIST_FLAG={f} FLAG_AFTER=1 STABLE_KEY=SH3:GROUND:FLAG:{f}\n' for f in self.flags)
    def write(self,path,data,stamp=None):
        path.write_bytes(data.encode());stamp=self.now if stamp is None else stamp
        os.utime(path,ns=(stamp,stamp))
    async def sync(self,world='1'):
        await ns['_sync_locations'](self.ctx,{'WORLD':world})
    def bridge(self,flags=(),extra='',stamp=None):
        self.write(self.events,'SESSION VERSION=2\n'+''.join(f'CHECK FLAG={f}\n' for f in flags)+extra+'HEARTBEAT\n',stamp)
    async def test_reported_ten_stale_pickups_and_start_signal_are_ignored(self):
        self.write(self.trace,self.start+self.newgame+self.raw13+self.pickups,self.started-10_000_000_000)
        await self.sync()
        self.assertEqual([],self.submitted)
        ns['_clear_unlock_all_new_game_inventory'].assert_not_called()
    async def test_even_current_diagnostic_pickups_never_send(self):
        self.write(self.trace,self.start+self.pickups)
        await self.sync();self.assertEqual([],self.submitted)
    async def test_valid_livebridge_sends_reported_pickups_once(self):
        self.bridge(self.flags)
        await self.sync();await self.sync();self.assertEqual(self.ids,set(self.submitted));self.assertEqual(10,len(self.submitted))
    async def test_fresh_newgame_sends_only_three_start_checks(self):
        self.bridge();self.write(self.trace,self.start+self.newgame+self.pickups)
        await self.sync();await self.sync()
        self.assertEqual(set(d.START_LOCATION_IDS),set(self.submitted));self.assertEqual(3,len(self.submitted))
        ns['_clear_unlock_all_new_game_inventory'].assert_called_once()
    async def test_save_load_after_newgame_signal_cancels_cleanup(self):
        self.bridge();self.write(self.trace,self.start+self.newgame+self.raw13+'AP_SAVE_LOAD_OBSERVED LOAD=1\n')
        await self.sync();self.assertEqual([],self.submitted)
        ns['_clear_unlock_all_new_game_inventory'].assert_not_called()
    async def test_title_screen_cannot_clean_inventory_or_send(self):
        self.bridge(self.flags);self.write(self.trace,self.start+self.newgame+self.raw13)
        await self.sync('0');self.assertEqual([],self.submitted)
        ns['_clear_unlock_all_new_game_inventory'].assert_not_called()
    async def test_recent_previous_process_bridge_rejected(self):
        self.bridge(self.flags,stamp=self.started-100_000_000)
        await self.sync();self.assertEqual([],self.submitted)
    async def test_expired_heartbeat_rejected(self):
        self.identity=(42,self.now-20_000_000_000);self.bridge(self.flags,stamp=self.now-10_000_000_000)
        await self.sync();self.assertEqual([],self.submitted)
    async def test_unknown_process_fails_closed(self):
        self.identity=None;self.bridge(self.flags);await self.sync();self.assertEqual([],self.submitted)
    async def test_same_pid_new_creation_resets_trace_cursor(self):
        self.bridge();self.write(self.trace,self.start+self.newgame)
        await self.sync();self.assertEqual(3,len(self.submitted))
        # Different process, same PID. Its shorter trace must be read again.
        self.identity=(42,self.started+100_000_000);self.ctx.checked_locations.clear()
        self.write(self.trace,self.start+self.newgame)
        await self.sync();self.assertEqual(6,len(self.submitted))
        self.assertEqual(2,ns['_clear_unlock_all_new_game_inventory'].call_count)
    async def test_second_newgame_excludes_previously_observed_checks(self):
        self.bridge(self.flags[:1]);self.write(self.trace,self.start+self.newgame)
        await self.sync();self.ctx.checked_locations.clear();self.submitted.clear()
        self.bridge(self.flags[:2]);self.write(self.trace,self.start+self.newgame+self.newgame)
        await self.sync()
        self.assertEqual(set(d.START_LOCATION_IDS)|{d.PERSIST_FLAG_TO_LOCATION_ID[self.flags[1]]},set(self.submitted))
    async def test_cleanup_retry_preserves_initial_baseline(self):
        ns['_clear_unlock_all_new_game_inventory'].side_effect=[(False,set(),set()),(True,set(),set())]
        self.bridge();self.write(self.trace,self.start+self.newgame)
        await self.sync()
        self.bridge(self.flags[:1]);await self.sync()
        self.assertEqual(set(d.START_LOCATION_IDS)|{d.PERSIST_FLAG_TO_LOCATION_ID[self.flags[0]]},set(self.submitted))
    async def test_partial_live_event_waits_for_newline(self):
        self.write(self.events,'SESSION VERSION=2\nCHECK FLAG=116')
        ok,locs,start=ns['_read_live_bridge_events'](self.started)
        self.assertTrue(ok);self.assertEqual(set(),locs)
        self.write(self.events,'SESSION VERSION=2\nCHECK FLAG=116\n')
        ok,locs,start=ns['_read_live_bridge_events'](self.started)
        self.assertEqual({d.SCRIPTED_FLAG_TO_LOCATION_ID[116]},locs)
    async def test_partial_trace_waits_then_consumes_exactly_once(self):
        self.write(self.trace,self.start+self.newgame.rstrip())
        offset,lines=ns['_read_new_runtime_trace'](None,self.started)
        self.assertEqual([self.start.strip()],lines)
        self.write(self.trace,self.start+self.newgame)
        offset,lines=ns['_read_new_runtime_trace'](offset,self.started)
        self.assertEqual([self.newgame.strip()],lines)
        self.assertEqual([],ns['_read_new_runtime_trace'](offset,self.started)[1])
    async def test_unknown_event_version_and_flags_ignored(self):
        self.write(self.events,'SESSION VERSION=99\nCHECK FLAG=116\n')
        self.assertEqual((False,set(),False),ns['_read_live_bridge_events'](self.started))
        self.bridge(extra='CHECK FLAG=garbage\nCHECK FLAG=999999\n')
        self.assertEqual((True,set(),False),ns['_read_live_bridge_events'](self.started))
    async def test_missing_auth_never_submits_or_cleans(self):
        self.ctx.server=None;self.bridge(self.flags);self.write(self.trace,self.start+self.newgame)
        await self.sync();self.assertEqual([],self.submitted)
        ns['_clear_unlock_all_new_game_inventory'].assert_not_called()

class PipeIdentityTests(unittest.TestCase):
    def test_win32_identity_conversion_caching_and_close(self):
        pipe=ns['PipeBridge']();pipe.file=Mock();pipe.file.fileno.return_value=3
        ticks=116444736000000000+123456789
        def pid_call(h,p):p._obj.value=42;return 1
        def time_call(h,c,e,k,u):c._obj.dwLowDateTime=ticks&0xffffffff;c._obj.dwHighDateTime=ticks>>32;return 1
        api=types.SimpleNamespace(GetNamedPipeServerProcessId=Mock(side_effect=pid_call),
              GetProcessTimes=Mock(side_effect=time_call),OpenProcess=Mock(return_value=99),CloseHandle=Mock())
        ns['_kernel32']=lambda:api
        fake_os=types.SimpleNamespace(name='nt')
        old=ns['os'];ns['os']=fake_os
        try:
            with patch.dict(sys.modules,{'msvcrt':types.SimpleNamespace(get_osfhandle=lambda fd:88)}):
                self.assertEqual((42,12345678900),pipe.event_process_identity())
                self.assertEqual((42,12345678900),pipe.event_process_identity())
                api.OpenProcess.assert_called_once_with(0x1000,False,42)
                api.CloseHandle.assert_called_once_with(99)
                pipe.close();self.assertIsNone(pipe.process_identity)
                self.assertIsNone(pipe.event_process_identity())
        finally:ns['os']=old

if __name__=='__main__':unittest.main(verbosity=2)
