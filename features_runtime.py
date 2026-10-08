"""Versioned mailbox for atomic bundle rewards and fresh-game start requests."""
import struct
CORE_RVA = 0x35000
UI_RVA = 0x399000
CORE_SIGNATURE = b'SH3AP_BUNDLE147\0'
UI_SIGNATURE = b'SH3AP_FEATURE147\0'


def bundle_ready(api):
    pid, modules = api._runtime_discovery().get_modules()
    base = modules.get('sh3ap.asi', 0)
    if not pid or not base:return False
    k = api._kernel32();h = k.OpenProcess(0x410, False, pid)
    if not h:return False
    try:
        return api._read_process_memory(h, base+CORE_RVA, len(CORE_SIGNATURE)) == CORE_SIGNATURE
    finally:k.CloseHandle(h)


def sync_random_start(ctx, api):
    data = getattr(ctx, 'slot_data', {})
    row = data.get('starting_area_row')
    enabled = (ctx.server is not None and ctx.slot is not None
               and getattr(ctx, 'location_catalogue_compatible', True)
               and data.get('random_starting_area', False)
               and isinstance(row, int) and not isinstance(row, bool) and 0 <= row < 29
               and bool(ctx.delivery_identity_token)
               and ctx.session_bound_token == ctx.delivery_identity_token)
    pid, modules = api._runtime_discovery().get_modules()
    base = modules.get('sh3ap_ui.asi', 0)
    if not pid or not base:return
    k = api._kernel32();h = k.OpenProcess(0x438, False, pid)
    if not h:return
    try:
        if api._read_process_memory(h, base+UI_RVA, len(UI_SIGNATURE)) != UI_SIGNATURE:
            if enabled:raise RuntimeError('Random Starting Area requires the bundled runtime; restart the game after updating.')
            return
        # Revoke first, configure, then publish a short lease. Native fresh-game
        # serials survive client reconnect and never change on Continue/load.
        if not api._write_process_memory(h, base+UI_RVA+0x24, bytes(4)):return
        if not enabled:return
        if not api._write_process_memory(h, base+UI_RVA+0x20, struct.pack('<I', row)):return
        if not api._write_process_memory(h, base+UI_RVA+0x38, struct.pack('<I', ctx.delivery_identity_token)):return
        api._write_process_memory(h, base+UI_RVA+0x24, struct.pack('<I', int(k.GetTickCount())&0xffffffff or 1))
    finally:k.CloseHandle(h)
