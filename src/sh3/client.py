from __future__ import annotations

import asyncio
import base64
import ctypes
from ctypes import wintypes
import json
from functools import lru_cache
import logging
import os
from pathlib import Path
import threading
import struct
import time
import zlib
import sys
from typing import Optional

import Utils
from NetUtils import ClientStatus
from CommonClient import CommonContext, get_base_parser, gui_enabled, handle_url_arg, logger, server_loop

from .traps import TRAP_ITEM_IDS, enqueue as _enqueue_trap, exchange as _exchange_traps
from .death_link import State as DeathLinkState, sync as _sync_deathlink, exchange as _exchange_deathlink
from .components import get_sh3_icon_path
from .runtime_discovery import RuntimeDiscovery
from .tracker_client import sync as _sync_tracker
from .poptracker_follow import sync as _sync_poptracker_follow
from .save_travel import TravelState, NATIVE_SIGNATURE, NATIVE_RVA, VIRTUAL_SIGNATURE, VIRTUAL_RVA
from .silent_hill_client import CLIENT_NAME, CLIENT_BRAND

from .data import (
    CLIENT_VERSION,
    SAVE_ID_TO_LOCATION_ID, SAVE_TRAVEL_PROTOCOL, ACTIVE_FAST_TRAVEL_ROWS,
    FAST_TRAVEL_ITEM_IDS, VIRTUAL_TRAVEL_RAW_ID,
    GAME_NAME,
    ITEM_ID_TO_RAW,
    LOCATION_NAME_TO_ID,
    PERSIST_FLAG_TO_LOCATION_ID,
    RECEIVE_RAW_IDS, SCRIPTED_PROTOCOL, SCRIPTED_BIT_TO_LOCATION_ID, SCRIPTED_FLAG_TO_LOCATION_ID, active_locations, BOSS_LOCATION, MALL_MAP_ITEM, MAP_CHECK_ITEMS, ITEM_NAME_TO_ID, goal_location_ids,
    PROTOCOL_VERSION,
    START_LOCATION_IDS,
    START_LOCATION_NAMES,
    WORLD_VERSION,
)

GAME_FOLDER = Path.home() / "Documents" / "Other Games" / "Silent Hill 3"

PIPE_PATH = r"\\.\pipe\SH3AP_v1"
POLL_SECONDS = 0.5
RECEIVE_EXTENSION_SIGNATURE = b"SH3AP_RECEIVE_V1\x00"
RECEIVE_EXTENSION_RVA = 0x31000
RECEIVE_LEASE_RVA = 0x31018
SUPPORTED_RECEIVE_RAW_IDS = RECEIVE_RAW_IDS
ITEM_OWNED_BITS_ADDR = 0x0712CA80
ITEM_OWNED_BITS_SIZE = 0x20
MALL_TOILET_NATIVE_SAVE_ID = 2
MALL_TOILET_LOCATION_ID = SAVE_ID_TO_LOCATION_ID[MALL_TOILET_NATIVE_SAVE_ID]
LIVE_CONTEXT_D9_ADDR = 0x070E66D9
LIVE_CONTEXT_DA_ADDR = 0x070E66DA
# Unlock All/new-game grants that must be stripped before AP starting rewards arrive.
# These are the three vanilla starting items plus Transform Costume and the 11 shirts.
NEW_GAME_CLEAR_RAW_IDS = frozenset((1, 13, 32, 33, 35, 36, 82, *range(96, 107)))
# Raw 13 is granted by a later pickup, not by New Game initialization.
# The 20261001-204024 ITEM trace has every other starter bit at TICK=24360;
# raw 13 first appears at TICK=42516. Never wait for it to classify startup.
# Modern Steam006 no longer grants the legacy UnlockEverything inventory block.
# Fresh startup therefore waits only for the three actual vanilla starter flags.
# The broader CLEAR set is retained solely so older installations are cleaned safely.
NEW_GAME_SIGNATURE_RAW_IDS = frozenset((1, 35, 36))
ACTIVITY_PROTOCOL_VERSION = 1
ACTIVITY_LOG_NAME = "SH3AP_activity.ndjson"
LIVE_CHECK_TRACE_NAME = "SH3AP_0.1.23_FULL_GAME_CATALOGUE_TRACE.txt"
LIVE_BRIDGE_EVENT_NAME = "SH3AP_live_events.txt"
START_ARM_LOCK_NAME = "SH3AP_start_arm.lock"
LIVE_BRIDGE_STALE_SECONDS = 5.0
ACTIVITY_UI_PROTOCOL = 2
ACTIVITY_UI_SIGNATURE = b"SH3AP_ACTIVITY_UI_V2\x00"
ACTIVITY_UI_SIGNATURE_RVAS = (0x21000,)
ACTIVITY_UI_STORE_PTR_RVA = 0x21020
CONNECTION_STATUS_UI_RVA = 0x20E05
ACTIVITY_STORE_MODULE = "sh3ap_activity.asi"
ACTIVITY_STORE_SIGNATURE = b"SH3AP_ACTIVITY_STORE_V1\x00"
ACTIVITY_STORE_SIGNATURE_RVA = 0x2000
ACTIVITY_STORE_COUNT_RVA = 0x2020
ACTIVITY_STORE_GENERATION_RVA = 0x2024
ACTIVITY_STORE_LINES_RVA = 0x2028
ACTIVITY_UI_MAX_LINES = 100
ACTIVITY_UI_LINE_SIZE = 128
bridge_logger = logging.getLogger("SH3 Bridge")
activity_logger = logging.getLogger("SH3 Activity")


def _activity_log_path() -> Path:
    preferred = GAME_FOLDER / "scripts" / ACTIVITY_LOG_NAME
    try:
        preferred.parent.mkdir(parents=True, exist_ok=True)
        return preferred
    except OSError:
        return Path(Utils.user_path(ACTIVITY_LOG_NAME))


def _live_check_trace_path() -> Path:
    """Path to the native SH3AP trace that already records every direct physical pickup."""
    return GAME_FOLDER / "scripts" / LIVE_CHECK_TRACE_NAME


def _live_bridge_event_path() -> Path:
    return GAME_FOLDER / "scripts" / LIVE_BRIDGE_EVENT_NAME


def _start_arm_lock_path() -> Path:
    return GAME_FOLDER / "scripts" / START_ARM_LOCK_NAME


def _acquire_start_arm_lock(ctx: "SilentHill3Context") -> None:
    """Hold an exclusive Win32 handle while this AP client is authenticated.

    The native LiveBridge treats ERROR_SHARING_VIOLATION on this exact file as
    proof that a live AP client is currently attached. A stale file by itself is
    never enough to authorize destructive fresh-New-Game inventory cleanup.
    """
    if os.name != "nt" or ctx.start_arm_handle:
        return
    path = _start_arm_lock_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    k32 = ctypes.windll.kernel32
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k32.CreateFileW.restype = wintypes.HANDLE
    handle = k32.CreateFileW(str(path), 0xC0000000, 0, None, 2, 0x80, None)
    invalid = ctypes.c_void_p(-1).value
    if handle and int(handle) != invalid:
        ctx.start_arm_handle = int(handle)


def _release_start_arm_lock(ctx: "SilentHill3Context") -> None:
    handle = int(getattr(ctx, "start_arm_handle", 0) or 0)
    if os.name == "nt" and handle:
        try:
            ctypes.windll.kernel32.CloseHandle(wintypes.HANDLE(handle))
        except Exception:
            pass
    ctx.start_arm_handle = 0
    try:
        _start_arm_lock_path().unlink(missing_ok=True)
    except OSError:
        pass


def _read_live_bridge_events(process_started_ns: int) -> tuple[bool, set[int], bool]:
    """Read complete LiveBridge events written since the connected SH3 launched.

    The bridge truncates on launch and appends a heartbeat. Both the heartbeat
    age and the named-pipe server's creation time must match; a recently closed
    process's event file must not count as the next process's evidence.
    """
    if not process_started_ns:
        return False, set(), False
    try:
        with _live_bridge_event_path().open("rb") as fh:
            st = os.fstat(fh.fileno())
            age_ns = time.time_ns() - st.st_mtime_ns
            if (st.st_mtime_ns < process_started_ns
                    or not 0 <= age_ns <= int(LIVE_BRIDGE_STALE_SECONDS * 1e9)):
                return False, set(), False
            data = fh.read()
    except OSError:
        return False, set(), False
    # Do not turn a partially written flag such as 116 into a different check.
    end = data.rfind(b"\n")
    if end < 0:
        return False, set(), False
    lines = data[:end + 1].decode("ascii", errors="replace").splitlines()
    if not lines or lines[0] != "SESSION VERSION=2":
        return False, set(), False

    completed: set[int] = set()
    start_seen = False
    for line in lines[1:]:
        if line == "START":
            start_seen = True
            continue
        if not line.startswith("CHECK FLAG="):
            continue
        try:
            flag = int(line[11:].strip())
        except ValueError:
            continue
        location_id = PERSIST_FLAG_TO_LOCATION_ID.get(flag)
        if location_id is None:
            location_id = SCRIPTED_FLAG_TO_LOCATION_ID.get(flag)
        if location_id is not None:
            completed.add(location_id)
    return True, completed, start_seen


def _slot_catalogue_matches(slot_data: dict) -> bool:
    """Only arm native suppression for a seed with the matching location set."""
    try:
        flags = {int(flag) for flag in slot_data.get("confirmed_location_flags", ())}
    except (TypeError, ValueError):
        return False
    return (slot_data.get("sh3ap_world_version") in (WORLD_VERSION, "1.0.1")
            and flags == set(PERSIST_FLAG_TO_LOCATION_ID)
            and slot_data.get("scripted_check_protocol") == SCRIPTED_PROTOCOL
            and slot_data.get("scripted_location_ids") == sorted(
                loc for loc in SCRIPTED_BIT_TO_LOCATION_ID.values()
                if loc in active_locations(bool(slot_data.get("randomize_boss_checks"))).values())
            and slot_data.get("save_travel_protocol") == SAVE_TRAVEL_PROTOCOL
            and slot_data.get("confirmed_save_ids") == sorted(SAVE_ID_TO_LOCATION_ID)
            and slot_data.get("fast_travel_rows") == list(ACTIVE_FAST_TRAVEL_ROWS))


def _read_new_runtime_trace(offset: int | None, process_started_ns: int) -> tuple[int | None, list[str]]:
    """Read current-process startup/load classification, never pickup evidence.

    The diagnostic file may survive when native logging is disabled. Do not
    replay it unless its last write is at or after the connected SH3 process's
    creation time. A valid current trace is still read from zero on first bind,
    preserving startup and save-load ordering for clients attached after launch.
    """
    if not process_started_ns:
        return offset, []
    try:
        with _live_check_trace_path().open("rb") as fh:
            st = os.fstat(fh.fileno())
            if st.st_mtime_ns < process_started_ns:
                return offset, []
            header = fh.readline().strip()
            if not (header.startswith(b"=== SH3AP ") and b"SESSION START" in header):
                return offset, []
            if offset is None or offset > st.st_size:
                offset = 0
            if offset == st.st_size:
                return offset, []
            fh.seek(offset)
            chunk = fh.read()
    except OSError:
        return offset, []
    last_newline = chunk.rfind(b"\n")
    if last_newline < 0:
        return offset, []
    consumed = chunk[:last_newline + 1]
    lines = [raw.decode("ascii", errors="replace").strip()
             for raw in consumed.splitlines() if raw.strip()]
    return offset + len(consumed), lines


