"""Install the user's five supplied PC Fix files with verified backups."""
from pathlib import Path
from importlib import resources
import hashlib,json,uuid
NAMES={'Silent_Hill_3_PC_Fix.ini','Silent_Hill_3_PC_Fix.dll','d3d8.dll','d3d9on12.dll','dxbcSigner.dll'}
def install_bundled_pcfix(folder: Path, is_game_running) -> tuple[str, ...]:
    from .runtime_setup import atomic_write
    folder=Path(folder)
    bundle=resources.files(__package__).joinpath('third_party','user_pcfix')
    manifest_raw=bundle.joinpath('manifest.json').read_bytes()
    manifest=json.loads(manifest_raw)
    if set(manifest)!=NAMES: raise ValueError('Invalid bundled PC Fix manifest.')
    payload={n:bundle.joinpath(n).read_bytes() for n in sorted(NAMES)}
    for name,data in payload.items():
        if hashlib.sha256(data).hexdigest()!=manifest[name]: raise ValueError('Bundled PC Fix checksum failed: '+name)
    mode=folder/'scripts'/'SH3AP_Mode_Data'
    marker=mode/'bundled_pcfix_v15.installed'
    version=hashlib.sha256(manifest_raw).hexdigest().encode('ascii')
    def safe(path):
        current=path
        while current!=folder:
            if current.is_symlink() or (hasattr(current,'is_junction') and current.is_junction()):
                raise ValueError('Refusing linked PC Fix installation path: '+str(path))
            current=current.parent
    safe(marker)
    installed=marker.is_file() and marker.read_bytes()==version
    changes=[]
    for name,new in payload.items():
        path=folder/name;safe(path)
        old=path.read_bytes() if path.exists() else None
        # Install supplied INI once; preserve later user edits and AP settings.
        if installed and name.endswith('.ini') and old is not None: continue
        if old!=new: changes.append((path,old,new))
    if not changes and installed: return ()
    if is_game_running(): raise ValueError('Close SH3 before installing bundled PC Fix files.')
    mode.mkdir(parents=True,exist_ok=True)
    backup=mode/('BundledPCFixBackups_'+uuid.uuid4().hex);backup.mkdir()
    for path,old,new in changes:
        if old is not None: (backup/(path.name+'.bak')).write_bytes(old)
    (backup/'manifest.json').write_text(json.dumps([{'name':p.name,'existed':o is not None,'old_sha256':hashlib.sha256(o).hexdigest() if o is not None else None,'new_sha256':hashlib.sha256(n).hexdigest()} for p,o,n in changes],indent=2))
    written=[]
    try:
        for path,old,new in changes:
            if is_game_running(): raise ValueError('SH3 started during PC Fix installation; close it and retry.')
            if (path.read_bytes() if path.exists() else None)!=old: raise ValueError('PC Fix file changed during installation: '+path.name)
            atomic_write(path,new);written.append((path,old,new))
        atomic_write(marker,version)
    except Exception:
        for path,old,new in reversed(written):
            if (path.read_bytes() if path.exists() else None)!=new: raise OSError('Concurrent change; original files retained in '+str(backup))
            if old is None: path.unlink()
            else: atomic_write(path,old)
        raise
    return tuple(p.name for p,_,_ in changes)
