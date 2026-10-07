"""Repair the one captured Reset Keybinds relocation defect, not plugin source."""
from pathlib import Path
import argparse,struct,hashlib
from pe_helper import PE
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
assert hashlib.sha256(a.input.read_bytes()).hexdigest()=='c0135d846b4bec8400879416488ca37f6f8cefece75128866c5bef65908c342e'
pe=PE(a.input);b=bytearray(pe.data);e=struct.unpack_from('<I',b,60)[0];rva,size=struct.unpack_from('<II',b,e+24+96+5*8);pos=pe.off(pe.base+rva);end=pos+size;found=[]
while pos<end:
 page,n=struct.unpack_from('<II',b,pos);assert n>=8 and pos+n<=end
 for j in range(pos+8,pos+n,2):
  if page==0x2000 and struct.unpack_from('<H',b,j)[0]==0x311f:found.append(j)
 pos+=n
assert len(found)==1
assert pe.at(pe.base+0x211d,7)==bytes.fromhex('0fb60530400010')
struct.pack_into('<H',b,found[0],0x3120)
assert hashlib.sha256(b).hexdigest()=='ca6fb3581ffa990ec0e43a366356ee897d1144440b61f7322c309c410c00979f'
a.output.write_bytes(b)
