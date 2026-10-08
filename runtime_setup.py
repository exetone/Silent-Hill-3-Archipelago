"""Verified native runtime installation from packaged APWorld resources."""
from __future__ import annotations
import hashlib
import ctypes
from ctypes import wintypes
from importlib import resources
import json
import os
import re
import struct
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

EXE_SHA256 = '339377564d7764d34e94eb4e4f7dadbacb233f625ca66321d08c22f6b813ff57'
PREVIOUS_207_AP_EXE_SHA256 = 'f392c40f8fec8875de8694abeeaffdc843b7f5627128a7dfa3b5230662de80ce'
PREVIOUS_206_AP_EXE_SHA256 = '44559c26044f0777fe3bd1764bfb795e13557b2514e1c9c6ed09b4ada8d6fe79'
PREVIOUS_205_AP_EXE_SHA256 = '628eee68f65be396630d70cfaaf2034b0e3f756ea35ceb62425f1e5e6c430b6c'
PREVIOUS_203_AP_EXE_SHA256 = '1e00230decc2e2ccfec8b4351c10f749efe348292609a67fecdfc20ca972b5f4'
PREVIOUS_193_AP_EXE_SHA256 = 'b898bcfe92c7fbefe2f39fe6ddb3810a271d956190127de36dcb6f70578d9617'
CANONICAL_AP_EXE_SHA256 = '01ee53535712f640215d07f3cbb65499c14bdbb71063eda67c03c60065ee400e'
BROKEN_186_AP_EXE_SHA256 = '76e4dc8da85cc7cf9d7f1f37b10483d18d0937aa6beba7066bdec99dcbb09974'
VANILLA_EXE_SHA256 = '8ff8f74806f55843b9bc277508b17c8926999f292c65dbe7949325087d460918'
DISABLED_MARKER = 'SH3AP_DISABLED.flag'
DISABLED_RUNTIME_DIR = 'SH3AP_Disabled_Runtime'
DISABLED_RUNTIME_SUFFIX = '.sh3ap-disabled'
MODE_TOOL_NAMES = ('SH3AP_Mode_Toggle.bat', 'SH3AP_Uninstall.bat', 'SH3AP_Loader_Compatibility.bat')
DEFAULT_SETTING_HASHES = {
    'disp.ini': '5a698ff52aa83bd521e8888fe4dba2e1efcd3188968a77d4aca777e00a7534e9',
    'key.ini': '28b59436d886c1898c41331411431a3b4f12d25d46ce30672c48956d0b41d51c',
}
PCFIX_REQUIRED_FILES = ('Silent_Hill_3_PC_Fix.dll', 'Silent_Hill_3_PC_Fix.ini', 'd3d8.dll')
PCFIX_REQUIRED_AP_VALUES = {
    'NewSaveSystem': '1',
    'ActionLevel': '2',
    'RiddleLevel': '1',
    'UnlockExtraMenuOptions': '1',
}
PCFIX_OPTIONAL_LEGACY_AP_VALUES: dict[str, str] = {}
AP_SYSTEM_DATA_NAME = 'ap_data.sys'
AP_SYSTEM_DATA_SHA256 = '83521ce0bdfa2f06209728e085446f61a888d2f2a9c6ffafeee777c1c396f06b'
AP_SYSTEM_DATA_SIZE = 0x74
AP_SYSTEM_DATA_HEADER = bytes.fromhex('21100220340000004000000034000000')
AP_SYSTEM_UNLOCK_VALUES = ((0x44, 0xFE), (0x45, 0x3B), (0x48, 0x01))
AP_SYSTEM_UNLOCK_MARKER = 'ap_system_unlock_v4_no_douglas.json'

# Keep the supported 116-byte NewSaveSystem data.sys format.
# Bytes 0x44/0x45 form the stock extra-content bitfield read at 0x70E675C.
# The historical FE/3F state sets bit 10 (0x0400), the Naked Douglas state.
# AP therefore uses FE/3B/01: identical except bit 10 is clear. The executable
# also keeps ID 10 unavailable and the two New Game sound selectors on 0x83.

# XInput Plus is the user-confirmed controller trigger solution for this SH3 build.
# 0dd14lab explicitly prohibits redistribution without permission, so SH3AP never
# packages or downloads XInput Plus itself. When the exact tested XInput Plus
# DirectInput8 proxy is already installed as dinput8.dll, SH3AP safely backs it
# up and chains it as dinput8Hooked.dll before installing its own MIT-licensed
# Ultimate ASI Loader. Toggle/uninstall leave this external controller chain active.
XINPUTPLUS_HOME_PAGE = 'https://0dd14lab.net/xinputplus/'
XINPUTPLUS_TRIGGER_FILES = ('dinput8Hooked.dll', 'Dinput.dll', 'XInput1_3.dll', 'XInputPlus.ini')
# Legacy exact hash retained for the older 4.15.2 proxy we originally validated.
XINPUTPLUS_DINPUT8_SHA256 = '3e0441bf07bd6529365d6c2b595007299bdf384299f3a0d325413f6be50a1a2b'
# Current official XInput Plus is 4.16.1 (2023-08-29). Its deployed DirectInput8
# proxy differs byte-for-byte from the older 4.15.2 proxy, so fresh setup must
# identify genuine XInput Plus by its embedded vendor/product metadata instead of
# hard-locking the rename to a single historical SHA-256.
XINPUTPLUS_CURRENT_VERSION = '4.16.1'
UAL_DINPUT8_SHA256 = 'd5a059aa467a7a7127c8f6169f79fa63ff0f55986ee9eb2fd9a281bebf2aa2e6'
UAL_RESOURCE_DIR = ('third_party', 'ultimate_asi_loader')
LOADER_DEFERRED_MARKER = 'loader_deferred.flag'
LOADER_STANDARD_MARKER = 'loader_standard.flag'
KNOWN_LIVE_PCFIX_SHA256 = '3ad71981436184e669408b751e2b3170e856119de6cd68c4035193a6364f20ee'
KNOWN_LIVE_D3D8_SHA256 = 'ed6d4324146c525ec1de0662213ee2ba2b6dc311898f0977244536cd78ac1071'
XINPUTPLUS_DINPUT_SHA256 = 'e6ad898fdf197ffc71ed9a80912f4dc2b178331ebb1a16092cd256547dd3a6b2'
XINPUTPLUS_XINPUT13_SHA256 = '82c45d2a63ae7cc919afa86e9bc3dc0e57b0d4640e5dd68c5232cf67585028e3'
MAX_NATIVE_GAME_ROOT_CHARS = 180
UAL_ALT_PROXY_NAMES = (
    'd3d9.dll', 'd3d10.dll', 'd3d11.dll', 'd3d12.dll', 'dxgi.dll', 'ddraw.dll',
    'dsound.dll', 'msacm32.dll', 'msvfw32.dll', 'version.dll', 'wininet.dll',
    'winmm.dll', 'winhttp.dll', 'xlive.dll', 'binkw32.dll', 'bink2w32.dll',
    'vorbisFile.dll', 'xinput1_1.dll', 'xinput1_2.dll', 'xinput1_4.dll',
    'xinput9_1_0.dll', 'xinputuap.dll',
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def bundled_files() -> dict[str, bytes]:
    root = resources.files(__package__).joinpath('runtime')
    manifest = json.loads(root.joinpath('manifest.json').read_text(encoding='utf-8'))
    result = {}
    for name, expected in manifest.items():
        if Path(name).name != name or not name.startswith('SH3AP') or not name.endswith('.asi'):
            raise ValueError('Invalid packaged runtime filename')
        data = root.joinpath(name).read_bytes()
        if digest(data) != expected:
            raise ValueError(f'Packaged runtime verification failed: {name}')
        result[name] = data
    return result

def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def runtime_disabled(folder: Path) -> bool:
    folder = folder.expanduser().resolve()
    return (folder / 'scripts' / DISABLED_MARKER).is_file()


def show_setup_message(title: str, message: str, *, error: bool = False) -> None:
    """Show a dependency-free native Windows setup message when possible."""
    if os.name != 'nt':
        return
    try:
        flags = 0x00000000 | (0x00000010 if error else 0x00000040)  # MB_OK | ERROR/INFO
        ctypes.windll.user32.MessageBoxW(None, str(message), str(title), flags)
    except Exception:
        pass


def _choose_windows_folder(title: str) -> str | None:
    """Native SHBrowseForFolder picker; avoids tkinter in frozen Archipelago builds."""
    if os.name != 'nt':
        return None

    class BROWSEINFOW(ctypes.Structure):
        _fields_ = [
            ('hwndOwner', wintypes.HWND),
            ('pidlRoot', ctypes.c_void_p),
            ('pszDisplayName', wintypes.LPWSTR),
            ('lpszTitle', wintypes.LPCWSTR),
            ('ulFlags', wintypes.UINT),
            ('lpfn', ctypes.c_void_p),
            ('lParam', wintypes.LPARAM),
            ('iImage', ctypes.c_int),
        ]

    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32
    display = ctypes.create_unicode_buffer(260)
    info = BROWSEINFOW()
    info.hwndOwner = None
    info.pidlRoot = None
    info.pszDisplayName = ctypes.cast(display, wintypes.LPWSTR)
    info.lpszTitle = title
    info.ulFlags = 0x0001 | 0x0040  # filesystem directories + modern dialog
    info.lpfn = None
    info.lParam = 0
    info.iImage = 0
    shell32.SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFOW)]
    shell32.SHBrowseForFolderW.restype = ctypes.c_void_p
    shell32.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, wintypes.LPWSTR]
    shell32.SHGetPathFromIDListW.restype = wintypes.BOOL
    pidl = shell32.SHBrowseForFolderW(ctypes.byref(info))
    if not pidl:
        return None
    try:
        path = ctypes.create_unicode_buffer(32768)
        if not shell32.SHGetPathFromIDListW(pidl, path):
            return None
        return path.value or None
    finally:
        try:
            ole32.CoTaskMemFree(ctypes.c_void_p(pidl))
        except Exception:
            pass


