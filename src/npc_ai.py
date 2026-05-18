"""
npc_ai.py — Advanced NPC AI: long-term goals, memory, adaptation.

NPCs are no longer just schedule-following agents. They have:
- Long-term goals they pursue across multiple sessions
- Memory of interactions with OWL and other NPCs
- Adaptation to changing world conditions
- Personality-driven decision making
- The ability to initiate actions, not just react

Design principles:
- NPCs pursue goals that make sense for their personality
- Memory shapes future behavior
- NPCs adapt to world changes (weather, economy, relationships)
- NPC actions create emergent stories
- NPCs can surprise the player
"""

import json
import random
import time
from typing import Optional

from .world_state import get_db, log_event, get_npc_schedule, get_npc_relationships, DB_PATH


# ── NPC GOAL TYPES — what NPCs want ──

GOAL_TYPES = {
    "career": {
        "description": "Advance in their trade",
        "actions": ["practice_skill", "seek_apprentice", "take_risk", "save_money"],
        "occupations": ["fisherman", "farmer", "craftsman", "merchant", "woodcutter", "shepherd"],
    },
    "family": {
        "description": "Start or grow a family",
        "actions": ["courting", "marry", "have_child", "care_for_elder"],
        "occupations": ["all"],
    },
    "wealth": {
        "description": "Accumulate wealth",
        "actions": ["trade", "invest", "save", "seek_opportunity"],
        "occupations": ["merchant", "fisherman", "craftsman"],
    },
    "reputation": {
        "description": "Be respected in the community",
        "actions": ["help_neighbor", "donate", "organize_event", "mentor"],
        "occupations": ["all"],
    },
    "knowledge": {
        "description": "Learn and understand",
        "actions": ["study", "travel", "experiment", "teach"],
        "occupations": ["herbalist", "clergyman", "lighthouse_keeper"],
    },
    "peace": {
        "description": "Live a quiet, peaceful life",
        "actions": ["garden", "walk", "read", "rest"],
        "occupations": ["all"],
    },
    "adventure": {
        "description": "See the world beyond the village",
        "actions": ["plan_departure", "explore", "save_for_journey", "talk_to_travelers"],
        "occupations": ["sailor", "young_fisherman", "apprentice"],
    },
    "craft_mastery": {
        "description": "Master their craft",
        "actions": ["practice", "create_masterpiece", "teach_apprentice", "innovate"],
        "occupations": ["craftsman", "seamstress", "carpenter", "baker"],
    },
}


class NPCMind:
    """Represents an NPC's inner life: goals, memories, personality."""

    def __init__(self, npc_id: str, db):
        self.npc_id = npc_id
        self.db = db
        self.npc = db.execute("SELECT * FROM agents WHERE id = ?", (npc_id,)).fetchone()
        self.properties = {}
        if self.npc and self.npc["properties"]:
            try:
                self.properties = json.loads(self.npc["properties"])
            except (json.JSONDecodeError, TypeError):
                self.properties = {}

        # Load or initialize memory
        self.memories = self.properties.get("memories", [])
        self.goals = self.properties.get("goals", [])
        self.current_mood = self.properties.get("mood", "content")

    def generate_goals(self):
        """Generate goals based on personality and occupation."""
        occupation = self.properties.get("occupation", "")
        traits = self.properties.get("traits", [])
        age = self.properties.get("age", 30)

        goals = []

        # Age-based goals
        if age < 25:
            goals.append(random.choice([GOAL_TYPES["adventure"], GOAL_TYPES["career"], GOAL_TYPES["family"]]))
        elif age < 50:
            goals.append(random.choice([GOAL_TYPES["career"], GOAL_TYPES["family"], GOAL_TYPES["wealth"]]))
        else:
            goals.append(random.choice([GOAL_TYPES["reputation"], GOAL_TYPES["peace"], GOAL_TYPES["knowledge"]]))

        # Personality-based goals
        if "ambitious" in traits or "proud" in traits:
            goals.append(GOAL_TYPES["reputation"])
        if "curious" in traits or "dreamy" in traits:
            goals.append(GOAL_TYPES["knowledge"])
        if "generous" in traits or "kind" in traits:
            goals.append(GOAL_TYPES["peace"])
        if "bold" in traits:
            goals.append(GOAL_TYPES["adventure"])

        # Occupation-based goals
        if occupation in ["craftsman", "seamstress", "baker"]:
            goals.append(GOAL_TYPES["craft_mastery"])
        if occupation in ["fisherman", "farmer", "merchant"]:
            goals.append(GOAL_TYPES["wealth"])

        self.goals = list(set(g["description"] for g in goals))[:3]  # Max 3 goals
        return self.goals

    def add_memory(self, content: str, importance: float = 0.5):
        """Add a memory."""
        memory = {
            "content": content,
            "importance": importance,
            "timestamp": time.time(),
        }
        self.memories.insert(0, memory)
        # Keep last 20 memories
        self.memories = self.memories[:20]

    def think(self) -> Optional[str]:
        """
        NPC thinks about what to do next.
        Returns an action description or None.
        """
        if not self.goals:
            self.generate_goals()

        # Base action on goals and current state
        action = None

        # Check relationships
        relationships = get_npc_relationships(self.db, self.npc_id)
        close_friends = [r for r in relationships if r["affinity"] > 0.6]
        rivals = [r for r in relationships if r["affinity"] < 0.3]

        # Goal-driven behavior
        if self.goals:
            current_goal = random.choice(self.goals)

            if "family" in current_goal and close_friends:
                friend = random.choice(close_friends)
                other_id = friend["npc_b"] if friend["npc_a"] == self.npc_id else friend["npc_a"]
                other = self.db.execute("SELECT name FROM agents WHERE id = ?", (other_id,)).fetchone()
                if other:
                    action = f"{self.npc['name']} spends time with {other['name']}, deepening their bond."
                    self.add_memory(f"Spent time with {other['name']}")

            elif "wealth" in current_goal:
                action = f"{self.npc['name']} works extra hours, focused on earning."

            elif "reputation" in current_goal:
                action = f"{self.npc['name']} helps a neighbor with a difficult task."

            elif "knowledge" in current_goal:
                action = f"{self.npc['name']} studies quietly, lost in thought."

            elif "adventure" in current_goal:
                action = f"{self.npc['name']} stares at the sea, dreaming of distant shores."

            elif "craft_mastery" in current_goal:
                action = f"{self.npc['name']} works on a new creation, pushing the boundaries of their craft."

            elif rivals:
                rival = random.choice(rivals)
                other_id = rival["npc_b"] if rival["npc_a"] == self.npc_id else rival["npc_a"]
                other = self.db.execute("SELECT name FROM agents WHERE id = ?", (other_id,)).fetchone()
                if other:
                    action = f"{self.npc['name']} avoids {other['name']}. Old tensions linger."

        return action

    def save(self):
        """Save the NPC's mental state back to the database."""
        self.properties["memories"] = self.memories
        self.properties["goals"] = self.goals
        self.properties["mood"] = self.current_mood

        self.db.execute(
            "UPDATE agents SET properties = ?, updated_at = ? WHERE id = ?",
            (json.dumps(self.properties), time.time(), self.npc_id)
        )
        self.db.commit()


