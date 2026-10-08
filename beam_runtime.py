"""Receipt gate for the verified game-thread Heather Beam controller."""
from . import tracker_model as model

def ready(api):
    pid,modules=api._runtime_discovery().get_modules()
    ui=modules.get('sh3ap_ui.asi',0)
    if not pid or not ui:return False
    k=api._kernel32();h=k.OpenProcess(0x410,False,pid)
    if not h:return False
    try:
        head=api._read_process_memory(h,ui+model.NATIVE_RVA,52)
        return bool(head and head[:16]==model.SIGNATURE and head[16:32]==model.SCHEMA_HASH and head[48:52]==b'\x01\0\0\0')
    finally:k.CloseHandle(h)