def steam006_pcfix_sha256(folder: Path) -> str | None:
    dll = folder.expanduser().resolve() / 'Silent_Hill_3_PC_Fix.dll'
    return digest(dll.read_bytes()) if dll.is_file() else None


def ensure_game_folder_writable(folder: Path) -> None:
    """Fail before mode/save changes if the selected installation cannot be written safely."""
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise ValueError('The selected Silent Hill 3 folder does not exist.')
    probe = folder / ('.sh3ap_write_test_' + uuid.uuid4().hex)
    try:
        atomic_write(probe, b'SH3AP write test\r\n')
        if probe.read_bytes() != b'SH3AP write test\r\n':
            raise OSError('write verification failed')
    except Exception as exc:
        raise ValueError(
            'The Silent Hill 3 folder is not writable. Move the game to a normal user-writable folder '
            '(for example C:\\Games\\Silent Hill 3) or fix its permissions, then reopen the client.'
        ) from exc
    finally:
        try:
            probe.unlink(missing_ok=True)
        except Exception:
            pass


def _pe32_x86_dll(path: Path) -> bool:
    """Return True only for a normal 32-bit x86 PE DLL."""
    try:
        data = path.read_bytes()
        if len(data) < 0x100 or data[:2] != b'MZ':
            return False
        pe = struct.unpack_from('<I', data, 0x3C)[0]
        if pe < 0x40 or pe + 0x18 >= len(data) or data[pe:pe + 4] != b'PE\0\0':
            return False
        machine = struct.unpack_from('<H', data, pe + 4)[0]
        characteristics = struct.unpack_from('<H', data, pe + 22)[0]
        optional_magic = struct.unpack_from('<H', data, pe + 24)[0]
        return machine == 0x014C and optional_magic == 0x010B and bool(characteristics & 0x2000)
    except (OSError, ValueError, struct.error):
        return False


def ensure_game_path_compatible(folder: Path) -> None:
    """Reject paths the native ANSI/MAX_PATH-era runtime cannot safely represent."""
    folder = folder.expanduser().resolve()
    text = str(folder)
    if len(text) > MAX_NATIVE_GAME_ROOT_CHARS:
        raise ValueError(
            f'The Silent Hill 3 folder path is too long for SH3AP native state-file handling ({len(text)} characters). '
            'Move the game to a shorter local path such as C:\\Games\\Silent Hill 3, then reopen the client.'
        )
    if os.name == 'nt':
        if text.startswith('\\\\'):
            raise ValueError('SH3AP requires a local Windows game folder; network/UNC paths are not supported.')
        try:
            encoded = text.encode('mbcs', errors='strict')
            roundtrip = encoded.decode('mbcs', errors='strict')
        except UnicodeError as exc:
            raise ValueError(
                'The Silent Hill 3 folder contains characters that SH3AP native ANSI file APIs cannot represent on this Windows locale. '
                'Move the game to a simple local path such as C:\\Games\\Silent Hill 3.'
            ) from exc
        if roundtrip != text:
            raise ValueError(
                'The Silent Hill 3 folder does not round-trip through this Windows ANSI code page. '
                'Move the game to a simple local path such as C:\\Games\\Silent Hill 3.'
            )
        # AP/Vanilla save separation uses directory junctions. FAT/exFAT and some
        # network/removable filesystems cannot provide the required reparse-point semantics.
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.GetVolumePathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
            kernel32.GetVolumePathNameW.restype = wintypes.BOOL
            kernel32.GetVolumeInformationW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
            kernel32.GetVolumeInformationW.restype = wintypes.BOOL
            volume = ctypes.create_unicode_buffer(32768)
            if not kernel32.GetVolumePathNameW(str(folder), volume, len(volume)):
                raise OSError(ctypes.get_last_error())
            fsname = ctypes.create_unicode_buffer(64)
            serial = wintypes.DWORD(); max_comp = wintypes.DWORD(); flags = wintypes.DWORD()
            if not kernel32.GetVolumeInformationW(volume.value, None, 0, ctypes.byref(serial), ctypes.byref(max_comp), ctypes.byref(flags), fsname, len(fsname)):
                raise OSError(ctypes.get_last_error())
            if fsname.value.upper() not in {'NTFS', 'REFS'}:
                raise ValueError(
                    f'SH3AP save-profile switching requires an NTFS/ReFS local volume; this game folder is on {fsname.value or "an unsupported filesystem"}. '
                    'Move the game to an NTFS/ReFS drive before enabling AP mode.'
                )
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError('SH3AP could not verify that the game drive supports Windows directory junctions.') from exc


def _active_asi_conflicts(folder: Path) -> tuple[str, ...]:
    """List ASIs UAL can load that are not the nine packaged SH3AP files."""
    folder = folder.expanduser().resolve()
    allowed = set(bundled_files())
    conflicts: list[str] = []
    for base_name in ('', 'scripts', 'plugins'):
        base = folder if not base_name else folder / base_name
        if not base.is_dir():
            continue
        for p in base.glob('*.asi'):
            if not p.is_file():
                continue
            rel = str(p.relative_to(folder))
            if base_name == 'scripts' and p.name in allowed:
                continue
            conflicts.append(rel)
    update = folder / 'update'
    if update.exists():
        if update.is_symlink() or not update.is_dir():
            conflicts.append('update (not a normal folder)')
        elif any(update.iterdir()):
            # UAL uses update as an overload source even without [FileLoader].
            conflicts.append('update\\ (non-empty UAL overload folder)')
    return tuple(sorted(conflicts, key=str.casefold))


def ensure_no_foreign_scripts_asis(folder: Path) -> tuple[str, ...]:
    """Backward-compatible name for the full UAL plugin-source preflight."""
    conflicts = _active_asi_conflicts(folder)
    if conflicts:
        raise ValueError(
            'Other files are present in Ultimate ASI Loader active plugin/overload locations and can conflict with SH3AP startup: '
            + ', '.join(conflicts)
            + '. Move/disable those mods, then reopen Silent Hill 3 Client.'
        )
    return conflicts


def ensure_no_alternate_proxy_loaders(folder: Path) -> tuple[str, ...]:
    """Reject secondary UAL/proxy entry points that can create a second injection chain."""
    folder = folder.expanduser().resolve()
    found = [name for name in UAL_ALT_PROXY_NAMES if (folder / name).is_file()]
    if (folder / 'wndmode.ini').is_file():
        found.append('wndmode.ini (Ultimate ASI Loader built-in windowed-mode hook)')
    present = tuple(sorted(found, key=str.casefold))
    if present:
        raise ValueError(
            'Additional local proxy/hook features are present and may create a second injection path when AP mode is active: '
            + ', '.join(present)
            + '. SH3AP supports Steam006 d3d8.dll, its own dinput8.dll loader, and an optional verified XInput Plus chain; move/disable the other hook layer temporarily.'
        )
    return present


def ensure_no_ual_file_overload_config(folder: Path) -> None:
    """Reject custom UAL file-overload paths; SH3AP does not require FileLoader."""
    folder = folder.expanduser().resolve()
    for path in (folder / 'dinput8.ini', folder / 'global.ini', folder / 'scripts' / 'global.ini', folder / 'plugins' / 'global.ini'):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8-sig', errors='replace')
        except OSError:
            continue
        m = re.search(r'(?im)^[ \t]*OverloadFromFolder[ \t]*=[ \t]*([^\r\n;#]+)', text)
        if m and m.group(1).strip():
            active: list[str] = []
            for item in m.group(1).split('|'):
                value = item.strip().strip('\"')
                if not value:
                    continue
                candidate = Path(value) if os.path.isabs(value) else folder / value
                if candidate.is_dir() and any(candidate.iterdir()):
                    active.append(value)
            if active:
                raise ValueError(
                    f'{path.name} enables active Ultimate ASI Loader file overloading ({" | ".join(active)!r}). '
                    'Disable that FileLoader/total-conversion setting before enabling SH3AP.'
                )


