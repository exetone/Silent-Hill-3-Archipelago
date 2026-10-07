"""Install a generated custom title using the proven indexed texture layout."""
from pathlib import Path
from importlib import resources
import gzip,hashlib,json,os,shutil,struct,tempfile
PIXELS=512*512*4
TARGET=b'data/pic/sy/sys_title.tex\0'
HEADER_SIZES={bytes.fromhex(k):v for k,v in {'20300000':96,'18300000':96,'08300000':96,'18500000':128,'20500000':128,'08200000':80}.items()}
def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def reject_link(path,root):
    p=path
    while p!=root:
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):raise ValueError('Title path is a link: '+str(path))
        p=p.parent

def locate_title(root):
    root=Path(root);data=root/'data';reject_link(data,root)
    index=data/'arc.arc';reject_link(index,root)
    raw=index.read_bytes()
    if raw.startswith(b'\x1f\x8b'):raw=gzip.decompress(raw)
    ids=[];start=0
    while (pos:=raw.find(TARGET,start))>=0:
        if pos>=8 and struct.unpack_from('<H',raw,pos-8)[0]==3:ids.append(struct.unpack_from('<H',raw,pos-4)[0])
        start=pos+1
    if len(ids)!=1:raise ValueError('Title archive index is missing or ambiguous.')
    matches=[]
    for path in sorted(data.glob('pic*.arc')):
        reject_link(path,root)
        with path.open('rb') as f:
            head=f.read(16)
            if len(head)!=16 or struct.unpack_from('<I',head)[0]!=0x20030507:continue
            count=struct.unpack_from('<I',head,4)[0]
            if ids[0]>=count or 16+count*16>path.stat().st_size:continue
            f.seek(16+ids[0]*16);entry=f.read(16);off,_,size,_=struct.unpack('<4I',entry)
            if off<16+count*16 or not PIXELS+0x80<=size<=PIXELS+0x4000 or off+size>path.stat().st_size:continue
            f.seek(off);tex=f.read(size)
        tail=size-PIXELS;candidates=[]
        for h in range(min(0x4000,size-24)+1):
            if struct.unpack_from('<HH',tex,h+8)!=(512,512):continue
            hs=HEADER_SIZES.get(tex[h+12:h+16])
            if hs and h+hs==tail:candidates.append(h)
        if len(candidates)==1:matches.append((path,off+tail,tex[tail:]))
    if len(matches)!=1:raise ValueError('Title texture layout is unsupported or ambiguous; archive unchanged.')
    return matches[0]

def sync_title(root,is_game_running):
    root=Path(root)
    bundle=resources.files(__package__).joinpath('defaults')
    meta=json.loads(bundle.joinpath('title_manifest.json').read_text())
    pixels=bundle.joinpath('ap_title.rgba').read_bytes()
    if len(pixels)!=PIXELS or hashlib.sha256(pixels).hexdigest()!=meta['sha256']:raise ValueError('Packaged title failed verification.')
    path,offset,old=locate_title(root)
    if old==pixels:return False
    if is_game_running():raise ValueError('Close SH3 and reopen the client to update the title image.')
    before=sha_file(path)
    backups=root/'scripts'/'SH3AP_Mode_Data'/'TitleBackups';reject_link(backups,root);backups.mkdir(parents=True,exist_ok=True)
    backup=backups/(path.name+'.'+before+'.bak');reject_link(backup,root)
    if not backup.exists():shutil.copy2(path,backup)
    if sha_file(backup)!=before:raise OSError('Title backup verification failed; original archive unchanged.')
    fd,name=tempfile.mkstemp(prefix=path.name+'.sh3ap-title-',suffix='.tmp',dir=path.parent);os.close(fd);tmp=Path(name)
    try:
        shutil.copy2(backup,tmp)
        with tmp.open('r+b') as f:
            f.seek(offset);f.write(pixels);f.flush();os.fsync(f.fileno())
        # Verify every byte outside the intended pixel range against the backup.
        with tmp.open('rb') as new,backup.open('rb') as original:
            cursor=0
            while True:
                a=new.read(1024*1024);b=original.read(1024*1024)
                if not a and not b:break
                expected=bytearray(b);lo=max(offset,cursor);hi=min(offset+PIXELS,cursor+len(b))
                if lo<hi:expected[lo-cursor:hi-cursor]=pixels[lo-offset:hi-offset]
                if a!=expected:raise OSError('Title temporary archive verification failed.')
                cursor+=len(b)
        if is_game_running():raise ValueError('SH3 started during title update; archive unchanged.')
        if sha_file(path)!=before:raise OSError('Archive changed during title update; refusing overwrite.')
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)
    return True
