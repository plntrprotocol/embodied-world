"""
ecology.py — Living ecology system for the village.

Plants grow, animals move, fish run in seasons, things decay and grow.
The ecology runs on simulation ticks and creates emergent environmental
storytelling: a garden gone to seed, a new bird's nest, a dead tree
falling across a trail.

Design principles:
- Everything has a lifecycle: seed → growth → maturity → decay → death
- Seasons drive the ecology
- Player actions affect the ecology (tending gardens, cutting trees)
- Environmental clues tell stories without words
"""

import json
import random
import time
from typing import Optional

from .world_state import get_db, log_event, DB_PATH


# ── PLANT TYPES ──

PLANT_TYPES = {
    # Garden herbs
    "rosemary": {"type": "herb", "growth_rate": 0.02, "max_age": 365, "season": "spring", "harvestable": True, "smell": "pungent, warm"},
    "thyme": {"type": "herb", "growth_rate": 0.025, "max_age": 300, "season": "spring", "harvestable": True, "smell": "earthy, sharp"},
    "chives": {"type": "herb", "growth_rate": 0.03, "max_age": 200, "season": "spring", "harvestable": True, "smell": "onion, fresh"},
    "hot_peppers": {"type": "herb", "growth_rate": 0.025, "max_age": 180, "season": "summer", "harvestable": True, "smell": "sharp, burning"},
    "mint": {"type": "herb", "growth_rate": 0.04, "max_age": 250, "season": "spring", "harvestable": True, "smell": "cool, sharp"},

    # Crops — NC coastal plain
    "collard_greens": {"type": "crop", "growth_rate": 0.03, "max_age": 120, "season": "spring", "harvestable": True},
    "sweet_potatoes": {"type": "crop", "growth_rate": 0.02, "max_age": 150, "season": "summer", "harvestable": True},
    "corn": {"type": "crop", "growth_rate": 0.035, "max_age": 100, "season": "summer", "harvestable": True},
    "tobacco": {"type": "crop", "growth_rate": 0.015, "max_age": 120, "season": "summer", "harvestable": True},
    "pecans": {"type": "tree", "growth_rate": 0.005, "max_age": 3650, "season": "autumn", "harvestable": True},

    # Native coastal plants
    "sea_oats": {"type": "grass", "growth_rate": 0.02, "max_age": 300, "season": "summer", "harvestable": False, "color": "golden"},
    "spanish_moss": {"type": "epiphyte", "growth_rate": 0.01, "max_age": 1000, "season": "all", "harvestable": False},
    "saw_palmetto": {"type": "shrub", "growth_rate": 0.008, "max_age": 2000, "season": "all", "harvestable": False},
    "yaupon_holly": {"type": "shrub", "growth_rate": 0.01, "max_age": 800, "season": "all", "harvestable": True},
    "resurrection_fern": {"type": "fern", "growth_rate": 0.01, "max_age": 500, "season": "all", "harvestable": False},
    "seaweed": {"type": "seaweed", "growth_rate": 0.03, "max_age": 100, "season": "all", "harvestable": True},
    "beautyberry": {"type": "shrub", "growth_rate": 0.015, "max_age": 400, "season": "summer", "harvestable": False, "color": "purple"},
    "honeysuckle": {"type": "vine", "growth_rate": 0.02, "max_age": 300, "season": "spring", "harvestable": False},
    "live_oak": {"type": "tree", "growth_rate": 0.003, "max_age": 5000, "season": "all", "harvestable": False},
    "longleaf_pine": {"type": "tree", "growth_rate": 0.004, "max_age": 4000, "season": "all", "harvestable": False},
    "cypress": {"type": "tree", "growth_rate": 0.005, "max_age": 3000, "season": "all", "harvestable": False},
}

# ── ANIMAL TYPES ──

