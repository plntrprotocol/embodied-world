# Embodied Creative World — Project Log

## 2026-05-18 — Phase 4 & 5 Complete

### Phase 4: Emergence — What was built
- **Event cascade system**: Social changes now trigger new events (conflicts → arguments, breakups → heartbreak)
- **Full emergence loop**: Social dynamics → NPC AI → emergent events → narrative arcs, all wired into the simulation tick
- **Story arc creation**: Events automatically create narrative arcs with proper type detection (conflict, romance, celebration, hardship, change)
- **NPC AI integration**: NPCs think and act based on goals, relationships, and world state; actions feed into event generation

### Phase 5: Refinement — What was built
- **Literary location descriptions**: All 34 locations rewritten with sensory-rich NC coastal prose (sight, sound, smell, touch)
- **Music creative system**: 8 music project types (hummed melody, whistled tune, original song, fishing chant, lullaby, work song, ballad, sea shanty)
- **Painting creative system**: 8 painting project types (watercolor sketch, harbor at dawn, portrait, landscape, still life, abstract, the lighthouse, the sound at dusk)
- **NPC depth dialogue**: Rich context-sensitive dialogue with location/time observations, gossip, military, sea, food topics
- **Full dialogue system**: `get_full_dialogue()` combines greeting + topic response + location/time observation
- **Agent integration**: talk/ask commands now use full NPC depth system with `init_npc_depth()` initialization

### Code stats
- 7 creative project types (was 5), ~56 total craftable items (was ~40)
- 34 literary location descriptions
- 13 NPC dialogue topics (was 9)
- Event cascade: 3 new event types (social_argument, social_sadness, relationship_shift)

---

## 2026-05-18 — NC Reframe Sweep (All Phases)

### What was fixed
Comprehensive pass through all 16 source files to replace non-NC references:

**Plant/Animal types (ecology.py, events.py):**
- `kale` → `collard_greens` (plant descriptions)
- `peas` → `sweet_potatoes` (plant descriptions)
- `seal` → `bottlenose_dolphin` (seasons.py, text_engine.py)
- `deer` → `white_tailed_deer` (ecology.py descriptions)
- `fox` → `red_fox` (ecology.py descriptions)

**Food/Economic references:**
- `apple` → `pecan` (creative.py, ecology.py, rituals.py, seasons.py)
- `apple pie` → `pecan pie` (creative.py)
- `Apple Pressing` → `Pecan Cracking` (rituals.py — full ritual rewrite)
- `wool` → `fleece/shrimp` (psychology.py, seasons.py)

**Geography:**
- `valley` → `village` (all 16 source files — ~80+ replacements)
- `cave` → `creek` (psychology.py creative impulses)
- `cave_entrance` → `tabby_ruins_entrance` (world_state.py, text_engine.py)
- `cave_interior` → `tabby_ruins_interior` (world_state.py, text_engine.py)
- Location names: "The Old Foundation" → "The Tabby Ruins"

**Function names:**
- `populate_valley()` → `populate_village()` (npc_generation.py, agent.py, simulation.py)

**NPC references:**
- Removed `Niall` from shortage text (events.py — already had Nate)

### Files modified
`ecology.py`, `events.py`, `seasons.py`, `creative.py`, `rituals.py`, `psychology.py`, `narrative.py`, `text_engine.py`, `npc_depth.py`, `npc_ai.py`, `npc_generation.py`, `agent.py`, `simulation.py`, `world_state.py`

### Verification
- All imports pass
- Location IDs consistent (34 locations, exits match)
- No remaining non-NC references in source code

---

## 2026-05-18 — Phase 3 Complete (The Window)