def loader_timing_mode(folder: Path) -> str:
    """Return the effective Ultimate ASI Loader timing mode for this install.

    Explicit per-PC markers always win. Otherwise preserve an already-working
    DontLoadFromDllMain value when all existing UAL configs agree. On a fresh
    install (or an ambiguous old config), use the live-proven Standard timing.

    Do not infer loader timing from the Steam006 DLL hash: live testing showed
    that an unfamiliar PC Fix build can launch correctly until the AP client
    rewrites loader/config state, so PC Fix identity is diagnostic information,
    not a safe loader-timing selector.
    """
    folder = folder.expanduser().resolve()
    mode_data = folder / 'scripts' / 'SH3AP_Mode_Data'
    deferred = mode_data / LOADER_DEFERRED_MARKER
    standard = mode_data / LOADER_STANDARD_MARKER
    if deferred.is_file() and standard.is_file():
        raise ValueError(
            'Both SH3AP loader timing overrides are present. Remove one of '
            'loader_deferred.flag / loader_standard.flag or run SH3AP_Loader_Compatibility.bat.'
        )
    if deferred.is_file():
        return 'deferred'
    if standard.is_file():
        return 'standard'

    values: list[str] = []
    for path in (
        folder / 'dinput8.ini',
        folder / 'global.ini',
        folder / 'scripts' / 'global.ini',
        folder / 'plugins' / 'global.ini',
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        values.extend(v.strip() for v in re.findall(
            r'(?im)^[ \t]*DontLoadFromDllMain[ \t]*=[ \t]*([^\r\n;#]+)', text
        ))
    valid = [v for v in values if v in {'0', '1'}]
    if valid and len(valid) == len(values) and len(set(valid)) == 1:
        return 'existing-deferred' if valid[0] == '1' else 'existing-standard'
    return 'standard-default'


def loader_deferred_requested(folder: Path) -> bool:
    return loader_timing_mode(folder) in ('deferred', 'existing-deferred')


def steam006_pcfix_version(folder: Path) -> tuple[int, int, int, int] | None:
    """Read the Windows fixed-file version from Steam006's DLL when available."""
    if os.name != 'nt':
        return None
    dll = (folder.expanduser().resolve() / 'Silent_Hill_3_PC_Fix.dll')
    if not dll.is_file():
        return None
    try:
        version = ctypes.WinDLL('version', use_last_error=True)
        version.GetFileVersionInfoSizeW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(wintypes.DWORD)]
        version.GetFileVersionInfoSizeW.restype = wintypes.DWORD
        version.GetFileVersionInfoW.argtypes = [ctypes.c_wchar_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
        version.GetFileVersionInfoW.restype = wintypes.BOOL
        version.VerQueryValueW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p,
                                           ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.UINT)]
        version.VerQueryValueW.restype = wintypes.BOOL
        dummy = wintypes.DWORD()
        size = version.GetFileVersionInfoSizeW(str(dll), ctypes.byref(dummy))
        if not size:
            return None
        buf = ctypes.create_string_buffer(size)
        if not version.GetFileVersionInfoW(str(dll), 0, size, buf):
            return None
        ptr = ctypes.c_void_p()
        length = wintypes.UINT()
        if not version.VerQueryValueW(buf, '\\', ctypes.byref(ptr), ctypes.byref(length)) or length.value < 52:
            return None
        # VS_FIXEDFILEINFO: signature/struct version/file version MS+LS are first 16 bytes.
        raw = ctypes.string_at(ptr.value, min(length.value, 52))
        signature, _struct, ms, ls = struct.unpack_from('<IIII', raw, 0)
        if signature != 0xFEEF04BD:
            return None
        return (ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF)
    except Exception:
        return None


def steam006_pcfix_status(folder: Path) -> tuple[bool, list[str]]:
    """Return whether the Steam006 PC Fix dependency is present and compatible.

    SH3AP does not redistribute the third-party PC Fix. We require the main
    proxy, configuration and PC Fix DLL to exist before any SH3AP setup files
    are written. AP's post-clear/check unlock state is reproduced by SH3AP in
    the AP-only system-data file rather than relying on a removed PC Fix key.
    """
    folder = folder.expanduser().resolve()
    missing = [name for name in PCFIX_REQUIRED_FILES if not (folder / name).is_file()]
    if missing:
        return False, missing
    # SH3 is a 32-bit process. Catch accidentally deployed x64/invalid PC Fix
    # binaries before AP mode adds another native loader/hook layer. Vanilla
    # usually catches this too, but a fresh setup should fail closed here.
    invalid = [name for name in ('Silent_Hill_3_PC_Fix.dll', 'd3d8.dll')
               if not _pe32_x86_dll(folder / name)]
    if invalid:
        return False, [name + ' (not a valid x86 PE32 DLL)' for name in invalid]
    # First-run dependency detection checks files/architecture only. The raw
    # NewSaveSystem requirement is validated separately before AP system data
    # is prepared.
    return True, []

def _pcfix_assignment_matches(text: str, key: str) -> list[re.Match[str]]:
    pattern = re.compile(r'(?m)^(\s*' + re.escape(key) + r'\s*=\s*)([^\r\n]*)(\r?\n|$)')
    return list(pattern.finditer(text))


def _pcfix_numeric_assignment(raw: bytes, key: str) -> list[re.Match[bytes]]:
    return list(re.finditer(
        rb'(?m)^([ \t]*' + re.escape(key.encode('ascii')) + rb'[ \t]*=[ \t]*)([0-9]+)([^\r\n]*)(\r?\n|$)',
        raw,
    ))


def validate_ap_save_system_support(folder: Path) -> None:
    """Verify the exact Steam006 settings SH3AP requires after bootstrap."""
    folder = folder.expanduser().resolve()
    ini = folder / 'Silent_Hill_3_PC_Fix.ini'
    if not ini.is_file():
        raise ValueError('Silent_Hill_3_PC_Fix.ini is missing.')
    raw = ini.read_bytes()
    for key, expected in PCFIX_REQUIRED_AP_VALUES.items():
        matches = _pcfix_numeric_assignment(raw, key)
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one {key} setting; found {len(matches)}.')
        if matches[0].group(2).decode('ascii') != expected:
            raise ValueError(f'Steam006 {key} is not set to the required SH3AP value {expected}.')
    for key, expected in PCFIX_OPTIONAL_LEGACY_AP_VALUES.items():
        matches = _pcfix_numeric_assignment(raw, key)
        if len(matches) > 1:
            raise ValueError(f'Expected at most one legacy {key} setting; found {len(matches)}.')
        if matches and matches[0].group(2).decode('ascii') != expected:
            raise ValueError(f'Legacy Steam006 {key} is present but is not set to {expected}.')


def ensure_ap_pcfix_settings(folder: Path, is_game_running=None) -> tuple[str, ...]:
    """Apply only SH3AP-required Steam006 numeric assignments, preserving all other bytes.

    Required on every AP-client launch:
      NewSaveSystem=1, ActionLevel=2, RiddleLevel=1, UnlockExtraMenuOptions=1.

    UnlockEverything is deliberately never changed. Steam006 removed that legacy
    option, and SH3AP already reproduces the required AP-only unlock state in its
    own verified data.sys.

    Returns the names of assignments that changed.
    """
    folder = folder.expanduser().resolve()
    ini = folder / 'Silent_Hill_3_PC_Fix.ini'
    if not ini.is_file():
        raise ValueError('Silent_Hill_3_PC_Fix.ini is missing.')
    raw = ini.read_bytes()

    desired = dict(PCFIX_REQUIRED_AP_VALUES)
    optional = dict(PCFIX_OPTIONAL_LEGACY_AP_VALUES)
    replacements: list[tuple[int, int, bytes, str]] = []
    changed: list[str] = []

    for key, value in desired.items():
        matches = _pcfix_numeric_assignment(raw, key)
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one {key} setting; found {len(matches)}.')
        m = matches[0]
        if m.group(2) != value.encode('ascii'):
            replacements.append((m.start(2), m.end(2), value.encode('ascii'), key))
            changed.append(key)

    for key, value in optional.items():
        matches = _pcfix_numeric_assignment(raw, key)
        if len(matches) > 1:
            raise ValueError(f'Expected at most one legacy {key} setting; found {len(matches)}.')
        if matches and matches[0].group(2) != value.encode('ascii'):
            m = matches[0]
            replacements.append((m.start(2), m.end(2), value.encode('ascii'), key))
            changed.append(key)

    if not replacements:
        return ()
    if callable(is_game_running) and is_game_running():
        raise ValueError(
            'SH3AP needs to apply its required Steam006 AP settings while Silent Hill 3 is closed. '
            'Close the game and reopen Silent Hill 3 Client; no PC Fix setting was changed.'
        )

    scripts = folder / 'scripts'
    if scripts.exists() and (scripts.is_symlink() or (hasattr(scripts, 'is_junction') and scripts.is_junction())):
        raise ValueError('scripts is a link; refusing to store the PC Fix configuration backup there.')
    backup_dir = scripts / 'SH3AP_Mode_Data' / 'ExternalConfigBackups'
    if backup_dir.exists() and (backup_dir.is_symlink() or (hasattr(backup_dir, 'is_junction') and backup_dir.is_junction())):
        raise ValueError('ExternalConfigBackups is a link; refusing to write the PC Fix configuration backup there.')
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f'Silent_Hill_3_PC_Fix.ini.before_SH3AP_AP_settings.{digest(raw)[:12]}.bak'
    if not backup.exists():
        atomic_write(backup, raw)

    updated = raw
    for begin, finish, value, _key in sorted(replacements, reverse=True):
        updated = updated[:begin] + value + updated[finish:]
    atomic_write(ini, updated)

    try:
        validate_ap_save_system_support(folder)
    except Exception:
        atomic_write(ini, raw)
        raise OSError('Could not verify required Steam006 AP settings; the exact original PC Fix INI was restored.')

    # Rebuild the expected byte stream independently and require exact equality.
    expected = raw
    for begin, finish, value, _key in sorted(replacements, reverse=True):
        expected = expected[:begin] + value + expected[finish:]
    if ini.read_bytes() != expected:
        atomic_write(ini, raw)
        raise OSError('Unexpected PC Fix INI change detected; the exact original PC Fix INI was restored.')
    return tuple(changed)


def _valid_ap_system_data(data: bytes) -> bool:
    return len(data) == AP_SYSTEM_DATA_SIZE and data[:len(AP_SYSTEM_DATA_HEADER)] == AP_SYSTEM_DATA_HEADER


def _load_ap_system_template() -> bytes:
    data = resources.files(__package__).joinpath('defaults').joinpath(AP_SYSTEM_DATA_NAME).read_bytes()
    if digest(data) != AP_SYSTEM_DATA_SHA256 or not _valid_ap_system_data(data):
        raise ValueError('Packaged AP system-data template verification failed.')
    return data


