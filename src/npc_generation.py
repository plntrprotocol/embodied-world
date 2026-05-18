"""
npc_generation.py — Procedural NPC generation for the village.

Expands the 15 hand-crafted key characters to a full population of ~200
procedurally generated NPCs, each with:
- A name (culturally consistent — coastal NC village)
- Age, gender, occupation
- Personality traits (from a trait system)
- A home location
- Daily routine
- Relationships with nearby NPCs

The 15 key NPCs are preserved as-is. The remaining ~185 are generated
to feel like real people who belong in this place.
"""

import json
import random
import time
from typing import Optional

# ── NAME POOLS — Coastal North Carolina ──
# Mix of Southern, military, and coastal NC heritage names

FIRST_NAMES_MALE = [
    "James", "John", "Robert", "William", "David", "Charles", "Thomas", "Michael",
    "Christopher", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul", "Steven",
    "Andrew", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward", "Ronald",
    "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
    "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel",
    "Raymond", "Gregory", "Frank", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
    "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary",
    "Peter", "Kyle", "Noah", "Ethan", "Jeremy", "Walter", "Christian", "Keith",
    "Roger", "Terry", "Austin", "Sean", "Gerald", "Carl", "Harold", "Dylan",
    "Arthur", "Lawrence", "Jordan", "Jesse", "Bryan", "Billy", "Bruce", "Gabriel",
    "Joe", "Logan", "Albert", "Willie", "Alan", "Eugene", "Russell", "Vincent",
    "Philip", "Bobby", "Johnny", "Ralph", "Roy", "Louis", "Howard", "Caleb",
    "Dale", "Nate", "Owen", "Finley", "Crawford", "Patrick", "Wayne", "Glen",
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica",
    "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley",
    "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa",
    "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy",
    "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen",
    "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Catherine",
    "Maria", "Heather", "Diane", "Ruth", "Julie", "Olivia", "Joyce", "Virginia",
    "Victoria", "Kelly", "Lauren", "Christina", "Joan", "Evelyn", "Judith", "Megan",
    "Andrea", "Cheryl", "Hannah", "Jacqueline", "Martha", "Gloria", "Teresa", "Ann",
    "Sara", "Madison", "Frances", "Kathryn", "Janice", "Jean", "Abigail", "Alice",
    "Judy", "Sophia", "Grace", "Denise", "Amber", "Doris", "Marilyn", "Danielle",
    "Beverly", "Isabella", "Theresa", "Diana", "Natalie", "Brittany", "Charlotte", "Marie",
    "Kayla", "Alexis", "Lori", "Asha", "Greta", "Marty", "Mary Beth", "Ellen",
    "Bridget", "Sarah", "Martha", "Aisling", "Cora", "Hazel", "Iris", "Pearl",
]

