from pathlib import Path
import struct
class PE:
 def __init__(self,path):
  self.data=Path(path).read_bytes();d=self.data;e=struct.unpack_from('<I',d,0x3c)[0];o=e+24;n=struct.unpack_from('<H',d,e+6)[0];so=o+struct.unpack_from('<H',d,e+20)[0];self.base=struct.unpack_from('<I',d,o+28)[0];self.sections=[]
  for i in range(n):
   s=so+i*40;vs,rv,sz,raw=struct.unpack_from('<IIII',d,s+8);self.sections.append((d[s:s+8].rstrip(b'\0').decode(),rv,sz,raw,vs))
 def off(self,va):
  for name,r,sz,raw,vs in self.sections:
   if self.base+r<=va<self.base+r+sz:return raw+va-self.base-r
  raise ValueError(hex(va))
 def at(self,va,n):return self.data[self.off(va):self.off(va)+n]
 def string(self,va):return self.data[self.off(va):].split(b'\0',1)[0]
 def find(self,p,mask=None):
  result=[];mask=mask or b'x'*len(p)
  for name,r,sz,raw,vs in self.sections:
   if name!='.text':continue
   buf=self.data[raw:raw+sz]
   # pick longest fixed prefix
   prefix=p[:next((i for i,x in enumerate(mask) if x!=120),len(mask))]
   pos=0
   while True:
    j=buf.find(prefix,pos)
    if j<0:break
    if j+len(mask)<=len(buf) and all(m!=120 or buf[j+k]==p[k] for k,m in enumerate(mask)):result.append(self.base+r+j)
    pos=j+1
  return result