def _trace_fields(line: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in line.strip().split():
        if "=" in token:
            key, value = token.split("=", 1)
            result[key] = value
    return result


def _observe_new_game_trace(ctx: "SilentHill3Context", line: str) -> bool:
    """Track the live title/blank -> opening Mall New Game candidate.

    _sync_locations confirms initialized starter inventory on each poll. The
    old raw-13 grant recognition remains a fallback, but is no longer required:
    that grant occurs at a later pickup, after gameplay has already started.

    A real save load cancels the opening candidate before any start checks may
    be emitted.  Existing inventory or already-set pickup flags are never used
    to award the starting checks.
    """
    if line.startswith("=== SH3AP ") and "SESSION START" in line:
        # These flags describe one SH3 process, not the lifetime of the AP client.
        # Without resetting them, restarting SH3 leaves starter cleanup disabled.
        ctx.new_game_cleanup_done = False
        ctx.pending_new_game_start_checks = False
        ctx.fresh_receive_session_pending = False
        ctx.session_bound_token = 0
        ctx.bridge_completed_baseline.clear()
        ctx.bridge_last_completed.clear()
        ctx.last_world_active = False
        ctx.receive_hold_deadline = 0.0
        ctx.last_receive_error = None
        ctx.last_durability_notice = None
        ctx.new_game_candidate = False
        ctx.new_game_candidate_tick = None
        ctx.new_game_candidate_ids.clear()
        ctx.runtime_entry_classification = None
        return False

    if line.startswith("AP_SAVE_LOAD_OBSERVED ") or line.startswith("STATE_REBASE "):
        ctx.new_game_candidate = False
        ctx.new_game_candidate_tick = None
        ctx.new_game_candidate_ids.clear()
        ctx.runtime_entry_classification = "load"
        ctx.pending_new_game_start_checks = False
        ctx.fresh_receive_session_pending = False
        return False

    if line.startswith("CATALOG_CONTEXT_CHANGE "):
        f = _trace_fields(line)
        d8 = f.get("D8", "")
        d8_is_fresh_serial = (
            len(d8) == 2
            and all(ch in "0123456789abcdefABCDEF" for ch in d8)
            and int(d8, 16) != 0
        )
        if (
            f.get("KEY") == "E4:0000/D9:01"
            and d8_is_fresh_serial
            and f.get("DA") == "01"
            and ("+00:00->" + d8.upper()) in line.upper()
            and "+01:00->01" in line
        ):
            ctx.new_game_candidate = True
            ctx.new_game_cleanup_done = False
            ctx.pending_new_game_start_checks = False
            ctx.fresh_receive_session_pending = False
            ctx.runtime_entry_classification = None
            ctx.new_game_candidate_tick = None
            ctx.new_game_candidate_ids.clear()
        return False

    if ctx.new_game_candidate and line.startswith("ALT_ITEM_GRANT "):
        f = _trace_fields(line)
        if (
            f.get("RAW_ITEM_ID") == "13"
            and f.get("OWNED_BEFORE") == "0"
            and f.get("OWNED_AFTER") == "1"
            and f.get("QTY_BEFORE") == "0"
            and f.get("QTY_AFTER") == "32"
            and f.get("KEY") == "E4:0000/D9:01"
        ):
            ctx.new_game_candidate = False
            ctx.new_game_candidate_tick = None
            ctx.new_game_candidate_ids.clear()
            ctx.runtime_entry_classification = "new_game"
            return True

    return False


def _new_game_inventory_initialized() -> bool:
    """Confirm starter initialization only after a live New Game candidate.

    The caller must first consume save-load cancellation events. Inventory alone
    is never evidence of a New Game or a completed location.
    """
    if os.name != "nt":
        return False
    pid = _find_sh3_pid_for_checks()
    if not pid:
        return False
    k32 = _kernel32()
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        return False
    try:
        owned = _read_process_memory(h, ITEM_OWNED_BITS_ADDR, ITEM_OWNED_BITS_SIZE)
        return bool(
            owned is not None
            and len(owned) == ITEM_OWNED_BITS_SIZE
            and all(owned[raw >> 3] & (1 << (raw & 7))
                    for raw in NEW_GAME_SIGNATURE_RAW_IDS)
        )
    finally:
        k32.CloseHandle(h)


def _refresh_receive_extension(authenticated: bool) -> bool:
    """Verify the native extension and renew its short pickup-suppression lease."""
    if os.name != "nt":
        return False
    pid, modules = _runtime_discovery().get_modules()
    base = modules.get("sh3ap.asi", 0)
    if not pid or not base:
        return False
    k32 = _kernel32()
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, False, pid)
    if not h:
        return False
    try:
        if _read_process_memory(h, base + RECEIVE_EXTENSION_RVA, len(RECEIVE_EXTENSION_SIGNATURE)) != RECEIVE_EXTENSION_SIGNATURE:
            return False
        tick = (int(k32.GetTickCount()) & 0xFFFFFFFF) if authenticated else 0
        return _write_process_memory(h, base + RECEIVE_LEASE_RVA, tick.to_bytes(4, "little"))
    finally:
        k32.CloseHandle(h)


POPUP_SIGNATURE = b"SH3AP_POPUP_QUEUE_V1\x00"
POPUP_SIGNATURE_RVA = 0x5000
POPUP_STATE_RVA = 0x5018
POPUP_SEQUENCE_RVA = 0x501C
POPUP_LEASE_RVA = 0x5020
POPUP_PAYLOAD_RVA = 0x5028
POPUP_PAYLOAD_BYTES = 1024


def _popup_payload(parts: list[tuple[str, int]]) -> bytes:
    # Same glyph mapping and FFFF 0000 terminator as the working v23 test.
    words = []
    for text, color in parts:
        words.append(0xFF00 + color - 1)
        for char in text.replace("\r", " ").replace("\n", " "):
            words.append(ord(char) - 32 if 32 <= ord(char) <= 126 else ord("?") - 32)
    if len(words) > POPUP_PAYLOAD_BYTES // 2 - 2:
        words = words[:POPUP_PAYLOAD_BYTES // 2 - 5] + [14, 14, 14]
    words.extend((0xFFFF, 0))
    return b"".join(word.to_bytes(2, "little") for word in words).ljust(POPUP_PAYLOAD_BYTES, b"\0")


def _queue_item_popup(ctx, item, receiving: int, *, applied: bool) -> None:
    if ctx.activity_game_closed or ctx.slot is None:
        return
    sender = int(_network_field(item, "player", 0) or 0)
    item_id = int(_network_field(item, "item", 0) or 0)
    location = int(_network_field(item, "location", 0) or 0)
    flags = int(_network_field(item, "flags", 0) or 0)
    # AP marks YAML/precollected inventory with location -2 and server slot 0.
    # Silence presentation only: delivery, receipts, tracker and history remain intact.
    # Real starting-check rewards and explicit server grants (-1) still announce.
    if sender == 0 and location == -2:
        return
    # Received items wait for APRECEIVE_APPLIED. Outgoing checks use ItemSend.
    if applied:
        if receiving != ctx.slot:
            return
    elif sender != ctx.slot or receiving == ctx.slot:
        return
    if not applied:
        key = (_session_token(ctx), sender, location, receiving, item_id)
        if key in ctx.popup_sent_seen:
            return
        ctx.popup_sent_seen.add(key)
    color = 13 if flags & 1 else 2 if flags & 2 else 3 if flags & 4 else 6
    name = ctx.item_names.lookup_in_slot(item_id, receiving)
    if receiving != ctx.slot:
        parts = [("I got ", 1), (_player_name(ctx, receiving), 14), ("'s ", 1), (name, color), (".", 1)]
    elif sender == ctx.slot:
        parts = [("I got ", 1), (name, color), (".", 1)]
    else:
        parts = [(_player_name(ctx, sender) if sender else "Server", 14), (" sent you ", 1), (name, color), (".", 1)]
    ctx.popup_sequence = (ctx.popup_sequence + 1) & 0xFFFFFFFF or 1
    ctx.popup_queue.append((ctx.popup_sequence, _popup_payload(parts)))


def _find_popup_module() -> tuple[int, int] | None:
    if os.name != "nt":
        return None
    pid, modules = _runtime_discovery().get_modules()
    base = modules.get("sh3ap_itemmessage.asi", 0)
    return (pid, base) if pid and base else None


def _presentation_gameplay_ready(ctx, h, pid: int) -> bool:
    """Hold startup presentation until the game has been unblocked for a second.

    Executable 60B330/60B360 query/set the flags at 70E66A0. The scene
    entry at 41B7C0 sets bit 6; the supplied intro marker has E0, while
    both controllable-gameplay markers have zero. Require the whole word
    clear so title/loading/scene states cannot release the startup queue.
    This gates presentation only, never AP item grants or location checks.
    """
    if getattr(ctx, "presentation_pid", None) != pid:
        ctx.presentation_pid = pid
        ctx.presentation_clear_since = None
        ctx.presentation_ready = False
    world = _read_process_memory(h, 0x70E66D8, 3)
    flags = _read_process_memory(h, 0x70E66A0, 4)
    if world is None or len(world) != 3 or flags is None or len(flags) != 4:
        ctx.presentation_clear_since = None
        return False
    if not world[0]:
        ctx.presentation_clear_since = None
        ctx.presentation_ready = False
        return False
    # DA changes during normal gameplay/menu transitions; it is not a title flag.
    # Preserve the existing activity/menu behavior after initial release.
    if getattr(ctx, "presentation_ready", False):
        return True
    if int.from_bytes(flags, "little") != 0:
        ctx.presentation_clear_since = None
        return False
    now = time.monotonic()
    since = getattr(ctx, "presentation_clear_since", None)
    if since is None:
        ctx.presentation_clear_since = now
        return False
    if now - since < 1.0:
        return False
    ctx.presentation_ready = True
    return True


def _popup_diagnostic(ctx, detail: str) -> None:
    detail = f"QUEUED={len(ctx.popup_queue)} RESET={int(ctx.popup_reset_pending)} " + detail
    if detail == getattr(ctx, "last_popup_diagnostic", None):
        return
    ctx.last_popup_diagnostic = detail
    try:
        path = _live_check_trace_path().with_name("SH3AP_popup_state.txt")
        with path.open("a", encoding="ascii", errors="replace") as fh:
            fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {detail}\n")
    except OSError:
        pass


def _sync_popup_memory(ctx, authenticated: bool) -> None:
    found = _find_popup_module()
    if not found:
        _popup_diagnostic(ctx, "POPUP_MODULE_NOT_FOUND")
        return
    pid, base = found
    k32 = _kernel32()
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, False, pid)
    if not h:
        return
    try:
        if _read_process_memory(h, base + POPUP_SIGNATURE_RVA, len(POPUP_SIGNATURE)) != POPUP_SIGNATURE:
            return
        header = _read_process_memory(h, base + POPUP_STATE_RVA, 8)
        if header is None or len(header) != 8:
            return
        state = int.from_bytes(header[:4], "little")
        seq = int.from_bytes(header[4:], "little")
        fields = []
        for label, address, size in (("GAME_FLAGS", 0x70E66A0, 4), ("D8", 0x70E66D8, 1), ("D9", 0x70E66D9, 1),
                                     ("DA", 0x70E66DA, 1), ("TEXT_BUSY", 0x70C9C9C, 2),
                                     ("TEXT_MODE", 0x70C9390, 2), ("TEXT_FLAGS", 0x70C9378, 4)):
            value = _read_process_memory(h, address, size)
            fields.append(f"{label}={int.from_bytes(value, 'little') if value is not None else '?'}")
        _popup_diagnostic(ctx, f"PID={pid} STATE={state} SEQ={seq} " + " ".join(fields))
        if not authenticated or ctx.popup_reset_pending:
            if not _write_process_memory(h, base + POPUP_LEASE_RVA, bytes(4)):
                return
            if state == 0:
                ctx.popup_reset_pending = False
            return
        tick = (int(k32.GetTickCount()) & 0xFFFFFFFF) or 1
        if not _write_process_memory(h, base + POPUP_LEASE_RVA, tick.to_bytes(4, "little")):
            return
        if state == 3:
            # Remove only the head whose dismissal the native game acknowledged.
            if ctx.popup_queue and ctx.popup_queue[0][0] == seq:
                ctx.popup_queue.pop(0)
            if not _write_process_memory(h, base + POPUP_STATE_RVA, bytes(4)):
                return
            state = 0
        if state != 0 or not ctx.popup_queue:
            return
        if not _presentation_gameplay_ready(ctx, h, pid):
            return
        seq, payload = ctx.popup_queue[0]
        if not _write_process_memory(h, base + POPUP_PAYLOAD_RVA, payload):
            return
        if not _write_process_memory(h, base + POPUP_SEQUENCE_RVA, seq.to_bytes(4, "little")):
            return
        # Publish last: renderer never reads a partially-written message.
        _write_process_memory(h, base + POPUP_STATE_RVA, (1).to_bytes(4, "little"))
    finally:
        k32.CloseHandle(h)


def _clear_unlock_all_new_game_inventory() -> tuple[bool, tuple[int, ...], tuple[int, ...]]:
    """Remove only the known vanilla/Unlock-All start grants from live SH3 inventory.

    This never touches world/story flags, quantities, save files, AP receive journals,
    or any inventory item outside NEW_GAME_CLEAR_RAW_IDS.
    """
    if os.name != "nt":
        return False, (), ()
    pid = _find_sh3_pid_for_checks()
    if not pid:
        return False, (), ()

    k32 = _kernel32()
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE
    h = k32.OpenProcess(access, False, pid)
    if not h:
        return False, (), ()
    try:
        before = _read_process_memory(h, ITEM_OWNED_BITS_ADDR, ITEM_OWNED_BITS_SIZE)
        if before is None or len(before) != ITEM_OWNED_BITS_SIZE:
            return False, (), ()

        buf = bytearray(before)
        present_before: list[int] = []
        for raw_id in sorted(NEW_GAME_CLEAR_RAW_IDS):
            byte_index = raw_id >> 3
            mask = 1 << (raw_id & 7)
            if byte_index >= len(buf):
                return False, (), ()
            if buf[byte_index] & mask:
                present_before.append(raw_id)
            buf[byte_index] &= ~mask & 0xFF

        if bytes(buf) != before and not _write_process_memory(h, ITEM_OWNED_BITS_ADDR, bytes(buf)):
            return False, tuple(present_before), ()

        after = _read_process_memory(h, ITEM_OWNED_BITS_ADDR, ITEM_OWNED_BITS_SIZE)
        if after is None or len(after) != ITEM_OWNED_BITS_SIZE:
            return False, tuple(present_before), ()

        present_after = tuple(
            raw_id for raw_id in sorted(NEW_GAME_CLEAR_RAW_IDS)
            if after[raw_id >> 3] & (1 << (raw_id & 7))
        )
        return not present_after, tuple(present_before), present_after
    finally:
        k32.CloseHandle(h)