SURNAMES = [
    "Brennan", "Henderson", "Doyle", "Moss", "Bowen", "Smith", "Johnson", "Williams",
    "Brown", "Jones", "Miller", "Davis", "Wilson", "Moore", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez",
    "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen",
    "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green",
    "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts",
    "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart",
    "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy",
    "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres",
    "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders",
    "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
    "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler",
    "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", "Russell", "Griffin", "Diaz",
    "Hayes", "Myers", "Ford", "Hamilton", "Graham", "Sullivan", "Wallace", "Woods",
    "Cole", "West", "Jordan", "Owens", "Reynolds", "Fisher", "Ellis", "Harrison",
    "Gibson", "Mcdonald", "Cruz", "Marshall", "Ortiz", "Gomez", "Murray", "Freeman",
    "Wells", "Webb", "Simpson", "Stevens", "Tucker", "Porter", "Hunter", "Hicks",
    "Crawford", "Boyd", "Mason", "Warren", "Fox", "Rose", "Rice", "Moreno",
    "Schmidt", "Patel", "Nichols", "Herrera", "Medina", "Ryan", "Fernandez", "Weaver",
    "Daniels", "Stephens", "Payne", "Kelley", "Dunn", "Pierce", "Arnold", "Tran",
    "Spencer", "Peters", "Hawkins", "Grant", "Hansen", "Castro", "Hoffman", "Hart",
    "Elliott", "Cunningham", "Knight", "Bradley", "Carroll", "Hudson", "Duncan",
    "Armstrong", "Berry", "Andrews", "Johnston", "Ray", "Lane", "Riley", "Carpenter",
    "Perkins", "Aguilar", "Silva", "Richards", "Willis", "Matthews", "Chapman", "Lawrence",
    "Garza", "Vargas", "Watkins", "Wheeler", "Larson", "Carlson", "Harper", "George",
    "Greene", "Burke", "Guzman", "Morrison", "Munoz", "Jacobs", "Obrien", "Lawson",
    "Franklin", "Lynch", "Bishop", "Carr", "Salazar", "Austin", "Mendez", "Gilbert",
    "Jensen", "Williamson", "Montgomery", "Harvey", "Oliver", "Howell", "Dean", "Hanson",
    "Weber", "Garrett", "Sims", "Burton", "Fuller", "Soto", "Mccoy", "Welch", "Chen",
    "Schultz", "Walters", "Reid", "Fields", "Walsh", "Little", "Bowman", "Davidson",
    "May", "Day", "Schneider", "Newman", "Brewer", "Lucas", "Holland", "Wong",
    "Banks", "Santos", "Curtis", "Pearson", "Delgado", "Valdez", "Pena", "Rios",
    "Douglas", "Sandoval", "Barrett", "Hopkins", "Keller", "Guerrero", "Stanley", "Bates",
    "Alvarado", "Beck", "Ortega", "Wade", "Estrada", "Contreras", "Barnett", "Caldwell",
    "Santiago", "Lambert", "Powers", "Chambers", "Nunez", "Craig", "Leonard", "Lowe",
    "Rhodes", "Byrd", "Shelton", "Frost", "Norris", "Leach", "Orr", "Berger",
    "Mckee", "Conway", "Stein", "Bullock", "Knox", "Meadows", "Solomon", "Vaughn",
    "Eagles", "Bender", "Blevins", "Guthrie", "Seymour", "Yates", "Pugh", "Salinas",
    "Schwartz", "Rutledge", "Mcintosh", "Puckett", "Kern", "Benton", "Mcgowan", "Mcmillan",
    "Elmore", "Faulk", "Williford", "Sumner", "Stallings", "Alderman", "Batts", "Blalock",
    "Braswell", "Bunn", "Creech", "Daughtry", "Dawson", "Eason", "Fonville", "Godwin",
    "Hardison", "Holliday", "Ipock", "Jessup", "Kittrell", "Lassiter", "Mabry", "Mangum",
    "Merritt", "Outlaw", "Pate", "Peacock", "Privett", "Riggs", "Rogers", "Sasser",
    "Scarborough", "Sugg", "Tilghman", "Tyson", "Vick", "Walston", "Wheaton", "Whitfield",
    "Wiggins", "Willoughby", "Wooten", "Yarborough",
]

# ── OCCUPATIONS ──