def init_npc_ai(db):
    """Initialize NPC AI tables and generate initial goals for all NPCs."""
    db.executescript("""
        CREATE TABLE IF NOT EXISTS npc_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            npc_id TEXT NOT NULL REFERENCES agents(id),
            timestamp REAL NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT NOT NULL,
            location_id TEXT DEFAULT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_npc_actions_npc ON npc_actions(npc_id);
        CREATE INDEX IF NOT EXISTS idx_npc_actions_time ON npc_actions(timestamp);
    """)
    db.commit()

    # Generate goals for all NPCs that don't have them
    npcs = db.execute("SELECT * FROM agents WHERE type = 'npc'").fetchall()
    for npc in npcs:
        try:
            props = json.loads(npc["properties"]) if npc["properties"] else {}
        except (json.JSONDecodeError, TypeError):
            props = {}

        if not props.get("goals"):
            mind = NPCMind(npc["id"], db)
            mind.generate_goals()
            mind.save()


def run_npc_ai_tick(db, hour: int) -> list:
    """
    Run AI for all NPCs. Each NPC thinks and may take an action.
    Returns a list of notable NPC actions.
    """
    actions = []

    # Only run AI during waking hours (6-22)
    if hour < 6 or hour > 22:
        return actions

    npcs = db.execute("SELECT * FROM agents WHERE type = 'npc' AND state = 'active'").fetchall()

    # Not every NPC acts every tick — stochastic
    for npc in npcs:
        if random.random() > 0.15:  # 15% chance per NPC per tick
            continue

        try:
            mind = NPCMind(npc["id"], db)
            action = mind.think()

            if action:
                actions.append({
                    "npc_id": npc["id"],
                    "npc_name": npc["name"],
                    "action": action,
                    "location_id": npc["location_id"],
                })

                # Log the action
                db.execute("""
                    INSERT INTO npc_actions (npc_id, timestamp, action_type, description, location_id)
                    VALUES (?, ?, 'ai_action', ?, ?)
                """, (npc["id"], time.time(), action, npc["location_id"]))

                mind.save()
        except Exception:
            continue  # Skip NPCs that fail

    db.commit()
    return actions


def get_npc_story(db, npc_id: str) -> dict:
    """Get the story of an NPC: their goals, memories, and recent actions."""
    npc = db.execute("SELECT * FROM agents WHERE id = ?", (npc_id,)).fetchone()
    if not npc:
        return {}

    try:
        props = json.loads(npc["properties"]) if npc["properties"] else {}
    except (json.JSONDecodeError, TypeError):
        props = {}

    recent_actions = db.execute("""
        SELECT * FROM npc_actions WHERE npc_id = ?
        ORDER BY timestamp DESC LIMIT 10
    """, (npc_id,)).fetchall()

    relationships = get_npc_relationships(db, npc_id)

    return {
        "name": npc["name"],
        "occupation": props.get("occupation", ""),
        "personality": props.get("personality", ""),
        "goals": props.get("goals", []),
        "memories": props.get("memories", [])[:5],
        "recent_actions": [dict(a) for a in recent_actions],
        "relationships": [
            {
                "other": r["npc_b"] if r["npc_a"] == npc_id else r["npc_a"],
                "type": r["relationship"],
                "affinity": r["affinity"],
            }
            for r in relationships[:10]
        ],
    }