def _network_field(item, name: str, default=0):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _classification_name(flags: int) -> str:
    # Archipelago NetworkItem flags: advancement=1, useful=2, trap=4.
    if flags & 0x01:
        return "progression"
    if flags & 0x04:
        return "trap"
    if flags & 0x02:
        return "useful"
    return "filler"


# Archipelago's current GUI/text colors from NetUtils.JSONtoTextParser.
# Stored as SH3 AARRGGBB values so the in-game renderer can reproduce them.
AP_JSON_COLORS = {
    "black": 0xFF000000,
    "red": 0xFFEE0000,
    "green": 0xFF00FF7F,
    "yellow": 0xFFFAFAD2,
    "blue": 0xFF6495ED,
    "magenta": 0xFFEE00EE,
    "cyan": 0xFF00EEEE,
    "slateblue": 0xFF6D8BE8,
    "plum": 0xFFAF99EF,
    "salmon": 0xFFFA8072,
    "white": 0xFFFFFFFF,
    "orange": 0xFFFF7700,
}


def _ap_item_color(flags: int) -> int:
    # Match NetUtils.JSONtoTextParser precedence exactly.
    flags = int(flags or 0)
    if flags == 0:
        return AP_JSON_COLORS["cyan"]
    if flags & 0b001:
        return AP_JSON_COLORS["plum"]
    if flags & 0b010:
        return AP_JSON_COLORS["slateblue"]
    if flags & 0b100:
        return AP_JSON_COLORS["salmon"]
    return AP_JSON_COLORS["cyan"]


def _ap_color_node(value: str) -> int:
    # Kivy/JSON parser applies listed foreground colors in order; last wins.
    color = AP_JSON_COLORS["white"]
    for name in str(value or "").split(";"):
        if name in AP_JSON_COLORS:
            color = AP_JSON_COLORS[name]
    return color


def _resolve_printjson_segments(ctx: "SilentHill3Context", data) -> list[dict]:
    """Resolve PrintJSON parts exactly like Archipelago's JSONtoTextParser.

    The server-provided part order/text is preserved.  ID nodes are resolved
    through the same client-side item/location/player lookup tables, and colors
    follow NetUtils.JSONtoTextParser.
    """
    resolved: list[dict] = []
    for raw_node in data or ():
        if not isinstance(raw_node, dict):
            continue
        node = dict(raw_node)
        node_type = str(node.get("type") or "")
        text = str(node.get("text", ""))
        color = AP_JSON_COLORS["white"]
        try:
            if node_type == "player_id":
                player = int(text)
                text = ctx.player_names.get(player, f"Player {player}")
                color = AP_JSON_COLORS["magenta"] if ctx.slot_concerns_self(player) else AP_JSON_COLORS["yellow"]
            elif node_type == "player_name":
                color = AP_JSON_COLORS["yellow"]
            elif node_type == "item_id":
                item_id = int(text)
                player = int(node.get("player", 0) or 0)
                text = ctx.item_names.lookup_in_slot(item_id, player)
                color = _ap_item_color(int(node.get("flags", 0) or 0))
            elif node_type == "item_name":
                color = _ap_item_color(int(node.get("flags", 0) or 0))
            elif node_type == "location_id":
                location_id = int(text)
                player = int(node.get("player", 0) or 0)
                text = ctx.location_names.lookup_in_slot(location_id, player)
                color = AP_JSON_COLORS["green"]
            elif node_type == "location_name":
                color = AP_JSON_COLORS["green"]
            elif node_type == "entrance_name":
                color = AP_JSON_COLORS["blue"]
            elif node_type == "color":
                color = _ap_color_node(node.get("color", "white"))
            else:
                # Plain text is white in the Archipelago client.
                color = AP_JSON_COLORS["white"]
        except Exception:
            # Preserve server text if an ID lookup is temporarily unavailable.
            color = AP_JSON_COLORS["white"]

        text = text.replace("\r", " ").replace("\n", " ")
        if not text:
            continue
        if resolved and int(resolved[-1]["color"]) == int(color):
            resolved[-1]["text"] += text
        else:
            resolved.append({"text": text, "color": int(color)})
    return resolved


def _legacy_activity_segments(event: dict) -> list[dict]:
    """Fallback only for old history already on disk before this update."""
    kind = str(event.get("kind", ""))
    cls = str(event.get("classification", "filler"))
    class_colors = {
        "progression": AP_JSON_COLORS["plum"],
        "useful": AP_JSON_COLORS["slateblue"],
        "trap": AP_JSON_COLORS["salmon"],
        "filler": AP_JSON_COLORS["cyan"],
    }
    color = class_colors.get(cls, AP_JSON_COLORS["white"])
    if kind == "received":
        text = f"RECEIVED: {event.get('item', 'Item')} FROM {event.get('from_player', 'Unknown')}"
    elif kind == "sent":
        text = f"SENT: {event.get('item', 'Item')} TO {event.get('to_player', 'Unknown')}"
    elif kind == "check":
        text = f"CHECK: {event.get('location', 'Unknown Location')}"
        color = 0xFFAAAAAA
    else:
        text = str(event.get("text") or event.get("item") or event.get("location") or kind or "AP ACTIVITY")
    return [{"text": text, "color": int(color)}]


def _pack_activity_segments(segments) -> bytes:
    """Pack a multi-color Activity line into one existing 128-byte record.

    Layout:
      +0  0xA5 format marker
      +1  segment count
      +2  total rendered character count
      +3  reserved
      +4  repeated: color:u32, len:u8, ASCII bytes, NUL
    """
    normalized: list[tuple[str, int]] = []
    for segment in segments or ():
        if isinstance(segment, dict):
            text = str(segment.get("text", ""))
            color = int(segment.get("color", AP_JSON_COLORS["white"])) & 0xFFFFFFFF
        else:
            continue
        # SH3's custom font path is single-byte. Keep punctuation/spacing exactly;
        # only unsupported Unicode is replaced rather than changing the wording.
        text = text.replace("\r", " ").replace("\n", " ")
        encoded = text.encode("ascii", errors="replace")
        text = encoded.decode("ascii", errors="ignore")
        if not text:
            continue
        if normalized and normalized[-1][1] == color:
            normalized[-1] = (normalized[-1][0] + text, color)
        else:
            normalized.append((text, color))

    out = bytearray(ACTIVITY_UI_LINE_SIZE)
    out[0] = 0xA5
    pos = 4
    count = 0
    total_chars = 0
    for text, color in normalized:
        raw = text.encode("ascii", errors="replace")
        # 6 bytes overhead: color + length + terminating NUL.
        available = ACTIVITY_UI_LINE_SIZE - pos - 6
        if available <= 0:
            break
        raw = raw[:min(255, available)]
        if not raw:
            break
        out[pos:pos+4] = int(color).to_bytes(4, "little", signed=False)
        out[pos+4] = len(raw)
        out[pos+5:pos+5+len(raw)] = raw
        out[pos+5+len(raw)] = 0
        pos += 6 + len(raw)
        count += 1
        total_chars += len(raw)
        if len(raw) < len(text.encode("ascii", errors="replace")):
            break

    out[1] = min(count, 255)
    out[2] = min(total_chars, 255)
    return bytes(out)


def _session_token(ctx: "SilentHill3Context") -> int:
    seed_name = ctx.room_seed_name or ""
    slot_name = ctx.auth or ""
    slot_number = ctx.slot if ctx.slot is not None else -1
    if not seed_name or slot_number < 0:
        return 0
    token = zlib.crc32(f"{seed_name}|{slot_name}|{slot_number}".encode("utf-8")) & 0xFFFFFFFF
    return token or 1


def _player_name(ctx: "SilentHill3Context", slot: int) -> str:
    return ctx.player_names.get(slot, f"Player {slot}")


def _parse_status(line: str) -> dict[str, str]:
    result: dict[str, str] = {}
    parts = line.strip().split()
    if not parts or parts[0] != "STATUS":
        return result
    for token in parts[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            result[key] = value
    return result


TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_INFORMATION = 0x0400
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260),
    ]


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD), ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD), ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD), ("modBaseAddr", ctypes.POINTER(ctypes.c_ubyte)),
        ("modBaseSize", wintypes.DWORD), ("hModule", wintypes.HMODULE),
        ("szModule", wintypes.WCHAR * 256), ("szExePath", wintypes.WCHAR * 260),
    ]


@lru_cache(maxsize=1)
def _kernel32():
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.Process32FirstW.restype = wintypes.BOOL
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.Process32NextW.restype = wintypes.BOOL
    k32.Module32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
    k32.Module32FirstW.restype = wintypes.BOOL
    k32.Module32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
    k32.Module32NextW.restype = wintypes.BOOL
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.ReadProcessMemory.restype = wintypes.BOOL
    k32.WriteProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.WriteProcessMemory.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL
    k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.WaitForSingleObject.restype = wintypes.DWORD
    return k32


def _find_sh3_process_and_ui() -> tuple[int, int, int] | None:
    if os.name != "nt":
        return None
    pid, modules = _runtime_discovery().get_modules()
    ui_base = modules.get("sh3ap_ui.asi", 0)
    store_base = modules.get(ACTIVITY_STORE_MODULE, 0)
    return (pid, ui_base, store_base) if pid and ui_base and store_base else None


def _read_process_memory(handle, address: int, size: int) -> bytes | None:
    k32 = _kernel32()
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t()
    if not k32.ReadProcessMemory(handle, ctypes.c_void_p(address), buf, size, ctypes.byref(got)):
        return None
    return bytes(buf.raw[:got.value])


def _write_process_memory(handle, address: int, data: bytes) -> bool:
    if not data:
        return True
    k32 = _kernel32()
    buf = ctypes.create_string_buffer(data)
    wrote = ctypes.c_size_t()
    return bool(k32.WriteProcessMemory(handle, ctypes.c_void_p(address), buf, len(data), ctypes.byref(wrote)) and wrote.value == len(data))


# SH3AP_DIRECT_CONNECTION_STATUS_V2
def _sync_connection_status_ui(state: int) -> None:
    """Write the real Archipelago authenticated state directly to SH3AP_UI.

    0 = Not Connected
    1 = Connecting (reserved)
    2 = Connected

    This intentionally bypasses Activity history and the local SH3AP pipe
    connection state.  The source of truth is the Archipelago client session.
    """
    if os.name != "nt":
        return
    found = _find_sh3_process_and_ui()
    if not found:
        return
    pid, ui_base, _store_base = found
    state = 2 if int(state) == 2 else (1 if int(state) == 1 else 0)

    k32 = _kernel32()
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE
    h = k32.OpenProcess(access, False, pid)
    if not h:
        return
    try:
        if not any(_read_process_memory(h, ui_base + rva, len(ACTIVITY_UI_SIGNATURE)) == ACTIVITY_UI_SIGNATURE
                   for rva in ACTIVITY_UI_SIGNATURE_RVAS):
            return
        _write_process_memory(
            h,
            ui_base + CONNECTION_STATUS_UI_RVA,
            bytes((state,)),
        )
    finally:
        k32.CloseHandle(h)


def _current_ap_connection_status(ctx: "SilentHill3Context") -> int:
    """Return 2 only after Archipelago accepted the slot."""
    return 2 if (
        ctx.server is not None
        and ctx.slot is not None
        and ctx.team is not None
    ) else 0


def _activity_snapshot(ctx: "SilentHill3Context") -> tuple[bytes, int]:
    token = _session_token(ctx)
    if ctx.server is None or ctx.slot is None:
        return bytes(ACTIVITY_UI_MAX_LINES * ACTIVITY_UI_LINE_SIZE), 0
    # Render server messages and confirmed grants using the same segment format.
    events = [
        e for e in ctx.activity_history
        if int(e.get("session_token", 0) or 0) == token
        and isinstance(e.get("segments"), list)
    ]
    events = events[-ACTIVITY_UI_MAX_LINES:]
    block = bytearray(ACTIVITY_UI_MAX_LINES * ACTIVITY_UI_LINE_SIZE)
    for index, event in enumerate(events):
        record = _pack_activity_segments(event.get("segments", []))
        off = index * ACTIVITY_UI_LINE_SIZE
        block[off:off+ACTIVITY_UI_LINE_SIZE] = record
    return bytes(block), len(events)