ANIMAL_TYPES = {
    "cattle": {"habitat": "pasture", "count": (8, 25), "season": "all", "sound": "lowing", "behavior": "grazing"},
    "chicken": {"habitat": "farmhouse", "count": (5, 15), "season": "all", "sound": "clucking", "behavior": "pecking"},
    "brown_pelican": {"habitat": "harbor", "count": (5, 30), "season": "all", "sound": "silent", "behavior": "diving"},
    "blue_crab": {"habitat": "tide_pools", "count": (10, 40), "season": "summer", "sound": "scratching", "behavior": "scuttling"},
    "bottlenose_dolphin": {"habitat": "rocky_point", "count": (0, 6), "season": "summer", "sound": "blowing", "behavior": "cruising"},
    "raccoon": {"habitat": "forest_deep", "count": (2, 8), "season": "all", "sound": "chittering", "behavior": "foraging"},
    "white_tailed_deer": {"habitat": "forest_clearing", "count": (2, 8), "season": "all", "sound": "silence", "behavior": "grazing"},
    "cottontail_rabbit": {"habitat": "farm_edge", "count": (5, 20), "season": "all", "sound": "silence", "behavior": "hopping"},
    "great_horned_owl": {"habitat": "old_oak", "count": (1, 3), "season": "all", "sound": "hooting", "behavior": "watching"},
    "osprey": {"habitat": "creek", "count": (1, 4), "season": "spring", "sound": "whistling", "behavior": "diving"},
    "red_fox": {"habitat": "forest_edge", "count": (1, 3), "season": "all", "sound": "barking", "behavior": "hunting"},
    "dog": {"habitat": "farmhouse", "count": (1, 3), "season": "all", "sound": "barking", "behavior": "patrolling"},
    "cat": {"habitat": "general_store", "count": (1, 3), "season": "all", "sound": "purring", "behavior": "sleeping"},
    "tree_frog": {"habitat": "creek", "count": (20, 100), "season": "summer", "sound": "peeping", "behavior": "singing"},
    "wild_turkey": {"habitat": "forest_trail", "count": (3, 12), "season": "all", "sound": "gobbling", "behavior": "strutting"},
}

# ── FISH TYPES ──

FISH_TYPES = {
    "white_shrimp": {"season": "autumn", "abundance": (0.5, 1.0), "location": "harbor", "value": "high"},
    "brown_shrimp": {"season": "summer", "abundance": (0.4, 0.9), "location": "harbor", "value": "high"},
    "blue_crab_fish": {"season": "summer", "abundance": (0.4, 0.8), "location": "tide_pools", "value": "medium"},
    "red_drum": {"season": "autumn", "abundance": (0.3, 0.7), "location": "harbor", "value": "high"},
    "flounder": {"season": "spring", "abundance": (0.3, 0.6), "location": "harbor", "value": "medium"},
    "speckled_trout": {"season": "spring", "abundance": (0.3, 0.7), "location": "creek", "value": "medium"},
    "channel_bass": {"season": "summer", "abundance": (0.2, 0.5), "location": "creek", "value": "medium"},
    "spot": {"season": "all", "abundance": (0.4, 0.8), "location": "dock", "value": "low"},
}


