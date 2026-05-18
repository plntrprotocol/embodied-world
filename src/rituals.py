"""
rituals.py — Seasonal events and rituals.

The village has a living calendar. Each season has rituals that NPCs prepare for,
participate in, and talk about. These aren't just flavor — they affect NPC moods,
create gathering points, and give the village a sense of rhythm and tradition.

Rituals:
- Spring: Planting Festival, First Catch, Blossom Walk
- Summer: Midsummer Bonfire, Sea Swimming, Harvest Dance
- Autumn: Harvest Feast, Pecan Cracking, Remembrance
- Winter: Solstice Gathering, Story Night, New Year's Fire

Design principles:
- Rituals are prepared for in advance (NPCs talk about them coming)
- Rituals bring NPCs together (social bonding)
- Rituals affect mood and create memories
- OWL can participate, observe, or help organize
- Each ritual has a unique feel and description
"""

import json
import random
import time
from typing import Optional

from .world_state import get_db, log_event, DB_PATH


# ── RITUAL DEFINITIONS ──

RITUALS = {
    # ── SPRING ──
    "planting_festival": {
        "season": "spring",
        "day": 15,  # Day of the month
        "preparation_days": 5,
        "title": "The Planting Festival",
        "preparation": [
            "The fields are being prepared. Everyone is talking about the planting festival.",
            "Seeds are sorted and blessed. The planting festival approaches.",
            "Maeve organizes the planting crews. The festival will be a good one this year.",
        ],
        "day_of": [
            "The Planting Festival! The whole village gathers in the fields. Seeds are sown with ceremony and song. Maeve leads the blessing of the soil. There's food, music, and the feeling that anything is possible.",
            "Planting day. The village comes together to sow the season's crops. Children run between the furrows. The elders tell stories of plantings past. The earth smells of hope.",
        ],
        "after": [
            "The planting is done. The fields are sown. Now we wait, and hope.",
            "After the festival, the village feels lighter. The work is begun. The rest is up to the weather and the gods.",
        ],
        "mood_effect": "hopeful",
        "social_bonus": 0.1,
        "locations": ["farm_edge", "farmhouse", "town_square"],
    },
    "first_catch": {
        "season": "spring",
        "day": 20,
        "preparation_days": 3,
        "title": "The First Catch",
        "preparation": [
            "The fishermen are preparing for the first catch of the season. The boats are ready.",
            "Cormac checks his nets one more time. The first catch is tomorrow.",
        ],
        "day_of": [
            "The First Catch! The harbor is alive. Every boat goes out at dawn. The first mackerel of the season is cause for celebration. Cormac's catch is the largest — he'll be insufferable for weeks.",
            "First catch day. The sea provides. The harbor fills with silver fish and louder voices. Brigid gets the pick of the haul. The rivalry with Cormac is already heating up.",
        ],
        "after": [
            "The season's first catch was good. The village breathes easier.",
            "With the first catch in, the hunger winter is truly over.",
        ],
        "mood_effect": "content",
        "social_bonus": 0.05,
        "locations": ["harbor", "dock"],
    },

    # ── SUMMER ──
    "midsummer_bonfire": {
        "season": "summer",
        "day": 15,
        "preparation_days": 7,
        "title": "The Midsummer Bonfire",
        "preparation": [
            "Wood is being stacked on the beach. The midsummer bonfire is coming.",
            "Children gather driftwood. The bonfire will be the biggest in years.",
            "Saoirse is sewing new clothes for the festival. Everyone wants to look their best.",
        ],
        "day_of": [
            "Midsummer! The bonfire on the beach lights up the night. The whole village is there. Music, dancing, food, and the warmth of the fire. The night is short and full of joy. Padraig tells stories that grow taller with each telling. Even Greta from the lighthouse comes down.",
            "The longest day. The bonfire roars against the twilight that never quite comes. Faces glow in the firelight. Strangers become friends. Friends become family. This is what the village is for.",
        ],
        "after": [
            "The bonfire is embers now. But the warmth lingers.",
            "After midsummer, the village feels closer. Like we're all in this together.",
        ],
        "mood_effect": "alive",
        "social_bonus": 0.15,
        "locations": ["beach", "town_square"],
    },
    "sea_swimming": {
        "season": "summer",
        "day": 25,
        "preparation_days": 2,
        "title": "Sea Swimming Day",
        "preparation": [
            "The water is finally warm enough. Sea swimming day is coming.",
            "The young people are planning to swim out to the point. The elders shake their heads.",
        ],
        "day_of": [
            "Sea swimming day! The brave (or foolish) swim out to the rocky point. Cheers from the beach. Finn makes it first — of course he does. The water is cold but the sun is warm.",
            "The annual swim. Bodies in the water, laughter on the beach. The sea is kind today.",
        ],
        "after": [
            "Sore muscles and sunburns. Worth it.",
            "The sea swimming is done for another year. We survived.",
        ],
        "mood_effect": "excited",
        "social_bonus": 0.05,
        "locations": ["beach", "rocky_point"],
    },

    # ── AUTUMN ──
    "harvest_feast": {
        "season": "autumn",
        "day": 15,
        "preparation_days": 10,
        "title": "The Harvest Feast",
        "preparation": [
            "The harvest is coming in. Preparations for the feast have begun.",
            "Mara is brewing extra ale. The harvest feast will be legendary.",
            "Tables are being built in the square. The whole village will eat together.",
            "The kitchen is chaos. Every cook in the village is preparing something.",
        ],
        "day_of": [
            "The Harvest Feast! Long tables fill the square. More food than anyone can eat. Maeve's harvest was bountiful. The ale flows. Brother Aiden says a blessing. Old Tomas tells the story of the first harvest. Everyone cries a little. It's perfect.",
            "Harvest day. The village gives thanks. The tables groan under the weight of the season's work. Strangers are fed. Enemies share bread. For one night, all is well in the world.",
        ],
        "after": [
            "The feast is over. The tables are empty. The memories are full.",
            "After the harvest feast, the village feels grateful. And very full.",
        ],
        "mood_effect": "grateful",
        "social_bonus": 0.2,
        "locations": ["town_square", "farmhouse", "tavern"],
    },
    "apple_pressing": {
        "season": "autumn",
        "day": 22,
        "preparation_days": 3,
        "title": "Pecan Cracking",
        "preparation": [
            "The pecans are ripe. It's almost time for cracking.",
            "The orchard is heavy with pecans. Everyone is recruited to help.",
        ],
        "day_of": [
            "Pecan cracking day! The whole village turns out. Baskets of pecans, the old cracker, and the smell of fresh nuts. Children stomp apples in barrels. The cider will last all winter.",
            "The cracker is working. Shells fly. The orchard smells of pecans and community. This is tradition.",
        ],
        "after": [
            "The pecans are stored. Winter tastes a little better already.",
            "Sacks of pecans in the cellar. The orchard is bare. But the village is prepared.",
        ],
        "mood_effect": "content",
        "social_bonus": 0.1,
        "locations": ["orchard", "farmhouse"],
    },

    # ── WINTER ──
    "solstice_gathering": {
        "season": "winter",
        "day": 21,
        "preparation_days": 7,
        "title": "The Solstice Gathering",
        "preparation": [
            "The shortest day approaches. Candles are being made for the solstice.",
            "The chapel is being prepared. Brother Aiden is planning the ceremony.",
            "Everyone is crafting gifts. The solstice is about giving.",
        ],
        "day_of": [
            "The Solstice. The longest night. Every candle in the village is lit. The chapel overflows. Brother Aiden speaks of darkness and light, of endings and beginnings. The singing is beautiful. Afterward, the tavern is warm and full. Gifts are exchanged. The darkness outside makes the warmth inside mean more.",
            "Midnight of the longest night. Candles everywhere. The whole village gathered. The darkness is complete, but we are not afraid. We have each other. We have light. Tomorrow, the days begin to lengthen again.",
        ],
        "after": [
            "The solstice has passed. The light will return. We endured the dark.",
            "After the longest night, there's a feeling of triumph. We made it. The light is coming back.",
        ],
        "mood_effect": "peaceful",
        "social_bonus": 0.15,
        "locations": ["chapel", "tavern", "town_square"],
    },
    "story_night": {
        "season": "winter",
        "day": 28,
        "preparation_days": 3,
        "title": "Story Night",
        "preparation": [
            "Story night is coming. Old Tomas is preparing his best tales.",
            "The firewood is stacked high. Story night will be warm.",
        ],
        "day_of": [
            "Story Night! The tavern is packed. Old Tomas tells the story of the great storm. Padraig tells a tale that may or may not be true. Even Greta shares a story from her lighthouse. The fire burns low. The stories burn bright.",
            "The longest nights are for stories. Tonight, the village remembers. Old stories, new stories, true stories, tall stories. The fire crackles. The ale flows. We are storytellers, all of us.",
        ],
        "after": [
            "The stories linger. Tomorrow, they'll be told again, slightly different.",
            "After story night, the village feels connected. We share the same stories. We share the same past.",
        ],
        "mood_effect": "content",
        "social_bonus": 0.1,
        "locations": ["tavern"],
    },
    "new_years_fire": {
        "season": "winter",
        "day": 30,
        "preparation_days": 5,
        "title": "The New Year's Fire",
        "preparation": [
            "The year is ending. The New Year's fire is being prepared.",
            "A massive pile of wood on the beach. The biggest fire of the year.",
            "People are writing down things they want to let go of. To burn in the fire.",
        ],
        "day_of": [
            "The New Year's Fire! The biggest bonfire the village has ever seen. Everyone writes down the old year's burdens and throws them into the flames. The fire reaches the sky. At midnight, cheers. Hugs. Tears. The new year begins with light and warmth and community.",
            "The old year burns. The new year begins. The fire is so bright it lights up the whole bay. We stand together, watching the flames. What we release, what we carry forward. The village turns the page.",
        ],
        "after": [
            "A new year. The fire is ash. The village is renewed.",
            "The new year begins. The village feels fresh. Anything is possible.",
        ],
        "mood_effect": "hopeful",
        "social_bonus": 0.2,
        "locations": ["beach", "town_square"],
    },
}


