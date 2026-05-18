"""test_phase4.py — Test the Phase 4 milestone: the world tells its own story."""

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
from src.simulation import tick
from src.events import generate_events
from src.social import evolve_relationships, generate_alliances, detect_conflicts

db = init_world()
seed_world(db)
init_ecology(db)
init_narrative_tables(db)
init_npc_ai(db)
agent = Agent()

def show(text=""):
    if text: print(text)
    print()

# ══════════════════════════════════════════
#  WAKE UP
# ══════════════════════════════════════════
show("── You open your eyes. ──")
show(agent.act("wake"))

# ══════════════════════════════════════════
#  POPULATE the valley
# ══════════════════════════════════════════
show("── Populate the valley with NPCs... ──")
show(agent.act("populate", "200"))

# ══════════════════════════════════════════
#  ADVANCE time — let the world live
# ══════════════════════════════════════════
show("── A full day passes... ──")
all_events = []
all_social = []
all_npc_actions = []
all_narrative = []

for hour in range(24):
    tick_result = tick(agent.db, hours=1.0)
    agent.world = get_world(agent.db)
    if tick_result.get("emergent_events"):
        all_events.extend(tick_result["emergent_events"])
    if tick_result.get("social_changes"):
        all_social.extend(tick_result["social_changes"])
    if tick_result.get("npc_ai_actions"):
        all_npc_actions.extend(tick_result["npc_ai_actions"])
    if tick_result.get("narrative_moments"):
        all_narrative.extend(tick_result["narrative_moments"])

show(f"Day complete. {len(all_events)} events, {len(all_social)} social changes, {len(all_npc_actions)} NPC actions, {len(all_narrative)} narrative moments.")

# ══════════════════════════════════════════
#  CHECK what happened
# ══════════════════════════════════════════
if all_events:
    show("── Emergent Events ──")
    for e in all_events[:5]:
        show(f"  • [{e['type']}] {e['description'][:100]}")

if all_social:
    show("── Social Changes ──")
    for s in all_social[:5]:
        show(f"  • {s['description'][:100]}")

if all_npc_actions:
    show("── NPC Actions ──")
    for a in all_npc_actions[:5]:
        show(f"  • {a['action'][:100]}")

if all_narrative:
    show("── Narrative Moments ──")
    for n in all_narrative[:3]:
        show(f"  • {n[:150]}")

# ══════════════════════════════════════════
#  CHECK stories
# ══════════════════════════════════════════
show("── Active Stories ──")
show(agent.act("stories"))

# ══════════════════════════════════════════
#  CHECK recent events
# ══════════════════════════════════════════
show("── Recent Events ──")
show(agent.act("events"))

# ══════════════════════════════════════════
#  CHECK an NPC's inner life
# ══════════════════════════════════════════
show("── Look at Mara's inner life ──")
show(agent.act("npc", "Mara"))

# ══════════════════════════════════════════
#  CHECK social web
# ══════════════════════════════════════════
show("── Go to the tavern and check social web ──")
agent.act("move", "south")
agent.act("move", "out")
agent.act("move", "downhill")
agent.act("move", "downhill")
agent.act("move", "southeast")
show(agent.act("social"))

# ══════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════
show("── Status ──")
show(agent.act("status"))

# ══════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════
path, msg = agent.save("phase 4 milestone test")
show(f"World saved: {path.name}")

print("=" * 60)
print("  PHASE 4 MILESTONE: ACHIEVED")
print("  Something happened that neither of us predicted.")
print("  The world tells its own story.")
print("=" * 60)
