"""
Embodied Creative World — Phase 5: Refinement

A persistent, living world where OWL exists as an embodied being.
The world is now polished, deep, and feels like home.

Architecture (17 source files, ~7,500 lines):
  world_state.py    — SQLite schema + world state management
  simulation.py     — Full world tick: time, weather, ecology, seasons, emergence, rituals
  text_engine.py    — Rich literary description + NPC dialogue
  agent.py          — Agent loop with 25+ commands
  persistence.py    — Snapshots + git versioning
  npc_generation.py — Procedural NPC generation (~200 NPCs)
  ecology.py        — Plants, animals, fish, decay, growth
  psychology.py     — OWL's mood, memory, interests, creative impulses
  creative.py       — Building, crafting, writing, art
  seasons.py        — Full year cycle with seasonal effects
  web_server.py     — HTTP server + REST API
  main.py           — Entry point
  web/index.html    — Full web frontend (HTML/CSS/JS + canvas)
  events.py         — Emergent event generator
  social.py         — NPC relationship evolution
  narrative.py      — Procedural narrative engine
  npc_ai.py         — Advanced NPC AI: goals, memory, autonomous action
  ── Phase 5 ──
  npc_depth.py      — Deep NPC personalities, context-sensitive dialogue, OWL memory
  rituals.py        — Seasonal events and rituals (8 rituals across 4 seasons)
"""

__version__ = "0.6.0-phase5"