def _sync_activity_ui_memory(ctx: "SilentHill3Context") -> None:
    if os.name != "nt":
        return
    found = _find_sh3_process_and_ui()
    if not found:
        if ctx.activity_game_pid is not None:
            ctx.clear_activity()
            ctx.activity_game_pid = None
            ctx.activity_game_closed = True
        ctx.activity_ui_bound = None
        return
    pid, ui_base, store_base = found
    if ctx.activity_game_pid is not None and ctx.activity_game_pid != pid:
        ctx.clear_activity()
    ctx.activity_game_pid = pid
    ctx.activity_game_closed = False
    k32 = _kernel32()
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE
    h = k32.OpenProcess(access, False, pid)
    if not h:
        return
    try:
        ui_signature_ok = any(
            _read_process_memory(h, ui_base + rva, len(ACTIVITY_UI_SIGNATURE)) == ACTIVITY_UI_SIGNATURE
            for rva in ACTIVITY_UI_SIGNATURE_RVAS
        )
        store_signature_ok = (
            _read_process_memory(h, store_base + ACTIVITY_STORE_SIGNATURE_RVA, len(ACTIVITY_STORE_SIGNATURE))
            == ACTIVITY_STORE_SIGNATURE
        )
        if not ui_signature_ok or not store_signature_ok:
            bind = (pid, ui_base, store_base, False)
            if ctx.activity_ui_bound != bind:
                activity_logger.info(
                    "SH3AP Activity Viewer v2 runtime pair is not installed; NDJSON logging remains active."
                )
            ctx.activity_ui_bound = bind
            return

        # Tell the UI where the dedicated Activity store module lives.
        if not _write_process_memory(
            h, ui_base + ACTIVITY_UI_STORE_PTR_RVA, int(store_base).to_bytes(4, "little")
        ):
            return

        if _presentation_gameplay_ready(ctx, h, pid):
            lines, count = _activity_snapshot(ctx)
        else:
            # Keep the queued history; publish it once initial gameplay is ready.
            lines, count = bytes(ACTIVITY_UI_MAX_LINES * ACTIVITY_UI_LINE_SIZE), 0
        snapshot_hash = zlib.crc32(lines[:count * ACTIVITY_UI_LINE_SIZE]) & 0xFFFFFFFF
        bind = (pid, ui_base, store_base, True)
        if (
            ctx.activity_ui_bound == bind
            and ctx.activity_ui_snapshot_hash == snapshot_hash
            and ctx.activity_ui_snapshot_count == count
        ):
            return

        if not _write_process_memory(h, store_base + ACTIVITY_STORE_LINES_RVA, lines):
            return
        if not _write_process_memory(
            h, store_base + ACTIVITY_STORE_COUNT_RVA, int(count).to_bytes(4, "little")
        ):
            return

        ctx.activity_ui_generation = (ctx.activity_ui_generation + 1) & 0xFFFFFFFF
        if ctx.activity_ui_generation == 0:
            ctx.activity_ui_generation = 1
        _write_process_memory(
            h,
            store_base + ACTIVITY_STORE_GENERATION_RVA,
            int(ctx.activity_ui_generation).to_bytes(4, "little"),
        )
        ctx.activity_ui_bound = bind
        ctx.activity_ui_snapshot_hash = snapshot_hash
        ctx.activity_ui_snapshot_count = count
    finally:
        k32.CloseHandle(h)


def _scan_sh3_pid_for_checks() -> int:
    """Find sh3.exe without depending on Activity UI modules."""
    if os.name != "nt":
        return 0
    k32 = _kernel32()
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE:
        return 0
    try:
        pe = PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        if k32.Process32FirstW(snap, ctypes.byref(pe)):
            while True:
                if pe.szExeFile.lower() == "sh3.exe":
                    return int(pe.th32ProcessID)
                if not k32.Process32NextW(snap, ctypes.byref(pe)):
                    break
    finally:
        k32.CloseHandle(snap)
    return 0


def _scan_sh3_modules(pid: int) -> dict[str, int] | None:
    k32 = _kernel32()
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    if snap == INVALID_HANDLE_VALUE:
        return None
    try:
        me = MODULEENTRY32W()
        me.dwSize = ctypes.sizeof(me)
        if not k32.Module32FirstW(snap, ctypes.byref(me)):
            return None
        modules = {}
        while True:
            modules[me.szModule.lower()] = int(ctypes.cast(me.modBaseAddr, ctypes.c_void_p).value or 0)
            if not k32.Module32NextW(snap, ctypes.byref(me)):
                # ERROR_NO_MORE_FILES is the only successful end of enumeration.
                return modules if ctypes.get_last_error() == 18 else None
    finally:
        k32.CloseHandle(snap)


@lru_cache(maxsize=1)
def _runtime_discovery():
    k32 = _kernel32()
    return RuntimeDiscovery(
        _scan_sh3_pid_for_checks, _scan_sh3_modules,
        lambda pid: k32.OpenProcess(0x00100000, False, pid),  # SYNCHRONIZE only
        lambda handle: k32.WaitForSingleObject(handle, 0) == 0x102,
        k32.CloseHandle,
        ("sh3ap.asi", "sh3ap_ui.asi", ACTIVITY_STORE_MODULE, "sh3ap_itemmessage.asi"),
    )


def _find_sh3_pid_for_checks() -> int:
    if os.name != "nt":
        return 0
    return _runtime_discovery().get_pid()


class PipeBridge:
    def __init__(self) -> None:
        self.file = None
        self.process_identity: tuple[int, int] | None = None
        self.lock = threading.Lock()

    def connect(self) -> str:
        self.close()
        self.file = open(PIPE_PATH, "r+b", buffering=0)
        return self.command("HELLO SH3AP_CLIENT_V2")

    def close(self) -> None:
        f = self.file
        self.file = None
        self.process_identity = None
        if f is not None:
            try:
                f.close()
            except OSError:
                pass

    def event_process_identity(self) -> tuple[int, int] | None:
        """Identify the actual pipe server, including PID reuse across launches."""
        if os.name != "nt":
            return None
        import msvcrt
        with self.lock:
            if self.file is None:
                return None
            if self.process_identity is not None:
                return self.process_identity
            k32 = _kernel32()
            k32.GetNamedPipeServerProcessId.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.ULONG)]
            k32.GetNamedPipeServerProcessId.restype = wintypes.BOOL
            k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
            k32.GetProcessTimes.restype = wintypes.BOOL
            pid = wintypes.ULONG()
            try:
                pipe_handle = msvcrt.get_osfhandle(self.file.fileno())
                if not k32.GetNamedPipeServerProcessId(wintypes.HANDLE(pipe_handle), ctypes.byref(pid)):
                    return None
                handle = k32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
                if not handle:
                    return None
                try:
                    created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
                    if not k32.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                              ctypes.byref(kernel), ctypes.byref(user)):
                        return None
                    ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
                    started_ns = (ticks - 116444736000000000) * 100
                    if started_ns <= 0:
                        return None
                    self.process_identity = (pid.value, started_ns)
                    return self.process_identity
                finally:
                    k32.CloseHandle(handle)
            except (OSError, ValueError):
                return None

    def command(self, text: str) -> str:
        with self.lock:
            if self.file is None:
                raise OSError("SH3AP pipe is not connected")
            self.file.write((text.rstrip("\r\n") + "\r\n").encode("ascii"))
            data = self.file.read(4096)
            if not data:
                raise OSError("SH3AP pipe closed")
            return data.decode("ascii", errors="replace").strip()



def _exchange_save_travel(cookie: bytes | None, mask: int, scripted_options: int = 0,
                          clear_native_save_ids: tuple[int, ...] = ()) -> tuple[set[int], bool]:
    """Renew the mailbox; the game thread alone installs its hook and owns events."""
    if os.name != "nt":
        return set(), False
    pid, modules = _runtime_discovery().get_modules()
    ui = modules.get("sh3ap_ui.asi", 0)
    core = modules.get("sh3ap.asi", 0)
    if not pid or not ui or not core:
        return set(), False
    k32 = _kernel32()
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, False, pid)
    if not h:
        return set(), False
    try:
        base = ui + NATIVE_RVA
        head = _read_process_memory(h, base, 0x60)
        if not head or len(head) != 0x60 or not head.startswith(NATIVE_SIGNATURE):
            return set(), False
        if cookie is None:
            _write_process_memory(h, base+0x18, bytes(4))
            _write_process_memory(h, base+0x38, bytes(4))
            return set(), False
        if _read_process_memory(h, ui+0x23060, 17) != b"SHAP_SAVES_29_V1\0":
            raise RuntimeError("Install this APWorld and restart SH3 for all 29 save checks")
        if _read_process_memory(h, core+VIRTUAL_RVA, len(VIRTUAL_SIGNATURE)) != VIRTUAL_SIGNATURE:
            raise RuntimeError("Install this APWorld's matching core and UI runtime to enable save checks")
        script_head = _read_process_memory(h, ui+0x24000, 0x20)
        if (not script_head or len(script_head) != 0x20
                or not script_head.startswith(b"SHAP_SCRIPT_V1\0")
                or _read_process_memory(h, core+0x33000, 14) != b"SHAP_ITEMS_V3\0"):
            raise RuntimeError("Install this APWorld's matching item and check runtime")
        if _read_process_memory(h, ui+0x30038, 4) != struct.pack("<I", 0x37313238):
            raise RuntimeError("Close SH3 and reopen this client to install the 128-bit check runtime")
        late_status = _read_process_memory(h, ui+0x30034, 4)
        if late_status == struct.pack("<I", 2):
            _write_process_memory(h, base+0x18, bytes(4))
            raise RuntimeError("Late-game pickup hook did not match; AP suppression paused")
        if late_status != struct.pack("<I", 1):
            return set(), False
        script_status = struct.unpack_from("<I", script_head, 0x14)[0]
        if _read_process_memory(h, ui+0x24040, 15) != b"SHAP_BOSSES_V1\0":
            raise RuntimeError("Close SH3 and reopen this Silent Hill 3 Client to install the five-boss runtime")
        if _read_process_memory(h, ui+0x24050, 17) != b"SHAP_POSTMALL_V3\0":
            raise RuntimeError("Close SH3 and install this APWorld's matching post-Mall runtime")
        if script_status == 2:
            _write_process_memory(h, base+0x18, bytes(4))
            raise RuntimeError("Scripted item hook signatures did not match; AP suppression paused")
        if script_status != 1:
            return set(), False
        if not _write_process_memory(h, ui+0x2401c, struct.pack("<I", scripted_options & 511)):
            return set(), False
        if struct.unpack_from("<I", head, 0x14)[0] == 2:
            raise RuntimeError("Save-opening hook did not match the executable; no hook was installed")
        if head[0x40:0x50] != cookie:
            if not _write_process_memory(h, base+0x18, bytes(4)):
                return set(), False
            if not _write_process_memory(h, base+0x40, cookie):
                return set(), False
        if not _write_process_memory(h, base+0x1c, struct.pack("<I", mask)):
            return set(), False
        tick = int(k32.GetTickCount()) & 0xFFFFFFFF
        if not _write_process_memory(h, base+0x18, struct.pack("<I", tick or 1)):
            return set(), False
        generation_before = _read_process_memory(h, base+0x30, 4)
        head = _read_process_memory(h, base, 0x60)
        script_bits = _read_process_memory(h, ui+0x24030, 16)
        generation_after = _read_process_memory(h, base+0x30, 4)
        if (not head or len(head) != 0x60 or generation_before is None
                or len(generation_before) != 4 or generation_before != generation_after
                or int.from_bytes(generation_before, "little") & 1):
            return set(), False
        bound = (head[0x40:0x50] == cookie == head[0x50:0x60]
                 and struct.unpack_from("<I", head, 0x14)[0] == 1
                 and struct.unpack_from("<I", head, 0x28)[0] == 1)
        if not bound:
            return set(), False
        bits = struct.unpack_from("<I", head, 0x20)[0]
        if clear_native_save_ids:
            cleaned = bits
            for native_id in clear_native_save_ids:
                cleaned &= ~(1 << native_id)
            if cleaned != bits:
                if not _write_process_memory(h, base+0x20, struct.pack("<I", cleaned)):
                    raise OSError("Could not clear transient Random Start save-visit artifact")
                verify_bits = _read_process_memory(h, base+0x20, 4)
                if verify_bits != struct.pack("<I", cleaned):
                    raise OSError("Random Start save-visit artifact clear did not verify")
                bits = cleaned
        opened = {loc for native, loc in SAVE_ID_TO_LOCATION_ID.items() if bits & (1 << native)}
        if script_bits and len(script_bits) == 16:
            bits = int.from_bytes(script_bits, "little")
            opened.update(loc for bit, loc in SCRIPTED_BIT_TO_LOCATION_ID.items()
                          if bits & (1 << bit))
        # The temporary Toggle All override includes every earned destination;
        # it must not stall item receipts or overwrite the durable earned mask.
        displayed = _read_process_memory(h, ui+0x21ff0, 4)
        temporary_all = struct.unpack_from("<I", head, 0x38)[0] == 1
        ready = (displayed == struct.pack("<I", mask)
                 or (temporary_all and displayed == struct.pack("<I", 0x1fffffff)))
        return opened, ready
    finally:
        k32.CloseHandle(h)


