# -*- coding: utf-8 -*-
"""
Circuit Breaker & Offline Bunker Fallback Cascade.
Shields agents against upstream LLM gateway outages, rate limits (429), and service downtimes (503).
"""

import time
from typing import Callable, Any, Optional

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = 0.0

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False

class FallbackCascade:
    def __init__(self, primary_fn: Callable[..., Any], fallback_fn: Callable[..., Any], breaker: Optional[CircuitBreaker] = None):
        self.primary_fn = primary_fn
        self.fallback_fn = fallback_fn
        self.breaker = breaker or CircuitBreaker()

    def execute(self, *args, **kwargs) -> Any:
        if not self.breaker.can_execute():
            # Upstream circuit is open -> route directly to bunker fallback
            return self.fallback_fn(*args, **kwargs)

        try:
            res = self.primary_fn(*args, **kwargs)
            self.breaker.record_success()
            return res
        except Exception as e:
            self.breaker.record_failure()
            # Seamless fallback to safe local heuristic or bunker response
            return self.fallback_fn(*args, **kwargs)
