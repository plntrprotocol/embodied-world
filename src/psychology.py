"""
psychology.py — OWL's inner life: mood, memory, interests, creative impulses.

This is what makes the experience feel like *living* rather than *playing*.
OWL's internal state evolves based on:
- What happens in the world
- Body state (hunger, energy, comfort)
- Social interactions
- Creative output
- Time passing
- Novelty (or lack thereof)

Design principles:
- Mood is a felt quality, not a number
- Memory colors perception — remembering something makes you notice related things
- Interests drift naturally — you get obsessed, then move on
- Creative impulses arise from accumulated experience
- Boredom drives exploration
"""

import json
import time
import random
from typing import Optional

from .world_state import get_db, update_internal, update_body, log_event, DB_PATH


# ── MOOD SYSTEM ──

MOOD_DESCRIPTIONS = {
    "content": [
        "A quiet contentment settles over you.",
        "You feel at ease with the world.",
        "Everything feels right, for now.",
    ],
    "restless": [
        "You can't settle. Something is pulling at you.",
        "Restlessness. The walls feel close.",
        "You need to move, to do something.",
    ],
    "curious": [
        "Your mind is sharp. You want to know more.",
        "Something has caught your attention.",
        "Curiosity hums in your chest.",
    ],
    "melancholy": [
        "A gentle sadness, like rain on the window.",
        "You feel the weight of something unnamed.",
        "The world feels distant, softened.",
    ],
    "inspired": [
        "Ideas spark and connect. You need to make something.",
        "The creative urge is strong.",
        "You see possibilities everywhere.",
    ],
    "tired": [
        "Your limbs are heavy. Your mind is slow.",
        "You need rest. Real rest.",
        "Everything takes effort.",
    ],
    "hungry": [
        "Your stomach is a hollow thing.",
        "Food. You need food.",
        "Hunger makes everything sharper and less pleasant.",
    ],
    "lonely": [
        "You miss the sound of another voice.",
        "The solitude feels heavy today.",
        "You need to see someone. Anyone.",
    ],
    "peaceful": [
        "A deep peace. The world is exactly as it should be.",
        "You breathe slowly. Everything is enough.",
        "Stillness, and it's good.",
    ],
    "excited": [
        "Your heart beats faster. Something is coming.",
        "Anticipation thrums through you.",
        "The world feels vivid, alive.",
    ],
    "frustrated": [
        "Nothing is going right. You grind your teeth.",
        "A knot of frustration in your chest.",
        "You want to throw something.",
    ],
    "grateful": [
        "You notice the small good things.",
        "Warmth spreads through you. This life. This place.",
        "You are lucky. You know it.",
    ],
    "bored": [
        "Nothing holds your interest.",
        "The hours stretch. You need something new.",
        "Boredom is an itch you can't scratch.",
    ],
    "sleepy": [
        "Your eyes are heavy. The world softens at the edges.",
        "Sleep pulls at you.",
        "You could lie down right here.",
    ],
    "awake": [
        "You are alert. The world is sharp.",
        "Wide awake. Ready.",
        "Your mind is clear.",
    ],
    "cold": [
        "You shiver. The cold gets into your bones.",
        "You can't get warm.",
        "Your fingers are stiff. Your teeth chatter.",
    ],
    "thirsty": [
        "Your throat is parched. Your lips are cracked.",
        "Water. You need water.",
        "Everything is dry.",
    ],
}

# Interest drift: what OWL might become interested in
INTERESTS = [
    "carpentry", "the_sea", "the_forest", "the_creek", "herbs",
    "fishing", "the_lighthouse", "the_stars", "birds", "stones",
    "weather", "the_town", "music", "writing", "painting",
    "cooking", "the_harbor", "the_beach", "the_hills", "people_watching",
    "boat_building", "carving", "weaving", "pottery", "gardening",
    "the_chapel", "history", "stories", "the_night", "the_dawn",
]

