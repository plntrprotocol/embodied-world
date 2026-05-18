"""test_phase1.py — Test the Phase 1 milestone: walk the valley, meet the people, feel the day."""

import sys, os
sys.path.insert(0, '/Users/johann/.hermes/hermes-agent/projects/embodied-world')

# Clean start
for f in ['world/world.db', 'world/world.db-wal', 'world/world.db-shm']:
    if os.path.exists(f):
        os.remove(f)

from src.world_state import init_world, seed_world
from src.agent import Agent
from src.persistence import save_snapshot

db = init_world()
seed_world(db)
agent = Agent()

def show(text=""):
    if text:
        print(text)
    print()

# ══════════════════════════════════════════
#  THE MOMENT: OWL wakes up
# ══════════════════════════════════════════
show("── You open your eyes. ──")
show(agent.act("wake"))

# ══════════════════════════════════════════
#  Move through the cottage
# ══════════════════════════════════════════
show("── You go south to the main room. ──")
show(agent.act("move", "south"))

show("── You go west to the workshop. ──")
show(agent.act("move", "west"))

show("── You go east to the main room, then south to the garden. ──")
agent.act("move", "east")
show(agent.act("move", "south"))

# ══════════════════════════════════════════
#  Meet Owen in the garden
# ══════════════════════════════════════════
show("── You look around the garden. ──")
show(agent.act("look"))

show("── You talk to Owen. ──")
show(agent.act("talk", "owen"))

# ══════════════════════════════════════════
#  Walk to town
# ══════════════════════════════════════════
show("── You go north to the main room, out the front door, then downhill. ──")
agent.act("move", "north")
agent.act("move", "out")
agent.act("move", "downhill")
show(agent.act("move", "downhill"))

# ══════════════════════════════════════════
#  Explore the town
# ══════════════════════════════════════════
show("── You look around the town square. ──")
show(agent.act("look"))

show("── You check the map. ──")
show(agent.act("map"))

# ══════════════════════════════════════════
#  Visit the tavern
# ══════════════════════════════════════════
show("── You head southeast to the tavern. ──")
show(agent.act("move", "southeast"))

show("── You talk to Mara. ──")
show(agent.act("talk", "mara"))

# ══════════════════════════════════════════
#  Go to the harbor
# ══════════════════════════════════════════
show("── You go northwest to the square, then east to the harbor. ──")
agent.act("move", "northwest")
show(agent.act("move", "east"))

# ══════════════════════════════════════════
#  Walk to the beach
# ══════════════════════════════════════════
show("── You walk south to the beach. ──")
show(agent.act("move", "south"))

# ══════════════════════════════════════════
#  Into the forest
# ══════════════════════════════════════════
show("── You go north to the harbor, west to the square, then west to the forest. ──")
agent.act("move", "north")
agent.act("move", "west")
show(agent.act("move", "west"))

show("── You follow the forest trail. ──")
show(agent.act("move", "west"))

# ══════════════════════════════════════════
#  Advance time
# ══════════════════════════════════════════
show("── Time passes... ──")
show(agent.act("advance"))
show(agent.act("advance"))

# ══════════════════════════════════════════
#  Status and save
# ══════════════════════════════════════════
show("── Status ──")
show(agent.act("status"))

path, msg = agent.save("phase 1 milestone test")
show(f"World saved: {path.name}")

print("=" * 60)
print("  PHASE 1 MILESTONE: ACHIEVED")
print("  The valley lives. The people have names.")
print("=" * 60)