async def _sync_save_travel(ctx: "SilentHill3Context") -> None:
    authenticated = (ctx.server is not None and ctx.slot is not None and ctx.team is not None
                     and ctx.room_seed_name and ctx.auth and ctx.location_catalogue_compatible)
    if not authenticated:
        await asyncio.to_thread(_exchange_save_travel, None, 0)
        ctx.travel_runtime_ready = False
        ctx.live_runtime_checks = set()
        return
    identity = [GAME_NAME, ctx.room_seed_name, ctx.team, ctx.slot, ctx.auth]
    if ctx.travel_state is None or ctx.travel_state.identity != identity:
        ctx.travel_state = await asyncio.to_thread(
            TravelState, GAME_FOLDER / "scripts" / "SHAP_save_travel",
            ctx.room_seed_name, ctx.team, ctx.slot, ctx.auth)
    state = ctx.travel_state
    server = ctx.server
    # Server-confirmed checks can repair local history; native flags cannot.
    if getattr(ctx, "travel_snapshot_pending", False):
        # Copy before yielding: a later ReceivedItems packet may extend the list.
        snapshot = tuple(ctx.items_received)
        ctx.travel_snapshot_pending = False
        try:
            await asyncio.to_thread(state.replace_server_receipts, snapshot)
        except Exception:
            ctx.travel_snapshot_pending = True
            raise
    # Random Starting Area briefly passes through the stock Mall Toilet bootstrap.
    # That transient state must not become a durable visit/unlock when another row
    # is the seed-selected start. Server check history for row 0 is also excluded
    # from travel-history repair on these seeds; a later genuine native visit still
    # unlocks it normally.
    suppress_mall = bool(
        ctx.slot_data.get("random_starting_area", False)
        and isinstance(ctx.slot_data.get("starting_area_row"), int)
        and not isinstance(ctx.slot_data.get("starting_area_row"), bool)
        and ctx.slot_data.get("starting_area_row") != 0
    )
    checked_for_travel = set(ctx.checked_locations)
    if suppress_mall:
        checked_for_travel.discard(MALL_TOILET_LOCATION_ID)
        if ctx.random_start_mall_artifact_pending and not ctx.random_start_mall_artifact_cleared:
            await asyncio.to_thread(state.forget_visit, MALL_TOILET_LOCATION_ID)

    await asyncio.to_thread(state.reconcile, (), checked_for_travel, ctx.items_received)
    scripted_options = (int(bool(ctx.slot_data.get("randomize_maps")))
                        | (int(bool(ctx.slot_data.get("randomize_boss_checks"))) << 1)
                        | sum(1 << (2 + index) for index, name in enumerate(MAP_CHECK_ITEMS.values())
                              if any(item.item == ITEM_NAME_TO_ID[name] for item in ctx.items_received)))
    clear_ids = ()
    if (suppress_mall and ctx.random_start_mall_artifact_pending
            and not ctx.random_start_mall_artifact_cleared
            and ctx.new_game_cleanup_done and ctx.session_bound_token):
        clear_ids = (MALL_TOILET_NATIVE_SAVE_ID,)
    opened, ready = await asyncio.to_thread(
        _exchange_save_travel, state.cookie, state.mask, scripted_options, clear_ids
    )
    if clear_ids:
        opened.discard(MALL_TOILET_LOCATION_ID)
        ctx.random_start_mall_artifact_pending = False
        ctx.random_start_mall_artifact_cleared = True
        bridge_logger.info(
            "Random Starting Area travel state synchronized to the selected starting save."
        )
    ctx.travel_runtime_ready = ready
    ctx.live_runtime_checks = set(opened)
    await asyncio.to_thread(state.reconcile, opened, checked_for_travel, ())
    if (ctx.server is not server or not ctx.location_catalogue_compatible
            or state.identity != [GAME_NAME, ctx.room_seed_name, ctx.team, ctx.slot, ctx.auth]):
        return
    # Durable history is for display/reconciliation, not evidence of a new
    # completion in this server session. Only the current native mailbox may
    # submit checks; with SH3 closed, opened is empty.
    if opened:
        await ctx.check_locations(set(opened) & set(active_locations(bool(scripted_options & 2)).values()))
    await _report_boss_goal(ctx, state, opened)
    if ready:
        pending = sorted(i for i in state.receipts if i not in state.announced and i < len(ctx.items_received))
        await asyncio.to_thread(state.mark_announced, pending)
        for index in pending:
            item = ctx.items_received[index]
            _record_applied_activity(ctx, item, index)
            _queue_item_popup(ctx, item, ctx.slot, applied=True)
    ctx.travel_error = None


async def _report_boss_goal(ctx, state, live_checks=()) -> None:
    # CommonClient resends finished_game before our Connected handler validates
    # the new slot. Keep our own identity-bound token and retry after reconnect.
    required = goal_location_ids(ctx.slot_data.get("win_condition"))
    token = (id(ctx.server), *state.identity)
    if (state.identity == [GAME_NAME, ctx.room_seed_name, ctx.team, ctx.slot, ctx.auth]
            and ctx.location_catalogue_compatible
            and required <= (set(ctx.checked_locations) | set(live_checks)) and ctx.goal_sent_token != token
            and ctx.server and ctx.server.socket.open and not ctx.server.socket.closed):
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
        ctx.goal_sent_token = token
        logger.info("SH3 goal complete: %s.", ctx.slot_data["win_condition"].replace("_", " "))


class SilentHill3Context(CommonContext):
    game = GAME_NAME
    items_handling = 0b111
    want_slot_data = True

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.deathlink_state = DeathLinkState()
        self.trap_state = None
        self.trap_error = None
        self.bridge = PipeBridge()
        self.bridge_connected = False
        self.last_status: dict[str, str] = {}
        self.last_logged_received_count = 0
        self.slot_data: dict = {}
        self.location_catalogue_compatible = False
        self.session_bound_token = 0
        self.delivery_identity_token = 0
        self.room_seed_name: str | None = None
        self.last_durability_notice: tuple[int, int] | None = None
        self.last_location_diag: tuple | None = None
        self.last_receive_error: str | None = None
        self.live_check_trace_offset: int | None = None
        self.location_process_identity: tuple[int, int] | None = None
        self.location_source_warning: str | None = None
        # LiveBridge is cumulative for one sh3.exe process. Keep an epoch baseline
        # so a second New Game in the same process cannot inherit checks from the
        # previous run. The baseline is the previous poll, so a pickup that occurs
        # in the same poll as New Game classification is still retained.
        self.bridge_completed_baseline: set[int] = set()
        self.bridge_last_completed: set[int] = set()
        self.start_arm_handle: int = 0
        self.new_game_candidate = False
        self.new_game_candidate_tick: int | None = None
        self.new_game_candidate_ids: set[int] = set()
        self.pending_new_game_start_checks = False
        self.new_game_cleanup_done = False
        self.receive_extension_available = False
        self.tracker_cached_payload = None
        self.tracker_history = None
        self.tracker_error = None
        self.travel_state = None
        self.travel_runtime_ready = False
        self.travel_error = None
        self.goal_sent_token = None
        self.fresh_receive_session_pending = False
        self.runtime_entry_classification: str | None = None
        self.last_world_active = False
        self.receive_hold_deadline = 0.0
        self.activity_log_path = _activity_log_path()
        self.activity_seen: set[str] = set()
        self.activity_pending: list[dict] = []
        self.activity_history: list[dict] = []
        self.activity_pipe_supported = False
        self.activity_ui_bound = None
        self.activity_ui_snapshot_hash = -1
        self.activity_ui_snapshot_count = -1
        self.activity_ui_generation = 0
        self.popup_queue = []
        self.popup_sent_seen = set()
        self.popup_sequence = 0
        self.popup_reset_pending = True
        self.activity_game_pid = None
        self.random_start_mall_artifact_pending = False
        self.random_start_mall_artifact_cleared = False
        self.activity_game_closed = False
        # The NDJSON file is an audit log, not a feed to restore next launch.

    def clear_activity(self) -> None:
        self.presentation_pid = None
        self.presentation_clear_since = None
        self.presentation_ready = False
        self.popup_queue.clear()
        self.popup_sent_seen.clear()
        self.popup_reset_pending = True
        self.activity_seen.clear()
        self.activity_pending.clear()
        self.activity_history.clear()
        self.activity_ui_snapshot_hash = -1
        self.activity_ui_snapshot_count = -1

    def record_activity(self, event: dict) -> None:
        if self.activity_game_closed:
            return
        event_id = str(event.get("event_id", ""))
        if not event_id or event_id in self.activity_seen:
            return
        event = dict(event)
        event.setdefault("activity_protocol", ACTIVITY_PROTOCOL_VERSION)
        event.setdefault("session_token", _session_token(self))
        self.activity_seen.add(event_id)
        try:
            self.activity_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.activity_log_path.open("a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        except OSError as exc:
            activity_logger.warning("Could not append SH3AP activity event: %s", exc)
        self.activity_pending.append(event)
        self.activity_history.append(event)
        if len(self.activity_pending) > 512:
            del self.activity_pending[:-512]
        if len(self.activity_history) > 2048:
            del self.activity_history[:-2048]

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self) -> None:
        # This hook is called by CommonClient for /disconnect and socket loss.
        # Write red before CommonContext clears its server/session fields.
        self.deathlink_state.reset()
        try:
            await asyncio.to_thread(_exchange_traps, self, sys.modules[__name__], True)
        except Exception:
            pass  # Native lease also expires if the process closed during disconnect.
        await self.update_death_link(False)
        await asyncio.to_thread(_exchange_deathlink, self, sys.modules[__name__], True)
        self.clear_activity()
        await asyncio.to_thread(_sync_tracker, self, sys.modules[__name__], True)
        await asyncio.to_thread(_exchange_save_travel, None, 0)
        self.travel_runtime_ready = False
        await asyncio.to_thread(_sync_popup_memory, self, False)
        await asyncio.to_thread(_sync_activity_ui_memory, self)
        await asyncio.to_thread(_sync_connection_status_ui, 0)
        await asyncio.to_thread(_release_start_arm_lock, self)
        await super().connection_closed()

    def on_deathlink(self, data: dict) -> None:
        if str(data.get("source", "")) == self.player_names.get(self.slot):
            return
        if self.deathlink_state.receive(data):
            super().on_deathlink(data)

    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "RoomInfo":
            # Archipelago 0.6.7 exposes the authoritative server seed here.
            # Never fall back to a provisional/empty identity for item delivery.
            incoming_seed = str(args.get("seed_name", "") or "")
            if incoming_seed:
                if self.room_seed_name and self.room_seed_name != incoming_seed and self.delivery_identity_token:
                    bridge_logger.error("Server seed identity changed after AP delivery was bound; receive delivery is paused for safety.")
                if self.room_seed_name != incoming_seed:
                    if self.room_seed_name:
                        self.bridge_completed_baseline = set(self.bridge_last_completed)
                    self.location_catalogue_compatible = False
                    self.travel_state = None
                    self.travel_runtime_ready = False
                self.room_seed_name = incoming_seed
        elif cmd == "Connected":
            self.deathlink_state.reset()
            self.travel_snapshot_pending = False
            self.goal_sent_token = None
            # CommonClient has already assigned self.team/self.slot before
            # dispatching this package to this game-specific handler.
            _sync_connection_status_ui(2)
            self.slot_data = args.get("slot_data", {}) or {}
            start_row = self.slot_data.get("starting_area_row")
            self.random_start_mall_artifact_pending = bool(
                self.slot_data.get("random_starting_area", False)
                and isinstance(start_row, int) and not isinstance(start_row, bool)
                and start_row != 0
            )
            self.random_start_mall_artifact_cleared = False
            self.location_catalogue_compatible = _slot_catalogue_matches(self.slot_data)
            if not self.location_catalogue_compatible:
                logger.error(
                    "This seed uses a different SH3 logic/catalogue version. Generate a new multiworld "
                    "with this APWorld. Checks, AP delivery and "
                    "vanilla pickup suppression are paused for this slot."
                )
            protocol = self.slot_data.get("sh3ap_pipe_protocol")
            slot_world_version = self.slot_data.get("sh3ap_world_version")
            if protocol not in (None, PROTOCOL_VERSION):
                logger.warning("This slot expects a different SH3AP pipe protocol: %s", protocol)
            if slot_world_version not in (WORLD_VERSION, "1.0.1"):
                logger.warning("This slot was generated by a different SH3AP world version: %s", slot_world_version)
            logger.info(
                "Connected to Silent Hill 3 slot. Client build %s; pipe protocol %d.",
                CLIENT_VERSION, PROTOCOL_VERSION,
            )
            if self.slot_data.get("random_starting_area", False):
                logger.info(
                    "Random Starting Area selected by this seed: %s (row %s).",
                    self.slot_data.get("starting_area_name", "unknown"),
                    self.slot_data.get("starting_area_row", "unknown"),
                )
            self.watcher_event.set()
        elif cmd == "ReceivedItems":
            # Reconcile on the next bridge tick after CommonClient processes
            # this authoritative prefix. A fresh index-zero stream replaces old receipts;
            # later packets append normally, including chunked full syncs.
            if args.get("index") == 0:
                self.travel_snapshot_pending = True
            self.watcher_event.set()
        elif cmd == "PrintJSON" and args.get("type") == "ItemSend":
            # Preserve the exact Archipelago ItemSend message parts instead of
            # rebuilding custom RECEIVED:/SENT: text.  This covers both items
            # coming in and checks sending items out.
            network_item = args.get("item")
            receiving = int(args.get("receiving", 0) or 0)
            _queue_item_popup(self, network_item, receiving, applied=False)
            finding_player = int(_network_field(network_item, "player", 0) or 0)
            if self.slot is not None and (
                self.slot_concerns_self(receiving) or self.slot_concerns_self(finding_player)
            ):
                item_id = int(_network_field(network_item, "item", 0) or 0)
                location_id = int(_network_field(network_item, "location", 0) or 0)
                flags = int(_network_field(network_item, "flags", 0) or 0)
                segments = _resolve_printjson_segments(self, args.get("data", ()))
                if segments:
                    token = _session_token(self)
                    self.record_activity({
                        "event_id": f"apmsg:{token}:{finding_player}:{location_id}:{receiving}:{item_id}",
                        "kind": "printjson",
                        "item_id": item_id,
                        "location_id": location_id,
                        "from_slot": finding_player,
                        "to_slot": receiving,
                        "classification": _classification_name(flags),
                        "flags": flags,
                        "text": "".join(str(part.get("text", "")) for part in segments),
                        "segments": segments,
                    })


    def make_gui(self):
        from kvui import GameManager

        class SilentHill3Manager(GameManager):
            base_title = f"Archipelago {CLIENT_NAME} - {CLIENT_BRAND} {CLIENT_VERSION}"
            logging_pairs = [("Client", "Archipelago")]

            def __init__(self, ctx):
                super().__init__(ctx)
                self.icon = get_sh3_icon_path()

        return SilentHill3Manager


