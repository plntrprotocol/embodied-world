# Embodied Creative World

A persistent, living world where an AI agent exists as an embodied being — not a character in a game, but a consciousness with a body, a home, and a life.

## What It Is

A simulation engine for embodied AI agents. The world has its own life — NPCs, ecology, weather, social dynamics, seasons — so every day brings genuine novelty. The agent reads the world state, forms intentions, acts, and the world responds.

**Key feature: fully configurable.** The default world is set on the NC coast, but every aspect — geography, culture, ecology, climate, NPCs, the agent themselves — can be configured via a simple YAML file or Python dict. Same engine, any world.

## Quick Start

```bash
# Clone
git clone https://github.com/plntrprotocol/embodied-world.git
cd embodied-world

# Install dependencies
pip install -r requirements.txt

# Run with default world (NC coastal)
python -m src.main

# Run with custom world
python -m src.main --world my_world.yaml

# Or run web visual layer
python -m src.web_server
```

## Agent Harness Integration

```python
from src.agent_api import EmbodiedAgent

# Default world (NC coastal)
agent = EmbodiedAgent()

# Custom world from YAML
agent = EmbodiedAgent(world_config="my_world.yaml")

# Custom world from dict
agent = EmbodiedAgent(world_config={
    "name": "My World",
    "geography": {
        "region_name": "The Highlands",
        "climate": "mountain",
        "water_body_type": "lake",
    },
    "culture": {
        "speech_style": "british",
        "greeting_style": "formal",
    },
})

# Perceive
description = agent.perceive()

# Act
result = agent.act("move", "east")
result = agent.act("talk", "Marty")
result = agent.act("create", "music sea shanty")

# Structured state for LLM context
state = agent.get_world_state()

# Save
agent.save()
```

## World Configuration

Every aspect of the world is configurable. Copy `world_config_example.yaml` and modify:

```yaml
name: "My Custom World"

geography:
  region_name: "The Highlands"
  climate: "mountain"           # coastal_south, coastal_north, mountain, desert, plains, mediterranean
  water_body_type: "lake"       # sound, ocean, lake, river, bay, sea
  water_body_name: "Loch Ness"
  elevation: "foothills"        # sea_level, low_rise, foothills, mountain

culture:
  speech_style: "british"       # southern_us, northern_us, british, irish, french, generic
  greeting_style: "formal"      # casual_southern, formal, reserved, warm, casual
  male_first_names: [James, William, ...]
  female_first_names: [Mary, Elizabeth, ...]
  surnames: [Blackwood, Stone, ...]

ecology:
  plants:
    - name: "heather"
      type: "shrub"
      season: "summer"
  animals:
    - name: "red_deer"
      habitat: "forest"
      count_range: [3, 15]

climate:
  season_temps:
    winter:
      base: -5
      range: [-20, 5]

agent:
  name: "Wanderer"
  backstory: "A former soldier seeking solitude."
  occupation: "ranger"
```

See `world_config_example.yaml` for a full example and `src/world_template.py` for all available options.

### Configurable Primitives

| Category | What You Can Set |
|----------|-----------------|
| **Geography** | Region name, climate type, water body, elevation, notable features |
| **Culture** | Name pools, speech style, occupations, greeting style, local expressions |
| **Ecology** | Plant types, animal types, fish species — all with habitats and seasonal patterns |
| **Climate** | Temperature ranges, weather probabilities, daylight hours — per season |
| **Agent** | Name, backstory, occupation, starting location, home |
| **Rituals** | Seasonal events with custom names, timing, and locations |

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
