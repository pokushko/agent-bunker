# -*- coding: utf-8 -*-
"""
AgentBunker Quickstart: Wrapping an autonomous LLM agent turn in 4 lines.
"""

from agent_bunker import Bunker

# 1. Initialize Bunker harness with 256MB memory cap and atomic WAL journal
bunker = Bunker(
    memory_limit_mb=256.0,
    wal_path="./state/my_agent.wal"
)

# 2. Decorate any agent execution cycle
@bunker.guard(step_type="user_turn")
def run_autonomous_agent(user_prompt: str) -> str:
    print(f"🤖 Processing prompt: {user_prompt}")
    # Simulating LLM query or tool execution
    if "simulate_outage" in user_prompt:
        raise ConnectionResetError("Remote LLM API gateway dropped connection!")
    return f"Response to: {user_prompt}"

if __name__ == "__main__":
    print("--- 1. Normal Turn ---")
    res1 = run_autonomous_agent("How to calculate portfolio Sharpe ratio?")
    print("Result:", res1)

    print("\n--- 2. Upstream Network Outage (Bunker Auto-Recovers) ---")
    res2 = run_autonomous_agent("simulate_outage")
    print("Result:", res2)
    print("\n✅ Agent did not crash! State is preserved in ./state/my_agent.wal")
