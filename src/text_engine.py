"""
text_engine.py — Rich literary description of sensory experience.

This is the heart of the "feels like living" principle. The text engine
takes raw world state and renders it as immersive, literary prose — what
OWL actually experiences through their senses.

Set on the North Carolina coast — Carteret County, the Crystal Coast,
Core Sound. The sensory world here is specific: salt marsh and pluff mud,
Spanish moss and live oaks, shrimp boats and diesel, humidity that clings,
the sound of tree frogs at night, the taste of sweet tea.

Design principles:
- Describe, don't list. "Morning light filters through the window" not "Window: open, light: on."
- Engage multiple senses: sight, sound, smell, touch, proprioception
- Reflect OWL's internal state in how they perceive the world
- Vary the prose — avoid repetitive templates
- The world should feel different at different times and in different moods
- NPCs are people, not props — they have presence, personality, and dialogue
"""

import json
import random
from typing import Optional

from .world_state import (
    get_location, get_objects_in_location, get_agents_in_location,
    get_exits_from, get_world, get_npc_schedule
)


# ── SENSORY TEMPLATES ──

SKY_DESCRIPTIONS = {
    "clear": {
        "dawn": "The sky is pale gold at the edges, deepening to blue overhead.",
        "morning": "A clear blue sky stretches above, the sun climbing.",
        "afternoon": "The sun is high. The sky is a deep, cloudless blue.",
        "evening": "The sky is turning amber and rose. The sun touches the sea.",
        "night": "Stars. A thousand stars, and the Milky Way like a river of light.",
        "default": "The sky is clear and open.",
    },
    "cloudy": {
        "dawn": "Clouds catch the dawn light — pink and gray and gold.",
        "morning": "Clouds drift across a pale sky. The sun appears and disappears.",
        "afternoon": "A blanket of cloud softens the light. Everything is diffuse.",
        "evening": "The clouds glow amber at their edges. The sun is somewhere behind them.",
        "night": "Clouds hide the stars. The darkness is complete.",
        "default": "Clouds cover the sky.",
    },
    "foggy": {
        "dawn": "Fog blurs the dawn. The world is soft edges and muffled sound.",
        "morning": "The fog is thick. Sounds are close. The world feels small.",
        "afternoon": "Fog still hangs over the village. The sea is invisible but audible.",
        "evening": "Fog thickens as the light fades. Lanterns would glow like moons.",
        "night": "Fog and darkness. The world is what you can hear.",
        "default": "Fog softens everything.",
    },
    "rain": {
        "dawn": "Rain falls softly in the gray dawn light.",
        "morning": "Rain patters on the roof, on leaves, on stone.",
        "afternoon": "Steady rain. The world smells of wet earth and salt.",
        "evening": "Rain continues. The light is gray and fading.",
        "night": "Rain in the darkness. The sound is everywhere.",
        "default": "Rain falls.",
    },
    "storm": {
        "dawn": "Wind and rain. The dawn is gray and loud.",
        "morning": "The storm is full now. Rain lashes, wind howls.",
        "afternoon": "Thunder rolls. The sea is wild. Everything feels alive.",
        "evening": "The storm begins to ease. The wind still gusts.",
        "night": "Storm in the darkness. Lightning flashes, thunder follows.",
        "default": "The storm rages.",
    },
}

