"""Durable AP save visits and travel receipts, independent of SH3 save rollback."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

from .data import (GAME_NAME, SAVE_ID_TO_LOCATION_ID, FAST_TRAVEL_ITEM_IDS,
                   FAST_TRAVEL_ITEM_TO_ROW, ITEM_NAME_TO_ID, ITEM_PROGRESSIVE_FAST_TRAVEL,
                   ACTIVE_FAST_TRAVEL_ROWS, SCRIPTED_BIT_TO_LOCATION_ID, SAVE_ID_TO_MENU_ROW)

TRACKED_LOCATION_IDS = frozenset(SAVE_ID_TO_LOCATION_ID.values()) | frozenset(SCRIPTED_BIT_TO_LOCATION_ID.values())

NATIVE_SIGNATURE = b"SHAP_SAVE_TRAVEL_V1\0"
NATIVE_RVA = 0x23000
VIRTUAL_SIGNATURE = b"SHAP_VIRTUAL_RECEIVE_V1\0"
VIRTUAL_RVA = 0x32000


class TravelState:
    def __init__(self, folder: Path, seed: str, team: int, slot: int, name: str):
        if not seed or team < 0 or slot < 0 or not name:
            raise ValueError("Travel tracking requires a complete authenticated AP identity")
        self.identity = [GAME_NAME, seed, team, slot, name]
        digest = hashlib.sha256(json.dumps(self.identity, ensure_ascii=True,
                                        separators=(",", ":")).encode()).digest()
        self.cookie = digest[:16]
        self.path = folder / (digest.hex() + ".json")
        self.visited: set[int] = set()
        self.receipts: dict[int, int] = {}
        self.announced: set[int] = set()
        if self.path.exists():
            record = json.loads(self.path.read_text(encoding="utf-8"))
            if record.get("version") != 1 or record.get("identity") != self.identity:
                raise ValueError("Save/travel journal identity or version mismatch")
            self.visited = set(record["visited"])
            self.receipts = {int(i): item for i, item in record["receipts"].items()}
            self.announced = set(record["announced"])
            if (not self.visited <= set(TRACKED_LOCATION_IDS)
                    or any(i < 0 or item not in FAST_TRAVEL_ITEM_IDS for i, item in self.receipts.items())
                    or not self.announced <= self.receipts.keys()):
                raise ValueError("Invalid save/travel journal contents; existing file retained")

    @property
    def mask(self) -> int:
        rows = {FAST_TRAVEL_ITEM_TO_ROW[item] for item in self.receipts.values()
                if item in FAST_TRAVEL_ITEM_TO_ROW}
        progressive = sum(item == ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_FAST_TRAVEL]
                          for item in self.receipts.values())
        rows.update(ACTIVE_FAST_TRAVEL_ROWS[:progressive])
        rows.update(SAVE_ID_TO_MENU_ROW[native] for native, location in SAVE_ID_TO_LOCATION_ID.items()
                    if location in self.visited)
        return sum(1 << row for row in rows)

    def _commit(self, visited, receipts, announced):
        record = dict(version=1, identity=self.identity, visited=sorted(visited),
                      receipts={str(i): item for i, item in sorted(receipts.items())},
                      announced=sorted(announced))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=self.path.stem+".", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
                json.dump(record, output, sort_keys=True, separators=(",", ":"))
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        # Publish memory only after successful replacement. Retry after I/O failure.
        self.visited, self.receipts, self.announced = set(visited), dict(receipts), set(announced)

    def reconcile(self, opened, checked, items):
        visits = self.visited | ((set(opened) | set(checked)) & set(TRACKED_LOCATION_IDS))
        receipts = dict(self.receipts)
        for index, item in enumerate(items):
            item_id = int(item.item)
            if index in receipts and receipts[index] != item_id:
                raise ValueError("AP item stream changed at an already recorded travel receipt")
            if item_id in FAST_TRAVEL_ITEM_IDS:
                receipts[index] = item_id
        if visits != self.visited or receipts != self.receipts:
            self._commit(visits, receipts, self.announced)

    def replace_server_receipts(self, items):
        """Replace receipt indices only after an authoritative index-zero sync.

        AP can reorder delivery when the same seed is hosted with reset server
        progress. Visits remain durable; travel rewards follow the server's
        current ordered stream. An incomplete initial chunk never retains an
        unverified tail from an older stream.
        """
        receipts = {i: int(item.item) for i, item in enumerate(items)
                    if int(item.item) in FAST_TRAVEL_ITEM_IDS}
        if receipts == self.receipts:
            return
        announced = {i for i in self.announced
                     if i in receipts and receipts[i] == self.receipts.get(i)}
        displaced = any(receipts.get(i) != item for i, item in self.receipts.items())
        if displaced and self.path.exists():
            # Preserve exact prior bytes before replacing any obsolete receipts.
            # Exclusive creation keeps every earlier recovery backup intact.
            backup = self.path.with_name(self.path.name + ".receipts.bak")
            number = 0
            while True:
                try:
                    with backup.open("xb") as output:
                        output.write(self.path.read_bytes())
                        output.flush()
                        os.fsync(output.fileno())
                    break
                except FileExistsError:
                    number += 1
                    backup = self.path.with_name(self.path.name + f".receipts.{number}.bak")
        self._commit(self.visited, receipts, announced)

    def forget_visit(self, location_id: int):
        """Remove one synthetic visit while preserving receipts and announcements.

        Used only for the stock Mall bootstrap artifact on a non-Mall Random Start.
        A received destination item still unlocks through receipts, and a later real
        save opening can add the visit again.
        """
        if location_id not in self.visited:
            return
        visits = set(self.visited)
        visits.discard(location_id)
        self._commit(visits, self.receipts, self.announced)

    def mark_announced(self, indices):
        announced = self.announced | set(indices)
        if not announced <= self.receipts.keys():
            raise ValueError("Cannot announce an uncommitted travel receipt")
        if announced != self.announced:
            self._commit(self.visited, self.receipts, announced)