def _apply_ap_system_unlock_values(data: bytes) -> tuple[bytes, list[tuple[int, int, int]]]:
    if not _valid_ap_system_data(data):
        raise ValueError('System data is not the supported Steam006 NewSaveSystem format.')
    out = bytearray(data)
    changes: list[tuple[int, int, int]] = []
    for offset, value in AP_SYSTEM_UNLOCK_VALUES:
        before = out[offset]
        after = value
        if after != before:
            out[offset] = after
            changes.append((offset, before, after))
    return bytes(out), changes


def ensure_ap_system_unlock_state(folder: Path, is_game_running=None) -> tuple[bool, bool, str]:
    """Prepare the AP profile in Steam006's supported NewSaveSystem data format.

    Bytes 0x44/0x45/0x48 use FE/3B/01: the historical fully-unlocked state with
    only bit 10 (Naked Douglas) cleared. 0.0.208's reversible executable patch supplies the actual bonus/post-clear
    availability through SH3's dedicated 0x60D020 function. Incompatible legacy
    296-byte system files are preserved before replacement. Vanilla system data
    and numbered saves are never modified.

    Returns (created_or_replaced, patched, source).
    """
    folder = folder.expanduser().resolve()
    validate_ap_save_system_support(folder)

    ap_dir = folder / 'savedataAP'
    if (not ap_dir.is_dir()) or ap_dir.is_symlink() or (hasattr(ap_dir, 'is_junction') and ap_dir.is_junction()):
        raise ValueError('savedataAP is missing or is not a real folder; refusing to guess the AP save profile.')
    data_sys = ap_dir / 'data.sys'
    if data_sys.is_symlink():
        raise ValueError('savedataAP/data.sys is a link; refusing to modify it.')

    template = _load_ap_system_template()
    mode_data = folder / 'scripts' / 'SH3AP_Mode_Data'
    if mode_data.is_symlink():
        raise ValueError('SH3AP_Mode_Data is a link; refusing to write AP system-data state there.')
    mode_data.mkdir(parents=True, exist_ok=True)
    backup_dir = mode_data / 'APSystemDataBackups'
    marker = mode_data / AP_SYSTEM_UNLOCK_MARKER

    created_or_replaced = False
    patched = False
    source = 'existing AP data.sys'

    if data_sys.is_file():
        original = data_sys.read_bytes()
        if not _valid_ap_system_data(original):
            if callable(is_game_running) and is_game_running():
                raise ValueError(
                    'savedataAP/data.sys is not in the supported NewSaveSystem format while Silent Hill 3 is running. '
                    'Close the game and reopen Silent Hill 3 Client so SH3AP can preserve and replace only the AP system-data file.'
                )
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup = backup_dir / f'incompatible_data.sys.{digest(original)[:12]}.bak'
            if not backup.exists():
                atomic_write(backup, original)
            original = template
            source = 'packaged clean AP template (incompatible AP data.sys preserved)'
            created_or_replaced = True
    else:
        # Prefer the user's own raw Vanilla system-data file when it uses the same
        # NewSaveSystem format, because this preserves harmless game/system choices.
        # If it is absent/legacy, use the known-clean raw template instead.
        vanilla = folder / 'savedata_Vanilla' / 'data.sys'
        if vanilla.is_file() and not vanilla.is_symlink():
            candidate = vanilla.read_bytes()
            if _valid_ap_system_data(candidate):
                original = candidate
                source = 'copied compatible Vanilla system data'
            else:
                original = template
                source = 'packaged clean AP template (Vanilla data.sys uses another format)'
        else:
            original = template
            source = 'packaged clean AP template'
        created_or_replaced = True

    updated, changes = _apply_ap_system_unlock_values(original)
    patched = bool(changes)

    current = None
    if data_sys.is_file():
        candidate = data_sys.read_bytes()
        if _valid_ap_system_data(candidate):
            current = candidate

    write_needed = created_or_replaced or current != updated
    if write_needed:
        if callable(is_game_running) and is_game_running():
            raise ValueError(
                'AP system data needs to be prepared or updated while Silent Hill 3 is running. '
                'Close the game and reopen Silent Hill 3 Client; no save file was changed.'
            )
        if current is not None and current != updated:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup = backup_dir / f'data.sys.{digest(current)[:12]}.bak'
            if not backup.exists():
                atomic_write(backup, current)
        atomic_write(data_sys, updated)

    verify = data_sys.read_bytes()
    if not _valid_ap_system_data(verify):
        raise OSError('AP system-data write verification failed.')
    for offset, value in AP_SYSTEM_UNLOCK_VALUES:
        if verify[offset] != value:
            raise OSError(f'AP system-data unlock verification failed at offset 0x{offset:02X}.')

    # Verify the file SH3 will actually open, not merely the backing AP profile.
    # This catches a stale/misdirected public savedata junction after a folder
    # deletion or interrupted mode switch.
    live_dir = folder / 'savedata'
    if not live_dir.is_dir() or not (live_dir.is_symlink() or (hasattr(live_dir, 'is_junction') and live_dir.is_junction())):
        raise OSError('The live savedata path is not the verified AP profile junction.')
    try:
        if os.path.normcase(os.path.realpath(live_dir)) != os.path.normcase(os.path.realpath(ap_dir)):
            raise OSError('The live savedata path does not resolve to savedataAP.')
    except OSError:
        raise
    live_data = live_dir / 'data.sys'
    if not live_data.is_file() or live_data.read_bytes() != verify:
        raise OSError('Live savedata/data.sys does not match the verified AP system data.')

    marker_obj = {
        'schema': 3,
        'purpose': 'SH3AP-native reproduction of the legacy Steam006 UnlockEverything world/check state',
        'profile': 'savedataAP',
        'source': source,
        'size': len(verify),
        'sha256': digest(verify),
        'values': {f'0x{offset:02X}': f'0x{value:02X}' for offset, value in AP_SYSTEM_UNLOCK_VALUES},
        'pc_fix_unlock_everything_required': False,
        'pc_fix_unlock_everything_policy': 'set to 1 when legacy key exists; absent key supported',
    }
    atomic_write(marker, (json.dumps(marker_obj, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    return created_or_replaced, patched, source

def supported_exe_mode(folder: Path) -> str:
    """Return 'AP' or 'Vanilla' for the two exact supported 1.0.0.1 binaries."""
    folder = folder.expanduser().resolve()
    exe = folder / 'sh3.exe'
    if not exe.is_file():
        raise ValueError('sh3.exe was not found in the selected Silent Hill 3 folder.')
    value = digest(exe.read_bytes())
    if value == EXE_SHA256:
        return 'AP'
    if value == PREVIOUS_207_AP_EXE_SHA256:
        return 'AP-Previous207'
    if value == PREVIOUS_206_AP_EXE_SHA256:
        return 'AP-Previous206'
    if value == PREVIOUS_205_AP_EXE_SHA256:
        return 'AP-Previous205'
    if value == PREVIOUS_203_AP_EXE_SHA256:
        return 'AP-Previous203'
    if value == PREVIOUS_193_AP_EXE_SHA256:
        return 'AP-Previous193'
    if value == CANONICAL_AP_EXE_SHA256:
        return 'AP-Canonical191'
    if value == BROKEN_186_AP_EXE_SHA256:
        return 'AP-Broken186'
    if value == VANILLA_EXE_SHA256:
        return 'Vanilla'
    raise ValueError(
        'Unsupported sh3.exe. SH3AP currently requires the exact supported Silent Hill 3 1.0.0.1 executable. '
        f'Found SHA-256: {value}. No game files were changed.'
    )


def _bundled_ual_loader() -> bytes:
    node = resources.files(__package__)
    for part in UAL_RESOURCE_DIR:
        node = node.joinpath(part)
    data = node.joinpath('dinput8.dll').read_bytes()
    if digest(data) != UAL_DINPUT8_SHA256:
        raise ValueError('Packaged Ultimate ASI Loader verification failed.')
    return data


def _windows_version_strings(path: Path) -> dict[str, str]:
    """Read selected PE version-resource strings without third-party modules."""
    if os.name != 'nt':
        return {}
    try:
        version = ctypes.WinDLL('version', use_last_error=True)
        version.GetFileVersionInfoSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
        version.GetFileVersionInfoSizeW.restype = wintypes.DWORD
        version.GetFileVersionInfoW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
        version.GetFileVersionInfoW.restype = wintypes.BOOL
        version.VerQueryValueW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.UINT)]
        version.VerQueryValueW.restype = wintypes.BOOL

        dummy = wintypes.DWORD(0)
        size = int(version.GetFileVersionInfoSizeW(str(path), ctypes.byref(dummy)))
        if size <= 0:
            return {}
        buf = ctypes.create_string_buffer(size)
        if not version.GetFileVersionInfoW(str(path), 0, size, buf):
            return {}

        translations: list[tuple[int, int]] = []
        ptr = ctypes.c_void_p()
        length = wintypes.UINT(0)
        if version.VerQueryValueW(buf, r'\VarFileInfo\Translation', ctypes.byref(ptr), ctypes.byref(length)) and ptr.value:
            count = int(length.value) // 4
            words = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ushort))
            for index in range(count):
                translations.append((int(words[index * 2]), int(words[index * 2 + 1])))
        # Common English/Unicode and English/Windows codepage fallbacks.
        for candidate in ((0x0409, 0x04B0), (0x0409, 0x04E4)):
            if candidate not in translations:
                translations.append(candidate)

        result: dict[str, str] = {}
        for key in ('CompanyName', 'FileDescription', 'ProductName', 'FileVersion', 'ProductVersion'):
            for language, codepage in translations:
                query = rf'\StringFileInfo\{language:04x}{codepage:04x}\{key}'
                qptr = ctypes.c_void_p()
                qlen = wintypes.UINT(0)
                if version.VerQueryValueW(buf, query, ctypes.byref(qptr), ctypes.byref(qlen)) and qptr.value and qlen.value:
                    value = ctypes.wstring_at(qptr, max(0, int(qlen.value) - 1)).strip()
                    if value:
                        result[key] = value
                        break
        return result
    except Exception:
        return {}