OCCUPATIONS = {
    "shrimper": {"count": 20, "locations": ["harbor", "dock", "fisher_house"], "skills": ["fishing", "net_mending", "boat_repair", "tide_reading"]},
    "crabber": {"count": 10, "locations": ["harbor", "dock"], "skills": ["crab_potting", "crab_selling", "boat_handling"]},
    "farmer": {"count": 15, "locations": ["farm_edge", "farmhouse", "orchard", "pasture"], "skills": ["farming", "animal_care", "harvesting"]},
    "cattle_hand": {"count": 6, "locations": ["pasture", "farm_edge"], "skills": ["cattle_care", "fence_repair", "weather_reading"]},
    "woodcutter": {"count": 8, "locations": ["forest_edge", "forest_trail", "forest_deep"], "skills": ["woodcutting", "forest_knowledge", "firewood"]},
    "craftsman": {"count": 12, "locations": ["town_square", "general_store"], "skills": ["carpentry", "metalwork", "repair"]},
    "seamstress": {"count": 6, "locations": ["town_square"], "skills": ["sewing", "mending", "embroidery"]},
    "cook": {"count": 8, "locations": ["tavern", "fisher_house", "farmhouse"], "skills": ["cooking", "baking", "preserving"]},
    "merchant": {"count": 6, "locations": ["market_stall", "general_store"], "skills": ["trading", "negotiation", "appraisal"]},
    "herbalist": {"count": 4, "locations": ["forest_edge", "cottage_garden", "beach"], "skills": ["herb_knowledge", "healing", "gathering"]},
    "sailor": {"count": 8, "locations": ["harbor", "dock", "tavern"], "skills": ["sailing", "navigation", "ropework"]},
    "child": {"count": 30, "locations": ["town_square", "farmhouse", "fisher_house"], "skills": ["playing", "learning", "helping"]},
    "elder": {"count": 12, "locations": ["town_square", "chapel", "general_store"], "skills": ["storytelling", "wisdom", "history"]},
    "apprentice": {"count": 10, "locations": ["cottage_workshop", "general_store", "harbor"], "skills": ["learning", "assisting", "carrying"]},
    "housekeeper": {"count": 8, "locations": ["fisher_house", "farmhouse", "lighthouse_keeper_house"], "skills": ["cleaning", "cooking", "mending"]},
    "midwife": {"count": 2, "locations": ["town_square", "chapel"], "skills": ["healing", "childbirth", "herbal_remedies"]},
    "bartender": {"count": 4, "locations": ["tavern"], "skills": ["mixing", "listening", "conflict_resolution"]},
    "fishmonger": {"count": 8, "locations": ["market_stall", "fisher_house", "harbor"], "skills": ["fish_selling", "cleaning", "pricing"]},
    "mechanic": {"count": 5, "locations": ["harbor", "general_store"], "skills": ["engine_repair", "welding", "electrical"]},
    "teacher": {"count": 3, "locations": ["town_square", "chapel"], "skills": ["teaching", "mentoring", "organizing"]},
    "nurse": {"count": 3, "locations": ["town_square", "chapel"], "skills": ["healing", "triage", "herbal_remedies"]},
    "trucker": {"count": 6, "locations": ["general_store", "harbor"], "skills": ["driving", "loading", "route_knowledge"]},
    "hunter": {"count": 4, "locations": ["forest_edge", "forest_deep"], "skills": ["hunting", "tracking", "butchering"]},
}

# ── PERSONALITY TRAITS ──

PERSONALITY_TRAITS = [
    "warm", "reserved", "boisterous", "quiet", "cheerful", "melancholy",
    "practical", "dreamy", "sharp", "gentle", "stubborn", "easygoing",
    "proud", "humble", "curious", "cautious", "bold", "timid",
    "generous", "frugal", "honest", "cunning", "loyal", "independent",
    "patient", "impatient", "thoughtful", "impulsive", "serious", "playful",
    "kind", "stern", "optimistic", "pessimistic", "romantic", "pragmatic",
    "spiritual", "skeptical", "traditional", "progressive", "gregarious", "solitary",
]

SPEECH_PATTERNS = [
    "direct and plain", "soft and measured", "loud and laughing",
    "sparse but meaningful", "fast and animated", "slow and deliberate",
    "full of proverbs", "dry humor", "warm and motherly",
    "gruff but kind", "poetic", "blunt", "gentle",
    "storyteller", "questioner", "listener", "joker",
]

# ── HOME LOCATIONS ──

HOME_LOCATIONS = [
    "fisher_house", "farmhouse", "lighthouse_keeper_house",
    "cottage_main_room", "town_square", "general_store",
    "tavern", "chapel",
]


def _pick_name(used_names: set, gender: str) -> str:
    """Pick a unique name."""
    pool = FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE
    available = [n for n in pool if n not in used_names]
    if not available:
        available = pool  # fallback: allow duplicates with surname differentiation
    first = random.choice(available)
    used_names.add(first)
    return first


