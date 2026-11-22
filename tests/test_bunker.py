# -*- coding: utf-8 -*-
import sys
import shutil
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_bunker import Bunker, WALJournal, MemoryGuard, CircuitBreaker

TEST_DIR = Path("./temp_test_bunker")

@pytest.fixture(autouse=True)
def cleanup():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR, ignore_errors=True)

def test_wal_journal():
    wal_file = TEST_DIR / "test.wal"
    wal = WALJournal(str(wal_file))
    
    tx1 = wal.record_step("intent", {"query": "hello"})
    tx2 = wal.record_step("action", {"tool": "search"})
    
    records = wal.recover_state()
    assert len(records) == 2
    assert records[0]["tx_id"] == tx1
    assert records[0]["type"] == "intent"
    assert records[1]["tx_id"] == tx2
    assert records[1]["type"] == "action"

def test_memory_guard():
    guard = MemoryGuard(limit_mb=1024.0)
    status = guard.check()
    assert "current_rss_mb" in status
    assert status["breached"] is False

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.5)
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is False # Breaker is now OPEN

def test_bunker_decorator():
    wal_file = TEST_DIR / "bunker_dec.wal"
    bunker = Bunker(wal_path=str(wal_file), memory_limit_mb=512.0)

    @bunker.guard()
    def sample_agent(msg: str):
        if "crash" in msg:
            raise ConnectionError("Simulated LLM Gateway Outage")
        return f"Echo: {msg}"

    # Normal execution
    res1 = sample_agent("hello world")
    assert res1 == "Echo: hello world"

    # Outage execution -> triggers offline bunker fallback without unhandled exception!
    res2 = sample_agent("simulate crash")
    assert res2["status"] == "bunker_offline"

    # Check WAL recorded both
    records = bunker.wal.recover_state()
    assert len(records) >= 4
