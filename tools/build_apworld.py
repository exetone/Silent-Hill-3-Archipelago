#!/usr/bin/env python3
"""Package reviewed source with exact binary payloads from the matching APWorld.
This does not compile the legacy native plugins.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--payload-apworld',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.payload_apworld.resolve()==a.output.resolve():p.error('Output must differ from payload APWorld.')
 entries={}
 for f in (ROOT/'src/sh3').rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':entries['sh3/'+f.relative_to(ROOT/'src/sh3').as_posix()]=f.read_bytes()
 with zipfile.ZipFile(a.payload_apworld) as z:
  for name,h in json.loads((ROOT/'reference/binary_payload_manifest.json').read_text()).items():
   if name in entries:raise ValueError('Payload overlaps source: '+name)
   data=z.read(name)
   if hashlib.sha256(data).hexdigest()!=h:raise ValueError('Payload checksum mismatch: '+name)
   entries[name]=data
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.output,'w') as z:
  for name,data in sorted(entries.items()):
   info=zipfile.ZipInfo(name,(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data,compresslevel=9)
 print(a.output)
if __name__=='__main__':main()