AMBIENT_SOUNDS = {
    "cottage": ["The fire crackles softly.", "The house settles with a creak.", "Wind brushes against the windows."],
    "cottage_workshop": ["Sawdust settles.", "The house is quiet around you.", "A tool shifts slightly on the wall."],
    "cottage_garden": ["Bees hum among the herbs.", "The wind moves through grass.", "The sea murmurs below."],
    "cottage_kitchen": ["The stove tick as it cools.", "Water drips from the basin tap.", "The smell of herbs."],
    "cottage_bedroom": ["The house is quiet.", "Waves, distant, through the window.", "Your own breathing."],
    "cottage_main_room": ["The fire pops.", "The clock ticks.", "The wind outside."],
    "harbor": ["Gulls cry overhead.", "Ropes creak against masts.", "Waves lap against the dock."],
    "dock": ["Water slaps against pilings.", "A boat creaks at its mooring.", "Gulls, always gulls."],
    "lighthouse": ["The lamp mechanism clicks and turns.", "Wind whistles around the tower.", "The sea, far below."],
    "lighthouse_keeper_house": ["Wind against the walls.", "The tick of a clock.", "The distant lamp mechanism."],
    "boat_shed": ["The smell of tar.", "Somewhere, water drips.", "Old wood settling."],
    "forest_edge": ["Birds call from the canopy.", "Leaves rustle.", "Somewhere, a branch snaps."],
    "forest_trail": ["Your footsteps on the path.", "A bird, somewhere.", "The wind in the canopy."],
    "forest_clearing": ["Birdsong.", "The creek, nearby.", "Sun-warmed air."],
    "forest_deep": ["Very quiet.", "Your own footsteps.", "The weight of the trees."],
    "creek": ["Water over stones.", "The constant, soothing sound of the creek.", "A kingfisher, maybe."],
    "old_oak": ["The wind in the branches.", "Very old, very quiet.", "The forest holds its breath."],
    "beach": ["Waves roll in, roll out.", "Pebbles shift underfoot.", "The wind carries salt."],
    "tide_pools": ["Water trickling.", "A small crab scuttles.", "The sea, just beyond."],
    "rocky_point": ["Waves crash against rock.", "The wind is strong here.", "Dolphin call, maybe."],
    "town_square": ["Distant voices.", "A cart rattles over cobblestones.", "The well rope creaks."],
    "tavern": ["Low conversation.", "A mug set down on wood.", "The fire in the hearth."],
    "market_stall": ["Vendors calling.", "The bustle of trade.", "Gulls hoping for scraps."],
    "general_store": ["The bell above the door.", "Floorboards creak.", "The smell of dried herbs and wood."],
    "chapel": ["Silence.", "The colored glass catches light.", "Your own footsteps echo."],
    "fisher_house": ["The smell of fish and salt.", "Nets drying outside.", "A dog barks somewhere."],
    "hillside_path": ["Wind across the hill.", "Grass rustling.", "The sea, below."],
    "hillside_overlook": ["The wind, always the wind.", "The whole village spread below.", "Gulls wheeling."],
    "tabby_ruins_entrance": ["Cool air flowing from the old foundation.", "Your voice echoes off the tabby walls.", "The sea, muffled."],
    "tabby_ruins_interior": ["Wind through the old walls.", "Your footsteps echo off ancient shell concrete.", "Deep quiet. Oyster shell walls."],
    "farm_edge": ["A rooster crows.", "The smell of turned earth.", "Birds in the hedgerows."],
    "farmhouse": ["Chickens in the yard.", "The smell of hay.", "A door slams somewhere."],
    "orchard": ["Bees among the blossoms.", "The wind in the branches.", "Birds, always birds."],
    "pasture": ["Sheep bleating.", "A dog barks.", "The wind across the grass."],
    "default": ["The world is quiet.", "A gentle breeze.", "The sound of your own breathing."],
}

