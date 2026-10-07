from pathlib import Path
import unittest,tempfile,sys,types,importlib.util,ast
ROOT=Path(__file__).resolve().parents[1]/'src/sh3'
pkg=types.ModuleType('sassy_test');pkg.__path__=[str(ROOT)];pkg.__spec__=importlib.util.spec_from_file_location('sassy_test',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)]);sys.modules['sassy_test']=pkg
from sassy_test.bundled_pcfix import install_bundled_pcfix
from sassy_test import runtime_setup as rt
from sassy_test import data
class CompatibilityTests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.folder=Path(t.name)
 def test_recorded_dll_and_fresh_setup(self):
  install_bundled_pcfix(self.folder,lambda:False)
  self.assertEqual(rt.digest((self.folder/'Silent_Hill_3_PC_Fix.dll').read_bytes()),'5c4028c674ea9820183144e6b47372216d5c1b3c147659e175ec2ffce0ca6fbb')
  self.assertEqual(rt.ensure_ap_pcfix_settings(self.folder,lambda:False),())
  self.assertIn(b'UnlockEverything = 0',(self.folder/'Silent_Hill_3_PC_Fix.ini').read_bytes())
  self.assertEqual(rt.loader_timing_mode(self.folder),'standard-default')
 def test_existing_deferred_preserved(self):
  (self.folder/'dinput8.ini').write_text('[GlobalSets]\nDontLoadFromDllMain=1\n')
  install_bundled_pcfix(self.folder,lambda:False);rt.ensure_ual_scripts_only_config(self.folder)
  self.assertEqual(rt.loader_timing_mode(self.folder),'existing-deferred')
  self.assertNotIn('ensure_steam006_pcfix', (ROOT/'client.py').read_text())
 def test_legacy_ap_system_preserved_before_replacement(self):
  install_bundled_pcfix(self.folder,lambda:False)
  ap=self.folder/'savedataAP';ap.mkdir();(ap/'data.sys').write_bytes(bytes(296));(ap/'sh3save0').write_bytes(b'numbered save')
  (self.folder/'savedata').symlink_to(ap, target_is_directory=True)
  rt.ensure_ap_system_unlock_state(self.folder,lambda:False)
  self.assertEqual((ap/'sh3save0').read_bytes(),b'numbered save')
  self.assertEqual(len((ap/'data.sys').read_bytes()),116)
  self.assertEqual(next(self.folder.glob('scripts/SH3AP_Mode_Data/APSystemDataBackups/incompatible*')).read_bytes(),bytes(296))
 def test_compatible_seed_versions(self):
  tree=ast.parse((ROOT/'client.py').read_text());fn=next(n for n in tree.body if getattr(n,'name',None)=='_slot_catalogue_matches')
  ns=dict(vars(data));exec(compile(ast.Module(body=[fn],type_ignores=[]),'client_subset','exec'),ns)
  slot={'confirmed_location_flags':list(data.PERSIST_FLAG_TO_LOCATION_ID),'scripted_check_protocol':data.SCRIPTED_PROTOCOL,
    'scripted_location_ids':sorted(loc for loc in data.SCRIPTED_BIT_TO_LOCATION_ID.values() if loc in data.active_locations(False).values()),
    'save_travel_protocol':data.SAVE_TRAVEL_PROTOCOL,'confirmed_save_ids':sorted(data.SAVE_ID_TO_LOCATION_ID),'fast_travel_rows':list(data.ACTIVE_FAST_TRAVEL_ROWS)}
  for version in ('1.0.1','1.0.2'):
   slot['sh3ap_world_version']=version;self.assertTrue(ns['_slot_catalogue_matches'](slot))
  slot['sh3ap_world_version']='1.0.0';self.assertFalse(ns['_slot_catalogue_matches'](slot))
  slot['sh3ap_world_version']='1.0.2';slot['confirmed_location_flags']=[];self.assertFalse(ns['_slot_catalogue_matches'](slot))
if __name__=='__main__':unittest.main()