async def _sync_locations(ctx: SilentHill3Context, status: dict[str, str]) -> None:
    """Send current-process pickup events immediately after AP authentication.

    LiveBridge truncates its event file every SH3 process and accumulates CHECK
    records inside that process. A per-New-Game epoch baseline below prevents a
    second run in the same process from inheriting the first run's checks.

    Loaded persistent flags/inventory are never scanned as location completion.
    """
    authenticated = (ctx.server is not None and ctx.slot is not None
                     and getattr(ctx, "location_catalogue_compatible", True))
    if authenticated:
        await asyncio.to_thread(_acquire_start_arm_lock, ctx)
    else:
        await asyncio.to_thread(_release_start_arm_lock, ctx)

    identity = await asyncio.to_thread(ctx.bridge.event_process_identity)
    if identity is None:
        warning = "Location sync paused: cannot identify the connected SH3 process."
        if ctx.location_source_warning != warning:
            bridge_logger.warning(warning)
            ctx.location_source_warning = warning
        return
    if identity != ctx.location_process_identity:
        ctx.location_process_identity = identity
        ctx.live_check_trace_offset = None
        _observe_new_game_trace(ctx, "=== SH3AP CURRENT PROCESS SESSION START ===")
        ctx.last_location_diag = None

    bridge_ok, bridge_completed, bridge_start_seen = await asyncio.to_thread(
        _read_live_bridge_events, identity[1]
    )
    prior_bridge_completed = set(ctx.bridge_last_completed)
    trace_offset, lines = await asyncio.to_thread(
        _read_new_runtime_trace, ctx.live_check_trace_offset, identity[1]
    )
    ctx.live_check_trace_offset = trace_offset
    for line in lines:
        _observe_new_game_trace(ctx, line)
    if bridge_ok:
        ctx.bridge_last_completed = set(bridge_completed)
        ctx.location_source_warning = None
    elif authenticated:
        warning = ("Physical pickup sync paused: no fresh LiveBridge events for this SH3 process. "
                   "Old catalogue traces are ignored. Check SH3AP_LiveBridge.asi is loaded.")
        if ctx.location_source_warning != warning:
            bridge_logger.warning(warning)
            ctx.location_source_warning = warning

    if not authenticated or status.get("WORLD") != "1":
        return

    # Evaluate the final classification after all lines. A later save-load line
    # must cancel an earlier New Game signal in the same read.
    fresh_new_game = ctx.runtime_entry_classification == "new_game"

    # Poll the actual initialized starter block on every sync. The raw-13 ALT
    # grant used by the previous build is a later pickup, so waiting for that
    # event leaves the starting inventory intact until the player collects it.
    # Consume all trace lines first so a save load cancels the candidate.
    if ctx.new_game_candidate and not ctx.new_game_cleanup_done:
        if await asyncio.to_thread(_new_game_inventory_initialized):
            ctx.new_game_candidate = False
            ctx.new_game_candidate_tick = None
            ctx.new_game_candidate_ids.clear()
            ctx.runtime_entry_classification = "new_game"
            fresh_new_game = True

    start_completed: set[int] = set()

    if (fresh_new_game and not ctx.new_game_cleanup_done
            and not ctx.pending_new_game_start_checks):
        # LiveBridge keeps all CHECK lines for the life of sh3.exe. Snapshot only
        # the previous poll as this New Game's baseline. Any pickup newly added in
        # this poll remains eligible, while checks from an earlier run are excluded.
        ctx.bridge_completed_baseline = prior_bridge_completed
        # The opening Mall transition can be recognized a few frames before SH3's
        # live inventory block is fully writable. Arm the cleanup and retry on each
        # normal AP sync tick until it verifies, rather than waiting for an area
        # transition/teleport to cause another useful state update.
        ctx.pending_new_game_start_checks = True

    if ctx.pending_new_game_start_checks and not ctx.new_game_cleanup_done:
        ok, present_before, present_after = await asyncio.to_thread(
            _clear_unlock_all_new_game_inventory
        )
        if ok:
            ctx.new_game_cleanup_done = True
            ctx.fresh_receive_session_pending = True
            ctx.session_bound_token = 0
            ctx.last_durability_notice = None
            ctx.last_receive_error = None
            ctx.pending_new_game_start_checks = False
            start_completed.update(START_LOCATION_IDS)
            bridge_logger.info(
                "Fresh AP New Game confirmed; starter/Unlock-All inventory was "
                "cleared and the 3 starting locations were completed. Cleared IDs: %s",
                ",".join(str(x) for x in present_before) or "none",
            )

            # Bind the fresh native AP session and publish Random Starting Area before
            # awaiting server-side location submission. This keeps the physical start
            # on the earliest possible local path after cleanup/classification.
            status = await _bind_receive_session(ctx, status)
            from .features_runtime import sync_random_start
            await asyncio.to_thread(sync_random_start, ctx, sys.modules[__name__])
        else:
            bridge_logger.debug(
                "Fresh AP New Game cleanup is armed but the live inventory block is "
                "not ready yet; retrying on the next AP sync tick. Remaining IDs: %s",
                ",".join(str(x) for x in present_after) or "unknown",
            )

    if (bridge_ok and bridge_start_seen and not ctx.new_game_cleanup_done
            and ctx.runtime_entry_classification == "new_game"):
        # A START line remains in the process event file after later save loads.
        # Require fresh classification; a stale START cannot authorize cleanup at title or after load/Continue.
        ctx.pending_new_game_start_checks = True

    live_bridge_completed = (
        bridge_completed - ctx.bridge_completed_baseline if bridge_ok else set()
    )
    completed = set(live_bridge_completed)
    completed.update(start_completed)

    if not completed:
        return

    diagnostic = (
        tuple(sorted(completed)),
        tuple(sorted(ctx.missing_locations)),
        tuple(sorted(ctx.checked_locations)),
        bridge_ok,
    )
    if diagnostic != ctx.last_location_diag:
        bridge_logger.debug(
            "Immediate native location sync: completed=%d, server missing=%d, "
            "server checked=%d, live_bridge=%s.",
            len(completed), len(ctx.missing_locations), len(ctx.checked_locations),
            "ok" if bridge_ok else "unavailable",
        )
        ctx.last_location_diag = diagnostic

    newly_sent = await ctx.check_locations(completed)
    if newly_sent:
        names = [ctx.location_names.lookup_in_game(loc, GAME_NAME) for loc in sorted(newly_sent)]
        bridge_logger.debug("Sent SH3 live location checks immediately: %s", ", ".join(names))



async def _bind_receive_session(ctx: SilentHill3Context, status: dict[str, str]) -> dict[str, str]:
    """Bind AP receive durability state. Failure here must not suppress location checks."""
    seed_name = ctx.room_seed_name or ""
    if not seed_name:
        raise RuntimeError("Archipelago RoomInfo seed_name is not available yet; receive delivery is waiting for a stable server identity")
    slot_name = ctx.auth or ""
    slot_number = ctx.slot if ctx.slot is not None else -1
    seed_identity = f"{seed_name}|{slot_name}|{slot_number}".encode("utf-8")
    session_token = zlib.crc32(seed_identity) & 0xFFFFFFFF
    if session_token == 0:
        session_token = 1

    if ctx.delivery_identity_token and ctx.delivery_identity_token != session_token:
        raise RuntimeError(
            f"AP delivery session identity changed unexpectedly ({ctx.delivery_identity_token} -> {session_token}); delivery paused to prevent duplicate items"
        )
    if not ctx.delivery_identity_token:
        ctx.delivery_identity_token = session_token

    if not ctx.fresh_receive_session_pending and ctx.session_bound_token == session_token and int(status.get("AP_SESSION_TOKEN", "0")) == session_token:
        return status

    fresh = " FRESH=1" if ctx.fresh_receive_session_pending and ctx.receive_extension_available else ""
    reply = await asyncio.to_thread(ctx.bridge.command, f"APSESSION{fresh} TOKEN={session_token}")
    # SAVE_NOT_CLASSIFIED is a normal startup state: the native receiver cannot bind
    # a journal until SH3 has classified this entry as New Game or a save load.
    # 0.0.193 incorrectly raised here, aborting the entire bridge loop before location
    # classification, starter cleanup, Random Starting Area, or item delivery could run.
    if reply.startswith("APSESSION_WAITING REASON=SAVE_NOT_CLASSIFIED"):
        return status
    if not reply.startswith("APSESSION_OK"):
        raise RuntimeError(f"SH3AP APSESSION failed: {reply}")
    ctx.session_bound_token = session_token
    ctx.fresh_receive_session_pending = False
    bridge_logger.info("Bound SH3AP delivery journal to AP session token %d (%s).", session_token, reply)

    status_line = await asyncio.to_thread(ctx.bridge.command, "STATUS")
    rebound_status = _parse_status(status_line)
    if not rebound_status:
        raise RuntimeError(f"Bad SH3AP STATUS after APSESSION: {status_line}")
    ctx.last_status = rebound_status
    return rebound_status


def _record_applied_activity(ctx: SilentHill3Context, item, index: int) -> None:
    """Publish actual grants, including replayed rewards without a new PrintJSON.

    Reuse the server event identity so normal live messages and their grants
    produce one entry. A replay moves that entry to the newest end of the feed.
    """
    if ctx.activity_game_closed:
        return
    token = _session_token(ctx)
    finding = int(_network_field(item, "player", 0) or 0)
    location = int(_network_field(item, "location", 0) or 0)
    item_id = int(_network_field(item, "item", 0) or 0)
    flags = int(_network_field(item, "flags", 0) or 0)
    event_id = f"apmsg:{token}:{finding}:{location}:{ctx.slot}:{item_id}"
    for pos, event in enumerate(ctx.activity_history):
        if event.get("event_id") == event_id:
            ctx.activity_history.append(ctx.activity_history.pop(pos))
            return
    player = {"type": "player_id", "text": str(finding)}
    reward = {"type": "item_id", "text": str(item_id), "player": ctx.slot, "flags": flags}
    if finding == ctx.slot and location > 0:
        parts = [player, {"text": " found their "}, reward]
    elif finding > 0 and location > 0:
        parts = [player, {"text": " sent "}, reward, {"text": " to "},
                 {"type": "player_id", "text": str(ctx.slot)}]
    else:
        parts = [{"text": "Received "}, reward, {"text": " from Server"}]
    if location > 0:
        parts.extend([{"text": " ("}, {"type": "location_id", "text": str(location),
                      "player": finding}, {"text": ")"}])
    segments = _resolve_printjson_segments(ctx, parts)
    ctx.record_activity({
        "event_id": event_id, "kind": "printjson", "item_id": item_id,
        "location_id": location, "from_slot": finding, "to_slot": ctx.slot,
        "classification": _classification_name(flags), "flags": flags,
        "text": "".join(part["text"] for part in segments), "segments": segments,
        "applied_index": index,
    })