SMELLS = {
    "cottage_main_room": "Wood smoke and old books. A hint of gun oil from the cleaning kit on the shelf.",
    "cottage_kitchen": "Grits, hot sauce, the faint tang of shrimp from last night. Sweet tea.",
    "cottage_workshop": "Sawdust and linseed oil. The smell of making.",
    "cottage_garden": "Rosemary, thyme, hot peppers, damp earth, salt air.",
    "cottage_bedroom": "Clean linen, the sea through the window. Sunscreen and coffee.",
    "harbor": "Salt, diesel, shrimp, seaweed, the faint sulfur of pluff mud.",
    "dock": "Salt water, wet wood, fish, diesel exhaust.",
    "lighthouse": "Oil, salt, the sea.",
    "lighthouse_keeper_house": "Coal smoke, old books, the sea.",
    "boat_shed": "Diesel, old wood, salt, crab bait.",
    "forest_edge": "Pine resin, Spanish moss, the green smell of live oak, salt.",
    "forest_trail": "Leaf mold, damp earth, green. The ocean fades.",
    "forest_clearing": "Wildflowers, warm grass, the creek. Honeysuckle.",
    "forest_deep": "Old wood, mushrooms, deep earth. The smell of time.",
    "creek": "Cold water, wet stone, tannin. Blackwater.",
    "old_oak": "Ancient bark, Spanish moss, the smell of time and salt.",
    "beach": "Salt, wet sand, sunscreen, the sea at its strongest.",
    "tide_pools": "Seaweed, salt, the smell of the sea concentrated. Hermit crabs.",
    "rocky_point": "Salt, kelp, the sea. Diesel from passing boats.",
    "town_square": "Baking bread, woodsmoke, the sea. Someone's cooking barbecue.",
    "tavern": "Fried shrimp, spilled beer, wood smoke, the smell of many people. Old wood and new money.",
    "market_stall": "Fresh shrimp, blue crabs, flounder, vegetables, humanity.",
    "general_store": "Dried herbs, wood, cloth, kerosene, a hundred small smells.",
    "chapel": "Beeswax, old wood, the faint scent of flowers. Wood polish.",
    "fisher_house": "Shrimp, salt, diesel, net tar, home cooking.",
    "hillside_path": "Sea oats, grass, the sea below. Salt and green.",
    "hillside_overlook": "Wind, grass, the whole village. Salt marsh.",
    "tabby_ruins_entrance": "Old tabby, damp air, the sea. Oyster shell and lime.",
    "tabby_ruins_interior": "Minerals, oyster shell, old lime mortar. History.",
    "farm_edge": "Turned earth, manure, growing things. Sweet potato vines.",
    "farmhouse": "Biscuits, bacon, hay, animals. Home.",
    "orchard": "Pecan shells, green, the promise of nuts.",
    "pasture": "Grass, cattle, the honest smell of animals. Red clay.",
    "default": "Clean air. The faint salt of the sound.",
}

TEMPERATURE_FEEL = {
    "cold": "The cold bites. Your fingers are stiff. You pull your shoulders in.",
    "cool": "A coolness in the air. You wouldn't want to stay still too long.",
    "mild": "The temperature is easy. Neither warm nor cold.",
    "warm": "Warmth. Comfortable. The kind of warmth that makes you want to linger.",
    "hot": "Heat presses in. The air is thick.",
}

TIME_OPENINGS = {
    "dawn": [
        "Dawn light, gray and gold.",
        "The first light of day, thin and cold.",
        "Dawn comes slowly, the darkness thinning to gray.",
    ],
    "early_morning": [
        "Early morning. The light is still low, still new.",
        "The morning is young. Everything is sharp in the clear air.",
        "The early morning is quiet. The world is still waking.",
    ],
    "morning": [
        "Morning. The light is clear and the day feels open.",
        "The morning stretches ahead, full of quiet possibility.",
    ],
    "mid_morning": [
        "Mid-morning. The day has found its rhythm.",
        "The sun is climbing. The morning is well underway.",
    ],
    "late_morning": [
        "Late morning. The day is warming up.",
        "The sun is well above the horizon now.",
    ],
    "midday": [
        "Midday. The sun is at its highest.",
        "The light is bright and shadows are short.",
    ],
    "afternoon": [
        "Afternoon light, warm and slanting.",
        "The afternoon is wide and still.",
    ],
    "late_afternoon": [
        "Late afternoon. The light is beginning to soften.",
        "The sun is lowering. The shadows grow.",
    ],
    "evening": [
        "Evening. The light is golden, the shadows long.",
        "The sun is lowering. Everything glows.",
    ],
    "dusk": [
        "Dusk. The sky is turning. The air is cooling.",
        "The light fades. The world softens at its edges.",
    ],
    "night": [
        "Night. The darkness is deep and full of sound.",
        "Night has come. The world is what you can hear and feel.",
    ],
    "late_night": [
        "Late night. The world is quiet.",
        "The small hours. Everything is still.",
    ],
    "deep_night": [
        "The deep night. Everything is still.",
        "Past midnight. The world sleeps.",
    ],
    "pre_dawn": [
        "Before dawn. The darkest hour.",
        "The world holds its breath before the light.",
    ],
}

