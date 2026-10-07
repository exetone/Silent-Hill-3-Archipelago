from pathlib import Path
import argparse,struct,json,hashlib
from pe_helper import PE
parser=argparse.ArgumentParser(description='Apply V16 menu alignment to the exact pre-V16 UI binary')
parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
assert hashlib.sha256(args.input.read_bytes()).hexdigest()=='18cae26e5746b8e7faf6dc4643f50fc816781c1b67fe193baa944366b9f65b08'
pe=PE(args.input);blob=bytearray(pe.data)
e=struct.unpack_from('<I',blob,60)[0];opt=e+24;ns=struct.unpack_from('<H',blob,e+6)[0];sh=opt+struct.unpack_from('<H',blob,e+20)[0]+40*(ns-1)
vs,rva,rs,raw=struct.unpack_from('<IIII',blob,sh+8);flags=struct.unpack_from('<I',blob,sh+36)[0];assert flags&0x20000000
cursor=(vs+15)&~15;start=cursor
# Replace complete MOV-immediate + MOVD instruction pairs with position-independent
# thunks. Original menu X is at entry ESP+0x8c; PUSHFD/PUSHAD/SUB 0x80 adds 0xa4.
patches=[(0x10021c21,1500.,1620.,'edx','xmm2'),(0x10021c2f,1900.,2020.,'edx','xmm2'),
 (0x10021c90,1500.,1620.,'eax','xmm0'),(0x10021c99,1900.,2020.,'eax','xmm2'),
 (0x10021cd2,1512.,1632.,'eax','xmm0'),(0x10021cfa,1776.,1896.,'eax','xmm0')]
log=[]
for addr,old,new,reg,xmm in patches:
 mov=bytes([0xba if reg=='edx' else 0xb8])+struct.pack('<f',old)
 mod={('edx','xmm2'):0xd2,('eax','xmm0'):0xc0,('eax','xmm2'):0xd0}[(reg,xmm)]
 expected=mov+bytes.fromhex('660f6e')+bytes([mod]);off=pe.off(addr);assert blob[off:off+9]==expected
 thunkaddr=pe.base+rva+cursor
 code=bytes([mov[0]])+struct.pack('<f',new)+expected[5:]
 code+=bytes.fromhex('f30f58')+bytes([0x84 if xmm=='xmm0' else 0x94])+bytes.fromhex('2430010000')
 code+=b'\xe9'+struct.pack('<i',addr+9-(thunkaddr+len(code)+5))
 assert cursor+len(code)<=rs;assert not any(blob[raw+cursor:raw+cursor+len(code)])
 blob[raw+cursor:raw+cursor+len(code)]=code
 blob[off:off+9]=b'\xe9'+struct.pack('<i',thunkaddr-(addr+5))+b'\x90'*4
 log.append({'site':hex(addr),'old':old,'new_relative_x':new,'thunk':hex(thunkaddr),'length':len(code),'bytes':code.hex()});cursor+=len(code)
# Bindings and Reset draw at 1620..2120 with text at 1632; match the UI's
# shared mouse hit-test table, which still held their older 1500..1900 bounds.
for row in (4,5,6):
 off=pe.off(0x10020b80+16*row);assert struct.unpack_from('<2f',blob,off)==(1500.,1900.)
 struct.pack_into('<2f',blob,off,1620.,2120.)
struct.pack_into('<I',blob,sh+8,max(vs,cursor))
# SizeOfImage already covers raw section tail; ensure this remains true.
assert struct.unpack_from('<I',blob,opt+56)[0]>=((rva+cursor+4095)&~4095)
args.output.write_bytes(blob)