def _pick_surname(used_combos: set, first: str) -> str:
    """Pick a surname, avoiding exact duplicates where possible."""
    available = [s for s in SURNAMES if f"{first} {s}" not in used_combos]
    if not available:
        available = SURNAMES
    surname = random.choice(available)
    used_combos.add(f"{first} {surname}")
    return surname


def generate_npc(population_index: int, used_names: set, used_combos: set) -> dict:
    """Generate a single procedural NPC."""
    gender = random.choice(["male", "female"])
    first = _pick_name(used_names, gender)
    surname = _pick_surname(used_combos, first)
    full_name = f"{first} {surname}"

    # Age distribution weighted toward working-age adults
    age_roll = random.random()
    if age_roll < 0.20:
        age = random.randint(5, 15)  # child
    elif age_roll < 0.30:
        age = random.randint(16, 22)  # young adult
    elif age_roll < 0.65:
        age = random.randint(23, 50)  # adult
    elif age_roll < 0.85:
        age = random.randint(51, 65)  # middle-aged
    else:
        age = random.randint(66, 85)  # elder

    # Occupation based on age
    if age < 12:
        occupation = "child"
    elif age < 18:
        occupation = random.choice(["apprentice", "child"])
    elif age > 70:
        occupation = random.choice(["elder", "housekeeper", "cook"])
    else:
        # Weight toward common occupations
        occ_choices = []
        for occ, data in OCCUPATIONS.items():
            if occ not in ("child",):
                occ_choices.extend([occ] * data["count"])
        occupation = random.choice(occ_choices)

    occ_data = OCCUPATIONS.get(occupation, {})
    work_locations = occ_data.get("locations", ["town_square"])
    skills = occ_data.get("skills", [])

    # Personality
    traits = random.sample(PERSONALITY_TRAITS, k=random.randint(2, 4))
    speech = random.choice(SPEECH_PATTERNS)

    # Home
    if age < 18:
        home = random.choice(["fisher_house", "farmhouse", "town_square"])
    else:
        home = random.choice(HOME_LOCATIONS)

    # Description
    descriptions = {
        "shrimper": f"A weathered {gender} with salt in their hair and diesel on their hands.",
        "crabber": f"A tough {gender} with quick hands and a quicker temper.",
        "farmer": f"A sturdy {gender} with soil under their nails and seasons in their bones.",
        "cattle_hand": f"A patient {gender} who speaks more easily to animals than people.",
        "woodcutter": f"A strong, quiet {gender} who knows every tree in the forest.",
        "craftsman": f"A skilled {gender} with careful hands and an eye for detail.",
        "seamstress": f"A precise {gender} with needle and thread always at hand.",
        "cook": f"A round, warm {gender} who shows love through food.",
        "merchant": f"A sharp-eyed {gender} who can price anything at a glance.",
        "herbalist": f"A quiet {gender} who knows the secret uses of every plant.",
        "sailor": f"A weathered {gender} with stories from beyond the horizon.",
        "child": f"A small {gender} with bright eyes and boundless energy.",
        "elder": f"A {gender} whose face tells the story of decades on the coast.",
        "apprentice": f"A young {gender} eager to learn, all elbows and enthusiasm.",
        "housekeeper": f"A capable {gender} who keeps the household running.",
        "midwife": f"A calm, knowing {gender} who has brought many into the world.",
        "bartender": f"A steady {gender} who's heard every story and believes none of them.",
        "fishmonger": f"A sharp {gender} who can clean a flounder in thirty seconds.",
        "mechanic": f"A grease-stained {gender} who can fix anything with duct tape and determination.",
        "teacher": f"A patient {gender} who believes the kids are the future.",
        "nurse": f"A calm {gender} with steady hands and a warm manner.",
        "trucker": f"A road-weary {gender} who knows every pothole on Hwy 58.",
        "hunter": f"A quiet {gender} who moves through the forest like a shadow.",
    }

    npc_id = f"npc_{population_index:03d}"

    properties = {
        "age": age,
        "gender": gender,
        "occupation": occupation,
        "personality": ", ".join(traits),
        "speech": speech,
        "description": descriptions.get(occupation, f"A {gender} of the village."),
        "skills": skills,
        "home": home,
        "traits": traits,
        "generated": True,
    }

    return {
        "id": npc_id,
        "name": full_name,
        "home": home,
        "work_locations": work_locations,
        "occupation": occupation,
        "properties": properties,
    }