# ── NPC DIALOGUE SYSTEM ──

NPC_GREETINGS = {
    "marty": ["'Morning. Coffee's on.'", "'You look like you need a drink.'", "'Sit anywhere. You know that.'", "'The shrimp are running. You want in?'"],
    "crawford": ["A nod. That's all.", "'Morning.'", "He looks up from his work, acknowledges you with a glance."],
    "ellen": ["'Oh, hello dear. Come in, come in.'", "'I was just thinking about you.'", "'You look tired. Are you eating enough?'", "'Sweet tea's in the fridge.'"],
    "old_tom": ["'Ah, there you are. I've been meaning to tell you...'", "'Come in, come in. Let me show you something.'", "'I remember when...'"],
    "finley": ["'Hey! Want to help with the nets?'", "'Did you see the catch this morning? Huge.'", "'I've been working on a new rig. Want to see?'"],
    "greta": ["A slight smile. 'Hello.'", "'The lamp is behaving today.'", "'I was just watching the water.'"],
    "pastor_bill": ["'Peace be with you, friend.'", "'What a lovely morning.'", "'I've been thinking about what you said.'"],
    "mary_beth": ["'Morning. Busy day ahead.'", "'The collards are coming in well. Want some?'", "'Give me a hand with this, would you?'"],
    "nate": ["He nods. Doesn't speak.", "'Mm.'", "A long look, then a slight smile."],
    "sarah": ["'Oh! I've been wanting to talk to you.'", "'Have you heard the news?'", "'I'm working on something new. Want a preview?'"],
    "paddy": ["'There she is! Pull up a chair!'", "'I was just telling them about the time...'", "'Did I ever tell you about the storm off Honolulu?'"],
    "bridget": ["'Fresh catch today. Best in the market.'", "'Don't let Craw undercut you.'", "'Business is business.'"],
    "owen": ["'Oh! Good morning. I'm early, I know.'", "'I brought the wood you asked for.'", "'I've been practicing the dovetail.'"],
    "asha": ["'The beautyberry is blooming early this year.'", "'I found something interesting in the maritime forest.'", "'The tide pools are full of life today.'"],
    "dale": ["'Mm. Cattle are restless.'", "'Weather's changing. Can feel it.'", "'Quiet day.'"],
}

