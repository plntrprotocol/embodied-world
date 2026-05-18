"""test_phase0.py — Test the Phase 0 milestone: wake up, look around, feel the morning."""

import sys
sys.path.insert(0, '/Users/johann/.hermes/hermes-agent/projects/embodied-world')

from src.world_state import init_world, seed_world, get_world, DB_PATH
from src.agent import Agent
from src.persistence import save_snapshot, commit_snapshot

# Initialize fresh world
print("=" * 60)
print("  PHASE 0 MILESTONE TEST")
print("  Wake up in the cottage, look around, feel the morning.")
print("=" * 60)
print()

db = init_world()
seed_world(db)

agent = Agent()

# ── THE MOMENT: OWL wakes up ──
print("── You open your eyes. ──")
print()
result = agent.act("wake")
print(result)
print()

# ── Look around the bedroom ──
print("── You look around. ──")
print()
result = agent.act("look")
print(result)
print()

# ── Examine something ──
print("── You examine the window. ──")
print()
result = agent.act("examine", "window")
print(result)
print()

# ── Move to the main room ──
print("── You go south to the main room. ──")
print()
result = agent.act("move", "south")
print(result)
print()

# ── Move to the workshop ──
print("── You go west to the workshop. ──")
print()
result = agent.act("move", "west")
print(result)
print()

# ── Advance time ──
print("── Time passes... ──")
print()
result = agent.act("advance")
print(result)
print()

# ── Check status ──
print("── Status ──")
print()
result = agent.act("status")
print(result)
print()

# ── Save ──
path, msg = agent.save("phase 0 milestone test")
print(f"World saved: {path.name}")
if msg:
    print(f"Git commit: {msg}")

print()
print("=" * 60)
print("  PHASE 0 MILESTONE: ACHIEVED")
print("=" * 60)