def generate_npc_schedule(npc: dict, hour: int) -> dict:
    """Generate a schedule entry for an NPC at a given hour."""
    occupation = npc["occupation"]
    age = npc["properties"]["age"]
    work_locs = npc.get("work_locations", ["town_square"])
    home = npc.get("home", "town_square")

    # Sleep hours
    if hour >= 22 or hour < 6:
        if age < 12 and hour < 7:
            return {"activity": "sleeping", "location_id": home, "description": "Sleeping soundly."}
        if age > 70 and hour < 7:
            return {"activity": "sleeping", "location_id": home, "description": "Sleeping. The old need their rest."}
        return {"activity": "sleeping", "location_id": home, "description": "Sleeping."}

    # Morning routine
    if hour == 6:
        if age < 16:
            return {"activity": "resting", "location_id": home, "description": "Waking slowly."}
        return {"activity": "working", "location_id": home, "description": "Waking. Starting the day."}

    # Work hours (7-17)
    if 7 <= hour < 12:
        if occupation == "child":
            return {"activity": "learning", "location_id": random.choice(["town_square", "farmhouse"]), "description": "Learning and playing."}
        if occupation == "elder":
            return {"activity": "socializing", "location_id": random.choice(["town_square", "chapel", "general_store"]), "description": "Morning in town."}
        if occupation == "apprentice":
            return {"activity": "learning", "location_id": random.choice(work_locs), "description": "Learning the trade."}
        return {"activity": "working", "location_id": random.choice(work_locs), "description": f"Working. {occupation} at work."}

    if 12 <= hour < 14:
        if occupation in ("child", "elder"):
            return {"activity": "eating", "location_id": home, "description": "Lunch at home."}
        return {"activity": "eating", "location_id": random.choice([home, "tavern", "market_stall"]), "description": "Lunch break."}

    if 14 <= hour < 17:
        if occupation == "child":
            return {"activity": "playing", "location_id": random.choice(["town_square", "beach", "forest_edge"]), "description": "Playing."}
        if occupation == "elder":
            return {"activity": "resting", "location_id": random.choice(["town_square", "chapel"]), "description": "Afternoon rest."}
        return {"activity": "working", "location_id": random.choice(work_locs), "description": "Afternoon work."}

    # Evening (17-21)
    if 17 <= hour < 19:
        if occupation in ("fisherman", "farmer", "shepherd", "woodcutter"):
            return {"activity": "working", "location_id": random.choice(work_locs), "description": "End-of-day tasks."}
        return {"activity": "eating", "location_id": home, "description": "Evening meal."}

    if 19 <= hour < 22:
        roll = random.random()
        if roll < 0.3:
            return {"activity": "socializing", "location_id": "tavern", "description": "Evening at the tavern."}
        if roll < 0.5:
            return {"activity": "socializing", "location_id": "town_square", "description": "Evening in the square."}
        return {"activity": "resting", "location_id": home, "description": "Quiet evening at home."}

    return {"activity": "idle", "location_id": home, "description": "Going about their day."}


