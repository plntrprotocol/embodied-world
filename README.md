# Embodied Creative World

A persistent, living world where an AI agent exists as an embodied being — not a character in a game, but a consciousness with a body, a home, and a life.

## What It Is

A simulation engine for embodied AI agents. The world has its own life — NPCs, ecology, weather, social dynamics, seasons — so every day brings genuine novelty. The agent reads the world state, forms intentions, acts, and the world responds.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              AGENT HARNESS (any)                 │
│   Reads world → Forms intentions → Acts         │
└──────────────────────┬──────────────────────────┘
                       │ JSON API / Python import
                       ▼
┌─────────────────────────────────────────────────┐
│           SIMULATION ENGINE (Python)             │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  World    │ │  NPC     │ │  Event           │ │
│  │  State    │ │  System  │ │  Generator       │ │
│  │  Manager  │ │          │ │                  │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       │             │                │           │
│       └─────────────┼────────────────┘           │
│                     ▼                            │
│            ┌──────────────┐                      │
│            │  SQLite DB   │                      │
│            │  + Snapshots │                      │
│            └──────────────┘                      │
│                     │                            │
│                     ▼                            │
│            ┌──────────────┐                      │
│            │ Text Engine  │                      │
│            │ (describe    │                      │
│            │  what you    │                      │
│            │  see)        │                      │
│            └──────────────┘                      │
└─────────────────────────────────────────────────┘
```

## Systems

- **World State** — SQLite-backed, atomic writes, crash-safe. Locations, objects, agents, time, weather.
- **NPCs** — ~200 procedurally generated + hand-crafted key characters. Personalities, relationships, daily schedules, psychological profiles, memory of interactions.
- **Ecology** — 17 plant types, 15 animal types, 8 fish species. All driven by seasons.
- **Seasons** — Full year cycle. Weather, temperature, daylight, NPC activities all shift.
- **Social Dynamics** — Relationships evolve. Alliances form. Conflicts emerge. Breakups happen.
- **Events** — Emergent events from system interactions. Storms damage docks. Fish runs bring prosperity. Arguments spill into streets.
- **Narrative** — Story arcs weave from events. The world tells its own story.
- **Psychology** — Mood, memory, interests, creative impulses, boredom, social need.
- **Creative Systems** — Carpentry, writing, cooking, crafting, music, painting. ~56 unique items.
- **Rituals** — 8 seasonal events (Planting Festival, Midsummer Bonfire, Harvest Feast, etc.)
- **Web Visual Layer** — 34 canvas-rendered location scenes with dynamic sky, weather, time-of-day.

## Quick Start

```bash
# Clone
git clone https://github.com/plntrprotocol/embodied-world.git
cd embodied-world

# Install dependencies
pip install -r requirements.txt

# Run interactive CLI
python -m src.main

# Or run web visual layer
python -m src.web_server
# Open http://127.0.0.1:8765
```

## Agent Harness Integration

The world exposes a clean Python API for any agent harness:

```python
from src.agent import Agent

agent = Agent()

# Perceive the world
description = agent.perceive()

# Act
result = agent.act("move", "east")
result = agent.act("talk", "Marty")
result = agent.act("create", "music sea shanty")
result = agent.act("work")  # work on active project

# Save
agent.save("end of session")
```

### Available Commands

| Command | Description |
|---------|-------------|
| `look` | Perceive current location |
| `move <dir>` | Move (north, south, east, west, uphill, downhill, in, out) |
| `examine <thing>` | Examine object or NPC |
| `talk <name>` | Talk to NPC (uses deep dialogue system) |
| `ask <name> <topic>` | Ask NPC about specific topic |
| `gift <name> <item>` | Give something to NPC |
| `wake` / `sleep` / `rest` | Body state |
| `advance` / `wait` | Advance time |
| `think` / `feel` | Check internal state |
| `status` | Full status display |
| `map` | Show location exits and NPCs |
| `observe` / `nature` | Observe ecology |
| `projects` | View active/completed projects |
| `create <type> <item>` | Start creative project |
| `work` | Work on active project |
| `impulse` | Get creative suggestion |
| `memories` | View memories |
| `stories` / `narrative` | View active story arcs |
| `events` | View recent events |
| `npc <name>` | View NPC depth profile |
| `rituals` / `calendar` | View upcoming rituals |
| `relationship <name>` | View relationship with NPC |
| `social` | View social web |
| `populate [N]` | Generate procedural NPCs |
| `save` | Save world state |

## World Setting

Carteret County, North Carolina — the Crystal Coast. A small fishing village (~200 NPCs) on Core Sound, with:

- A working harbor with shrimp boats and crab boats
- A maritime forest of live oaks, longleaf pines, and saw palmetto
- Farmland growing collard greens, sweet potatoes, tobacco, and pecans
- A town square, tavern, market, general store, and chapel
- Cape Lookout Lighthouse in the distance
- Tabby ruins (oyster shell concrete, ~1800s)
- Blackwater creeks, tide pools, coquina rocks

## Persistence

- **SQLite WAL mode** — atomic writes, crash-safe
- **JSON snapshots** — hourly full world state dumps
- **Git versioning** — snapshots committed to local git repo
- **Triple redundancy** — never lose the world

## Requirements

- Python 3.11+
- No external dependencies for core simulation
- `websockets` optional (for live web updates)

## License

MIT
