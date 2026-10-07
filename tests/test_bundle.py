from pathlib import Path
import sys,types,tempfile,unittest,importlib.util
root=Path(__file__).resolve().parents[1]/'src/sh3'
pkg=types.ModuleType('bundle_test');pkg.__path__=[str(root)];pkg.__spec__=importlib.util.spec_from_file_location('bundle_test',root/'__init__.py',submodule_search_locations=[str(root)]);sys.modules['bundle_test']=pkg
from bundle_test.bundled_pcfix import install_bundled_pcfix,NAMES
from bundle_test.runtime_setup import steam006_pcfix_status,validate_ap_save_system_support
class BundleTests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.folder=Path(t.name)
 def test_fresh_verified_and_idempotent(self):
  self.assertEqual(set(install_bundled_pcfix(self.folder,lambda:False)),NAMES)
  for n in NAMES:self.assertEqual((self.folder/n).read_bytes(),(root/'third_party/user_pcfix'/n).read_bytes())
  self.assertTrue(steam006_pcfix_status(self.folder)[0]);validate_ap_save_system_support(self.folder)
  self.assertEqual(install_bundled_pcfix(self.folder,lambda:False),())
 def test_backup_and_preserve_later_ini(self):
  (self.folder/'d3d8.dll').write_bytes(b'old')
  install_bundled_pcfix(self.folder,lambda:False)
  self.assertEqual(next(self.folder.glob('scripts/SH3AP_Mode_Data/BundledPCFixBackups_*/d3d8.dll.bak')).read_bytes(),b'old')
  (self.folder/'Silent_Hill_3_PC_Fix.ini').write_bytes(b'user edits')
  self.assertEqual(install_bundled_pcfix(self.folder,lambda:False),())
  self.assertEqual((self.folder/'Silent_Hill_3_PC_Fix.ini').read_bytes(),b'user edits')
 def test_running_no_mutation(self):
  with self.assertRaises(ValueError):install_bundled_pcfix(self.folder,lambda:True)
  self.assertEqual(list(self.folder.iterdir()),[])
 def test_midway_rollback(self):
  (self.folder/'Silent_Hill_3_PC_Fix.dll').write_bytes(b'old')
  calls=[False,False,True]
  with self.assertRaises(ValueError):install_bundled_pcfix(self.folder,lambda:calls.pop(0))
  self.assertEqual((self.folder/'Silent_Hill_3_PC_Fix.dll').read_bytes(),b'old')
  self.assertFalse((self.folder/'Silent_Hill_3_PC_Fix.ini').exists())
 def test_missing_file_repaired(self):
  install_bundled_pcfix(self.folder,lambda:False);(self.folder/'d3d9on12.dll').unlink()
  self.assertEqual(install_bundled_pcfix(self.folder,lambda:False),('d3d9on12.dll',))
 def test_symlink_refused(self):
  (self.folder/'d3d8.dll').symlink_to(self.folder/'other')
  with self.assertRaises(ValueError):install_bundled_pcfix(self.folder,lambda:False)
if __name__=='__main__':unittest.main()