def generate_relationships(npc: dict, all_npcs: list) -> list:
    """Generate relationships between NPCs based on proximity and occupation."""
    relationships = []
    npc_id = npc["id"]
    npc_home = npc.get("home", "")
    npc_occ = npc["occupation"]
    npc_work = set(npc.get("work_locations", []))

    # Find candidates for relationships
    candidates = []
    for other in all_npcs:
        if other["id"] == npc_id:
            continue
        score = 0
        # Same home = family or neighbors
        if other.get("home", "") == npc_home:
            score += 3
        # Same workplace
        other_work = set(other.get("work_locations", []))
        if npc_work & other_work:
            score += 2
        # Same occupation
        if other["occupation"] == npc_occ:
            score += 1
        if score > 0:
            candidates.append((other, score))

    # Pick 1-3 relationships
    num_relationships = random.randint(1, 3)
    random.shuffle(candidates)
    for other, score in candidates[:num_relationships]:
        if score >= 3:
            rel_type = random.choice(["family", "close_friend", "neighbor"])
            affinity = random.uniform(0.6, 0.95)
        elif score >= 2:
            rel_type = random.choice(["friend", "coworker", "acquaintance"])
            affinity = random.uniform(0.4, 0.8)
        else:
            rel_type = "acquaintance"
            affinity = random.uniform(0.2, 0.6)

        relationships.append({
            "npc_a": npc_id,
            "npc_b": other["id"],
            "relationship": rel_type,
            "affinity": round(affinity, 2),
            "description": f"{rel_type.replace('_', ' ')}",
        })

    return relationships


def populate_village(db, target_population: int = 200) -> int:
    """
    Generate procedural NPCs to reach the target population.
    Returns the number of NPCs generated.
    """
    # Count existing NPCs
    existing = db.execute("SELECT COUNT(*) as cnt FROM agents WHERE type = 'npc'").fetchone()["cnt"]
    to_generate = max(0, target_population - existing)

    if to_generate == 0:
        return 0

    used_names = set()
    used_combos = set()

    # Load existing NPC names to avoid duplicates
    existing_npcs = db.execute("SELECT name FROM agents WHERE type = 'npc'").fetchall()
    for row in existing_npcs:
        parts = row["name"].split()
        if parts:
            used_names.add(parts[0])
        used_combos.add(row["name"])

    # Generate NPCs
    all_new_npcs = []
    for i in range(to_generate):
        idx = existing + i + 1
        npc = generate_npc(idx, used_names, used_combos)
        all_new_npcs.append(npc)

    # Insert NPCs
    now = time.time()
    for npc in all_new_npcs:
        db.execute("""
            INSERT OR IGNORE INTO agents (id, name, type, location_id, state, properties, created_at, updated_at)
            VALUES (?, ?, 'npc', ?, 'active', ?, ?, ?)
        """, (npc["id"], npc["name"], npc["work_locations"][0],
              json.dumps(npc["properties"]), now, now))

    # Generate schedules (every 2 hours to keep it manageable)
    for npc in all_new_npcs:
        for hour in range(0, 24, 2):
            sched = generate_npc_schedule(npc, hour)
            db.execute("""
                INSERT OR IGNORE INTO npc_schedules (npc_id, hour, activity, location_id, description)
                VALUES (?, ?, ?, ?, ?)
            """, (npc["id"], hour, sched["activity"], sched["location_id"], sched["description"]))

    # Generate relationships
    all_npcs = []
    for row in db.execute("SELECT id, name, properties FROM agents WHERE type = 'npc'").fetchall():
        props = json.loads(row["properties"]) if row["properties"] else {}
        all_npcs.append({
            "id": row["id"],
            "name": row["name"],
            "occupation": props.get("occupation", ""),
            "home": props.get("home", ""),
            "work_locations": OCCUPATIONS.get(props.get("occupation", ""), {}).get("locations", ["town_square"]),
        })

    relationship_count = 0
    for npc in all_npcs:
        rels = generate_relationships(npc, all_npcs)
        for rel in rels:
            # Avoid duplicate relationships
            existing = db.execute(
                "SELECT COUNT(*) as cnt FROM npc_relationships WHERE (npc_a = ? AND npc_b = ?) OR (npc_a = ? AND npc_b = ?)",
                (rel["npc_a"], rel["npc_b"], rel["npc_b"], rel["npc_a"])
            ).fetchone()["cnt"]
            if existing == 0:
                db.execute("""
                    INSERT INTO npc_relationships (npc_a, npc_b, relationship, affinity, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (rel["npc_a"], rel["npc_b"], rel["relationship"], rel["affinity"], rel["description"]))
                relationship_count += 1

    db.commit()
    return to_generate
