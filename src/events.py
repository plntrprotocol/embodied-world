"""
events.py — Emergent event generator.

Events arise from the interactions of systems, not from scripts.
The event generator reads the current world state and asks:
- What's unusual right now?
- What systems are interacting in interesting ways?
- What would a person in this world notice?

Event types:
- Weather events (storms, fog, heat waves)
- Social events (arguments, celebrations, arrivals, departures)
- Ecological events (fish runs, harvests, disease, growth)
- Economic events (market fluctuations, shortages, windfalls)
- Personal events (NPC milestones, OWL discoveries)

Design principles:
- Events are generated from system state, not random
- Events cascade — one event can trigger others
- Events have consequences that persist
- Events are narrated, not just logged
"""

import json
import random
import time
from typing import Optional

from .world_state import get_db, log_event, DB_PATH


# ── EVENT TEMPLATES ──

WEATHER_EVENTS = {
    "storm_approaching": {
        "condition": lambda w: w.get("wind_speed", 0) > 10 and w.get("humidity", 0) > 0.7,
        "probability": 0.3,
        "title": "Storm Approaching",
        "description": "The wind picks up. Dark clouds gather on the horizon. A storm is coming.",
        "consequences": {"dock_damage": 0.3, "fishing_halted": True},
    },
    "heavy_fog": {
        "condition": lambda w: w.get("condition") == "foggy" and w.get("humidity", 0) > 0.9,
        "probability": 0.2,
        "title": "Heavy Fog",
        "description": "The fog is so thick you can barely see across the harbor. The world has shrunk to arm's reach.",
        "consequences": {"travel_slow": True, "mood_effect": "melancholy"},
    },
    "clear_spell": {
        "condition": lambda w: w.get("condition") == "clear" and w.get("temperature", 10) > 15,
        "probability": 0.15,
        "title": "Clear Spell",
        "description": "The sky is clear and the air is warm. A rare perfect day on the coast.",
        "consequences": {"mood_effect": "content", "fishing_bonus": 0.2},
    },
    "cold_snap": {
        "condition": lambda w: w.get("temperature", 10) < 0,
        "probability": 0.4,
        "title": "Cold Snap",
        "description": "The cold bites. The creek has frozen. Breath hangs in the air.",
        "consequences": {"crop_damage": 0.2, "mood_effect": "cold"},
    },
}

SOCIAL_EVENTS = {
    "argument": {
        "condition": lambda db: _check_tension(db),
        "probability": 0.15,
        "title": "Argument in Town",
        "description_fn": lambda db: _generate_argument(db),
        "consequences": {"relationship_change": -0.1},
    },
    "celebration": {
        "condition": lambda db: _check_celebration(db),
        "probability": 0.1,
        "title": "Celebration",
        "description_fn": lambda db: _generate_celebration(db),
        "consequences": {"mood_effect": "content", "social_need": -0.2},
    },
    "newcomer": {
        "condition": lambda db: _check_newcomer(db),
        "probability": 0.05,
        "title": "Newcomer Arrives",
        "description": "A stranger arrives at the harbor. They're looking for work, or perhaps just a quiet place.",
        "consequences": {"new_npc": True},
    },
    "departure": {
        "condition": lambda db: _check_departure(db),
        "probability": 0.05,
        "title": "Someone Leaves",
        "description_fn": lambda db: _generate_departure(db),
        "consequences": {"npc_leaves": True, "mood_effect": "melancholy"},
    },
    "romance": {
        "condition": lambda db: _check_romance(db),
        "probability": 0.08,
        "title": "Romance Blossoms",
        "description_fn": lambda db: _generate_romance(db),
        "consequences": {"relationship_change": 0.2, "mood_effect": "content"},
    },
    "rivalry": {
        "condition": lambda db: _check_rivalry(db),
        "probability": 0.1,
        "title": "Rivalry Intensifies",
        "description_fn": lambda db: _generate_rivalry(db),
        "consequences": {"relationship_change": -0.15},
    },
}

