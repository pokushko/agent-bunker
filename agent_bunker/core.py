# -*- coding: utf-8 -*-
"""
Core Bunker Orchestrator.
Wraps agent turn cycles in a resilient harness: WAL + Memory Guard + Circuit Breaker + Offline Fallback.
"""

import functools
from typing import Callable, Any, Optional
from .wal import WALJournal
from .memory_guard import MemoryGuard
from .offline_fallback import CircuitBreaker, FallbackCascade

class Bunker:
    def __init__(
        self,
        memory_limit_mb: float = 256.0,
        wal_path: str = "./state/agent_bunker.wal",
        offline_fallback: Optional[Callable[..., Any]] = None,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 30.0
    ):
        self.wal = WALJournal(journal_path=wal_path)
        self.memory = MemoryGuard(limit_mb=memory_limit_mb)
        self.breaker = CircuitBreaker(failure_threshold=failure_threshold, recovery_timeout_sec=recovery_timeout_sec)
        self.offline_fallback = offline_fallback or self._default_fallback

    def _default_fallback(self, *args, **kwargs) -> dict:
        return {
            "status": "bunker_offline",
            "message": "AgentBunker: Primary upstream unavailable. Operating in autonomous offline safe mode.",
            "args": args
        }

    def guard(self, step_type: str = "agent_turn"):
        """
        Decorator wrapping any agent function with full Bunker resilience.
        """
        def decorator(fn: Callable[..., Any]):
            cascade = FallbackCascade(primary_fn=fn, fallback_fn=self.offline_fallback, breaker=self.breaker)

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                # 1. Pre-turn memory check
                mem_status = self.memory.check()

                # 2. Record step intent in WAL
                tx_id = self.wal.record_step(
                    step_type=f"{step_type}:start",
                    payload={"args": [str(a)[:100] for a in args], "rss_mb": mem_status["current_rss_mb"]}
                )

                # 3. Execute with circuit breaker & fallback
                res = cascade.execute(*args, **kwargs)

                # 4. Record step completion in WAL
                self.wal.record_step(
                    step_type=f"{step_type}:finish",
                    payload={"tx_id": tx_id, "success": True}
                )

                return res

            return wrapper
        return decorator