# Creative impulses that arise from interests
CREATIVE_IMPULSES = {
    "carpentry": ["Build a new chair", "Carve a wooden box", "Repair the garden fence", "Make a bookshelf", "Build a toy boat"],
    "the_sea": ["Write about the sea", "Paint the harbor at dawn", "Collect shells", "Sail to the rocky point", "Watch the tide for an hour"],
    "the_forest": ["Walk the deep forest trail", "Sketch the old oak", "Gather mushrooms", "Find the creek's source", "Sit in the clearing"],
    "the_creek": ["Explore the creek again", "Follow the creek to its source", "Listen to the water", "Look for fossils in the creek bed"],
    "herbs": ["Dry lavender", "Make a herb bundle", "Plant new herbs in the garden", "Brew tea from garden herbs", "Study the wild plants"],
    "fishing": ["Go fishing at dawn", "Mend the fishing nets", "Try a new fishing spot", "Clean and prepare fish", "Watch the fishermen"],
    "the_lighthouse": ["Visit Greta at the lighthouse", "Climb to the lamp room", "Watch the light at night", "Sketch the lighthouse"],
    "the_stars": ["Stay up to watch the stars", "Learn the constellations", "Write about the night sky", "Find a new stargazing spot"],
    "birds": ["Identify the birds of the village", "Listen to the dawn chorus", "Look for nests", "Sketch a gull", "Follow a bird"],
    "stones": ["Collect interesting stones", "Build a stone wall", "Skip stones on the beach", "Study the rock types", "Arrange stones in the garden"],
    "weather": ["Watch a storm from the overlook", "Record the weather patterns", "Feel the first warm day", "Watch the fog roll in", "Notice the wind"],
    "the_town": ["Walk every street in town", "Visit the market", "Sit in the square and watch", "Visit the chapel", "Talk to everyone"],
    "music": ["Hum a melody", "Whistle while working", "Listen to the wind", "Sing an old song", "Make a simple instrument"],
    "writing": ["Write in your journal", "Write a letter", "Describe the village", "Write a poem", "Record a dream"],
    "painting": ["Paint the view from the overlook", "Mix new colors", "Paint the harbor", "Sketch the cottage", "Paint the garden"],
    "cooking": ["Bake bread", "Make stew", "Try a new recipe", "Preserve herbs", "Cook something special"],
    "the_harbor": ["Watch the boats come in", "Walk the dock at dawn", "Talk to the fishermen", "Watch the nets drying", "Sit and watch the water"],
    "the_beach": ["Walk the beach at low tide", "Collect driftwood", "Watch the waves", "Find sea glass", "Sit on the rocky point"],
    "the_hills": ["Climb to the overlook", "Watch the sunset from the hill", "Find wildflowers", "Follow the path less taken", "Sit on the hill and think"],
    "people_watching": ["Sit in the square and watch", "Listen to conversations", "Notice who talks to whom", "Watch the market", "Observe the tavern regulars"],
    "boat_building": ["Design a small boat", "Select the right wood", "Study how the fishing boats are built", "Carve a model boat", "Plan a boat shed project"],
    "carving": ["Carve a figure from wood", "Practice chip carving", "Make a spoon", "Carve a walking stick", "Decorate a box"],
    "weaving": ["Try weaving with grass", "Study the fishing nets", "Make a simple basket", "Learn about net_mending", "Watch Saoirse work"],
    "pottery": ["Find clay by the creek", "Try shaping a pot", "Study the old pottery in the store", "Make a simple bowl", "Experiment with glazes"],
    "gardening": ["Weed the garden beds", "Plant something new", "Tend the herbs", "Build a new raised bed", "Plan next season's garden"],
    "the_chapel": ["Sit in the chapel", "Talk to Brother Aiden", "Look at the stained glass", "Listen to the silence", "Light a candle"],
    "history": ["Ask Old Tomas about the past", "Study the old buildings", "Look for traces of the past", "Ask about the lighthouse history", "Explore the creek for old signs"],
    "stories": ["Listen to Padraig's tales", "Ask the elders about the village", "Write down the stories", "Tell a story to Owen", "Collect the village's folklore"],
    "the_night": ["Walk at night", "Watch the stars", "Listen to the night sounds", "Sit by the fire late", "Watch the lighthouse beam"],
    "the_dawn": ["Wake before dawn", "Watch the sun rise", "Walk in the early light", "Feel the first warmth", "Hear the dawn chorus"],
}


def get_mood_description(mood: str) -> str:
    """Get a literary description of a mood."""
    options = MOOD_DESCRIPTIONS.get(mood, [f"You're feeling {mood}."])
    return random.choice(options)


