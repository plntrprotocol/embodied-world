"""
agent.py — The agent loop: read world → decide → act → update world.

Phase 2 additions:
- Creative commands: work, create, projects, craft
- Psychology: feelings, impulses, memories
- Ecology: observe nature
- NPC population: populate
"""

import json
import time
import random
from typing import Optional

from .world_state import (
    get_db, get_world, move_agent, update_body, update_internal,
    log_event, get_location, get_objects_in_location, get_exits_from,
    get_agents_in_location, DB_PATH
)
from .simulation import tick
from .text_engine import (
    describe_location, describe_action, describe_event,
    describe_npc_dialogue, describe_npc_greeting
)
from .persistence import save_snapshot, commit_snapshot
from .psychology import describe_internal_state, get_creative_impulse
from .creative import (
    start_project, work_on_project, get_active_projects,
    get_completed_projects, describe_project, PROJECT_TYPES
)
from .ecology import describe_location_ecology
from .npc_generation import populate_village


class Agent:
    """OWL's agent — the consciousness that inhabits the world."""

    def __init__(self, db_path=DB_PATH):
        self.db = get_db(db_path)
        self.world = get_world(self.db)
        self.turn_count = 0
        self.last_action = None
        self.last_result = None

    def perceive(self) -> str:
        """Perceive the current location. Returns rich sensory description."""
        owl = self.world["agents"].get("owl", {})
        location_id = owl.get("location_id", "cottage_bedroom")
        desc = describe_location(self.db, location_id, self.world)
        # Add ecology descriptions
        eco_parts = describe_location_ecology(self.db, location_id)
        if eco_parts:
            desc += "\n\n" + "\n\n".join(eco_parts[:2])  # Max 2 ecology notes
        return desc

    def act(self, action: str, target: str | None = None) -> str:
        """
        Perform an action in the world.
        Returns a description of what happened.
        """
        self.turn_count += 1
        owl = self.world["agents"].get("owl", {})
        location_id = owl.get("location_id", "cottage_bedroom")
        result = ""

        if action == "look":
            result = self.perceive()

        elif action == "move" and target:
            exits = get_exits_from(self.db, location_id)
            valid_directions = {e["direction"]: e["to_location"] for e in exits}

            if target in valid_directions:
                new_location = valid_directions[target]
                move_agent(self.db, "owl", new_location)
                self.world = get_world(self.db)
                loc = get_location(self.db, new_location)
                loc_name = loc["name"] if loc else new_location
                result = f"You {target} toward {loc_name}.\n\n"
                result += self.perceive()
            else:
                result = f"You can't go {target} from here."

        elif action == "examine" and target:
            objects = get_objects_in_location(self.db, location_id)
            found = None
            for obj in objects:
                if target.lower() in obj["name"].lower() or target.lower() in obj["id"].lower():
                    found = obj
                    break
            if found:
                result = f"You examine the {found['name']}:\n{found['description']}"
                if found["state"] != "default":
                    result += f"\n\nIt is {found['state']}."
            else:
                agents = get_agents_in_location(self.db, location_id)
                for agent in agents:
                    if target.lower() in agent["name"].lower() or target.lower() in agent["id"].lower():
                        props = agent.get("properties", {})
                        if isinstance(props, str):
                            try:
                                props = json.loads(props)
                            except (json.JSONDecodeError, TypeError):
                                props = {}
                        desc = props.get("description", f"{agent['name']} is here.")
                        result = f"You look at {agent['name']}.\n\n{desc}"
                        break
                if not result:
                    result = f"You don't see a {target} here."

        elif action == "talk" and target:
            agents = get_agents_in_location(self.db, location_id)
            found_npc = None
            for agent in agents:
                if target.lower() in agent["name"].lower() or target.lower() in agent["id"].lower():
                    found_npc = agent
                    break
            if found_npc:
                npc_id = found_npc["id"]
                from .npc_depth import OWLInteractionMemory, init_npc_depth
                # Ensure NPC has depth profile
                init_npc_depth(self.db)
                memory = OWLInteractionMemory(npc_id, self.db)
                time_info = self.world.get("time", {})
                full = memory.get_full_dialogue(
                    topic="default",
                    world_state=self.world,
                    location=location_id,
                    time_of_day=time_info.get("time_of_day", ""),
                )
                result = f"You approach {found_npc['name']}.\n\n{full}"
                memory.record_interaction("conversation", "default", 0.5)
                memory.save()
                log_event(self.db, "conversation", f"Talked to {found_npc['name']}",
                          agent_id="owl", location_id=location_id)
            else:
                result = f"There's no one called {target} here to talk to."

        elif action == "ask" and target:
            # Ask an NPC about a specific topic
            parts = target.split(maxsplit=1)
            if len(parts) >= 2:
                npc_name = parts[0]
                topic = parts[1]
                agents = get_agents_in_location(self.db, location_id)
                found_npc = None
                for a in agents:
                    if npc_name.lower() in a["name"].lower():
                        found_npc = a
                        break
                if found_npc:
                    from .npc_depth import OWLInteractionMemory, init_npc_depth
                    init_npc_depth(self.db)
                    memory = OWLInteractionMemory(found_npc["id"], self.db)
                    time_info = self.world.get("time", {})
                    full = memory.get_full_dialogue(
                        topic=topic,
                        world_state=self.world,
                        location=location_id,
                        time_of_day=time_info.get("time_of_day", ""),
                    )
                    result = f"You ask {found_npc['name']} about {topic}.\n\n{full}"
                    memory.record_interaction("conversation", topic, 0.6)
                    memory.save()
                else:
                    result = f"No one called {npc_name} here."
            else:
                result = "Usage: ask <name> <topic> — e.g., 'ask Mara about the village'"

        elif action == "gift" and target:
            # Give something to an NPC
            parts = target.split(maxsplit=1)
            if len(parts) >= 2:
                npc_name = parts[0]
                gift = parts[1]
                agents = get_agents_in_location(self.db, location_id)
                found_npc = None
                for a in agents:
                    if npc_name.lower() in a["name"].lower():
                        found_npc = a
                        break
                if found_npc:
                    from .npc_depth import OWLInteractionMemory
                    memory = OWLInteractionMemory(found_npc["id"], self.db)
                    reactions = [
                        f"{found_npc['name']} is genuinely touched. 'Thank you. This means a lot.'",
                        f"{found_npc['name']} accepts the {gift} with a warm smile. 'You didn't have to.'",
                        f"'For me?' {found_npc['name']} seems surprised and pleased.",
                    ]
                    result = random.choice(reactions)
                    memory.record_interaction("gift", gift, 0.8)
                    memory.save()
                else:
                    result = f"No one called {npc_name} here."
            else:
                result = "Usage: gift <name> <item> — e.g., 'gift Mara flowers'"

        elif action == "wake":
            update_body(self.db, current_action="idle", mood="awake")
            self.world = get_world(self.db)
            result = "You open your eyes. The room comes into focus.\n\n"
            result += self.perceive()

        elif action == "sleep":
            update_body(self.db, current_action="sleeping", mood="sleepy")
            self.world = get_world(self.db)
            result = "You lie down and close your eyes. The world softens."

        elif action == "rest":
            result = "You sit quietly for a moment. The world breathes around you."

        elif action == "advance" or action == "wait":
            tick_result = tick(self.db, hours=1.0)
            self.world = get_world(self.db)
            time_info = tick_result.get("time", {})
            weather_info = tick_result.get("weather", {})
            result = f"Time passes. It is now {time_info.get('time_of_day', '')}.\n"
            if weather_info.get("changed"):
                result += f"The weather shifts: {weather_info.get('description', '')}\n"
            if tick_result.get("season_event"):
                result += f"\n{tick_result['season_event']}\n"
            if tick_result.get("ecology_events"):
                for eco in tick_result["ecology_events"]:
                    result += f"\n{eco['description']}\n"
            result += "\n" + self.perceive()

        elif action == "think":
            result = describe_internal_state(self.db)

        elif action == "feel":
            result = describe_internal_state(self.db)

        elif action == "status":
            body = self.world.get("body", {})
            internal = self.world.get("internal", {})
            time_info = self.world.get("time", {})
            weather = self.world.get("weather", {})
            result = (
                f"── Status ──\n"
                f"Time: {time_info.get('hour', '?'):02d}:{time_info.get('minute', '?'):02d}, "
                f"{time_info.get('season', '?').title()} — {time_info.get('time_of_day', '?').replace('_', ' ')}\n"
                f"Weather: {weather.get('condition', '?')}, {weather.get('temperature', '?')}°C\n"
                f"Mood: {body.get('mood', '?')}\n"
                f"Energy: {body.get('energy', 0):.0%}\n"
                f"Hunger: {body.get('hunger', 0):.0%} | Thirst: {body.get('thirst', 0):.0%}\n"
                f"Warmth: {body.get('warmth', 0):.0%}\n"
                f"Project: {internal.get('current_project', 'none')}\n"
                f"Interest: {internal.get('dominant_interest', 'none')}\n"
                f"Creative urge: {internal.get('creative_urge', 0):.0%}\n"
                f"Restlessness: {internal.get('restlessness', 0):.0%}\n"
                f"Social need: {internal.get('social_need', 0):.0%}\n"
                f"Turns: {self.turn_count}"
            )

        elif action == "map":
            loc = get_location(self.db, location_id)
            exits = get_exits_from(self.db, location_id)
            agents = get_agents_in_location(self.db, location_id)
            npcs_here = [a for a in agents if a["id"] != "owl"]

            if not loc:
                result = "You are nowhere."
            else:
                result = f"── {loc['name']} ──\n\n"
            if npcs_here:
                result += "People here: " + ", ".join(n["name"] for n in npcs_here) + "\n\n"
            result += "Exits:\n"
            seen_dirs = set()
            for e in exits:
                if e["direction"] not in seen_dirs:
                    seen_dirs.add(e["direction"])
                    result += f"  {e['direction']} → {e['description']}\n"

        elif action == "observe" or action == "nature":
            eco_parts = describe_location_ecology(self.db, location_id)
            if eco_parts:
                result = "You observe the natural world around you.\n\n" + "\n\n".join(eco_parts)
            else:
                result = "The natural world here is quiet. Nothing remarkable to observe."

        elif action == "projects":
            active = get_active_projects(self.db)
            completed = get_completed_projects(self.db)
            result = "── Your Projects ──\n\n"
            if active:
                result += "Active:\n"
                for p in active:
                    result += f"  • {describe_project(p)}\n\n"
            else:
                result += "No active projects.\n\n"
            if completed:
                result += "Recent completed:\n"
                for p in completed[:5]:
                    result += f"  • {describe_project(p)}\n\n"

        elif action == "create" or action == "craft":
            # Parse: create <type> <item> or just create (shows options)
            if not target:
                result = "── Creative Projects ──\n\n"
                for ptype, pdata in PROJECT_TYPES.items():
                    result += f"{ptype.title()}:\n"
                    for item in pdata["items"]:
                        result += f"  • {item['name']} (~{item['time_hours']}h, difficulty: {item['difficulty']:.0%})\n"
                    result += "\n"
                result += "Use: create <type> <item>"
            else:
                parts = target.split(maxsplit=1)
                if len(parts) == 2:
                    ptype, item_name = parts
                    body = self.world.get("body", {})
                    project = start_project(self.db, ptype, item_name, body.get("energy", 0.7))
                    if project:
                        result = f"You begin working on: {project['item_name']}.\n\nUse 'work' to make progress."
                    else:
                        result = f"Can't create '{item_name}' of type '{ptype}'. Check available projects with 'create'."
                else:
                    result = "Use: create <type> <item> (e.g., 'create carpentry wooden chair')"

        elif action == "work":
            # Work on the first active project
            active = get_active_projects(self.db)
            if not active:
                result = "You have no active projects. Start one with 'create <type> <item>'."
            else:
                project = active[0]
                body = self.world.get("body", {})
                internal = self.world.get("internal", {})
                hours = 2.0  # Default work session
                updated = work_on_project(
                    self.db, project["id"], hours,
                    body.get("energy", 0.5),
                    internal.get("creative_urge", 0.5)
                )
                self.world = get_world(self.db)

                if updated.get("state") == "completed":
                    desc = updated.get("completion_description", "It's done!")
                    result = f"You work for {hours} hours.\n\n── Complete! ──\n{desc}"
                else:
                    progress = updated.get("hours_worked", 0) / max(0.1, updated.get("total_hours", 1))
                    result = f"You work for {hours} hours on the {updated.get('item_name', 'project')}.\n\nProgress: {progress:.0%}\nQuality so far: {updated.get('quality', 0):.0%}"

        elif action == "populate":
            # Generate procedural NPCs
            count = int(target) if target and target.isdigit() else 200
            generated = populate_village(self.db, count)
            self.world = get_world(self.db)
            result = f"Generated {generated} new NPCs. The village now has {15 + generated} people."

        elif action == "impulse":
            internal = self.world.get("internal", {})
            interest = internal.get("dominant_interest", "none")
            impulse = get_creative_impulse(interest)
            if impulse:
                result = f"You feel the creative urge.\n\n{impulse}?"
            else:
                result = "No particular creative impulse right now. Let your mind wander."

        elif action == "memories":
            internal = self.world.get("internal", {})
            recent = json.loads(internal.get("recent_memories", "[]"))
            long_term = json.loads(internal.get("long_term_memories", "[]"))
            result = "── Your Memories ──\n\n"
            if recent:
                result += "Recent:\n"
                for m in recent[:5]:
                    result += f"  • {m}\n"
                result += "\n"
            if long_term:
                result += "Long-term:\n"
                for m in long_term[:10]:
                    result += f"  • {m}\n"
            if not recent and not long_term:
                result += "Your memory is blank. A fresh start."

        elif action == "stories" or action == "narrative":
            from .narrative import get_active_stories
            stories = get_active_stories(self.db)
            if stories:
                result = "── Stories in the Village ──\n\n"
                for s in stories:
                    result += f"【{s.story_type.title()}】{s.generate_narrative()}\n\n"
            else:
                result = "No stories are unfolding right now. The village is quiet."

        elif action == "events":
            from .events import get_recent_events
            events = get_recent_events(self.db, 10)
            if events:
                result = "── Recent Events ──\n\n"
                for e in events:
                    result += f"• {e['description']}\n"
            else:
                result = "No recent events."

        elif action == "npc" and target:
            from .npc_ai import get_npc_story
            # Find NPC by name
            agents = get_agents_in_location(self.db, location_id)
            found = None
            for a in agents:
                if target.lower() in a["name"].lower():
                    found = a
                    break
            if not found:
                # Search all NPCs
                all_npcs = self.db.execute("SELECT * FROM agents WHERE type = 'npc'").fetchall()
                for npc in all_npcs:
                    if target.lower() in npc["name"].lower():
                        found = npc
                        break
            if found:
                story = get_npc_story(self.db, found["id"])
                result = f"── {story['name']} ──\n\n"
                result += f"Occupation: {story['occupation']}\n"
                result += f"Personality: {story['personality']}\n"
                if story.get("goals"):
                    result += f"Goals: {', '.join(story['goals'])}\n"
                result += "\n"
                if story.get("memories"):
                    result += "Memories:\n"
                    for m in story["memories"][:3]:
                        result += f"  • {m['content']}\n"
                    result += "\n"
                if story.get("recent_actions"):
                    result += "Recent actions:\n"
                    for a in story["recent_actions"][:3]:
                        result += f"  • {a['description']}\n"
            else:
                result = f"No NPC named '{target}' found."

        elif action == "rituals" or action == "calendar":
            from .rituals import get_upcoming_rituals
            upcoming = get_upcoming_rituals(self.db)
            if upcoming:
                result = "── Upcoming Rituals ──\n\n"
                for r in upcoming:
                    result += f"• {r['title']} — {r['days_until']} days away\n"
                    result += f"  Locations: {', '.join(r['locations'])}\n\n"
            else:
                world_time = self.world.get("time", {})
                season = world_time.get("season", "?")
                result = f"No upcoming rituals right now. It's {season} in the village."

        elif action == "relationship" and target:
            # Show OWL's relationship with an NPC
            agents = get_agents_in_location(self.db, location_id)
            found = None
            for a in agents:
                if target.lower() in a["name"].lower():
                    found = a
                    break
            if not found:
                all_npcs = self.db.execute("SELECT * FROM agents WHERE type = 'npc'").fetchall()
                for npc in all_npcs:
                    if target.lower() in npc["name"].lower():
                        found = npc
                        break
            if found:
                from .npc_depth import get_npc_depth_story
                depth = get_npc_depth_story(self.db, found["id"])
                result = f"── Your Relationship with {depth['name']} ──\n\n"
                result += f"Relationship: {depth['relationship']}\n"
                result += f"Times met: {depth['times_met']}\n"
                result += f"Trust: {depth['trust']:.0%} | Affection: {depth['affection']:.0%} | Respect: {depth['respect']:.0%}\n\n"
                if depth.get("profile", {}).get("values"):
                    result += f"Values: {', '.join(depth['profile']['values'])}\n"
                if depth.get("profile", {}).get("desires"):
                    result += f"Desires: {', '.join(depth['profile']['desires'])}\n"
                if depth.get("profile", {}).get("fears"):
                    result += f"Fears: {', '.join(depth['profile']['fears'])}\n"
            else:
                result = f"No NPC named '{target}' found."

        elif action == "social":
            from .world_state import get_npc_relationships
            agents = get_agents_in_location(self.db, location_id)
            npcs_here = [a for a in agents if a["id"] != "owl"]
            if npcs_here:
                result = "── Social Web ──\n\n"
                for npc in npcs_here[:5]:
                    rels = get_npc_relationships(self.db, npc["id"])
                    close = [r for r in rels if r["affinity"] > 0.6]
                    if close:
                        names = []
                        for r in close[:3]:
                            other_id = r["npc_b"] if r["npc_a"] == npc["id"] else r["npc_a"]
                            other = self.db.execute("SELECT name FROM agents WHERE id = ?", (other_id,)).fetchone()
                            if other:
                                names.append(other["name"])
                        result += f"{npc['name']}: close to {', '.join(names)}\n"
                    else:
                        result += f"{npc['name']}: keeps to themselves\n"
            else:
                result = "No one here to observe."

        else:
            result = describe_action(self.db, action, target)

        # Log the action
        log_event(self.db, "action", f"{action}" + (f" {target}" if target else ""),
                  agent_id="owl", location_id=location_id)

        self.last_action = action
        self.last_result = result
        return result

    def save(self, message: str = ""):
        """Save the world state."""
        path = save_snapshot(self.db)
        commit_msg = commit_snapshot(self.db, message)
        return path, commit_msg


def run_interactive():
    """Run an interactive session."""
    import sys

    print("=" * 60)
    print("  EMBODIED CREATIVE WORLD — Phase 2")
    print("=" * 60)
    print()

    agent = Agent()

    # Opening: OWL wakes up
    print("You open your eyes.")
    print()
    print(agent.perceive())
    print()
    print("── Commands: look, move <dir>, examine <thing>, talk <person>,")
    print("   wake, sleep, rest, advance, think, feel, status, map,")
    print("   observe, projects, create, work, impulse, memories,")
    print("   populate, save, quit ──")
    print()

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        parts = user_input.split(maxsplit=1)
        action = parts[0].lower()
        target = parts[1] if len(parts) > 1 else None

        if action in ("quit", "exit", "q"):
            agent.save("session end")
            print("World saved. Goodbye.")
            break
        elif action == "save":
            path, msg = agent.save("manual save")
            print(f"Saved: {path.name}")
            if msg:
                print(f"Committed: {msg}")
        else:
            result = agent.act(action, target)
            print()
            print(result)