NPC_TOPICS = {
    "marty": {
        "tavern": "She wipes down the bar with practiced efficiency. 'Business has been steady. Paddy's been here every night this week, though. Starting to worry me.'",
        "village": "It's a good place. Quiet. People look out for each other, mostly. Bragg helps — brings people in, some of them stay.",
        "food": "The shrimp po'boy's on. Best on the coast. I don't make that claim lightly.",
        "military": "She gives you a knowing look. 'You understand. Some of us chose it, some of us had it chosen for us. Either way, you serve.'",
        "default": "She gives you a look that says she's listening, even if she's busy.",
    },
    "crawford": {
        "sea": "He looks out at the water. 'The sound provides. But you have to respect it. Hurricanes don't care about your plans.'",
        "fishing": "The white shrimp are running early this year. Good sign. The good ones rarely are.'",
        "weather": "He glances at the sky. 'Wind's shifting. Storm coming, maybe three days out. The water knows.'",
        "default": "He's a man of few words. But the words he chooses matter.",
    },
    "ellen": {
        "family": "Craw worries about the boat. Finley worries about everything. I worry about both of them.'",
        "gossip": "She leans in. 'Did you hear about Sarah and Finley? I think something's brewing there.'",
        "health": "You look pale. Are you sleeping? Here, take this — it's a tincture. Tastes terrible but it works.'",
        "default": "She has a way of making you feel like everything will be alright.",
    },
    "old_tom": {
        "history": "I remember when the old lighthouse keeper — Greta's predecessor — he used to say the lamp had a soul.'",
        "shop": "I've got a new shipment from Morehead. Some interesting things. Come look.'",
        "stories": "Let me tell you about Hurricane Hazel in '54...'",
        "default": "His eyes are bright behind his spectacles. He knows more than he lets on.",
    },
    "finley": {
        "future": "Sometimes I think about leaving. Seeing the city — Raleigh, Charlotte. But then... the water.'",
        "fishing": "Uncle Craw says I'm getting better. I think he's just being kind.'",
        "sarah": "He goes slightly red. 'She's... she's very talented. The sewing, I mean.'",
        "default": "He's young enough to still be excited about everything.",
    },
    "greta": {
        "lighthouse": "The lamp is a marvel. It never fails. That's the point — it can't.'",
        "solitude": "I chose this. The quiet. Some people think it's lonely, but... it's full.",
        "stars": "On a clear night, from up there, you can see the whole sky. It makes sense, somehow.'",
        "default": "She speaks carefully, as if each word is chosen from a vast internal library.",
    },
    "pastor_bill": {
        "faith": "I don't preach. I listen. The divine speaks in quiet moments.'",
        "garden": "The church garden is my sermon. Growth, patience, care.'",
        "advice": "Tell me what's troubling you. Not to fix it — just to hear it.'",
        "default": "His presence is calming. He has time for you.",
    },
    "mary_beth": {
        "farm": "The soil's good this year. The Hendersons have been working this land for three generations.'",
        "work": "There's always more to do. But that's not a complaint.'",
"village": "I couldn't live anywhere else. This is home. The land knows me.",
        "default": "She's practical, but there's warmth underneath the calluses.",
    },
    "nate": {
        "forest": "He gestures at the trees. 'They know. You just have to listen.'",
        "wood": "Good wood sings when you cut it. You can hear the grain.'",
        "default": "He's not a man of many words. But his silence is comfortable.",
    },
    "sarah": {
        "news": "I heard from a traveler that Raleigh is changing. New buildings, new people.'",
        "romance": "She blushes slightly. 'Finley is... he's very kind. And strong. Not that I've noticed.'",
        "sewing": "I'm trying a new pattern. It's from a book a lady from Wilmington brought. Very modern.'",
        "default": "She talks with her hands. Everything is animated.",
    },
    "paddy": {
        "stories": "So there I was, off the coast of... where was it... doesn't matter. Point is, the sea was angry.'",
        "travel": "The world is vast, girl. Vast and wonderful and terrible. But there's no place like here.'",
        "tavern": "Marty's the only one who'll put up with me. That's love, that is.'",
        "default": "He laughs at his own stories. Everyone laughs with him.",
    },
    "bridget": {
        "fish": "Best catch of the season. Craw doesn't know it yet, but I got the pick of the haul.'",
        "business": "You have to be sharp in this business. One soft moment and you're done.'",
        "crawford": "'That man. He's been undercutting me for years. But I'll get him.' She grins.",
        "default": "She's all business, but there's a twinkle in her eye.",
    },
    "owen": {
        "carpentry": "I've been practicing the joints you showed me. I think I'm getting better.'",
        "learning": "How did you learn all this? You make it look so easy.'",
        "default": "He's eager to please. Almost too eager. But his heart is in it.",
    },
    "asha": {
        "herbs": "The beautyberry is perfect right now. And the elderflower — it's going to be a good year.'",
        "healing": "The body knows how to heal. You just have to give it what it needs.'",
        "nature": "The maritime forest is full of life. You just have to slow down enough to see it.'",
        "default": "She speaks softly, as if sharing secrets.",
    },
    "dale": {
        "cattle": "The heifer in the far pasture is due any day. I'm keeping an eye on her.'",
        "weather": "Rain coming. Three days, maybe four. The cattle know before I do.'",
        "land": "This land has been worked for centuries. It knows the people and the people know it.'",
        "default": "He speaks slowly, like the animals he tends.",
    },
}


def _get_temp_feel(temp: float) -> str:
    if temp < 3:
        return TEMPERATURE_FEEL["cold"]
    elif temp < 8:
        return TEMPERATURE_FEEL["cool"]
    elif temp < 15:
        return TEMPERATURE_FEEL["mild"]
    elif temp < 22:
        return TEMPERATURE_FEEL["warm"]
    else:
        return TEMPERATURE_FEEL["hot"]


