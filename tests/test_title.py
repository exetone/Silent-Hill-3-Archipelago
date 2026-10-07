import gzip, importlib.util, json, pathlib, struct, tempfile, unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
STAGE=ROOT/'src/sh3'
spec=importlib.util.spec_from_file_location('title_texture',STAGE/'title_texture.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TitleTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)
  (self.root/'data').mkdir();self.path=self.root/'data/pic.arc'
  index=struct.pack('<4H',3,0,1,0)+m.TARGET
  (self.root/'data/arc.arc').write_bytes(index)
  self.off=0x310;self.tail=0xc0
  tex=bytearray(self.tail+m.PIXELS);struct.pack_into('<HH',tex,0x68,512,512);tex[0x6c:0x70]=bytes.fromhex('18300000')
  archive=bytearray(self.off);struct.pack_into('<II',archive,0,0x20030507,2);struct.pack_into('<4I',archive,32,self.off,0,len(tex),0)
  self.old=bytes(archive+tex+b'UNCHANGED TRAILER');self.path.write_bytes(self.old)
  self.resource=patch.object(m.resources,'files',return_value=STAGE);self.resource.start();self.addCleanup(self.resource.stop)
 def test_pixels_backup_and_idempotence(self):
  self.assertTrue(m.sync_title(self.root,lambda:False));b=self.path.read_bytes();p=self.off+self.tail
  self.assertEqual(b[:p],self.old[:p]);self.assertEqual(b[p+m.PIXELS:],self.old[p+m.PIXELS:]);self.assertEqual(b[p:p+m.PIXELS],(STAGE/'defaults/ap_title.rgba').read_bytes())
  backups=list(self.root.rglob('*.bak'));self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),self.old);self.assertFalse(m.sync_title(self.root,lambda:False))
 def test_gzip_index(self):
  p=self.root/'data/arc.arc';p.write_bytes(gzip.compress(p.read_bytes()));self.assertEqual(m.locate_title(self.root)[1],self.off+self.tail)
 def test_ambiguous_archive(self):
  (self.root/'data/pic2.arc').write_bytes(self.old)
  with self.assertRaises(ValueError):m.sync_title(self.root,lambda:False)
  self.assertEqual(self.path.read_bytes(),self.old)
 def test_bad_header(self):
  b=bytearray(self.old);b[self.off+0x6c]=0xff;self.path.write_bytes(b)
  with self.assertRaises(ValueError):m.sync_title(self.root,lambda:False)
  self.assertEqual(self.path.read_bytes(),b)
 def test_running(self):
  with self.assertRaises(ValueError):m.sync_title(self.root,lambda:True)
  self.assertEqual(self.path.read_bytes(),self.old)
 def test_starts_during_update(self):
  calls=iter([False,True])
  with self.assertRaises(ValueError):m.sync_title(self.root,lambda:next(calls))
  self.assertEqual(self.path.read_bytes(),self.old);self.assertEqual(list(self.path.parent.glob('*.tmp')),[])
 def test_failed_replace(self):
  with patch.object(m.os,'replace',side_effect=OSError('locked')):
   with self.assertRaises(OSError):m.sync_title(self.root,lambda:False)
  self.assertEqual(self.path.read_bytes(),self.old);self.assertEqual(list(self.path.parent.glob('*.tmp')),[])
if __name__=='__main__':unittest.main()
