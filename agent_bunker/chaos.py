# -*- coding: utf-8 -*-
"""
Chaos Engine for Autonomous AI Agents.
Injects controlled faults (network partitions, API drops, random delays) to certify 24/7 resilience.
"""

import time
import random
from typing import Callable, Any, Dict, List, Optional

class ChaosEngine:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.fault_log: List[Dict[str, Any]] = []

    def simulate_latency(self, min_sec: float = 0.1, max_sec: float = 0.5):
        """Simulates intermittent high network jitter."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        self.fault_log.append({"fault": "latency", "duration_sec": delay, "ts": time.time()})

    def inject_network_blackout(self, failure_probability: float = 0.3):
        """Randomly raises network partition exception based on probability."""
        if random.random() < failure_probability:
            self.fault_log.append({"fault": "blackout", "ts": time.time()})
            raise ConnectionError("ChaosEngine: Simulating simulated network partition (socket drop).")

    def run_stress_suite(self, agent_fn: Callable[[str], Any], test_inputs: List[str], chaos_prob: float = 0.25) -> dict:
        """
        Executes a continuous stress loop over the agent with injected chaos faults.
        Verifies that zero unhandled fatal exceptions bubble up.
        """
        results = {"total": len(test_inputs), "passed": 0, "failed": 0, "faults_injected": 0}
        for inp in test_inputs:
            try:
                if random.random() < chaos_prob:
                    results["faults_injected"] += 1
                    self.inject_network_blackout(failure_probability=1.0)
                agent_fn(inp)
                results["passed"] += 1
            except Exception:
                # If agent handles or if test captures
                results["failed"] += 1
        return results