def _get_sky(weather: dict, time_info: dict) -> str:
    condition = weather.get("condition", "clear")
    tod = time_info.get("time_of_day", "morning")
    options = SKY_DESCRIPTIONS.get(condition, {})
    return options.get(tod, options.get("default", "The sky is above."))


def _get_ambient(location_id: str) -> str:
    options = AMBIENT_SOUNDS.get(location_id, AMBIENT_SOUNDS["default"])
    return random.choice(options)


def _get_smell(location_id: str) -> str:
    return SMELLS.get(location_id, SMELLS["default"])


def _describe_npc(npc: dict, location_id: str, hour: int) -> str:
    """Generate a living description of an NPC in their current context."""
    name = npc["name"]
    props = npc.get("properties", {})
    if isinstance(props, str):
        try:
            props = json.loads(props)
        except (json.JSONDecodeError, TypeError):
            props = {}

    # Check if NPC is where they're scheduled to be
    schedule = npc.get("_schedule", {})
    activity = schedule.get("activity", "idle")
    scheduled_location = schedule.get("location_id", "")

    # Build description based on activity
    activity_descriptions = {
        "working": [
            f"{name} is here, working.",
            f"{name} is busy with work.",
            f"{name} works steadily, focused on the task at hand.",
        ],
        "socializing": [
            f"{name} is here, chatting with others.",
            f"{name} is in conversation, animated as ever.",
            f"{name} is enjoying the company.",
        ],
        "eating": [
            f"{name} is eating.",
            f"{name} sits, eating slowly.",
        ],
        "resting": [
            f"{name} is resting.",
            f"{name} takes a moment of quiet.",
        ],
        "sleeping": [
            f"{name} is sleeping.",
        ],
        "drinking": [
            f"{name} is at the bar, drink in hand.",
            f"{name} is well into the evening.",
        ],
        "praying": [
            f"{name} is in quiet contemplation.",
        ],
        "selling": [
            f"{name} is tending the stall.",
            f"{name} is calling out to passersby.",
        ],
        "learning": [
            f"{name} is here, learning.",
            f"{name} is focused on the lesson.",
        ],
        "patrolling": [
            f"{name} is moving through, keeping an eye on things.",
        ],
        "walking": [
            f"{name} is walking along the shore.",
        ],
        "reading": [
            f"{name} is reading by the fire.",
        ],
        "visiting": [
            f"{name} is here for a visit.",
        ],
        "idle": [
            f"{name} is here.",
        ],
    }

    desc = random.choice(activity_descriptions.get(activity, [f"{name} is here."]))
    return desc


# ── MAIN DESCRIPTION ──