ECOLOGY_EVENTS = {
    "fish_run": {
        "condition": lambda db: _check_fish_run(db),
        "probability": 0.3,
        "title": "Great Fish Run",
        "description": "The fish are running! The harbor is alive with activity. Every boat is out.",
        "consequences": {"fishing_bonus": 0.5, "market_fish": True},
    },
    "poor_harvest": {
        "condition": lambda db: _check_poor_harvest(db),
        "probability": 0.15,
        "title": "Poor Harvest",
        "description": "The crops are thin this year. The stores are running low. People worry.",
        "consequences": {"food_shortage": True, "mood_effect": "worried"},
    },
    "bountiful_harvest": {
        "condition": lambda db: _check_bountiful_harvest(db),
        "probability": 0.15,
        "title": "Bountiful Harvest",
        "description": "The fields are heavy with grain. The orchard bends with fruit. There will be plenty.",
        "consequences": {"food_surplus": True, "mood_effect": "grateful"},
    },
    "animal_sighting": {
        "condition": lambda db: _check_animal_sighting(db),
        "probability": 0.1,
        "title": "Rare Animal Sighting",
        "description_fn": lambda db: _generate_animal_sighting(db),
        "consequences": {"mood_effect": "excited"},
    },
    "disease": {
        "condition": lambda db: _check_disease(db),
        "probability": 0.05,
        "title": "Sickness in the Village",
        "description": "A sickness is going around. Several people are ill. Aisling the herbalist is busy.",
        "consequences": {"npc_sick": True, "mood_effect": "worried"},
    },
}

ECONOMIC_EVENTS = {
    "merchant_arrival": {
        "condition": lambda db: random.random() < 0.02,
        "probability": 0.5,
        "title": "Traveling Merchant",
        "description": "A traveling merchant arrives with exotic goods. The market buzzes with excitement.",
        "consequences": {"new_goods": True, "mood_effect": "excited"},
    },
    "shortage": {
        "condition": lambda db: _check_shortage(db),
        "probability": 0.2,
        "title": "Shortage",
        "description_fn": lambda db: _generate_shortage(db),
        "consequences": {"prices_up": True, "mood_effect": "worried"},
    },
    "windfall": {
        "condition": lambda db: _check_windfall(db),
        "probability": 0.1,
        "title": "Windfall",
        "description_fn": lambda db: _generate_windfall(db),
        "consequences": {"prices_down": True, "mood_effect": "content"},
    },
}


# ── CONDITION CHECKERS ──

def _check_tension(db):
    """Check if any NPC relationships are strained."""
    rows = db.execute(
        "SELECT COUNT(*) as cnt FROM npc_relationships WHERE affinity < 0.3 AND relationship NOT IN ('rival', 'enemy')"
    ).fetchone()
    return rows["cnt"] > 0 if rows else False

def _check_celebration(db):
    """Check if conditions are right for a celebration."""
    time_row = db.execute("SELECT * FROM weather WHERE id = 1").fetchone()
    if time_row and time_row["condition"] == "clear" and time_row["temperature"] > 12:
        # Check season — celebrations more likely in summer/autumn
        world_time = db.execute("SELECT * FROM world_time WHERE id = 1").fetchone()
        if world_time and world_time["season"] in ("summer", "autumn"):
            return True
    return False

def _check_newcomer(db):
    """Check if a newcomer should arrive."""
    npc_count = db.execute("SELECT COUNT(*) as cnt FROM agents WHERE type = 'npc'").fetchone()["cnt"]
    return npc_count < 250 and random.random() < 0.3

def _check_departure(db):
    """Check if someone should leave."""
    npc_count = db.execute("SELECT COUNT(*) as cnt FROM agents WHERE type = 'npc'").fetchone()["cnt"]
    return npc_count > 50 and random.random() < 0.2

def _check_romance(db):
    """Check if any NPCs should fall for each other."""
    rows = db.execute(
        "SELECT COUNT(*) as cnt FROM npc_relationships WHERE affinity > 0.6 AND relationship = 'acquaintance'"
    ).fetchone()
    return rows["cnt"] > 0 if rows else False