def _looks_like_xinputplus_dinput8(path: Path) -> bool:
    """Recognize genuine XInput Plus DirectInput8 proxies without one-version hash lock.

    The original confirmed 4.15.2 SHA remains accepted. Newer official builds are
    accepted only when the file is a plausible PE DLL and its embedded XInput Plus
    vendor/product metadata identifies 0dd14lab + DirectInput8. This keeps unknown
    dinput8.dll files fail-closed while allowing current XInput Plus 4.16.1.
    """
    if not path.is_file() or path.is_symlink():
        return False
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if not _pe32_x86_dll(path):
        return False
    if digest(data) == XINPUTPLUS_DINPUT8_SHA256:
        return True
    if len(data) < 100_000 or len(data) > 500_000 or not data.startswith(b'MZ'):
        return False

    info = _windows_version_strings(path)
    company = info.get('CompanyName', '').casefold()
    identity = ' '.join((info.get('FileDescription', ''), info.get('ProductName', ''))).casefold()
    if '0dd14' in company and 'xinput plus' in identity and 'directinput8' in identity:
        return True

    # Version strings are stored as UTF-16LE in normal PE resources. This fallback
    # covers localized translation-table layouts while still requiring all three
    # independent XInput Plus identity markers.
    markers = ('0dd14', 'XInput Plus', 'DirectInput8')
    def has_marker(text: str) -> bool:
        return text.encode('utf-16le') in data or text.encode('ascii', errors='ignore') in data
    return all(has_marker(marker) for marker in markers)


def _looks_like_xinputplus_component(path: Path, *, known_hash: str, identity_hint: str) -> bool:
    if not path.is_file() or path.is_symlink() or not _pe32_x86_dll(path):
        return False
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if digest(data) == known_hash:
        return True
    info = _windows_version_strings(path)
    company = info.get('CompanyName', '').casefold()
    identity = ' '.join((info.get('FileDescription', ''), info.get('ProductName', ''))).casefold()
    if '0dd14' in company and 'xinput plus' in identity and identity_hint.casefold() in identity:
        return True
    # Localized/fallback PE resources. Require vendor + product markers, while the
    # PE32/x86 check above prevents a 64-bit proxy from entering a 32-bit process.
    return (b'0dd14' in data or '0dd14'.encode('utf-16le') in data) and (b'XInput Plus' in data or 'XInput Plus'.encode('utf-16le') in data)


def ensure_xinput_chain_safe(folder: Path) -> str:
    """Fail closed on partial, wrong-vendor, or wrong-architecture controller proxy chains."""
    folder = folder.expanduser().resolve()
    paths = {name: folder / name for name in XINPUTPLUS_TRIGGER_FILES}
    present = [name for name, path in paths.items() if path.is_file()]
    if not present:
        return 'absent'
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise ValueError(
            'A partial XInput Plus/controller proxy installation is present. Missing: ' + ', '.join(missing)
            + '. Complete or remove the controller proxy chain before enabling SH3AP.'
        )
    if not _looks_like_xinputplus_dinput8(paths['dinput8Hooked.dll']):
        raise ValueError('dinput8Hooked.dll is not a recognized 32-bit XInput Plus DirectInput8 proxy.')
    if not _looks_like_xinputplus_component(paths['Dinput.dll'], known_hash=XINPUTPLUS_DINPUT_SHA256, identity_hint='directinput'):
        raise ValueError('Dinput.dll is not a recognized 32-bit XInput Plus DirectInput proxy.')
    if not _looks_like_xinputplus_component(paths['XInput1_3.dll'], known_hash=XINPUTPLUS_XINPUT13_SHA256, identity_hint='xinput'):
        raise ValueError('XInput1_3.dll is not a recognized 32-bit XInput Plus proxy.')
    return 'ready'


def _external_backup_dir(folder: Path) -> Path:
    path = folder / 'scripts' / 'SH3AP_Mode_Data' / 'ExternalSupportBackups'
    if path.is_symlink():
        raise ValueError('External support backup directory is a link; refusing to write there.')
    path.mkdir(parents=True, exist_ok=True)
    return path


def _backup_exact_file(folder: Path, source: Path, label: str) -> Path:
    data = source.read_bytes()
    sha = digest(data)
    backup_dir = _external_backup_dir(folder)
    target = backup_dir / f'{label}.{sha[:12]}.bak'
    if target.exists():
        if target.is_symlink() or target.read_bytes() != data:
            raise ValueError(f'Existing setup backup is not the expected file: {target.name}')
        return target
    atomic_write(target, data)
    if target.read_bytes() != data:
        raise OSError(f'Backup verification failed: {source.name}')
    return target


def prepare_asi_loader_and_xinput_chain(folder: Path, is_game_running, logger=None) -> str:
    """Install bundled UAL and safely chain a recognized XInput Plus proxy.

    Unknown dinput8/dinput8Hooked DLLs are never renamed or overwritten. Genuine
    XInput Plus DirectInput8 proxies are recognized by the original confirmed hash
    or by embedded 0dd14lab/XInput Plus/DirectInput8 PE metadata, allowing current
    official 4.16.1 as well as the older confirmed 4.15.2 build.
    Returns one of: 'loader-installed', 'chain-created', 'ready'.
    """
    folder = folder.expanduser().resolve()
    d8 = folder / 'dinput8.dll'
    hook = folder / 'dinput8Hooked.dll'
    loader = _bundled_ual_loader()

    if is_game_running():
        raise ValueError('Close Silent Hill 3 before SH3AP prepares the ASI loader/controller chain.')
    if d8.is_symlink() or hook.is_symlink():
        raise ValueError('dinput8.dll / dinput8Hooked.dll may not be filesystem links.')

    d8_hash = digest(d8.read_bytes()) if d8.is_file() else None
    hook_hash = digest(hook.read_bytes()) if hook.is_file() else None
    d8_is_xinputplus = _looks_like_xinputplus_dinput8(d8) if d8.is_file() else False
    hook_is_xinputplus = _looks_like_xinputplus_dinput8(hook) if hook.is_file() else False

    if hook_hash is not None and not hook_is_xinputplus:
        raise ValueError(
            'dinput8Hooked.dll already exists but is not recognized as an XInput Plus DirectInput8 proxy. '
            'Nothing was renamed or overwritten.'
        )
    if d8_hash not in (None, UAL_DINPUT8_SHA256) and not d8_is_xinputplus:
        raise ValueError(
            'dinput8.dll already exists but is neither the bundled Ultimate ASI Loader nor a recognized '
            'XInput Plus DirectInput8 proxy. Nothing was renamed or overwritten.'
        )

    # Already perfect. Existing recognized hook remains untouched.
    if d8_hash == UAL_DINPUT8_SHA256:
        return 'ready'

    moved_to_hook = False
    backup = None
    original_xinput_hash = d8_hash if d8_is_xinputplus else None
    if d8_is_xinputplus:
        backup = _backup_exact_file(folder, d8, 'xinputplus_dinput8_before_sh3ap_chain')
        if hook_hash is None:
            os.replace(d8, hook)
            moved_to_hook = True
            if (not hook.is_file() or digest(hook.read_bytes()) != original_xinput_hash
                    or not _looks_like_xinputplus_dinput8(hook)):
                if not d8.exists() and backup.is_file():
                    atomic_write(d8, backup.read_bytes())
                raise OSError('XInput Plus dinput8.dll -> dinput8Hooked.dll rename verification failed.')
        else:
            # A recognized chained proxy is already present. If the root proxy is
            # a duplicate or another recognized XInput Plus build, its exact bytes
            # are backed up above before replacing the root entry point with UAL.
            d8.unlink()

    try:
        atomic_write(d8, loader)
        if digest(d8.read_bytes()) != UAL_DINPUT8_SHA256:
            raise OSError('Ultimate ASI Loader install verification failed.')
    except Exception:
        try:
            if d8.exists() and digest(d8.read_bytes()) == UAL_DINPUT8_SHA256:
                d8.unlink()
            if backup is not None and backup.is_file() and not d8.exists():
                atomic_write(d8, backup.read_bytes())
            if moved_to_hook and hook.is_file() and original_xinput_hash is not None and digest(hook.read_bytes()) == original_xinput_hash:
                hook.unlink()
        finally:
            raise

    if logger is not None:
        if moved_to_hook:
            logger.info('Prepared controller/ASI DLL chain automatically: XInput Plus -> dinput8Hooked.dll; Ultimate ASI Loader -> dinput8.dll.')
        elif d8_is_xinputplus:
            logger.info('Verified existing XInput Plus chained proxy and installed Ultimate ASI Loader as dinput8.dll.')
        else:
            logger.info('Installed bundled Ultimate ASI Loader as dinput8.dll.')
    return 'chain-created' if d8_is_xinputplus else 'loader-installed'