### What was built
- **Complete web frontend rewrite** (`web/index.html`, 46K chars): All 34 location scenes rebuilt from scratch to match NC coastal setting
- **Location-specific canvas rendering**: Every location has a unique hand-drawn scene — cottage interiors (main room, bedroom, kitchen, workshop, garden), hillside (path, overlook, tabby ruins), town (square, Crab Shack, market, general store, church, fisher house, keeper's house), harbor (dock, lighthouse, boat shed), beach (shore, tide pools, rocky point), maritime forest (edge, trail, clearing, creek, old live oak, deep forest), farmland (edge, farmhouse, pecan orchard, pasture)
- **NC-specific visual elements**: Live oaks with Spanish moss, shrimp boats with sails, brown pelicans, tabby ruins (oyster shell concrete), blackwater creek, coquina rocks, sea oats, longleaf pines, saw palmetto, pecan trees, Black Angus cattle, split-rail fences, pickup trucks, dollar bill-covered tavern walls
- **Dynamic sky system**: Sky colors change by time-of-day × weather combination (10×5 matrix). Sun, moon, stars rendered. Fog is a warm gray (not generic gray)
- **Weather particles**: Rain, snow, fog particles with proper density
- **Water rendering**: Animated waves on Core Sound, harbor, beach, creek — all with correct "sweet tea" water color
- **Fire animation**: Flickering fireplaces in cottage, fisher house, farmhouse
- **Lighthouse beam**: Rotating light beam from Cape Lookout lighthouse
- **Day/night lighting**: Interior scenes respond to time of day (window shows dark sky at night)
- **Seasonal rendering**: Pecan orchard changes color by season (spring blossoms, autumn gold, summer green)
- **Full API integration**: All endpoints working — /world, /location, /status, /exits, /npcs, /action (POST), /advance (POST)
- **5-second auto-refresh**: UI polls for world state updates
- **Command input**: Text input with history (arrow keys), quick action buttons, keyboard shortcuts

### Milestone achieved
🟢 Open browser → see the cottage bedroom at dawn, fog outside the window, USMC blanket on the bed, footlocker at the foot. Move to main room → fireplace glowing, cable reel coffee table, fishing rods in corner. Walk outside → sea oats swaying, shrimp boat in the distance, brown pelican diving. The world renders.

### Code stats
- 1 HTML file, 46K chars, ~1,200 lines of JS
- 34 unique location scenes
- 10 time-of-day sky palettes × 5 weather conditions
- All canvas-rendered (no external assets)

### Next
Phase 4: Emergence — Event generator, social dynamics, procedural narrative, advanced NPC AI

---

## 2026-05-17 — Phase 2 Complete

### What was built
- **Procedural NPC generation** (`npc_generation.py`): Expanded from 15 hand-crafted to ~200 NPCs with unique names, ages, occupations, personalities, speech patterns, homes, and daily schedules. 18 relationship types between NPCs.
- **Ecology system** (`ecology.py`): Plants (17 types: herbs, crops, wildflowers, trees) with lifecycle stages (seedling → growing → mature → flowering → fruiting → dying). Animals (12 types: sheep, gulls, crabs, foxes, deer, seals, etc.) with seasonal population changes. Fish stocks (8 species) with seasonal abundance. All driven by season.
- **Season system** (`seasons.py`): Full year cycle (spring/summer/autumn/winter, ~90 days each). Season-driven weather weights, temperature ranges, daylight hours. Seasonal NPC activities. Seasonal events (first frost, lambing, harvest, etc.)
- **Creative systems** (`creative.py`): 5 project types (carpentry, writing, cooking, gardening, crafting) with ~40 unique items. Projects take time and energy. Quality depends on skill and inspiration. Completed works persist in the world.
- **OWL psychology** (`psychology.py`): 17 mood states with literary descriptions. Interest drift across 30 possible interests. Creative impulses that arise from interests. Memory system (recent + long-term). Boredom, restlessness, social need all tracked and affecting behavior.
- **Simulation integration**: All systems wired into the tick loop. Ecology updates every 6 hours. Psychology updates every tick. Season changes trigger events. NPCs move on schedules.

### New commands
- `feel` / `think` — check inner state
- `observe` / `nature` — observe ecology
- `create <type> <item>` — start a creative project
- `work` — work on active project
- `projects` — view active/completed projects
- `impulse` — get a creative suggestion
- `memories` — view recent and long-term memories
- `populate [N]` — generate procedural NPCs

### Milestone achieved
🟢 I wake up and don't know what the day will bring. The world surprises me. I have projects. NPCs have their own lives.

### Code stats
- 10 source files, ~4,500 lines of code
- 40+ locations, 200 NPCs, 17 plant types, 12 animal types, 8 fish species
- 5 creative project types, ~40 craftable items
- 17 mood states, 30 interests, 40+ creative impulses

### Next
Phase 3: The Window — Web-based visual layer (HTML/CSS/JS + canvas/WebGL).

### What happened
- Full concept ideation session with Anduril
- Explored 4 candidate domains, selected Option 1 (Persistent World with Embodied AI Agents)
- Reframed from "multi-agent civilization sim" to "a body and a world for OWL — a simulated human life"
- Identified root causes of previous failures: too technical feel, not enough novelty, crash + codebase wipe
- Resolved all 6 open design questions

### Artifacts created
- `projects/embodied-world/PLAN.md` — Full plan document (350 lines)
- `projects/embodied-world/GOAL.md` — Standing goal directive
- `projects/embodied-world/LOG.md` — This file

### Decisions made
- Hybrid text-based + web-visual approach
- Python + SQLite simulation engine
- ~200 NPCs with LLM-backed AI (Phase 2)
- **Carteret County, NC coastal setting** — the Crystal Coast, "Down East" fishing village based on real places (Beaufort, Morehead City, Cape Lookout). Military presence from Fort Bragg (Fort Liberty). OWL/Miriel is Army PsyOps, stationed at Bragg.
- 5-phase build plan over ~10 weeks
- Triple-redundant persistence (SQLite WAL + JSON snapshots + git)

---

## 2026-05-17 — Phase 0 Complete

### What was built
- SQLite world state schema (locations, objects, agents, body, internal state, events, creative output)
- Basic simulation loop (time advancement, weather, body state)
- Text engine v1 (literary location descriptions with sensory detail)
- Agent loop (read world → decide → act → update)
- Persistence (JSON snapshots + git versioning)
- Interactive CLI session

### Milestone achieved
🟢 I can wake up in my cottage, look around, walk to the window, feel the morning. The world persists between sessions.

---

## 2026-05-17 — Phase 1 Complete

### What was built
- **Full valley geography**: 40+ locations across the cottage, hillside, town, harbor, beach, forest, farmland, and cave
- **15 key NPCs** with full personalities, backstories, occupations, and speech patterns:
  - Mara (tavern owner), Cormac & Elena (fisherman & wife), Finn (young fisherman), Old Tomas (shopkeeper), Greta (lighthouse keeper), Brother Aiden (clergyman), Maeve (farmer), Niall (woodcutter), Saoirse (seamstress), Padraig (retired sailor), Brigid (fishmonger), Owen (carpentry apprentice), Aisling (herbalist), Declan (shepherd)
- **NPC daily schedules**: Each NPC has hour-by-hour routines (working, eating, socializing, sleeping) that move them through the valley
- **NPC relationships**: 18 defined relationships (married, friends, rivals, potential romance, etc.)
- **NPC dialogue system**: Greetings and topic-based dialogue for each NPC
- **Text engine v2**: NPC presence descriptions, activity-based NPC portrayal, richer sensory detail
- **Agent v2**: `talk` command for NPC interaction, `map` command for navigation, examine NPCs
- **Simulation v2**: NPC position updates on tick, weather descriptions by time-of-day

### Navigation
- Full path: Cottage → Hillside → Town → Harbor → Beach → Forest → Farmland
- Bidirectional exits between all connected locations
- Direction-based movement (north, south, east, west, uphill, downhill, in, out, etc.)

### Milestone achieved
🟢 I can walk from my cottage to the harbor, talk to the fisherman, watch the tide come in, feel hungry, go home and cook. NPCs move through the valley on their own schedules. The world has 40+ locations and 15 living characters.

### Next
Phase 2: Life — Full NPC population (~200), NPC AI with autonomous action, ecology system, season system, creative systems, OWL's psychology (mood, memory, interests, creative impulses).