def _check_rivalry(db):
    """Check if any rivalries should intensify."""
    rows = db.execute(
        "SELECT COUNT(*) as cnt FROM npc_relationships WHERE relationship = 'rival' AND affinity < 0.4"
    ).fetchone()
    return rows["cnt"] > 0 if rows else False

def _check_fish_run(db):
    """Check if fish are running."""
    rows = db.execute("SELECT * FROM fish_stock WHERE abundance > 0.8").fetchall()
    return len(rows) > 0

def _check_poor_harvest(db):
    """Check if crops are failing."""
    plants = db.execute("SELECT * FROM plants WHERE plant_type IN ('collard_greens','sweet_potatoes','corn','tobacco') AND health < 0.4").fetchall()
    return len(plants) > 2

def _check_bountiful_harvest(db):
    """Check if crops are thriving."""
    plants = db.execute("SELECT * FROM plants WHERE plant_type IN ('collard_greens','sweet_potatoes','corn','tobacco') AND health > 0.8 AND stage = 'mature'").fetchall()
    return len(plants) > 2

def _check_animal_sighting(db):
    """Check for rare animal sightings."""
    animals = db.execute("SELECT * FROM animals WHERE animal_type IN ('bottlenose_dolphin','white_tailed_deer','red_fox','osprey') AND count > 0").fetchall()
    return len(animals) > 0 and random.random() < 0.3

def _check_disease(db):
    """Check if disease should spread."""
    animals = db.execute("SELECT * FROM animals WHERE health < 0.5 AND count > 5").fetchall()
    return len(animals) > 0

def _check_shortage(db):
    """Check if there's a food shortage."""
    fish = db.execute("SELECT AVG(abundance) as avg FROM fish_stock").fetchone()
    return fish and fish["avg"] < 0.3 if fish else False

def _check_windfall(db):
    """Check for economic windfall."""
    fish = db.execute("SELECT AVG(abundance) as avg FROM fish_stock").fetchone()
    return fish and fish["avg"] > 0.7 if fish else False


# ── EVENT GENERATORS ──

def _generate_argument(db):
    """Generate an argument between NPCs."""
    row = db.execute("""
        SELECT r.npc_a, r.npc_b, a1.name as name_a, a2.name as name_b
        FROM npc_relationships r
        JOIN agents a1 ON r.npc_a = a1.id
        JOIN agents a2 ON r.npc_b = a2.id
        WHERE r.affinity < 0.4
        ORDER BY r.affinity ASC
        LIMIT 1
    """).fetchone()
    if row:
        topics = ["money", "a boundary dispute", "a misunderstanding", "old gossip", "a broken promise"]
        topic = random.choice(topics)
        return f"{row['name_a']} and {row['name_b']} had a heated argument about {topic}. The whole town is talking."
    return "Tensions flare in the town square. Voices raised, then silence."

def _generate_celebration(db):
    """Generate a celebration event."""
    celebrations = [
        "The whole town gathers in the square for a spontaneous celebration. Someone brought out a fiddle.",
        "A wedding! The chapel is full. The whole village celebrates.",
        "The harvest feast. Long tables in the square, food and drink for everyone.",
        "A birthday. The tavern is full of laughter and song.",
        "The fishermen return with an extraordinary catch. The whole harbor celebrates.",
    ]
    return random.choice(celebrations)

def _generate_departure(db):
    """Generate a departure event."""
    row = db.execute("""
        SELECT a.name, a.properties FROM agents a
        WHERE a.type = 'npc' AND a.state = 'active'
        ORDER BY RANDOM() LIMIT 1
    """).fetchone()
    if row:
        reasons = ["to seek work in the city", "to join family elsewhere", "for reasons unknown", "after a disagreement", "to start a new life"]
        reason = random.choice(reasons)
        return f"{row['name']} has left the village, {reason}. Their absence is felt."
    return "Someone has left the village. Their cottage stands empty."