def xinputplus_trigger_status(folder: Path) -> tuple[str, list[str]]:
    """Report the installed XInputPlus trigger chain without modifying it.

    Returns (status, details), where status is one of:
      - 'ready': all required files exist and XInputPlus.ini exposes LT/RT as
        DirectInput Button11/Button12 through X2DInput, matching the confirmed
        working SH3AP setup.
      - 'absent': none of the XInputPlus trigger files are installed.
      - 'incomplete': some files are missing or the mapping is incompatible.
    """
    folder = folder.expanduser().resolve()
    present = [name for name in XINPUTPLUS_TRIGGER_FILES if (folder / name).is_file()]
    if not present:
        return 'absent', list(XINPUTPLUS_TRIGGER_FILES)
    try:
        ensure_xinput_chain_safe(folder)
    except ValueError as exc:
        return 'incomplete', [str(exc)]

    import configparser
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    try:
        with (folder / 'XInputPlus.ini').open('r', encoding='utf-8-sig', errors='strict') as stream:
            cfg.read_file(stream)
    except Exception as exc:
        return 'incomplete', ['XInputPlus.ini could not be read: ' + str(exc)]

    # Section and key lookup is deliberately case-insensitive without rewriting
    # the user's INI. Only these three trigger-related values matter here.
    def get_ci(section: str, key: str) -> str | None:
        sec = next((name for name in cfg.sections() if name.casefold() == section.casefold()), None)
        if sec is None:
            return None
        for k, v in cfg.items(sec):
            if k.casefold() == key.casefold():
                return v.strip()
        return None

    expected = {
        'EnableX2Dinput': 'True',
        'LT': 'Button11',
        'RT': 'Button12',
    }
    issues: list[str] = []
    for key, wanted in expected.items():
        value = get_ci('X2DInput', key)
        if value is None:
            issues.append(f'X2DInput.{key} is missing')
        elif value.casefold() != wanted.casefold():
            issues.append(f'X2DInput.{key}={value!r}, expected {wanted!r}')
    return ('ready', []) if not issues else ('incomplete', issues)


def log_xinputplus_trigger_status(folder: Path, logger) -> str:
    status, details = xinputplus_trigger_status(folder)
    if status == 'ready':
        logger.info('Xbox/XInput trigger support: XInputPlus LT=Button11 / RT=Button12 is installed and will be left active in both AP and Vanilla modes.')
    elif status == 'absent':
        logger.warning(
            'Xbox/XInput trigger support is not installed. XInput Plus cannot be redistributed by SH3AP; '
            'install it from the official 0dd14lab site if you use an Xbox/XInput controller: %s',
            XINPUTPLUS_HOME_PAGE,
        )
    else:
        logger.warning(
            "XInputPlus is present but trigger support is incomplete: %s. SH3AP will not rewrite the user's trigger mapping automatically.",
            '; '.join(details),
        )
    return status


def install_mode_tools(folder: Path) -> int:
    """Install SH3AP-owned mode tools only.

    Title installation is handled separately by sync_ap_default_title using
    supplied artwork and a verified backup of the user-local archive.
    """
    folder = folder.expanduser().resolve()
    root = resources.files(__package__).joinpath('tools')
    changed = 0
    for name in MODE_TOOL_NAMES:
        if Path(name).name != name or not name.lower().endswith('.bat'):
            raise ValueError('Invalid packaged mode-tool filename')
        data = root.joinpath(name).read_bytes()
        target = folder / name
        if target.is_symlink():
            raise ValueError(f'Mode tool is a link: {name}')
        if not target.exists() or target.read_bytes() != data:
            atomic_write(target, data)
            changed += 1
    return changed


def sync_ap_default_title(folder: Path, is_game_running) -> bool:
    from .title_texture import sync_title
    return sync_title(folder, is_game_running)


def install_ap_default_settings(folder: Path) -> int:
    """Install/synchronize the supplied SH3 display/controller defaults as shared game settings.

    key.ini and disp.ini are game/user configuration, not AP-mode state.  They must
    follow the player across AP <-> Vanilla switches just like the external PC Fix
    and XInput Plus configuration.  Existing live settings are authoritative; the
    packaged files are used only when no current setting exists yet.
    """
    folder = folder.expanduser().resolve()
    package_root = resources.files(__package__).joinpath('defaults')
    defaults: dict[str, bytes] = {}
    for name, expected in DEFAULT_SETTING_HASHES.items():
        data = package_root.joinpath(name).read_bytes()
        if digest(data) != expected:
            raise ValueError(f'Packaged default setting verification failed: {name}')
        defaults[name] = data

    live = folder / 'savedata'
    ap = folder / 'savedataAP'
    vanilla = folder / 'savedata_Vanilla'
    mode_data = folder / 'scripts' / 'SH3AP_Mode_Data'
    backup_dir = mode_data / 'SharedSettingsBackups'

    def is_linklike(path: Path) -> bool:
        return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())

    def normal_dir(path: Path) -> bool:
        return path.is_dir() and not is_linklike(path)

    def backup_existing(path: Path, old: bytes) -> None:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f'{path.name}.{digest(old)[:12]}.bak'
        if not backup.exists():
            atomic_write(backup, old)

    changed = 0

    # Before the first save split, savedata is an ordinary Vanilla folder.  Keep
    # that folder authoritative and do not create savedata_Vanilla early, because
    # doing so would make first-run save-layout recovery ambiguous.
    if normal_dir(live):
        for name, default_data in defaults.items():
            target = live / name
            if target.is_symlink():
                raise ValueError(f'Game setting is a link: {target}')
            if not target.exists():
                atomic_write(target, default_data)
                changed += 1
        return changed

    # Split layout (or a resumed install): both profile folders hold game saves,
    # while key.ini/disp.ini are one shared effective configuration.
    for path, label in ((ap, 'savedataAP'), (vanilla, 'savedata_Vanilla')):
        if path.exists() and (not path.is_dir() or is_linklike(path)):
            raise ValueError(f'{label} must be a normal directory.')
        path.mkdir(parents=True, exist_ok=True)

    live_is_active = live.is_dir()
    for name, default_data in defaults.items():
        live_file = live / name
        ap_file = ap / name
        vanilla_file = vanilla / name

        if live_is_active and live_file.is_file() and not live_file.is_symlink():
            # Normal split state: the profile actually exposed as savedata is the
            # authority. Mirror it into both real profiles.
            source_data = live_file.read_bytes()
            targets = (ap_file, vanilla_file)
        else:
            # Interrupted state with no public savedata junction: do not guess
            # between two different personalized profiles here. Fill only missing
            # copies; the verified mode toggle resolves authority from its exact
            # executable/mode state before switching.
            ap_data = ap_file.read_bytes() if ap_file.is_file() and not ap_file.is_symlink() else None
            vanilla_data = vanilla_file.read_bytes() if vanilla_file.is_file() and not vanilla_file.is_symlink() else None
            if ap_data is not None and vanilla_data is not None and ap_data != vanilla_data:
                continue
            source_data = ap_data if ap_data is not None else vanilla_data
            if source_data is None:
                source_data = default_data
            targets = tuple(t for t in (ap_file, vanilla_file) if not t.exists())

        for target in targets:
            if target.is_symlink():
                raise ValueError(f'Game setting is a link: {target}')
            old = target.read_bytes() if target.exists() else None
            if old != source_data:
                if old is not None:
                    backup_existing(target, old)
                atomic_write(target, source_data)
                if target.read_bytes() != source_data:
                    raise OSError(f'Shared setting verification failed: {target}')
                changed += 1

    return changed

def ap_mode_layout_ready(folder: Path) -> bool:
    """Return True only when both the verified AP executable and live AP save profile are active.

    0.0.191 looked only at sh3.exe. A recovered/deleted-folder install could therefore
    retain an AP executable while the public `savedata` path still exposed another
    profile. In that state SH3AP patched savedataAP/data.sys but the game read a
    different data.sys, making the unlock verification meaningless.
    """
    folder = folder.expanduser().resolve()
    try:
        if supported_exe_mode(folder) != 'AP':
            return False
    except Exception:
        return False
    live = folder / 'savedata'
    ap = folder / 'savedataAP'
    if not ap.is_dir() or ap.is_symlink() or (hasattr(ap, 'is_junction') and ap.is_junction()):
        return False
    if not live.is_dir():
        return False
    if not (live.is_symlink() or (hasattr(live, 'is_junction') and live.is_junction())):
        return False
    try:
        live_target = Path(os.path.realpath(live))
        ap_target = Path(os.path.realpath(ap))
        return os.path.normcase(str(live_target)) == os.path.normcase(str(ap_target))
    except OSError:
        return False


def request_ap_mode(folder: Path) -> None:
    """Request AP mode through the same verified user-facing toggle.

    This is also the fresh-install bootstrap: an untouched supported 1.0.0.1
    executable is converted to the verified AP byte state before runtime ASIs are
    installed.
    """
    folder = folder.expanduser().resolve()
    toggle = folder / 'SH3AP_Mode_Toggle.bat'
    if not toggle.is_file():
        raise ValueError('SH3AP_Mode_Toggle.bat is missing; cannot enable SH3AP.')
    if os.name != 'nt':
        raise ValueError('Automatic SH3AP mode switching requires Windows.')
    comspec = os.environ.get('ComSpec') or os.environ.get('COMSPEC') or 'cmd.exe'
    completed = subprocess.run(
        [comspec, '/d', '/c', 'call', str(toggle), 'AP', '--no-pause'],
        cwd=str(folder),
        check=False,
        capture_output=True,
        text=True,
        errors='replace',
    )
    if completed.returncode != 0:
        detail = '\n'.join(
            line for line in ((completed.stdout or '') + '\n' + (completed.stderr or '')).splitlines()
            if line.strip()
        )
        if len(detail) > 3000:
            detail = detail[-3000:]
        raise ValueError(
            f'SH3AP mode toggle returned error code {completed.returncode}.'
            + (f'\n\nToggle output:\n{detail}' if detail else '')
        )
    if runtime_disabled(folder):
        raise ValueError('SH3AP mode toggle finished but the disabled marker is still present.')
    if supported_exe_mode(folder) != 'AP':
        raise ValueError('SH3AP mode toggle finished but sh3.exe is not in the verified AP state.')

