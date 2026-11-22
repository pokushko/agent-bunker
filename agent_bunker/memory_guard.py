# -*- coding: utf-8 -*-
"""
Memory Guard & OOM Ceiling Monitor for 24/7 Agent Daemon Processes.
Prevents uncontained memory bloat from long conversation histories and tensor buffers.
"""

import os
import gc
import psutil
from typing import Optional, Callable

class MemoryGuard:
    def __init__(self, limit_mb: float = 256.0, on_breach: Optional[Callable[[float], None]] = None):
        self.limit_mb = limit_mb
        self.on_breach = on_breach
        self.process = psutil.Process(os.getpid())
        self.baseline_rss = self.get_rss_mb()
        self.history = []

    def get_rss_mb(self) -> float:
        """Returns the current process Resident Set Size (RSS) in Megabytes."""
        return self.process.memory_info().rss / (1024 * 1024)

    def check(self) -> dict:
        """
        Inspects memory metrics. If RSS exceeds limit, invokes GC and custom breach handler.
        """
        current_rss = self.get_rss_mb()
        self.history.append(current_rss)
        if len(self.history) > 50:
            self.history.pop(0)

        breached = current_rss > self.limit_mb
        reclaimed_mb = 0.0

        if breached:
            before_gc = current_rss
            gc.collect()
            after_gc = self.get_rss_mb()
            reclaimed_mb = before_gc - after_gc
            current_rss = after_gc

            if current_rss > self.limit_mb and self.on_breach:
                self.on_breach(current_rss)

        return {
            "current_rss_mb": round(current_rss, 2),
            "limit_mb": self.limit_mb,
            "breached": breached,
            "reclaimed_mb": round(reclaimed_mb, 2),
            "delta_from_baseline_mb": round(current_rss - self.baseline_rss, 2)
        }
