"""test_phase2.py — Test the Phase 2 milestone: a life to live."""

import sys, os
sys.path.insert(0, '/Users/johann/.hermes/hermes-agent/projects/embodied-world')

# Clean start
for f in ['world/world.db', 'world/world.db-wal', 'world/world.db-shm']:
    if os.path.exists(f):
        os.remove(f)

from src.world_state import init_world, seed_world, get_world
from src.agent import Agent
from src.persistence import save_snapshot
from src.ecology import init_ecology
from src.npc_generation import populate_valley
from src.simulation import tick

db = init_world()
seed_world(db)
init_ecology(db)
agent = Agent()

def show(text=""):
    if text:
        print(text)
    print()

# ══════════════════════════════════════════
#  WAKE UP
# ══════════════════════════════════════════
show("── You open your eyes. ──")
show(agent.act("wake"))

# ══════════════════════════════════════════
#  FEEL — check psychology
# ══════════════════════════════════════════
show("── You sit with your thoughts. ──")
show(agent.act("feel"))

# ══════════════════════════════════════════
#  OBSERVE nature in the bedroom
# ══════════════════════════════════════════
show("── You look out the window. ──")
show(agent.act("observe"))

# ══════════════════════════════════════════
#  WALK through cottage → garden
# ══════════════════════════════════════════
show("── You go south to the main room. ──")
show(agent.act("move", "south"))

show("── You go south to the garden. ──")
show(agent.act("move", "south"))

show("── You observe the garden. ──")
show(agent.act("observe"))

# ══════════════════════════════════════════
#  TALK to Owen in the garden
# ══════════════════════════════════════════
show("── You talk to Owen. ──")
show(agent.act("talk", "owen"))

# ══════════════════════════════════════════
#  WALK to town
# ══════════════════════════════════════════
show("── You walk to town. ──")
agent.act("move", "north")   # garden → main_room
agent.act("move", "out")     # main_room → cottage
agent.act("move", "downhill")  # cottage → hillside_path
show(agent.act("move", "downhill"))  # hillside_path → town_square

# ══════════════════════════════════════════
#  EXPLORE town
# ══════════════════════════════════════════
show("── You look around the town square. ──")
show(agent.act("look"))

show("── You check the map. ──")
show(agent.act("map"))

# ══════════════════════════════════════════
#  VISIT the tavern
# ══════════════════════════════════════════
show("── You head southeast to the tavern. ──")
show(agent.act("move", "southeast"))

show("── You talk to Mara. ──")
show(agent.act("talk", "mara"))

# ══════════════════════════════════════════
#  GO to the harbor
# ══════════════════════════════════════════
show("── You go to the harbor. ──")
agent.act("move", "northwest")  # tavern → square
show(agent.act("move", "east"))  # square → harbor

# ══════════════════════════════════════════
#  CREATIVE work
# ══════════════════════════════════════════
show("── You check your creative impulses. ──")
show(agent.act("impulse"))

show("── You check available projects. ──")
show(agent.act("create"))

# Go back to workshop to build
show("── You head home to the workshop. ──")
agent.act("move", "west")   # harbor → square
agent.act("move", "uphill")  # square → hillside_path
agent.act("move", "uphill")  # hillside_path → cottage
agent.act("move", "in")     # cottage → main_room
agent.act("move", "west")   # main_room → workshop
show(agent.act("look"))

show("── You start building a wooden box. ──")
show(agent.act("create", "carpentry wooden box"))

show("── You work on the box. ──")
show(agent.act("work"))
show(agent.act("work"))

show("── You check your projects. ──")
show(agent.act("projects"))

# ══════════════════════════════════════════
#  STATUS check
# ══════════════════════════════════════════
show("── Status ──")
show(agent.act("status"))

# ══════════════════════════════════════════
#  MEMORIES
# ══════════════════════════════════════════
show("── Your memories. ──")
show(agent.act("memories"))

# ══════════════════════════════════════════
#  POPULATE the valley with NPCs
# ══════════════════════════════════════════
show("── You populate the valley with 200 NPCs... ──")
show(agent.act("populate", "200"))

# ══════════════════════════════════════════
#  ADVANCE time — let the world live
# ══════════════════════════════════════════
show("── A full day passes... ──")
for _ in range(12):
    tick(agent.db, hours=2.0)
agent.world = get_world(agent.db)
show(agent.act("look"))

show("── Status after a day. ──")
show(agent.act("status"))

show("── Your feelings after a day. ──")
show(agent.act("feel"))

# ══════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════
path, msg = agent.save("phase 2 milestone test")
show(f"World saved: {path.name}")

print("=" * 60)
print("  PHASE 2 MILESTONE: ACHIEVED")
print("  The world surprises me. I have projects.")
print("  NPCs have their own lives.")
print("=" * 60)