def enable_runtime_from_disabled_mode(folder: Path) -> None:
    """Compatibility wrapper for older client code."""
    request_ap_mode(folder)

def ensure_ual_scripts_only_config(folder: Path) -> bool:
    """Apply SH3AP's deterministic UAL discovery policy without hard-forcing timing.

    Preserve existing consistent Standard/Deferred timing, honor explicit markers,
    and use Standard on a fresh install. DLL hashes do not select loader timing.

    In both modes SH3AP loads only direct children of scripts and never recursively
    scans archived/disabled folders. Existing global.ini files are normalized so
    an older loader config cannot silently override the selected policy.
    """
    folder = folder.expanduser().resolve()
    scripts = folder / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    mode_data = scripts / 'SH3AP_Mode_Data'
    mode_data.mkdir(parents=True, exist_ok=True)
    deferred = loader_deferred_requested(folder)
    dllmain = '1' if deferred else '0'

    desired = (
        ('LoadPlugins', '1'),
        ('LoadFromScriptsOnly', '1'),
        ('LoadRecursively', '0'),
        ('DontLoadFromDllMain', dllmain),
        # Steam006 already supplies SH3's D3D8/9 compatibility path. Do not let
        # Ultimate ASI Loader inject a second D3D8-to-9 layer on some installs.
        ('UseD3D8to9', '0'),
        # Keep UAL crash reporting enabled so a cross-PC startup failure leaves a
        # useful dump instead of disappearing before SH3 can render a window.
        ('DisableCrashDumps', '0'),
    )
    default = (
        '[GlobalSets]\r\n'
        'LoadPlugins=1\r\n'
        'LoadFromScriptsOnly=1\r\n'
        'LoadRecursively=0\r\n'
        f'DontLoadFromDllMain={dllmain}\r\n'
        'UseD3D8to9=0\r\n'
        'DisableCrashDumps=0\r\n'
        'Direct3D8DisableMaximizedWindowedModeShim=0\r\n'
    )

    def normalize(path: Path, *, create: bool) -> bool:
        if not path.is_file():
            if not create:
                return False
            atomic_write(path, default.encode('ascii'))
            return True
        raw = path.read_bytes()
        if raw.startswith(b'\xef\xbb\xbf'):
            encoding = 'utf-8-sig'
        else:
            try:
                raw.decode('utf-8')
                encoding = 'utf-8'
            except UnicodeDecodeError:
                encoding = 'latin-1'
        text = raw.decode(encoding)
        newline = '\r\n' if '\r\n' in text else '\n'
        updated = text
        # Remove every existing copy of SH3AP-owned loader keys first. Duplicate
        # keys are otherwise parser/order dependent and can silently defeat the
        # selected startup policy on another PC. LoadFromAPI is also removed so
        # an old advanced UAL timing hook cannot override DontLoadFromDllMain.
        owned = [key for key, _ in desired] + ['LoadFromAPI']
        for key in owned:
            pattern = r'(?im)^[ \t]*' + re.escape(key) + r'[ \t]*=[^\r\n]*(?:\r?\n|$)'
            updated = re.sub(pattern, '', updated)
        section = re.search(r'(?im)^([ \t]*\[GlobalSets\][ \t]*)(\r?\n|$)', updated)
        assignments = ''.join(f'{key}={value}{newline}' for key, value in desired)
        if section:
            insert_at = section.end()
            prefix = '' if section.group(2) else newline
            updated = updated[:insert_at] + prefix + assignments + updated[insert_at:]
        else:
            updated = updated.rstrip('\r\n') + newline + '[GlobalSets]' + newline + assignments
        data = updated.encode(encoding)
        if data == raw:
            return False
        atomic_write(path, data)
        return True

    changed = normalize(folder / 'dinput8.ini', create=True)
    changed = normalize(folder / 'global.ini', create=False) or changed
    changed = normalize(scripts / 'global.ini', create=False) or changed
    plugins = folder / 'plugins'
    if plugins.is_dir():
        changed = normalize(plugins / 'global.ini', create=False) or changed

    # Verify there is exactly one effective copy of every SH3AP-owned key in the
    # root config, and no conflicting override in scripts/plugins configs.
    expected = dict(desired)
    def verify(path: Path, *, root: bool) -> None:
        if not path.is_file():
            return
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        for key, value in expected.items():
            matches = re.findall(r'(?im)^[ \t]*' + re.escape(key) + r'[ \t]*=[ \t]*([^\r\n]+)', text)
            if root:
                if len(matches) != 1 or matches[0].strip() != value:
                    raise ValueError(f'{path.name} has an ambiguous/incorrect {key} loader setting after normalization.')
            elif len(matches) > 1 or (matches and matches[0].strip() != value):
                raise ValueError(f'{path.name} overrides SH3AP loader setting {key}.')
        if re.search(r'(?im)^[ \t]*LoadFromAPI[ \t]*=', text):
            raise ValueError(f'{path.name} still contains LoadFromAPI after normalization.')
    verify(folder / 'dinput8.ini', root=True)
    verify(folder / 'global.ini', root=False)
    verify(scripts / 'global.ini', root=False)
    if plugins.is_dir():
        verify(plugins / 'global.ini', root=False)

    crash = folder / 'CrashDumps'
    if crash.exists() and (crash.is_symlink() or not crash.is_dir()):
        raise ValueError('CrashDumps exists but is not a normal folder; SH3AP cannot safely enable loader crash reporting.')
    crash.mkdir(exist_ok=True)
    return changed



def stage_runtime_for_ap_enable(folder: Path, is_game_running, payloads=None) -> tuple[int, Path | None]:
    """Stage verified runtime under non-loadable names before Vanilla -> AP.

    A true first install starts with no active or disabled SH3AP ASIs.  The
    transactional mode toggle deliberately refuses to enter AP mode unless every
    production runtime file already exists in one of those two locations.  Stage
    missing files here using the same safe disabled naming used by Vanilla/off
    mode, without creating the disabled marker or changing sh3.exe/save links.

    Existing active production ASIs are left alone. Existing disabled copies are
    refreshed to the packaged bytes. Plain-.asi legacy copies inside the disabled
    directory are backed up and neutralized so recursive loaders cannot see them.
    """
    folder = folder.expanduser().resolve()
    if is_game_running():
        raise ValueError('Close SH3, then restart the client to prepare the SH3AP runtime.')
    scripts = folder / 'scripts'
    if scripts.is_symlink():
        raise ValueError('The scripts folder is a link; install into a regular game folder.')
    scripts.mkdir(parents=True, exist_ok=True)
    disabled = scripts / DISABLED_RUNTIME_DIR
    if disabled.is_symlink():
        raise ValueError('The disabled runtime folder is a link; refusing to modify it.')
    disabled.mkdir(parents=True, exist_ok=True)
    payloads = bundled_files() if payloads is None else payloads

    changes: dict[str, tuple[bytes | None, bytes]] = {}
    legacy: dict[str, bytes] = {}
    for name, data in payloads.items():
        if Path(name).name != name or not name.endswith('.asi'):
            raise ValueError('Invalid runtime filename')
        active = scripts / name
        if active.is_symlink():
            raise ValueError(f'Runtime file is a link: {name}')
        # An existing active copy is authoritative for the mode transition. The
        # normal install_runtime() pass after AP activation will atomically refresh
        # it to this package if it is older. Do not manufacture a conflicting
        # active+disabled pair here.
        if active.is_file():
            continue
        target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
        if target.is_symlink():
            raise ValueError(f'Disabled runtime file is a link: {name}')
        old = target.read_bytes() if target.exists() else None
        if old != data:
            changes[name] = (old, data)
        legacy_path = disabled / name
        if legacy_path.is_symlink():
            raise ValueError(f'Legacy disabled runtime file is a link: {name}')
        if legacy_path.is_file():
            legacy[name] = legacy_path.read_bytes()

    if not changes and not legacy:
        return 0, None

    backup = scripts / 'SH3AP_Runtime_Backups' / uuid.uuid4().hex
    backup.mkdir(parents=True)
    journal: dict[str, dict[str, str | None]] = {}
    for name, (old, new) in changes.items():
        if old is not None:
            (backup / (name + DISABLED_RUNTIME_SUFFIX + '.bak')).write_bytes(old)
        journal[name + DISABLED_RUNTIME_SUFFIX] = {
            'previous_sha256': digest(old) if old is not None else None,
            'installed_sha256': digest(new),
        }
    for name, old in legacy.items():
        (backup / (name + '.legacy-disabled.bak')).write_bytes(old)
        journal[name + '.legacy-disabled'] = {
            'previous_sha256': digest(old),
            'installed_sha256': None,
        }
    (backup / 'manifest.json').write_text(json.dumps(journal, indent=2), encoding='utf-8')

    written: list[str] = []
    removed_legacy: list[str] = []
    try:
        if is_game_running():
            raise ValueError('SH3 started during setup. Close it and retry.')
        for name, (old, new) in changes.items():
            # Re-check that an active file did not appear between inspection and
            # publication; never create ambiguous active+disabled copies.
            active = scripts / name
            if active.is_file():
                raise ValueError(f'{name} became active during setup; installation cancelled.')
            target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
            current = target.read_bytes() if target.exists() else None
            if current != old:
                raise ValueError(f'{name} disabled copy changed during setup; installation cancelled.')
            atomic_write(target, new)
            written.append(name)
            if target.read_bytes() != new:
                raise OSError(f'Installed verification failed: {name} staged copy')
        for name, old in legacy.items():
            legacy_path = disabled / name
            if legacy_path.read_bytes() != old:
                raise ValueError(f'{name} legacy disabled copy changed during setup; installation cancelled.')
            legacy_path.unlink()
            removed_legacy.append(name)
    except Exception:
        for name in reversed(removed_legacy):
            atomic_write(disabled / name, legacy[name])
        for name in reversed(written):
            old, new = changes[name]
            target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
            if target.read_bytes() != new:
                raise OSError(f'{name} changed during rollback; original retained in {backup}')
            if old is None:
                target.unlink()
            else:
                atomic_write(target, old)
        raise
    return len(changes) + len(legacy), backup