def init_ritual_tables(db):
    """Initialize ritual tracking tables."""
    db.executescript("""
        CREATE TABLE IF NOT EXISTS ritual_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ritual_key TEXT NOT NULL,
            season TEXT NOT NULL,
            year INTEGER NOT NULL,
            phase TEXT DEFAULT 'upcoming',
            triggered_at REAL DEFAULT NULL,
            UNIQUE(ritual_key, season, year)
        );
    """)
    db.commit()


def check_rituals(db) -> list:
    """
    Check if any rituals should be triggered, prepared for, or concluded.
    Returns a list of ritual events.
    """
    # Gracefully handle missing ritual_state table
    table_exists = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='ritual_state'"
    ).fetchone()
    if not table_exists:
        return []

    events = []
    world_time = db.execute("SELECT * FROM world_time WHERE id = 1").fetchone()
    if not world_time:
        return events

    current_season = world_time["season"]
    current_day = world_time["day"]
    current_year = world_time["year"]
    now = time.time()

    for ritual_key, ritual in RITUALS.items():
        if ritual["season"] != current_season:
            continue

        ritual_day = ritual["day"]
        prep_days = ritual["preparation_days"]
        days_until = ritual_day - current_day

        # Check if already triggered this year
        existing = db.execute(
            "SELECT * FROM ritual_state WHERE ritual_key = ? AND season = ? AND year = ?",
            (ritual_key, current_season, current_year)
        ).fetchone()

        if existing and existing["phase"] == "completed":
            continue

        # Preparation phase
        if 0 < days_until <= prep_days and (not existing or existing["phase"] == "upcoming"):
            prep_msg = random.choice(ritual["preparation"])
            events.append({
                "type": "ritual_preparation",
                "title": ritual["title"],
                "description": prep_msg,
                "ritual_key": ritual_key,
            })

            if existing:
                db.execute("UPDATE ritual_state SET phase = 'preparing' WHERE id = ?", (existing["id"],))
            else:
                db.execute(
                    "INSERT INTO ritual_state (ritual_key, season, year, phase) VALUES (?, ?, ?, 'preparing')",
                    (ritual_key, current_season, current_year)
                )

        # Day of ritual
        elif days_until == 0:
            day_msg = random.choice(ritual["day_of"])
            events.append({
                "type": "ritual_day",
                "title": ritual["title"],
                "description": day_msg,
                "ritual_key": ritual_key,
                "mood_effect": ritual.get("mood_effect"),
                "social_bonus": ritual.get("social_bonus", 0),
            })

            if existing:
                db.execute("UPDATE ritual_state SET phase = 'active', triggered_at = ? WHERE id = ?", (now, existing["id"]))
            else:
                db.execute(
                    "INSERT INTO ritual_state (ritual_key, season, year, phase, triggered_at) VALUES (?, ?, ?, 'active', ?)",
                    (ritual_key, current_season, current_year, now)
                )

            # Apply social bonus to NPCs at ritual locations
            if ritual.get("social_bonus"):
                for loc in ritual.get("locations", []):
                    npcs_here = db.execute(
                        "SELECT * FROM agents WHERE type = 'npc' AND location_id = ?", (loc,)
                    ).fetchall()
                    for npc in npcs_here:
                        try:
                            props = json.loads(npc["properties"]) if npc["properties"] else {}
                        except:
                            props = {}
                        mood = props.get("mood", "calm")
                        # Boost mood
                        props["mood"] = ritual.get("mood_effect", mood)
                        db.execute("UPDATE agents SET properties = ? WHERE id = ?", (json.dumps(props), npc["id"]))

        # After ritual (1 day after)
        elif days_until == -1:
            after_msg = random.choice(ritual["after"])
            events.append({
                "type": "ritual_after",
                "title": f"After {ritual['title']}",
                "description": after_msg,
                "ritual_key": ritual_key,
            })

            if existing:
                db.execute("UPDATE ritual_state SET phase = 'completed' WHERE id = ?", (existing["id"],))

    db.commit()
    return events


def get_upcoming_rituals(db) -> list:
    """Get upcoming rituals for the current season."""
    world_time = db.execute("SELECT * FROM world_time WHERE id = 1").fetchone()
    if not world_time:
        return []

    current_season = world_time["season"]
    current_day = world_time["day"]

    upcoming = []
    for ritual_key, ritual in RITUALS.items():
        if ritual["season"] == current_season:
            days_until = ritual["day"] - current_day
            if 0 < days_until <= ritual["preparation_days"]:
                upcoming.append({
                    "title": ritual["title"],
                    "days_until": days_until,
                    "locations": ritual.get("locations", []),
                })

    return upcoming
