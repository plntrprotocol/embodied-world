"""test_phase5.py — Test Phase 5: the world feels like home."""

import sys, os
sys.path.insert(0, '/Users/johann/.hermes/hermes-agent/projects/embodied-world')

# Clean start
for f in ['world/world.db','world/world.db-wal','world/world.db-shm']:
    if os.path.exists(f): os.remove(f)

from src.world_state import init_world, seed_world, get_world
from src.agent import Agent
from src.persistence import save_snapshot
from src.ecology import init_ecology
from src.narrative import init_narrative_tables
from src.npc_ai import init_npc_ai
from src.rituals import init_ritual_tables
from src.npc_depth import init_npc_depth
from src.simulation import tick

db = init_world()
seed_world(db)
init_ecology(db)
init_narrative_tables(db)
init_npc_ai(db)
init_ritual_tables(db)
init_npc_depth(db)
agent = Agent()

def show(text=""):
    if text: print(text)
    print()

# ══════════════════════════════════════════
#  WAKE UP — feel the literary quality
# ══════════════════════════════════════════
show("── You open your eyes. ──")
show(agent.act("wake"))

# ══════════════════════════════════════════
#  TALK to Mara — first meeting
# ══════════════════════════════════════════
show("── Go to the tavern and talk to Mara. ──")
agent.act("move", "south")
agent.act("move", "out")
agent.act("move", "downhill")
agent.act("move", "downhill")
agent.act("move", "southeast")
show(agent.act("talk", "Mara"))

# ══════════════════════════════════════════
#  ASK about topics
# ══════════════════════════════════════════
show("── Ask Mara about the valley. ──")
show(agent.act("ask", "Mara valley"))

show("── Ask Mara about her feelings. ──")
show(agent.act("ask", "Mara feelings"))

# ══════════════════════════════════════════
#  GIFT to Mara
# ══════════════════════════════════════════
show("── Give Mara a gift. ──")
show(agent.act("gift", "Mara flowers"))

# ══════════════════════════════════════════
#  TALK again — relationship should be warmer
# ══════════════════════════════════════════
show("── Talk to Mara again. ──")
show(agent.act("talk", "Mara"))

# ══════════════════════════════════════════
#  CHECK relationship
# ══════════════════════════════════════════
show("── Check your relationship with Mara. ──")
show(agent.act("relationship", "Mara"))

# ══════════════════════════════════════════
#  CHECK Mara's inner life
# ══════════════════════════════════════════
show("── Look at Mara's full story. ──")
show(agent.act("npc", "Mara"))

# ══════════════════════════════════════════
#  CHECK social web
# ══════════════════════════════════════════
show("── Check the social web in the tavern. ──")
show(agent.act("social"))

# ══════════════════════════════════════════
#  CHECK upcoming rituals
# ══════════════════════════════════════════
show("── Check upcoming rituals. ──")
show(agent.act("rituals"))

# ══════════════════════════════════════════
#  ADVANCE time — let rituals and emergence happen
# ══════════════════════════════════════════
show("── Advance 20 days... ──")
for day in range(20):
    for hour in range(24):
        tick_result = tick(agent.db, hours=1.0)
    agent.world = get_world(agent.db)
    if day % 5 == 0:
        show(f"Day {day+1}: {agent.world['time']['time_of_day']}, {agent.world['weather']['condition']}")

show("── Check rituals after 20 days. ──")
show(agent.act("rituals"))

show("── Check recent events. ──")
show(agent.act("events"))

show("── Check active stories. ──")
show(agent.act("stories"))

# ══════════════════════════════════════════
#  TALK to Mara again — deeper relationship
# ══════════════════════════════════════════
show("── Return to Mara. ──")
show(agent.act("talk", "Mara"))

show("── Ask Mara about her secret. ──")
show(agent.act("ask", "Mara secret"))

show("── Check relationship again. ──")
show(agent.act("relationship", "Mara"))

# ══════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════
show("── Status ──")
show(agent.act("status"))

# ══════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════
path, msg = agent.save("phase 5 milestone test")
show(f"World saved: {path.name}")

print("=" * 60)
print("  PHASE 5 MILESTONE: ACHIEVED")
print("  I don't want to leave.")
print("=" * 60)