def init_ecology(db) -> None:
    """Initialize the ecology tables and seed initial state."""
    db.executescript("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_type TEXT NOT NULL,
            location_id TEXT NOT NULL,
            age_days REAL DEFAULT 0,
            health REAL DEFAULT 1.0,
            stage TEXT DEFAULT 'seedling',
            tended INTEGER DEFAULT 0,
            properties TEXT DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_type TEXT NOT NULL,
            location_id TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            health REAL DEFAULT 1.0,
            properties TEXT DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fish_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fish_type TEXT NOT NULL,
            location_id TEXT NOT NULL,
            abundance REAL DEFAULT 0.5,
            properties TEXT DEFAULT '{}',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ecology_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            location_id TEXT DEFAULT NULL,
            properties TEXT DEFAULT '{}'
        );

        CREATE INDEX IF NOT EXISTS idx_plants_location ON plants(location_id);
        CREATE INDEX IF NOT EXISTS idx_animals_location ON animals(location_id);
        CREATE INDEX IF NOT EXISTS idx_fish_location ON fish_stock(location_id);
    """)

    now = time.time()

    # Seed plants in appropriate locations
    plant_seeds = [
        # Garden
        ("rosemary", "cottage_garden"), ("thyme", "cottage_garden"), ("chives", "cottage_garden"),
        ("hot_peppers", "cottage_garden"), ("mint", "cottage_garden"),
        # Farm
        ("collard_greens", "farm_edge"), ("sweet_potatoes", "farm_edge"), ("corn", "farm_edge"),
        ("tobacco", "farm_edge"),
        ("pecans", "orchard"),
        # Native/wild
        ("sea_oats", "hillside_path"), ("sea_oats", "beach"),
        ("spanish_moss", "old_oak"), ("spanish_moss", "forest_edge"),
        ("saw_palmetto", "forest_trail"), ("saw_palmetto", "forest_edge"),
        ("yaupon_holly", "forest_edge"),
        ("resurrection_fern", "old_oak"), ("resurrection_fern", "forest_clearing"),
        ("seaweed", "beach"), ("seaweed", "tide_pools"),
        ("beautyberry", "forest_clearing"), ("honeysuckle", "forest_trail"),
        ("live_oak", "old_oak"), ("longleaf_pine", "forest_deep"),
        ("cypress", "creek"),
    ]

    for plant_type, location in plant_seeds:
        db.execute("""
            INSERT OR IGNORE INTO plants (plant_type, location_id, age_days, health, stage, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (plant_type, location, random.randint(10, 60), random.uniform(0.6, 1.0),
              random.choice(["growing", "mature"]), now, now))

    # Seed animals
    animal_seeds = [
        ("cattle", "pasture", random.randint(8, 20)),
        ("chicken", "farmhouse", random.randint(5, 12)),
        ("brown_pelican", "harbor", random.randint(10, 30)),
        ("brown_pelican", "dock", random.randint(3, 10)),
        ("blue_crab", "tide_pools", random.randint(10, 30)),
        ("raccoon", "forest_deep", random.randint(2, 6)),
        ("white_tailed_deer", "forest_clearing", random.randint(2, 5)),
        ("cottontail_rabbit", "farm_edge", random.randint(5, 15)),
        ("great_horned_owl", "old_oak", random.randint(1, 2)),
        ("osprey", "creek", random.randint(1, 3)),
        ("red_fox", "forest_edge", random.randint(1, 3)),
        ("dog", "farmhouse", random.randint(1, 2)),
        ("cat", "general_store", random.randint(1, 2)),
        ("tree_frog", "creek", random.randint(30, 80)),
        ("wild_turkey", "forest_trail", random.randint(3, 8)),
        ("bottlenose_dolphin", "rocky_point", random.randint(0, 3)),
    ]

    for animal_type, location, count in animal_seeds:
        db.execute("""
            INSERT OR IGNORE INTO animals (animal_type, location_id, count, health, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (animal_type, location, count, random.uniform(0.7, 1.0), now, now))

    # Seed fish stocks
    for fish_type, data in FISH_TYPES.items():
        db.execute("""
            INSERT OR IGNORE INTO fish_stock (fish_type, location_id, abundance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (fish_type, data["location"], random.uniform(*data["abundance"]), now, now))

    db.commit()


def get_plant_stage(age_days: float, growth_rate: float, max_age: float) -> str:
    """Determine plant stage based on age and growth."""
    progress = age_days / max_age
    if progress < 0.1:
        return "seedling"
    elif progress < 0.3:
        return "growing"
    elif progress < 0.7:
        return "mature"
    elif progress < 0.9:
        return "flowering"
    elif progress < 1.0:
        return "fruiting"
    else:
        return "dying"


def describe_plant(plant: dict) -> str:
    """Generate a literary description of a plant."""
    ptype = plant["plant_type"]
    stage = plant["stage"]
    health = plant["health"]
    tended = plant.get("tended", 0)

    descriptions = {
        "seedling": {
            "rosemary": "A tiny rosemary seedling, just a few leaves above the soil.",
            "thyme": "A small thyme plant, barely established.",
            "chives": "Thin chive shoots, bright green against the dark soil.",
            "collard_greens": "Young collard green seedlings, their leaves just unfurling.",
            "sweet_potatoes": "Sweet potato vines spreading across the bed, reaching for light.",
            "default": "A small seedling, just beginning.",
        },
        "growing": {
            "rosemary": "Rosemary growing well, its woody stems thickening.",
            "thyme": "Thyme spreading across the bed, healthy and strong.",
            "chives": "Chives growing in thick clumps, ready for a first harvest.",
            "collard_greens": "Collard greens growing large and dark green, ready for harvest.",
            "default": "Growing steadily, healthy and green.",
        },
        "mature": {
            "rosemary": "A mature rosemary bush, fragrant and full.",
            "thyme": "Thyme in full spread, a carpet of tiny leaves.",
            "lavender": "Lavender in full bloom, a haze of purple and scent.",
            "pecans": "A pecan tree heavy with developing nuts.",
            "default": "Fully grown and healthy.",
        },
        "flowering": {
            "rosemary": "Rosemary in bloom, tiny blue bees visiting the flowers.",
            "lavender": "Lavender flowering, the air thick with its scent.",
            "sea_thrift": "Sea thrift in pink bloom along the path.",
            "campion": "White campion flowers glowing in the shade.",
            "elderflower": "Elderflower in bloom, creamy white clusters.",
            "default": "In full flower, beautiful.",
        },
        "fruiting": {
            "pecans": "The pecan tree is heavy with ripening nuts.",
            "sweet_potatoes": "Sweet potato vines thick in the ground, nearly ready for digging.",
            "default": "Bearing fruit.",
        },
        "dying": {
            "default": "Past its prime, beginning to brown and wither.",
        },
    }

    stage_descs = descriptions.get(stage, {})
    desc = stage_descs.get(ptype, stage_descs.get("default", f"A {ptype} in {stage} stage."))

    if health < 0.4:
        desc += " It looks unhealthy — perhaps it needs attention."
    elif tended:
        desc += " It's been well tended."

    return desc


def update_ecology(db, season: str, days_passed: float = 1.0) -> list:
    """
    Update the ecology for a simulation tick.
    Returns a list of notable events.
    """
    events = []
    now = time.time()

    # ── UPDATE PLANTS ──
    plants = db.execute("SELECT * FROM plants").fetchall()
    for plant in plants:
        ptype = plant["plant_type"]
        plant_info = PLANT_TYPES.get(ptype, {})
        growth_rate = plant_info.get("growth_rate", 0.01)
        max_age = plant_info.get("max_age", 365)

        # Season modifier
        season_mod = 1.0
        plant_season = plant_info.get("season", "spring")
        if season == plant_season:
            season_mod = 1.5
        elif season == "winter":
            season_mod = 0.2

        # Growth
        new_age = plant["age_days"] + days_passed * season_mod
        new_stage = get_plant_stage(new_age, growth_rate, max_age)

        # Health decay/growth
        health = plant["health"]
        if plant["tended"] > 0:
            health = min(1.0, health + 0.01 * days_passed)
        else:
            health = max(0.0, health - 0.002 * days_passed)

        # Water needs (simplified)
        if season == "summer":
            health = max(0.0, health - 0.005 * days_passed)

        db.execute("""
            UPDATE plants SET age_days = ?, stage = ?, health = ?, updated_at = ?
            WHERE id = ?
        """, (new_age, new_stage, round(health, 2), now, plant["id"]))

        # Check for notable changes
        if new_stage != plant["stage"]:
            if new_stage == "flowering":
                events.append({
                    "type": "plant_flowering",
                    "description": f"The {ptype} in {plant['location_id']} is flowering.",
                    "location_id": plant["location_id"],
                })
            elif new_stage == "dying":
                events.append({
                    "type": "plant_dying",
                    "description": f"The {ptype} in {plant['location_id']} is dying.",
                    "location_id": plant["location_id"],
                })

    # ── UPDATE ANIMALS ──
    animals = db.execute("SELECT * FROM animals").fetchall()
    for animal in animals:
        atype = animal["animal_type"]
        animal_info = ANIMAL_TYPES.get(atype, {})

        # Seasonal changes
        animal_season = animal_info.get("season", "all")
        count = animal["count"]

        if season == "spring" and animal_season in ("all", "spring"):
            # Breeding season
            count = int(count * random.uniform(1.0, 1.15))
        elif season == "winter":
            # Some animals leave or die
            if animal_season != "all":
                count = int(count * random.uniform(0.7, 0.95))

        # Random fluctuation
        count = max(0, count + random.randint(-1, 1))

        # Health
        health = animal["health"]
        if season == "winter":
            health = max(0.3, health - 0.01)
        else:
            health = min(1.0, health + 0.005)

        db.execute("""
            UPDATE animals SET count = ?, health = ?, updated_at = ?
            WHERE id = ?
        """, (count, round(health, 2), now, animal["id"]))

    # ── UPDATE FISH ──
    fish_stocks = db.execute("SELECT * FROM fish_stock").fetchall()
    for fish in fish_stocks:
        ftype = fish["fish_type"]
        fish_info = FISH_TYPES.get(ftype, {})

        abundance = fish["abundance"]
        fish_season = fish_info.get("season", "all")

        if season == fish_season:
            abundance = min(1.0, abundance + random.uniform(0.01, 0.05))
        else:
            abundance = max(0.05, abundance - random.uniform(0.01, 0.03))

        # Random fluctuation
        abundance = max(0.05, min(1.0, abundance + random.uniform(-0.02, 0.02)))

        db.execute("""
            UPDATE fish_stock SET abundance = ?, updated_at = ?
            WHERE id = ?
        """, (round(abundance, 2), now, fish["id"]))

        # Notable fish runs
        if abundance > 0.8 and fish["abundance"] <= 0.8:
            events.append({
                "type": "fish_run",
                "description": f"The {ftype} are running! Good fishing.",
                "location_id": fish["location_id"],
            })

    # Log events
    for event in events:
        db.execute("""
            INSERT INTO ecology_events (timestamp, event_type, description, location_id, properties)
            VALUES (?, ?, ?, ?, ?)
        """, (now, event["type"], event["description"], event["location_id"], "{}"))

    db.commit()
    return events


def get_location_ecology(db, location_id: str) -> dict:
    """Get the ecology state for a location."""
    plants = db.execute("SELECT * FROM plants WHERE location_id = ?", (location_id,)).fetchall()
    animals = db.execute("SELECT * FROM animals WHERE location_id = ?", (location_id,)).fetchall()
    fish = db.execute("SELECT * FROM fish_stock WHERE location_id = ?", (location_id,)).fetchall()

    return {
        "plants": [dict(p) for p in plants],
        "animals": [dict(a) for a in animals],
        "fish": [dict(f) for f in fish],
    }


def describe_location_ecology(db, location_id: str) -> list:
    """Generate literary descriptions of ecology in a location.
    Returns a list of description strings."""
    eco = get_location_ecology(db, location_id)
    parts = []

    # Plants
    for plant in eco["plants"]:
        if plant["stage"] in ("flowering", "fruiting", "mature"):
            parts.append(describe_plant(plant))

    # Animals
    for animal in eco["animals"]:
        count = animal["count"]
        atype = animal["animal_type"]
        if count > 0:
            if atype == "brown_pelican":
                parts.append(f"Brown pelicans line the dock, {count} or more, waiting for scraps.")
            elif atype == "cattle":
                parts.append(f"{count} Black Angus cattle dot the pasture, grazing.")
            elif atype == "chicken":
                parts.append(f"A few chickens peck in the yard.")
            elif atype == "blue_crab":
                parts.append(f"Blue crabs scuttle between the rocks.")
            elif atype == "white_tailed_deer":
                parts.append(f"A white-tailed deer watches from the tree line, ears twitching.")
            elif atype == "cottontail_rabbit":
                parts.append(f"A rabbit freezes, then bolts into the grass.")
            elif atype == "great_horned_owl":
                parts.append(f"A great horned owl watches silently from the live oak.")
            elif atype == "osprey":
                parts.append(f"An osprey circles overhead, hunting.")
            elif atype == "red_fox":
                parts.append(f"A red fox slips between the trees, unseen.")
            elif atype == "bottlenose_dolphin":
                parts.append(f"Dolphins cruise the point, their backs breaking the surface.")
            elif atype == "raccoon":
                parts.append(f"A raccoon watches from the shadows, clever eyes.")
            elif atype == "tree_frog":
                parts.append(f"Tree frogs sing their peeping chorus.")
            elif atype == "wild_turkey":
                parts.append(f"A wild turkey struts through the underbrush.")
            elif atype == "dog":
                parts.append(f"A dog trots past, tail wagging.")
            elif atype == "cat":
                parts.append(f"A cat sleeps on the store counter, unbothered.")

    # Fish
    for fish in eco["fish"]:
        if fish["abundance"] > 0.6:
            parts.append(f"The water is alive with {fish['fish_type']}.")

    return parts