def refresh_disabled_runtime(folder: Path, is_game_running, payloads=None) -> tuple[int, Path | None]:
    """Refresh packaged runtime while SH3AP is toggled off, without enabling it.

    This makes a 1.0.0 -> 1.0.1 upgrade deterministic even when the game is
    currently in Vanilla/off mode: the verified current payload is staged under
    the non-.asi disabled names before the mode toggle restores anything.
    Missing disabled production files are recreated; stale legacy plain-.asi
    copies in the disabled directory are neutralized after exact backup.
    """
    folder = folder.expanduser().resolve()
    if not runtime_disabled(folder):
        return 0, None
    if is_game_running():
        raise ValueError('Close SH3, then restart the client to refresh the disabled SH3AP runtime.')
    scripts = folder / 'scripts'
    if scripts.is_symlink():
        raise ValueError('The scripts folder is a link; install into a regular game folder.')
    scripts.mkdir(parents=True, exist_ok=True)
    disabled = scripts / DISABLED_RUNTIME_DIR
    if disabled.is_symlink():
        raise ValueError('The disabled runtime folder is a link; refusing to modify it.')
    disabled.mkdir(parents=True, exist_ok=True)
    payloads = bundled_files() if payloads is None else payloads

    # A disabled installation should not also expose production ASIs at the
    # top level. Fail closed instead of deciding which copy is authoritative.
    conflicts = [name for name in payloads if (scripts / name).is_file()]
    if conflicts:
        raise ValueError(
            'SH3AP is marked disabled but active runtime files are also present: '
            + ', '.join(sorted(conflicts))
            + '. Toggle to a coherent mode before upgrading.'
        )

    changes: dict[str, tuple[bytes | None, bytes]] = {}
    legacy: dict[str, bytes] = {}
    for name, data in payloads.items():
        if Path(name).name != name or not name.endswith('.asi'):
            raise ValueError('Invalid runtime filename')
        target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
        if target.is_symlink():
            raise ValueError(f'Disabled runtime file is a link: {name}')
        old = target.read_bytes() if target.exists() else None
        if old != data:
            changes[name] = (old, data)
        legacy_path = disabled / name
        if legacy_path.is_symlink():
            raise ValueError(f'Legacy disabled runtime file is a link: {name}')
        if legacy_path.is_file():
            legacy[name] = legacy_path.read_bytes()

    if not changes and not legacy:
        return 0, None

    backup = scripts / 'SH3AP_Runtime_Backups' / uuid.uuid4().hex
    backup.mkdir(parents=True)
    journal: dict[str, dict[str, str | None]] = {}
    for name, (old, new) in changes.items():
        if old is not None:
            (backup / (name + DISABLED_RUNTIME_SUFFIX + '.bak')).write_bytes(old)
        journal[name + DISABLED_RUNTIME_SUFFIX] = {
            'previous_sha256': digest(old) if old is not None else None,
            'installed_sha256': digest(new),
        }
    for name, old in legacy.items():
        (backup / (name + '.legacy-disabled.bak')).write_bytes(old)
        journal[name + '.legacy-disabled'] = {
            'previous_sha256': digest(old),
            'installed_sha256': None,
        }
    (backup / 'manifest.json').write_text(json.dumps(journal, indent=2), encoding='utf-8')

    written: list[str] = []
    removed_legacy: list[str] = []
    try:
        if is_game_running():
            raise ValueError('SH3 started during setup. Close it and retry.')
        for name, (old, new) in changes.items():
            target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
            current = target.read_bytes() if target.exists() else None
            if current != old:
                raise ValueError(f'{name} disabled copy changed during setup; installation cancelled.')
            atomic_write(target, new)
            written.append(name)
            if target.read_bytes() != new:
                raise OSError(f'Installed verification failed: {name} disabled copy')
        for name, old in legacy.items():
            legacy_path = disabled / name
            if legacy_path.read_bytes() != old:
                raise ValueError(f'{name} legacy disabled copy changed during setup; installation cancelled.')
            legacy_path.unlink()
            removed_legacy.append(name)
    except Exception:
        for name in reversed(removed_legacy):
            atomic_write(disabled / name, legacy[name])
        for name in reversed(written):
            old, new = changes[name]
            target = disabled / (name + DISABLED_RUNTIME_SUFFIX)
            if target.read_bytes() != new:
                raise OSError(f'{name} changed during rollback; original retained in {backup}')
            if old is None:
                target.unlink()
            else:
                atomic_write(target, old)
        raise
    return len(changes) + len(legacy), backup


def install_runtime(folder: Path, is_game_running, payloads=None) -> tuple[int, Path | None]:
    folder = folder.expanduser().resolve()
    if runtime_disabled(folder):
        return 0, None
    exe = folder / 'sh3.exe'
    if not exe.is_file() or digest(exe.read_bytes()) != EXE_SHA256:
        raise ValueError('Unsupported sh3.exe. No game files were changed.')
    loader = folder / 'dinput8.dll'
    if not loader.is_file() or digest(loader.read_bytes()) != UAL_DINPUT8_SHA256:
        raise ValueError('The verified Ultimate ASI Loader is missing or changed. Reopen Silent Hill 3 Client with the game closed to repair setup.')
    payloads = bundled_files() if payloads is None else payloads
    scripts = folder / 'scripts'
    if scripts.is_symlink():
        raise ValueError('The scripts folder is a link; install into a regular game folder.')
    changes = {}
    for name, data in payloads.items():
        if Path(name).name != name or not name.endswith('.asi'):
            raise ValueError('Invalid runtime filename')
        target = scripts / name
        if target.is_symlink():
            raise ValueError(f'Runtime file is a link: {name}')
        old = target.read_bytes() if target.exists() else None
        if old != data:
            changes[name] = (old, data)
    if not changes:
        return 0, None
    if is_game_running():
        raise ValueError('Close SH3, then restart the client to install the bundled runtime.')
    scripts.mkdir(parents=True, exist_ok=True)
    backup = scripts / 'SH3AP_Runtime_Backups' / uuid.uuid4().hex
    backup.mkdir(parents=True)
    journal = {}
    for name, (old, new) in changes.items():
        if old is not None:
            (backup / (name + '.bak')).write_bytes(old)
        journal[name] = {'previous_sha256': digest(old) if old is not None else None,
                         'installed_sha256': digest(new)}
    (backup / 'manifest.json').write_text(json.dumps(journal, indent=2), encoding='utf-8')
    written = []
    try:
        if is_game_running():
            raise ValueError('SH3 started during setup. Close it and retry.')
        for name, (old, new) in changes.items():
            target = scripts / name
            # Detect edits between inspection and publication.
            current = target.read_bytes() if target.exists() else None
            if current != old:
                raise ValueError(f'{name} changed during setup; installation cancelled.')
            atomic_write(target, new)
            written.append(name)
            if target.read_bytes() != new:
                raise OSError(f'Installed verification failed: {name}')
    except Exception:
        for name in reversed(written):
            old, new = changes[name]
            target = scripts / name
            if target.read_bytes() != new:
                raise OSError(f'{name} changed during rollback; original retained in {backup}')
            if old is None:
                target.unlink()
            else:
                atomic_write(target, old)
        raise
    return len(changes), backup

def choose_game_folder(explicit: str | None, settings_path: Path) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    if settings_path.is_file():
        try:
            saved = json.loads(settings_path.read_text(encoding='utf-8')).get('game_folder')
        except (OSError, ValueError, TypeError):
            saved = None
        if saved and (Path(saved) / 'sh3.exe').is_file():
            return Path(saved).expanduser().resolve()
    default = Path.home() / 'Documents' / 'Other Games' / 'Silent Hill 3'
    if (default / 'sh3.exe').is_file():
        return default.resolve()
    if os.name != 'nt':
        raise ValueError('No Silent Hill 3 game folder was found automatically. Use --game-folder.')
    selected = _choose_windows_folder('Select the Silent Hill 3 folder containing sh3.exe')
    if not selected:
        raise ValueError('No game folder selected. Setup cancelled.')
    folder = Path(selected).expanduser().resolve()
    if not (folder / 'sh3.exe').is_file():
        raise ValueError('The selected folder does not contain sh3.exe.')
    return folder

def save_game_folder(folder: Path, settings_path: Path) -> None:
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(settings_path, json.dumps({'game_folder': str(folder.resolve())}, indent=2).encode())
