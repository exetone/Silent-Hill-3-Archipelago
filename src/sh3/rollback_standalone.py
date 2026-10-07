"""One-time removal of V8-V13 standalone integration; preserve all save data."""
from pathlib import Path
import hashlib
import json
import uuid

def rollback_standalone(folder: Path, is_game_running) -> tuple[str, ...]:
    from .runtime_setup import atomic_write
    folder = Path(folder)
    mode = folder / 'scripts' / 'SH3AP_Mode_Data'
    done = mode / 'standalone_rollback_v14.complete'
    def safe(path):
        current = path
        while current != folder:
            if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
                raise ValueError('Standalone rollback refuses linked path: ' + str(path))
            current = current.parent
    safe(done)
    names = [folder / 'scripts' / 'SH3AP_Standalone_Save.asi',
             folder / 'scripts' / 'SH3AP_Standalone_Save.asi.sh3ap-disabled',
             folder / 'scripts' / 'SH3AP_Disabled_Runtime' / 'SH3AP_Standalone_Save.asi',
             folder / 'scripts' / 'SH3AP_Disabled_Runtime' / 'SH3AP_Standalone_Save.asi.sh3ap-disabled',
             mode / 'standalone_save_v1.enabled', folder / 'SH3AP_Standalone.ini']
    for path in names: safe(path)
    active = [p for p in names if p.exists()]
    if not active:
        return ()
    if is_game_running():
        raise ValueError('Close SH3 before undoing standalone changes, then reopen the client.')
    changes = [(p, p.read_bytes(), None) for p in active]
    notes = []
    if not done.exists():
        backups = mode / 'StandaloneDisplayBackups'
        safe(backups)
        for profile in ('savedataAP', 'savedata_Vanilla'):
            target = folder / profile / 'disp.ini'
            safe(target)
            candidates = []
            for p in backups.glob(profile + '.disp.ini.*.bak'):
                safe(p)
                raw = p.read_bytes()
                if p.name != profile + '.disp.ini.' + hashlib.sha256(raw).hexdigest()[:16] + '.bak':
                    raise ValueError('Display backup checksum mismatch: ' + p.name)
                candidates.append((p.stat().st_mtime_ns, p.name, raw))
            if candidates:
                candidates.sort()
                if len(candidates)>1 and candidates[0][0]==candidates[1][0]:
                    raise ValueError('Display backup order is ambiguous; no rollback files changed.')
                desired = candidates[0][2]
                previous = target.read_bytes() if target.exists() else None
                if previous != desired:
                    changes.append((target, previous, desired))
                notes.append('Restored earliest saved display configuration: ' + profile)
            else:
                notes.append('No original display backup for ' + profile + '; current disp.ini retained.')
    mode.mkdir(parents=True, exist_ok=True)
    archive = mode / ('StandaloneRollback_' + uuid.uuid4().hex)
    archive.mkdir()
    journal = []
    for n,(path,old,new) in enumerate(changes):
        if old is not None:
            (archive / (str(n)+'.bak')).write_bytes(old)
        journal.append({'path':str(path.relative_to(folder)), 'backup':str(n)+'.bak' if old is not None else None,
                        'action':'remove' if new is None else 'restore_display'})
    (archive/'manifest.json').write_text(json.dumps(journal,indent=2))
    written = []
    try:
        for path,old,new in changes:
            if is_game_running(): raise ValueError('SH3 started during rollback. Close it and retry.')
            if (path.read_bytes() if path.exists() else None) != old:
                raise ValueError('A file changed during rollback: '+str(path))
            if new is None: path.unlink()
            else: atomic_write(path,new)
            written.append((path,old,new))
        atomic_write(done, b'Standalone removed. External Steam006 required.\r\n')
    except Exception:
        for path,old,new in reversed(written):
            if (path.read_bytes() if path.exists() else None) != new:
                raise OSError('Concurrent file change; originals retained in '+str(archive))
            if old is None: path.unlink(missing_ok=True)
            else: atomic_write(path,old)
        raise
    notes.append('Standalone plugin/config archived in '+str(archive))
    return tuple(notes)