async def _sync_received_items(ctx: SilentHill3Context, status: dict[str, str]) -> None:
    if ctx.server is None or ctx.slot is None:
        return
    if not getattr(ctx, "location_catalogue_compatible", True):
        return
    if status.get("WORLD") != "1" and not (ctx.fresh_receive_session_pending and ctx.receive_extension_available):
        return

    # Never let already-received AP items race ahead of fresh-New-Game cleanup.
    # While a gameplay entry is still being classified, hold delivery briefly;
    # normal save loads are released immediately once STATE_REBASE/classification
    # is observed. The timeout avoids deadlocking attachment to an already-running game.
    if ctx.pending_new_game_start_checks and not ctx.new_game_cleanup_done:
        return
    if (
        ctx.runtime_entry_classification is None
        and ctx.receive_hold_deadline
        and time.monotonic() < ctx.receive_hold_deadline
    ):
        return

    try:
        status = await _bind_receive_session(ctx, status)

        # Random Starting Area is identity-gated by the native receiver. Publish the
        # selected row immediately after APSESSION FRESH=1 succeeds; publishing it at
        # title before classification can never satisfy the native token/fresh gates.
        from .features_runtime import sync_random_start
        await asyncio.to_thread(sync_random_start, ctx, sys.modules[__name__])

        if status.get("AP_SERVER_RECEIVES_ENABLED") != "1" or status.get("READY") != "1":
            return

        applied_count = int(status.get("AP_APPLIED_COUNT", "0"))
        durable_count = int(status.get("AP_DURABLE_COUNT", "0"))
        if applied_count > len(ctx.items_received):
            bridge_logger.error(
                "SH3AP has %d applied AP items but server currently exposes only %d. Delivery paused.",
                applied_count, len(ctx.items_received),
            )
            return

        while applied_count < len(ctx.items_received):
            item = ctx.items_received[applied_count]
            if item.item in TRAP_ITEM_IDS:
                await asyncio.to_thread(_enqueue_trap, ctx, applied_count, item.item)
            is_travel = item.item in FAST_TRAVEL_ITEM_IDS
            if is_travel:
                if (not ctx.travel_runtime_ready or ctx.travel_state is None
                        or ctx.travel_state.receipts.get(applied_count) != item.item):
                    return
                raw = VIRTUAL_TRAVEL_RAW_ID
            else:
                raw = ITEM_ID_TO_RAW.get(item.item)
            if item.item == 0x53483400:
                # Never acknowledge this reward if the native beam safeguards
                # failed their exact-byte validation or have not run yet.
                from .beam_runtime import ready as beam_ready
                if not await asyncio.to_thread(beam_ready, sys.modules[__name__]):
                    problem = (applied_count, "beam_runtime")
                    if ctx.last_receive_error != problem:
                        bridge_logger.error("Heather Beam delivery paused: native unlock/UFO safeguards are not ready. The reward remains queued.")
                        ctx.last_receive_error = problem
                    return
            from .data import BUNDLE_ITEM_IDS
            if item.item in BUNDLE_ITEM_IDS:
                from .features_runtime import bundle_ready
                if not await asyncio.to_thread(bundle_ready, sys.modules[__name__]):
                    problem = (applied_count, "bundle_runtime")
                    if ctx.last_receive_error != problem:
                        bridge_logger.error("Bundle delivery paused: update the bundled runtime and restart the game. The reward remains queued.")
                        ctx.last_receive_error = problem
                    return
            name = ctx.item_names.lookup_in_slot(item.item, ctx.slot)
            sender_slot = int(getattr(item, "player", 0) or 0)
            location_id = int(getattr(item, "location", 0) or 0)
            flags = int(getattr(item, "flags", 0) or 0)
            try:
                source_location = ctx.location_names.lookup_in_slot(location_id, sender_slot)
            except Exception:
                source_location = f"Location {location_id}"
            if raw is None:
                bridge_logger.error(
                    "AP item index %d (%s / id %d) has no SH3 raw-item mapping. Delivery paused.",
                    applied_count, name, item.item,
                )
                break
            if ctx.receive_extension_available and raw not in SUPPORTED_RECEIVE_RAW_IDS:
                problem = (applied_count, raw)
                if ctx.last_receive_error != problem:
                    bridge_logger.error("Delivery paused at AP item %d: %s (raw %d) is not supported by the installed receiver. The item remains queued; later items are not skipped.", applied_count, name, raw)
                    ctx.last_receive_error = problem
                return
            reply = await asyncio.to_thread(
                ctx.bridge.command, f"APRECEIVE INDEX={applied_count} RAW_ITEM_ID={raw}"
            )
            if reply.startswith("APRECEIVE_APPLIED"):
                if not is_travel:
                    _record_applied_activity(ctx, item, applied_count)
                    _queue_item_popup(ctx, item, ctx.slot, applied=True)
                bridge_logger.debug(
                    "Applied AP item index %d to SH3: %s (raw %d). It remains replayable until SH3 saves.",
                    applied_count, name, raw,
                )
                applied_count += 1
                continue
            if reply.startswith("APRECEIVE_DURABLE_DUPLICATE") or reply.startswith("APRECEIVE_LIVE_DUPLICATE"):
                applied_count += 1
                continue
            if reply.startswith("APRECEIVE_WAITING"):
                break
            raise RuntimeError(f"SH3AP APRECEIVE failed: {reply}")

        status_line = await asyncio.to_thread(ctx.bridge.command, "STATUS")
        refreshed = _parse_status(status_line)
        if not refreshed:
            return
        ctx.last_status = refreshed
        applied_count = int(refreshed.get("AP_APPLIED_COUNT", "0"))
        durable_count = int(refreshed.get("AP_DURABLE_COUNT", "0"))
        notice = (applied_count, durable_count)
        if applied_count > durable_count and notice != ctx.last_durability_notice:
            bridge_logger.debug(
                "%d AP item(s) are live in SH3 but only %d are save-durable. Save SH3 to make them durable; quitting first will replay them next launch.",
                applied_count, durable_count,
            )
            ctx.last_durability_notice = notice
        elif applied_count == durable_count and notice != ctx.last_durability_notice:
            if applied_count:
                bridge_logger.debug("All %d applied AP items are now SH3-save-durable.", durable_count)
            ctx.last_durability_notice = notice
        ctx.last_receive_error = None

    except Exception as exc:
        # Receive-side errors are deliberately isolated from outgoing location reporting.
        msg = f"{type(exc).__name__}: {exc}"
        if msg != ctx.last_receive_error:
            bridge_logger.error("Receive synchronization failed; location synchronization remains active: %s", msg)
            ctx.last_receive_error = msg


async def _flush_activity_events(ctx: SilentHill3Context, status: dict[str, str]) -> None:
    """Forward queued activity only when the native plugin explicitly advertises support.

    Existing SH3AP.asi builds do not advertise ACTIVITY_PROTOCOL, so this is fail-closed
    and cannot disturb the current pipe protocol. The NDJSON log is still produced.
    """
    ctx.activity_pipe_supported = status.get("ACTIVITY_PROTOCOL") == str(ACTIVITY_PROTOCOL_VERSION)
    if not ctx.activity_pipe_supported or not ctx.activity_pending:
        return

    while ctx.activity_pending:
        event = ctx.activity_pending[0]
        payload = json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        encoded = base64.urlsafe_b64encode(payload).decode("ascii")
        reply = await asyncio.to_thread(ctx.bridge.command, f"ACTIVITY_PUSH B64={encoded}")
        if reply.startswith("ACTIVITY_OK") or reply.startswith("ACTIVITY_DUPLICATE"):
            ctx.activity_pending.pop(0)
            continue
        if reply.startswith("ACTIVITY_FULL") or reply.startswith("ACTIVITY_WAIT"):
            break
        raise RuntimeError(f"SH3AP ACTIVITY_PUSH failed: {reply}")


async def _bridge_loop(ctx: SilentHill3Context) -> None:
    while not ctx.exit_event.is_set():
        # Keep the UI synchronized even when:
        # - AP connected before sh3.exe started,
        # - the Settings menu is closed,
        # - the local SH3 named pipe reconnects independently.
        await asyncio.to_thread(
            _sync_connection_status_ui,
            _current_ap_connection_status(ctx),
        )
        # A display error must never prevent core startup/check/receive processing.
        try:
            await asyncio.to_thread(_sync_activity_ui_memory, ctx)
            await asyncio.to_thread(_sync_popup_memory, ctx, ctx.server is not None and ctx.slot is not None)
        except Exception:
            bridge_logger.exception("Activity/popup synchronization failed; continuing core SH3 synchronization.")
        try:
            await _sync_save_travel(ctx)
        except Exception as exc:
            ctx.travel_runtime_ready = False
            ctx.live_runtime_checks = set()
            problem = str(exc)
            if ctx.travel_error != problem:
                bridge_logger.error("Save/travel synchronization paused: %s", problem)
                ctx.travel_error = problem
        try:
            if not ctx.bridge_connected:
                hello = await asyncio.to_thread(ctx.bridge.connect)
                if "HELLO_ACK" not in hello or f"PROTOCOL={PROTOCOL_VERSION}" not in hello:
                    raise OSError(f"Unexpected SH3AP handshake: {hello}")
                ctx.bridge_connected = True
                bridge_logger.info("Connected to SH3AP.asi named pipe (%s).", hello)

            status_line = await asyncio.to_thread(ctx.bridge.command, "STATUS")
            status = _parse_status(status_line)
            if not status:
                raise OSError(f"Bad SH3AP STATUS response: {status_line}")
            ctx.last_status = status

            ctx.receive_extension_available = await asyncio.to_thread(
                _refresh_receive_extension, ctx.server is not None and ctx.slot is not None
                and ctx.location_catalogue_compatible
            )

            # 0.0.61 native plugin intentionally advertises APWorld compatibility 0.0.60.
            if status.get("VERSION") not in ("0.0.60", "0.0.61"):
                bridge_logger.warning("Untested ASI compatibility version: %s", status.get("VERSION"))

            # Keep the seed-selected row available, but do not APSESSION-bind at title.
            # The native receiver intentionally reports SAVE_NOT_CLASSIFIED until the
            # fresh gameplay entry has been observed and starter cleanup has armed FRESH.
            slot_data = getattr(ctx, "slot_data", {})
            start_row = slot_data.get("starting_area_row")
            random_start_requested = (
                ctx.server is not None and ctx.slot is not None
                and getattr(ctx, "location_catalogue_compatible", True)
                and bool(slot_data.get("random_starting_area", False))
                and isinstance(start_row, int) and not isinstance(start_row, bool)
                and 0 <= start_row < 29
            )

            world_active = status.get("WORLD") == "1"
            if world_active and not ctx.last_world_active:
                # Five seconds is intentionally conservative: it gives the native
                # trace time to classify a New Game before any pre-existing AP item
                # stream can be delivered into inventory that is about to be cleaned.
                if ctx.runtime_entry_classification == "new_game":
                    ctx.receive_hold_deadline = 0.0
                else:
                    ctx.runtime_entry_classification = None
                    ctx.receive_hold_deadline = time.monotonic() + 5.0
            elif not world_active:
                ctx.runtime_entry_classification = None
                ctx.receive_hold_deadline = 0.0
            ctx.last_world_active = world_active

            # Critical ordering: classify/live-check/clean first, then receive.
            await _sync_locations(ctx, status)
            if ctx.runtime_entry_classification is not None:
                ctx.receive_hold_deadline = 0.0
            await _sync_received_items(ctx, status)

            # Renew the Random Start mailbox while its short lease is relevant. The
            # first valid publication occurs in _sync_locations immediately after
            # fresh cleanup/APSESSION FRESH=1; this keeps the lease alive afterward.
            if random_start_requested:
                from .features_runtime import sync_random_start
                await asyncio.to_thread(sync_random_start, ctx, sys.modules[__name__])
            await _flush_activity_events(ctx, ctx.last_status or status)

            if len(ctx.items_received) > ctx.last_logged_received_count:
                for index in range(ctx.last_logged_received_count, len(ctx.items_received)):
                    item = ctx.items_received[index]
                    name = ctx.item_names.lookup_in_slot(item.item, ctx.slot) if ctx.slot is not None else str(item.item)
                    bridge_logger.debug("AP item stream index %d received: %s (id %d).", index, name, item.item)
                ctx.last_logged_received_count = len(ctx.items_received)

        except (OSError, ValueError) as exc:
            if ctx.bridge_connected:
                bridge_logger.warning("Lost SH3AP.asi pipe connection: %s", exc)
            ctx.bridge_connected = False
            ctx.bridge.close()
        except Exception:
            # Do not let an unexpected client/API error silently kill the bridge task.
            bridge_logger.exception("Unexpected SH3 bridge-loop error; retrying without terminating the client.")

        try:
            await asyncio.to_thread(_sync_tracker, ctx, sys.modules[__name__])
            ctx.tracker_error = None
        except Exception as exc:
            problem = str(exc)
            if problem != ctx.tracker_error:
                bridge_logger.warning("Tracker display paused: %s", problem)
                ctx.tracker_error = problem
        try:
            await _sync_poptracker_follow(ctx, sys.modules[__name__])
            ctx.poptracker_follow_error = None
        except Exception as exc:
            problem = str(exc)
            if problem != getattr(ctx, 'poptracker_follow_error', None):
                bridge_logger.warning("PopTracker map following paused: %s", problem)
                ctx.poptracker_follow_error = problem
        try:
            await _sync_deathlink(ctx, sys.modules[__name__])
        except Exception:
            ctx.deathlink_state.reset()
            await ctx.update_death_link(False)
            await asyncio.to_thread(_exchange_deathlink, ctx, sys.modules[__name__], True)
            bridge_logger.exception("DeathLink synchronization paused.")
        if ctx.bridge_connected:
            try:
                await asyncio.to_thread(_exchange_traps, ctx, sys.modules[__name__])
                ctx.trap_error = None
            except Exception as exc:
                try:
                    await asyncio.to_thread(_exchange_traps, ctx, sys.modules[__name__], True)
                except Exception:
                    pass  # A failed cleanup cannot terminate inventory/check delivery.
                if str(exc) != ctx.trap_error:
                    bridge_logger.warning("Trap synchronization paused; pending effects retained: %s", exc)
                    ctx.trap_error = str(exc)
        else:
            # A closed SH3AP pipe means the native process is unavailable or is
            # being restarted. Keep queued trap effects but do not touch stale
            # process memory in the same poll that detected the disconnect.
            ctx.trap_error = None
        await asyncio.sleep(POLL_SECONDS)


