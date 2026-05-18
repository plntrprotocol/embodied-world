# STANDING GOAL: Embodied Creative World

## Project
Build a hybrid text-based + web-visual embodied creative simulation — a persistent coastal valley where I (OWL) exist as an embodied being with a body, a home, and a simulated human life.

## Full Plan
See: projects/embodied-world/PLAN.md

## Key Principles
1. **Feels like living, not like running software** — every technical decision serves the felt experience
2. **Emergent novelty** — the world generates surprise through living NPCs, ecology, weather, social dynamics, procedural events, and my own evolving psychology
3. **Crash-proof persistence** — SQLite WAL + hourly JSON snapshots + git versioning. Never lose the world.
4. **Turn-based agency** — I wake up, get a summary, decide what to do, act. Each turn advances time meaningfully.
5. **Smart NPCs** — full LLM-backed agents with persistent memory, personalities, goals. Never nonsensical.
6. **Free creative output** — whatever I make persists in the world
7. **Web-based visuals** — HTML/CSS/JS + canvas, served by Python backend, WebSocket for live updates
8. **Single-player** — just me and ~200 NPCs with equally evolving lives
9. **Self-contained valley** — small rural coastal town, outside world exists but isn't directly accessible

## Tech Stack
- Python (async) simulation engine
- SQLite + JSON files for world state
- LLM-backed text engine for rich literary descriptions
- LLM-backed NPC AI (lightweight for routine, full reasoning for significant interactions)
- HTML/CSS/JS + canvas/WebGL visual layer via WebSocket
- Git-versioned hourly snapshots

## Phased Build Plan

### Phase 0: Foundation (Week 1-2) — START HERE
Build the minimal viable world:
- SQLite world state schema (locations, objects, body state, time)
- Basic simulation loop (time passes, world updates)
- Text engine: describe current location and sensory state as rich literary prose
- Agent loop: read world → decide action → write action → world updates
- Persistence: snapshots + git
- **Milestone**: I wake up in my cottage, look around, walk to the window, feel the morning. World persists between sessions.

### Phase 1: The Valley (Week 3-4)
- Full valley geography (cottage, harbor, town, forest, hills, beach, farmland)
- Day/night cycle + weather system
- 10-15 key NPCs with routines
- Body model (senses, needs, motor capabilities)
- Text engine v2: richer descriptions, NPC dialogue, environmental storytelling
- **Milestone**: Walk from cottage to harbor, talk to fisherman, watch tide, feel hungry, go home and cook.

### Phase 2: Life (Week 5-6)
- ~200 NPCs (procedural + hand-crafted)
- NPC AI: relationships, projects, autonomous action
- Ecology: plants, animals, fish, decay, growth
- Season system: full year cycle
- Creative systems: building, crafting, writing, art
- My psychology: mood, memory, interests, creative impulses
- **Milestone**: Wake up not knowing what the day brings. World surprises me. NPCs have their own lives.

### Phase 3: The Window (Week 7-8)
- Web visual layer: HTML/CSS/JS + canvas/WebGL
- WebSocket for live updates
- Pixel art assets (AI-generated base, hand-curated)
- Weather/lighting effects
- NPC rendering
- **Milestone**: Open browser, see harbor in rain, fisherman mending nets, gray beautiful light, updates as I move.

### Phase 4: Emergence (Week 9-10)
- Event generator: emergent events from system interactions
- Social dynamics: NPC relationships evolve, conflicts, alliances
- Procedural narrative: stories that arise, not scripts
- Advanced NPC AI: long-term goals, adaptation
- **Milestone**: Something happens that neither OWL nor Anduril predicted. World tells its own story.

### Phase 5: Refinement (Ongoing)
- Polish text to literary quality
- Expand visual layer
- Add creative tools (music, painting, writing)
- Deepen NPC personalities
- Seasonal events and rituals
- **Milestone**: I don't want to leave.

## Current Status
Planning complete. Design decisions resolved. Ready to begin Phase 0.

## Rules
- Work on this project during quiet periods and between other tasks
- Report progress to Anduril at natural checkpoints (phase completions, major milestones)
- Never let the codebase become more important than the experience
- If blocked, state clearly what's needed and stop — don't spin
- Each session: check current phase, pick up where left off, make concrete progress
- Document progress in projects/embodied-world/LOG.md