def update_psychology(db, hours_passed: float, events: list) -> dict:
    """
    Update OWL's internal state based on time passed and recent events.
    Returns a dict of what changed.
    """
    internal = db.execute("SELECT * FROM internal_state WHERE id = 1").fetchone()
    body = db.execute("SELECT * FROM body_state WHERE id = 1").fetchone()
    world = db.execute("SELECT * FROM world_time WHERE id = 1").fetchone()

    if not internal or not body:
        return {}

    changes = {}
    now = time.time()

    # ── MOOD UPDATE ──
    mood = internal["mood"]
    energy = internal["energy"]
    restlessness = internal["restlessness"]
    social_need = internal["social_need"]
    creative_urge = internal["creative_urge"]

    # Body state affects mood
    if body["hunger"] > 0.7:
        mood = "hungry"
    elif body["thirst"] > 0.7:
        mood = "thirsty"
    elif body["warmth"] < 0.3:
        mood = "cold"
    elif body["energy"] < 0.3:
        mood = "tired"
    else:
        # Mood drifts based on internal state
        if restlessness > 0.7:
            mood = "restless"
        elif creative_urge > 0.7:
            mood = "inspired"
        elif social_need > 0.7:
            mood = "lonely"
        elif energy > 0.7 and body["comfort"] > 0.6:
            if random.random() < 0.3:
                mood = random.choice(["content", "peaceful", "curious"])
        elif energy < 0.4:
            mood = random.choice(["tired", "melancholy"])

    # Events affect mood
    for event in events:
        etype = event.get("type", "")
        if etype == "conversation":
            social_need = max(0.0, social_need - 0.15)
            if mood == "lonely":
                mood = "content"
        elif etype == "creative_output":
            creative_urge = max(0.0, creative_urge - 0.2)
            mood = random.choice(["content", "inspired", "grateful"])
        elif etype == "fish_run":
            mood = "excited"
        elif etype == "plant_flowering":
            if random.random() < 0.3:
                mood = "grateful"

    # ── ENERGY DRIFT ──
    # Energy slowly returns to a baseline based on time of day
    hour = world["hour"] if world else 12
    if 6 <= hour <= 18:
        energy = min(1.0, energy + 0.005 * hours_passed)
    else:
        energy = max(0.1, energy - 0.005 * hours_passed)

    # ── RESTLESSNESS ──
    # Increases over time if nothing novel happens
    restlessness = min(1.0, restlessness + 0.01 * hours_passed)
    # Decreases when exploring or creating
    for event in events:
        if event.get("type") in ("move", "creative_output", "exploration"):
            restlessness = max(0.0, restlessness - 0.1)

    # ── SOCIAL NEED ──
    # Increases slowly over time
    social_need = min(1.0, social_need + 0.005 * hours_passed)

    # ── CREATIVE URGE ──
    # Builds up over time, especially when inspired
    creative_urge = min(1.0, creative_urge + 0.008 * hours_passed)
    if mood in ("inspired", "curious"):
        creative_urge = min(1.0, creative_urge + 0.02)

    # ── INTEREST DRIFT ──
    dominant_interest = internal["dominant_interest"]
    if restlessness > 0.6 or random.random() < 0.02 * hours_passed:
        # Interest shifts
        new_interest = random.choice(INTERESTS)
        if new_interest != dominant_interest:
            dominant_interest = new_interest
            changes["new_interest"] = new_interest

    # ── MEMORY UPDATE ──
    recent_memories = json.loads(internal["recent_memories"]) if internal["recent_memories"] else []
    long_term_memories = json.loads(internal["long_term_memories"]) if internal["long_term_memories"] else []

    # Add new memories from events
    for event in events:
        desc = event.get("description", "")
        if desc and random.random() < 0.3:
            memory = f"{desc} ({world['season']}, {world['time_of_day']})"
            recent_memories.insert(0, memory)

    # Trim recent memories (keep last 10)
    if len(recent_memories) > 10:
        # Move oldest to long-term
        old = recent_memories.pop()
        long_term_memories.insert(0, old)
        if len(long_term_memories) > 50:
            long_term_memories = long_term_memories[:50]

    # ── BOREDOM CHECK ──
    if restlessness > 0.8 and creative_urge < 0.3 and social_need < 0.3:
        mood = "bored"

    # Save changes
    update_internal(
        db,
        mood=mood,
        energy=round(energy, 2),
        restlessness=round(restlessness, 2),
        social_need=round(social_need, 2),
        creative_urge=round(creative_urge, 2),
        dominant_interest=dominant_interest,
        recent_memories=json.dumps(recent_memories),
        long_term_memories=json.dumps(long_term_memories),
    )

    changes.update({
        "mood": mood,
        "energy": round(energy, 2),
        "restlessness": round(restlessness, 2),
        "social_need": round(social_need, 2),
        "creative_urge": round(creative_urge, 2),
        "dominant_interest": dominant_interest,
    })

    return changes


def get_creative_impulse(interest: str) -> Optional[str]:
    """Get a creative impulse based on current interest."""
    impulses = CREATIVE_IMPULSES.get(interest, [])
    if impulses:
        return random.choice(impulses)
    return None


def describe_internal_state(db) -> str:
    """Generate a literary description of OWL's internal state."""
    internal = db.execute("SELECT * FROM internal_state WHERE id = 1").fetchone()
    if not internal:
        return "You are a blank. No thoughts. No feelings."

    parts = []

    # Mood
    mood_desc = get_mood_description(internal["mood"])
    parts.append(mood_desc)

    # Interest
    if internal["dominant_interest"] and internal["dominant_interest"] != "none":
        interest = internal["dominant_interest"].replace("_", " ")
        if internal["restlessness"] > 0.5:
            parts.append(f"You keep thinking about {interest}.")
        else:
            parts.append(f"{interest.replace('_', ' ').title()} is on your mind.")

    # Creative urge
    if internal["creative_urge"] > 0.6:
        impulse = get_creative_impulse(internal["dominant_interest"])
        if impulse:
            parts.append(f"You feel the urge to: {impulse}")
        else:
            parts.append("You want to make something. You're not sure what yet.")

    # Social need
    if internal["social_need"] > 0.6:
        parts.append("You miss people. The silence is too much.")

    # Recent memories
    recent = json.loads(internal["recent_memories"]) if internal["recent_memories"] else []
    if recent and random.random() < 0.4:
        memory = random.choice(recent[:3])
        parts.append(f"You remember: {memory}")

    return "\n\n".join(parts)
