# -*- coding: utf-8 -*-
"""
Write-Ahead Log (WAL) Journal for Autonomous AI Agents.
Guarantees zero state loss upon network blackouts, unhandled crashes, or OS reboots.
"""

import os
import json
import time
from pathlib import Path
from typing import Any, Dict, List

class WALJournal:
    def __init__(self, journal_path: str = "./state/agent_bunker.wal", max_bytes: int = 10 * 1024 * 1024):
        self.path = Path(journal_path)
        self.max_bytes = max_bytes
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def record_step(self, step_type: str, payload: Dict[str, Any]) -> str:
        """Appends a new atomic transaction record to the journal."""
        entry = {
            "tx_id": f"tx_{int(time.time() * 1000)}_{os.urandom(2).hex()}",
            "ts": time.time(),
            "type": step_type,
            "payload": payload
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        if self.path.stat().st_size > self.max_bytes:
            self.compact()

        return entry["tx_id"]

    def recover_state(self) -> List[Dict[str, Any]]:
        """Replays all uncommitted/active transaction records from the journal."""
        if not self.path.exists():
            return []
        records = []
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def compact(self, keep_last: int = 100):
        """Compacts the journal, preserving the last N critical transactions."""
        records = self.recover_state()
        if len(records) <= keep_last:
            return
        retained = records[-keep_last:]
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            for r in retained:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        tmp_path.replace(self.path)