def _generate_romance(db):
    """Generate a romance event."""
    row = db.execute("""
        SELECT r.npc_a, r.npc_b, a1.name as name_a, a2.name as name_b
        FROM npc_relationships r
        JOIN agents a1 ON r.npc_a = a1.id
        JOIN agents a2 ON r.npc_b = a2.id
        WHERE r.affinity > 0.6 AND r.relationship = 'acquaintance'
        ORDER BY r.affinity DESC
        LIMIT 1
    """).fetchone()
    if row:
        signs = ["They were seen walking together on the beach.", "They can't stop talking to each other at the tavern.", "Someone saw them exchanging glances across the market.", "They find excuses to be in the same place."]
        return f"Something is growing between {row['name_a']} and {row['name_b']}. {random.choice(signs)}"
    return "A new romance is whispered about in the village."

def _generate_rivalry(db):
    """Generate a rivalry event."""
    row = db.execute("""
        SELECT r.npc_a, r.npc_b, a1.name as name_a, a2.name as name_b
        FROM npc_relationships r
        JOIN agents a1 ON r.npc_a = a1.id
        JOIN agents a2 ON r.npc_b = a2.id
        WHERE r.relationship = 'rival'
        ORDER BY r.affinity ASC
        LIMIT 1
    """).fetchone()
    if row:
        escalations = ["The rivalry has turned bitter. Insults were exchanged.", "Their competition is affecting the whole town.", "It's gotten personal now. Friends are being forced to choose sides.", "A public confrontation in the square. It was ugly."]
        return f"The rivalry between {row['name_a']} and {row['name_b']} intensifies. {random.choice(escalations)}"
    return "Old rivalries resurface. The village feels tense."

def _generate_animal_sighting(db):
    """Generate an animal sighting."""
    row = db.execute("SELECT * FROM animals WHERE animal_type IN ('bottlenose_dolphin','white_tailed_deer','red_fox','osprey') AND count > 0 ORDER BY RANDOM() LIMIT 1").fetchone()
    if row:
        sightings = {
            "bottlenose_dolphin": "Dolphins have been spotted cruising the point. Their backs break the surface in the golden light.",
            "white_tailed_deer": "A white-tailed deer stands at the forest edge at dawn, watching the town. It's beautiful.",
            "red_fox": "A red fox has been seen near the cottage garden again. Bold as brass.",
            "osprey": "An osprey circles overhead, hunting the creek. Its cry is sharp and wild.",
        }
        return sightings.get(row["animal_type"], f"A {row['animal_type']} has been spotted.")
    return "An unusual animal has been seen in the village."

def _generate_shortage(db):
    """Generate a shortage event."""
    shortages = [
        "Fish are scarce. The nets come up nearly empty. The fishermen worry.",
        "The store shelves are thin. Supplies from Morehead City haven't arrived.",
        "Firewood is running low. Nate works double time to keep up.",
        "The well is lower than usual. Water must be rationed.",
        "The shrimp run was poor this season. Everyone feels it.",
    ]
    return random.choice(shortages)

def _generate_windfall(db):
    """Generate a windfall event."""
    windfalls = [
        "An extraordinary catch! The shrimp boats can barely haul it in. Shrimp for everyone.",
        "A merchant paid handsomely for the village's pecans. Money flows.",
        "The pecan harvest is the best in years. Pies for everyone.",
        "A traveler left a generous donation at the chapel. The village prospers.",
        "The white shrimp run came early and strong. The whole harbor celebrates.",
    ]
    return random.choice(windfalls)


# ── MAIN EVENT GENERATION ──