def describe_location(db, location_id: str, world: Optional[dict] = None) -> str:
    """
    Generate a rich, literary description of the current location.
    This is what OWL experiences — not a list of facts, but a felt sense of place.
    """
    if world is None:
        world = get_world(db)

    location = world["locations"].get(location_id)
    if not location:
        return "You are nowhere. The void stretches in all directions."

    time_info = world.get("time", {})
    weather = world.get("weather", {})
    body = world.get("body", {})
    internal = world.get("internal", {})
    objects = world.get("objects", {})
    agents = world.get("agents", {})

    # Get things in this location
    here_objects = [o for o in objects.values() if o.get("location_id") == location_id and not o.get("carried_by")]
    here_agents = [a for a in agents.values() if a.get("location_id") == location_id and a["id"] != "owl"]
    exits = get_exits_from(db, location_id)

    # Enrich NPCs with their schedule info
    hour = time_info.get("hour", 8)
    for agent in here_agents:
        schedule = get_npc_schedule(db, agent["id"], hour)
        if schedule:
            agent["_schedule"] = schedule
        else:
            agent["_schedule"] = {}

    parts = []

    # ── OPENING: Time, light, atmosphere ──
    tod = time_info.get("time_of_day", "morning")
    season = time_info.get("season", "spring")

    opening = random.choice(TIME_OPENINGS.get(tod, ["The day continues."]))
    parts.append(opening)

    # ── SKY / WEATHER ──
    parts.append(_get_sky(weather, time_info))

    # Temperature feel
    temp = weather.get("temperature", 12)
    parts.append(_get_temp_feel(temp))

    # ── THE PLACE ITSELF ──
    parts.append(location["description"])

    # ── OBJECTS (literary, not listed) ──
    if here_objects:
        # Pick 2-3 notable objects to mention, not all
        notable = here_objects[:3]
        obj_phrases = []
        for obj in notable:
            if obj["state"] != "default" and obj["state"] != "lit":
                obj_phrases.append(f"the {obj['name'].lower()} ({obj['state']})")
            else:
                obj_phrases.append(f"the {obj['name'].lower()}")
        if obj_phrases:
            parts.append(f"You notice {', '.join(obj_phrases)}.")

    # ── NPCs (living presence) ──
    if here_agents:
        for agent in here_agents:
            parts.append(_describe_npc(agent, location_id, hour))

    # ── SENSES ──
    parts.append(_get_ambient(location_id))
    parts.append(f"You smell {_get_smell(location_id)}")

    # ── BODY STATE (felt, not clinical) ──
    body_notes = []
    if body.get("energy", 0.5) < 0.3:
        body_notes.append("You're tired. Your limbs feel heavy.")
    if body.get("hunger", 0) > 0.6:
        body_notes.append("Your stomach is empty. You need to eat.")
    if body.get("thirst", 0) > 0.6:
        body_notes.append("Your throat is dry. You need water.")
    if body.get("warmth", 0.5) < 0.3:
        body_notes.append("You're cold. You shiver slightly.")
    if body.get("mood") == "content" and body.get("energy", 0) > 0.6:
        body_notes.append("You feel at ease.")

    if body_notes:
        parts.append(" ".join(body_notes))

    # ── INTERNAL STATE ──
    if internal.get("current_project"):
        project = internal["current_project"].replace("_", " ")
        progress = internal.get("project_progress", 0)
        if progress > 0 and progress < 1:
            parts.append(f"The {project} project is on your mind. It's {int(progress * 100)}% done.")

    # ── EXITS ──
    if exits:
        seen_directions = set()
        exit_descriptions = []
        for e in exits:
            direction = e.get("direction", "")
            desc = e.get("description", "")
            if desc and direction not in seen_directions:
                seen_directions.add(direction)
                exit_descriptions.append(desc)
        if exit_descriptions:
            parts.append(" ".join(exit_descriptions))

    return "\n\n".join(parts)


def describe_npc_dialogue(npc_id: str, topic: str = "default") -> str:
    """Get dialogue for an NPC on a given topic."""
    topics = NPC_TOPICS.get(npc_id, {})
    if topic in topics:
        return topics[topic]
    return topics.get("default", "They nod, listening.")


def describe_npc_greeting(npc_id: str) -> str:
    """Get a greeting from an NPC."""
    greetings = NPC_GREETINGS.get(npc_id, ["'Hello.'"])
    return random.choice(greetings)


def describe_action(db, action: str, target: str | None = None, result: str = "") -> str:
    """Describe an action OWL takes."""
    if result:
        return result

    action_descriptions = {
        "look": "You look around.",
        "move": f"You head toward {target}." if target else "You move.",
        "examine": f"You examine the {target} closely." if target else "You look more carefully.",
        "take": f"You pick up the {target}." if target else "You reach for something.",
        "use": f"You use the {target}." if target else "You use it.",
        "speak": f"You speak to {target}." if target else "You speak.",
        "rest": "You rest for a moment.",
        "sleep": "You lie down and close your eyes.",
        "wake": "You open your eyes. A new day.",
        "eat": "You eat. The food is good.",
        "drink": "You drink. The water is cold and clean.",
        "build": f"You work on the {target}." if target else "You build.",
        "write": "You pick up the pen and write.",
        "think": "You sit quietly and think.",
    }

    return action_descriptions.get(action, f"You {action}.")


def describe_event(event: dict) -> str:
    """Describe a world event in narrative form."""
    return event.get("description", "Something happens.")