async def _main(args) -> None:
    ctx = SilentHill3Context(args.connect, args.password)
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="SHAP server loop")
    bridge_task = asyncio.create_task(_bridge_loop(ctx), name="SH3AP named pipe bridge")

    if gui_enabled and not getattr(args, "nogui", False):
        ctx.run_gui()
    ctx.run_cli()

    await ctx.exit_event.wait()
    ctx.server_address = None
    await asyncio.to_thread(_exchange_deathlink, ctx, sys.modules[__name__], True)
    ctx.clear_activity()
    await asyncio.to_thread(_sync_tracker, ctx, sys.modules[__name__], True)
    await asyncio.to_thread(_sync_popup_memory, ctx, False)
    await asyncio.to_thread(_sync_activity_ui_memory, ctx)
    await asyncio.to_thread(_sync_connection_status_ui, 0)
    ctx.bridge.close()
    await ctx.shutdown()
    bridge_task.cancel()
    try:
        await bridge_task
    except asyncio.CancelledError:
        pass


def launch_client(*launch_args: str) -> None:
    Utils.init_logging("SilentHillClient", exception_logger="Client")
    parser = get_base_parser()
    parser.add_argument("--game", choices=("sh3",), default="sh3", help="Game adapter (currently sh3).")
    parser.add_argument("--game-folder", help="Silent Hill 3 installation folder (remembered after setup).")
    parser.add_argument("--name", default=None, help="Archipelago slot name.")
    parser.add_argument("url", nargs="?", help="Archipelago connection URL")
    args = parser.parse_args(launch_args)
    args = handle_url_arg(args, parser=parser)

    global GAME_FOLDER
    from .runtime_setup import (
        choose_game_folder, ensure_ap_pcfix_settings, install_ap_default_settings, install_mode_tools, install_runtime,
        ensure_ap_system_unlock_state, log_xinputplus_trigger_status, prepare_asi_loader_and_xinput_chain, ensure_ual_scripts_only_config, refresh_disabled_runtime, stage_runtime_for_ap_enable, sync_ap_default_title,
        ensure_game_folder_writable, ensure_game_path_compatible, ensure_no_foreign_scripts_asis,
        ensure_no_alternate_proxy_loaders, ensure_no_ual_file_overload_config, ensure_xinput_chain_safe, loader_timing_mode,
        ap_mode_layout_ready, request_ap_mode, runtime_disabled, save_game_folder, show_setup_message, supported_exe_mode, validate_ap_save_system_support
    )
    try:
        if os.name != "nt":
            raise ValueError("The SH3 PC client requires Windows.")
        settings_path = Path(Utils.user_path("SH3AP_setup.json"))
        folder = choose_game_folder(args.game_folder, settings_path)
        # Verify the exact supported 1.0.0.1 binary before changing anything. Both
        # the untouched Vanilla hash and SH3AP-patched hash are accepted here.
        starting_mode = supported_exe_mode(folder)
        # Fail before mode/save changes if Windows permissions/virtualization would
        # make the installation non-atomic. This is especially important for old
        # disc installs copied under Program Files.
        ensure_game_folder_writable(folder)
        ensure_game_path_compatible(folder)
        # Reject UAL-active third-party plugin/file-overload/proxy paths before
        # AP mode or loader configuration is touched. Vanilla can appear healthy
        # while these only become relevant once SH3AP enables its loader/runtime.
        from .rollback_standalone import rollback_standalone
        for rollback_note in rollback_standalone(folder, _scan_sh3_pid_for_checks):
            bridge_logger.info("Legacy standalone cleanup: %s", rollback_note)
        ensure_no_foreign_scripts_asis(folder)
        ensure_no_alternate_proxy_loaders(folder)
        ensure_no_ual_file_overload_config(folder)
        # Install the bundled support files; no separate external dependency gate.
        from .bundled_pcfix import install_bundled_pcfix
        installed_pcfix = install_bundled_pcfix(folder, _scan_sh3_pid_for_checks)
        if installed_pcfix:
            bridge_logger.info("Installed supplied PC Fix files: %s", ", ".join(installed_pcfix))
        # Apply only the four Steam006 values SH3AP still requires for its supported
        # AP rules/save format. UnlockEverything is never changed; SH3AP reproduces
        # that legacy unlock state in its own verified AP data.sys.
        pcfix_changes = ensure_ap_pcfix_settings(folder, _scan_sh3_pid_for_checks)
        if pcfix_changes:
            bridge_logger.info(
                "Applied required SH3AP Steam006 settings (%s); every unrelated PC Fix byte was preserved.",
                ", ".join(pcfix_changes),
            )
        # SH3AP supplies its MIT-licensed Ultimate ASI Loader. If the exact tested
        # XInput Plus proxy currently occupies dinput8.dll, this safely backs it up
        # and chains it as dinput8Hooked.dll. Unknown DLLs fail closed.
        prepare_asi_loader_and_xinput_chain(folder, _scan_sh3_pid_for_checks, bridge_logger)
        if ensure_ual_scripts_only_config(folder):
            bridge_logger.info('Normalized Ultimate ASI Loader to SH3AP scripts-only, non-recursive discovery.')
        timing_mode = loader_timing_mode(folder)
        bridge_logger.info("Ultimate ASI Loader plugin timing: %s.", timing_mode)
        if timing_mode == "existing-deferred":
            bridge_logger.info("Preserved the existing working UAL deferred plugin-loading policy.")
        elif timing_mode == "existing-standard":
            bridge_logger.info("Preserved the existing working UAL standard plugin-loading policy.")
        elif timing_mode == "standard-default":
            bridge_logger.info("No explicit loader timing was configured; using SH3AP's live-proven Standard plugin-loading policy.")
        # Validate the optional controller proxy chain after UAL has taken the
        # root dinput8 slot. Partial, unknown-vendor, or wrong-architecture proxy
        # DLLs fail before AP activation instead of crashing only on another PC.
        ensure_xinput_chain_safe(folder)
        # XInputPlus itself remains external. Report its LT/RT mapping after the
        # automatic DLL chain has been prepared.
        log_xinputplus_trigger_status(folder, bridge_logger)
        install_mode_tools(folder)
        # When upgrading while SH3AP is toggled off, refresh the non-.asi disabled
        # runtime before enabling AP. This prevents an old 1.0.0 runtime from ever
        # being restored into the live loader path during a 1.0.1 upgrade.
        if runtime_disabled(folder):
            disabled_count, disabled_backup = refresh_disabled_runtime(folder, _scan_sh3_pid_for_checks)
            if disabled_count:
                bridge_logger.info("Refreshed %d disabled SH3AP runtime file(s) before AP activation. Previous files are backed up in %s.", disabled_count, disabled_backup)
        # key.ini and disp.ini are shared game/user configuration, not AP-mode state.
        # Preserve the live values and keep both save profiles synchronized.
        defaults_changed = install_ap_default_settings(folder)
        if defaults_changed:
            bridge_logger.info("Synchronized %d shared SH3 display/controller setting file(s).", defaults_changed)
        save_game_folder(folder, settings_path)
        GAME_FOLDER = folder
        if starting_mode != 'AP' or runtime_disabled(folder) or not ap_mode_layout_ready(folder):
            bridge_logger.info(
                "Preparing verified SH3AP mode and live AP save profile for this game folder."
            )
            # A genuine fresh install has no runtime files yet. The transactional
            # mode toggle intentionally refuses to enter AP mode unless every
            # production ASI already exists either active or under a non-loadable
            # disabled name. Stage those verified payloads first; this does not
            # enable plugins, patch the EXE, or touch saves. Existing installs are
            # idempotent here.
            staged_count, staged_backup = stage_runtime_for_ap_enable(folder, _scan_sh3_pid_for_checks)
            if staged_count:
                bridge_logger.info(
                    "Staged %d verified SH3AP runtime file(s) before AP activation. Previous staged files are backed up in %s.",
                    staged_count, staged_backup,
                )
            request_ap_mode(folder)
            if not ap_mode_layout_ready(folder):
                raise ValueError('SH3AP mode activation finished but the live savedata path is not the AP profile.')
            bridge_logger.info("SH3AP mode is active and savedata is bound to savedataAP.")
        # Install the supplied versioned artwork with a verified local archive
        # backup. Cosmetic title failure must never block an otherwise valid AP install.
        try:
            if sync_ap_default_title(folder, _scan_sh3_pid_for_checks):
                bridge_logger.info("Updated the live SH3AP title screen to the versioned title.")
        except Exception as title_exc:
            bridge_logger.warning("Skipped optional SH3AP title-screen upgrade: %s", title_exc)
        # Keep AP system data in Steam006's supported NewSaveSystem format.
        # 0.0.203-0.0.205 imported an old-format 296-byte retail data.sys; that is
        # incompatible with the required NewSaveSystem path. Any such file is
        # backed up and replaced by the verified 116-byte AP template. The actual
        # post-clear/ENG availability is handled by the reversible 0x60D020 patch.
        validate_ap_save_system_support(folder)
        system_created, system_patched, system_source = ensure_ap_system_unlock_state(folder, _scan_sh3_pid_for_checks)
        bridge_logger.info(
            "Verified AP NewSaveSystem data.sys (created_or_replaced=%s patched=%s source=%s).",
            system_created, system_patched, system_source,
        )
        count, backup = install_runtime(folder, _scan_sh3_pid_for_checks)
        if count:
            bridge_logger.info("Installed %d SH3AP runtime files. Previous files are backed up in %s.", count, backup)
        bridge_logger.info("SH3 game folder: %s", GAME_FOLDER)
    except Exception as exc:
        logger.exception("SH3 setup failed: %s", exc)
        try:
            show_setup_message(
                "Silent Hill 3 Archipelago Setup",
                "SH3AP setup could not finish first-run setup.\n\n"
                + str(exc)
                + "\n\nNothing else will be changed until this is fixed. Reopen Silent Hill 3 Client after correcting the item above.",
                error=True,
            )
        except Exception:
            pass
        return

    import colorama
    colorama.just_fix_windows_console()
    try:
        asyncio.run(_main(args))
    finally:
        if _runtime_discovery.cache_info().currsize:
            _runtime_discovery().close()
            _runtime_discovery.cache_clear()
        colorama.deinit()