def generate_events(db) -> list:
    """
    Generate emergent events based on current world state.
    Returns a list of generated events.
    """
    events = []
    now = time.time()

    weather = db.execute("SELECT * FROM weather WHERE id = 1").fetchone()
    world_time = db.execute("SELECT * FROM world_time WHERE id = 1").fetchone()

    # Check all event categories
    all_event_categories = [
        ("weather", WEATHER_EVENTS),
        ("social", SOCIAL_EVENTS),
        ("ecology", ECOLOGY_EVENTS),
        ("economic", ECONOMIC_EVENTS),
    ]

    for category, event_dict in all_event_categories:
        for event_key, event_template in event_dict.items():
            try:
                # Check condition
                condition = event_template["condition"]
                # Check if this is a pure-chance event (merchant_arrival)
                is_pure_chance = (event_key == "merchant_arrival")
                if is_pure_chance:
                    should_trigger = True  # Probability check happens below
                elif category == "weather":
                    should_trigger = condition(weather) if weather else False
                else:
                    should_trigger = condition(db)

                if should_trigger:
                    # Roll probability
                    prob = event_template.get("probability", 0.1)
                    if random.random() < prob:
                        # Generate event
                        desc_fn = event_template.get("description_fn")
                        if desc_fn:
                            description = desc_fn(db)
                        else:
                            description = event_template["description"]

                        event = {
                            "type": f"{category}_{event_key}",
                            "title": event_template["title"],
                            "description": description,
                            "consequences": event_template.get("consequences", {}),
                            "category": category,
                        }
                        events.append(event)

                        # Log the event
                        db.execute("""
                            INSERT INTO events (timestamp, agent_id, event_type, description, location_id, properties)
                            VALUES (NULL, 'event', ?, ?, NULL, ?)
                        """, (event["type"], description, json.dumps(event["consequences"])))

                        # Apply consequences
                        _apply_consequences(db, event["consequences"])

            except Exception as e:
                # Skip events that fail — don't let one bad event crash the system
                continue

    db.commit()
    return events


def _apply_consequences(db, consequences: dict):
    """Apply event consequences to the world state."""
    if not consequences:
        return

    if consequences.get("dock_damage"):
        # Damage the dock area
        dock_objs = db.execute("SELECT * FROM objects WHERE location_id = 'dock'").fetchall()
        for obj in dock_objs:
            db.execute("UPDATE objects SET state = 'damaged' WHERE id = ?", (obj["id"],))

    if consequences.get("crop_damage"):
        # Damage crops
        db.execute("UPDATE plants SET health = MAX(0.1, health - 0.2) WHERE plant_type IN ('collard_greens','sweet_potatoes','corn','tobacco')")

    if consequences.get("fishing_bonus"):
        # Boost fish stocks
        db.execute("UPDATE fish_stock SET abundance = LEAST(1.0, abundance + 0.1)")

    if consequences.get("relationship_change"):
        change = consequences["relationship_change"]
        db.execute("UPDATE npc_relationships SET affinity = MAX(0.0, MIN(1.0, affinity + ?))", (change,))

    if consequences.get("mood_effect"):
        # Could affect OWL's mood or general village mood
        pass  # Handled by psychology system

    if consequences.get("new_npc"):
        # Add a new NPC
        from .npc_generation import generate_npc
        used_names = set(r["name"].split()[0] for r in db.execute("SELECT name FROM agents WHERE type = 'npc'").fetchall())
        used_combos = set(r["name"] for r in db.execute("SELECT name FROM agents WHERE type = 'npc'").fetchall())
        npc_count = db.execute("SELECT COUNT(*) as cnt FROM agents WHERE type = 'npc'").fetchone()["cnt"]
        new_npc = generate_npc(npc_count + 1, used_names, used_combos)
        db.execute("""
            INSERT OR IGNORE INTO agents (id, name, type, location_id, state, properties, created_at, updated_at)
            VALUES (?, ?, 'npc', ?, 'active', ?, ?, ?)
        """, (new_npc["id"], new_npc["name"], new_npc["work_locations"][0],
              json.dumps(new_npc["properties"]), time.time(), time.time()))

    db.commit()


def get_recent_events(db, limit: int = 10) -> list:
    """Get recent events."""
    rows = db.execute(
        "SELECT * FROM events WHERE agent_id = 'event' ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    return [dict(r) for r in rows]
