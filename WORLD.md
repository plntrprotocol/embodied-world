# Embodied Creative World — World Document

## Setting

**Carteret County, North Carolina** — the Crystal Coast. A small fishing village on Core Sound, population ~200. Fort Bragg (Fort Liberty) is an hour inland.

## The Village

The village sits on a slight rise overlooking Core Sound. A working harbor with shrimp boats and crab boats. A town square with a tavern, market stalls, general store, and chapel. Maritime forest to the west — live oaks draped in Spanish moss, longleaf pines, saw palmetto. Farmland to the northeast — collard greens, sweet potatoes, tobacco, pecan orchards. A blackwater creek runs through the forest. Tabby ruins (oyster shell concrete, ~1800s) on the hillside. Cape Lookout Lighthouse visible in the distance.

## Key NPCs (15 hand-crafted)

| Name | Role | Personality |
|------|------|-------------|
| Martha "Marty" Bowen | Tavern owner | Warm, sharp, no-nonsense. Former Marine. |
| Crawford "Craw" Brennan | Shrimper | Quiet, weathered, thoughtful. 3rd generation. |
| Ellen Brennan | Shrimper's wife | Practical, warm, stubborn. Runs the social calendar. |
| Old Tom Henderson | Shopkeeper | Grizzled, kind, storyteller. Remembers everything. |
| Finley Brennan | Young shrimper | Eager, restless, optimistic. Craw's nephew. |
| Greta Moss | Lighthouse keeper | Solitary, precise, poetic. Reads Latin. |
| Pastor Bill | Pastor | Gentle, thoughtful, slightly absent-minded. |
| Mary Beth Henderson | Farmer | Capable, warm, no time for nonsense. |
| Nate | Woodcutter | Quiet, strong, reliable. Iraq veteran. |
| Sarah | Seamstress | Bright, curious, romantic. From Wilmington. |
| Paddy | Retired sailor | Boisterous, storyteller, drinks at the tavern. |
| Bridget | Fishmonger | Sharp, competitive, business-first. |
| Owen | Carpentry apprentice | Eager to learn, almost too eager. |
| Asha | Herbalist | Quiet, knows every plant, heals. |
| Dale | Cattle hand | Slow-spoken, weather-wise, land-knowledgeable. |

Plus ~185 procedurally generated NPCs with unique names, personalities, occupations, and relationships.

## Systems

- **Time** — Full day/night cycle, 4 seasons (~90 days each)
- **Weather** — Season-driven (fog, rain, storms, clear). Affects everything.
- **Ecology** — 17 plant types, 15 animal types, 8 fish species. All lifecycle-driven.
- **Social Dynamics** — Relationships evolve. Alliances form. Conflicts emerge.
- **Events** — Emergent from system interactions. Storms, fish runs, arguments, celebrations.
- **Narrative** — Story arcs weave from events. The world tells its own story.
- **Psychology** — Mood, memory, interests, creative impulses, boredom, social need.
- **Creative Systems** — Carpentry, writing, cooking, crafting, music, painting. ~56 items.
- **Rituals** — 8 seasonal events across spring, summer, autumn, winter.

## Geography (34 locations)

**Cottage** (OWL's home): main room, bedroom, kitchen, workshop, garden

**Hillside**: path, overlook, tabby ruins (entrance + interior)

**Town**: square, tavern, market stalls, general store, chapel, fisher house, keeper's house

**Harbor**: harbor, dock, lighthouse, boat shed

**Beach**: beach, tide pools, rocky point

**Maritime Forest**: edge, trail, clearing, creek, old oak, deep forest

**Farmland**: edge, farmhouse, orchard, pasture

## How It Works

The world is a SQLite-backed simulation. An agent (any AI) reads the world state, decides what to do, and acts. The world responds. Time passes. NPCs live their own lives. Events emerge from system interactions, not scripts.

The agent experiences the world through rich literary prose — sensory, immersive, specific to the NC coast. Not "You are in a room. Exits: north." but "Morning light filters through the workshop window, catching dust motes. The smell of coffee from the kitchen mixes with sawdust. Outside, gulls are calling — the tide must be coming in."
