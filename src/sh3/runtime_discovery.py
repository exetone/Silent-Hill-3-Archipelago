"""Share process/module discovery across the SH3 client's polling consumers."""
from __future__ import annotations

import threading
import time


class RuntimeDiscovery:
    """Keep addresses only while their original process handle is alive.

    Memory signatures remain the responsibility of each consumer. Missing
    modules retry at the normal client interval; complete inventories refresh
    every five seconds. A failed snapshot never returns old module addresses.
    """

    def __init__(self, scan_pid, scan_modules, open_watch, is_alive, close_watch,
                 expected_modules, clock=time.monotonic):
        self.scan_pid = scan_pid
        self.scan_modules = scan_modules
        self.open_watch = open_watch
        self.is_alive = is_alive
        self.close_watch = close_watch
        self.expected_modules = frozenset(expected_modules)
        self.clock = clock
        self.lock = threading.Lock()
        self.pid = 0
        self.handle = None
        self.modules = {}
        self.next_process_scan = 0.0
        self.next_module_scan = 0.0

    def _clear(self):
        if self.handle:
            self.close_watch(self.handle)
        self.pid = 0
        self.handle = None
        self.modules = {}
        self.next_process_scan = 0.0
        self.next_module_scan = 0.0

    def close(self):
        with self.lock:
            self._clear()

    def _get_pid(self):
        if self.handle:
            if self.is_alive(self.handle):
                return self.pid
            # Invalidate immediately, even if Windows reuses the same PID.
            self._clear()
        now = self.clock()
        if now < self.next_process_scan:
            return 0
        self.next_process_scan = now + 0.5
        pid = self.scan_pid()
        if pid:
            handle = self.open_watch(pid)
            if handle:
                if self.is_alive(handle):
                    self.pid, self.handle = pid, handle
                else:
                    self.close_watch(handle)
        return self.pid

    def get_pid(self):
        with self.lock:
            return self._get_pid()

    def get_modules(self):
        with self.lock:
            pid = self._get_pid()
            if not pid:
                return 0, {}
            now = self.clock()
            if now >= self.next_module_scan:
                # Discard cached addresses before any fallible API call.
                self.modules = {}
                self.next_module_scan = now + 0.5
                modules = self.scan_modules(pid)
                if not self.is_alive(self.handle):
                    self._clear()
                    return 0, {}
                if modules is not None:
                    self.modules = dict(modules)
                    if self.expected_modules <= self.modules.keys():
                        self.next_module_scan = now + 5.0
            return pid, dict(self.modules)
