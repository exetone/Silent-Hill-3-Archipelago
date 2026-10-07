from pathlib import Path
import importlib.util,sys,types,tempfile,hashlib,os,unittest
root=Path(__file__).resolve().parents[1]/'src/sh3'
pkg=types.ModuleType('rollback_test');pkg.__path__=[str(root)];sys.modules['rollback_test']=pkg
from rollback_test.rollback_standalone import rollback_standalone
class RollbackTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.mode=self.root/'scripts/SH3AP_Mode_Data';self.mode.mkdir(parents=True)
  self.plugin=self.root/'scripts/SH3AP_Standalone_Save.asi';self.plugin.write_bytes(b'plugin')
  (self.root/'SH3AP_Standalone.ini').write_bytes(b'config')
  (self.mode/'standalone_save_v1.enabled').write_bytes(b'marker')
  self.backups=self.mode/'StandaloneDisplayBackups';self.backups.mkdir()
  for profile in ('savedataAP','savedata_Vanilla'):
   d=self.root/profile;d.mkdir();(d/'disp.ini').write_bytes(b'experimental');(d/'data.sys').write_bytes(b'save unchanged')
   for n,raw in enumerate((b'original',b'later')):
    p=self.backups/(profile+'.disp.ini.'+hashlib.sha256(raw).hexdigest()[:16]+'.bak');p.write_bytes(raw);os.utime(p,ns=(100+n,100+n))
 def test_restore_and_idempotence(self):
  rollback_standalone(self.root,lambda:False)
  self.assertFalse(self.plugin.exists());self.assertFalse((self.root/'SH3AP_Standalone.ini').exists())
  for profile in ('savedataAP','savedata_Vanilla'):
   self.assertEqual((self.root/profile/'disp.ini').read_bytes(),b'original')
   self.assertEqual((self.root/profile/'data.sys').read_bytes(),b'save unchanged')
  self.assertEqual(rollback_standalone(self.root,lambda:False),())
  self.assertTrue(list(self.mode.glob('StandaloneRollback_*/manifest.json')))
 def test_running_no_changes(self):
  with self.assertRaises(ValueError):rollback_standalone(self.root,lambda:True)
  self.assertTrue(self.plugin.exists());self.assertEqual((self.root/'savedataAP/disp.ini').read_bytes(),b'experimental')
 def test_corrupt_backup_no_changes(self):
  next(self.backups.glob('savedataAP*')).write_bytes(b'corrupt')
  with self.assertRaises(ValueError):rollback_standalone(self.root,lambda:False)
  self.assertTrue(self.plugin.exists())
 def test_midway_process_start_rolls_back(self):
  calls=[False,False,True]
  with self.assertRaises(ValueError):rollback_standalone(self.root,lambda:calls.pop(0))
  self.assertEqual(self.plugin.read_bytes(),b'plugin')
 def test_link_refused(self):
  self.plugin.unlink();self.plugin.symlink_to(self.root/'SH3AP_Standalone.ini')
  with self.assertRaises(ValueError):rollback_standalone(self.root,lambda:False)
 def test_no_backup_keeps_settings(self):
  for p in self.backups.iterdir():p.unlink()
  notes=rollback_standalone(self.root,lambda:False)
  self.assertTrue(any('No original' in n for n in notes));self.assertEqual((self.root/'savedataAP/disp.ini').read_bytes(),b'experimental')
if __name__=='__main__':unittest.main()
