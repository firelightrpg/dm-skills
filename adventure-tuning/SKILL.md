---
name: adventure-tuning
description: Transforms raw published D&D adventures into high-efficiency, DM-ready tactical encounter writeups with localized acoustics, gated observations, interactive stunts, and pre-rolled behavioral/morale engines based on the Dungeon Sheet system.
---

# Adventure Tuning Skill: The Dungeon Sheet In-Situ Engine

This skill guides the transformation of raw, narrative-heavy, or fragmented adventure modules (such as standard TSR/WotC 5e publications) into **operational, modular, table-ready encounter writeups**.

Instead of requiring the Dungeon Master to juggle rules from front-matter or roll multiple tables during play (from `Dungeon Sheet.pdf`), this system **pre-rolls, contextualizes, and bakes the entire Dungeon Turn engine directly into every keyed encounter**.

---

## The Core Design Philosophy

0. **Macro-Level Alignment (`Adventure Synopsis`)**:
   - Every converted module opens with a high-level, 4- to 5-bullet **Adventure Synopsis** before keyed encounters. It briefs the DM on the underlying conspiracy, the critical adventure path, escalating clocks, faction pivot points, and the transition mechanics to the next module.
1. **Zero Page-Flipping (Localization)**:
   - Global rules (water depth, ceiling height, door Strength DCs, geyser thrumming, wandering encounter schedules) are excised from module preambles and localized directly into each room's **Turn Cadence & Acoustics** and **Dungeon Features**.
2. **Layered Sensory Gating**:
   - The players only hear what their senses immediately perceive.
   - **Read-Aloud Boxed Text** contains *zero* spoilers, secret doors, hidden motives, or trap triggers.
   - All hidden details are locked behind standardized **Gated Observations** categorized by action type and insight lens.
3. **DM Readiness Pause (`DM Synopsis`)**:
   - Immediately after the Gated Observations and before "What do you do?", every encounter carries a short **DM-only** synopsis. It gives the DM a beat to confirm they understand the room, and gives players a natural moment to digest information and ask questions.
4. **Pacing Guarantee (`Declaration Phase`)**:
   - The universal DM prompt (`"What do you do?"`) is always paired with concrete room-specific choices in parentheses to immediately break tabletop analysis paralysis.
5. **Environmental Stunts**:
   - Every space provides 2 to 3 pre-calculated tactical stunts (swipes, contests, improvised actions) exploiting room geometry, furnishings, and hazards with explicit DCs and tactical benefits.
6. **Living Adversary Engine**:
   - Creatures are never passive bags of hit points. Each combatant has a pre-rolled activity state, a 2d6 initial reaction profile, a social influence DC matrix, scripted combat strategy, and a **2d6 dynamic bloodied morale response** triggered at $\le$ 50% HP.

---

## Module Architecture & Preamble Schema

Every tuned adventure document begins with standard YAML frontmatter and a macro-level **Adventure Synopsis** before launching into the approach or keyed encounters:

```markdown
---
title: [Adventure Title]
campaign_id: [ID]
audio:
  ambient:
    - [track]
  combat:
    - [track]
---

# [Adventure Title]

**DM View & Audio:**
<a href="http://127.0.0.1:26796/adventure/load?file=/absolute/path/to/[Adventure Title].md">📖 Open Interactive Adventure View</a> |
<a href="rpg-audio://load?file=/absolute/path/to/[Adventure Title].md">🎛️ Sync Audio Settings</a>

---

## Adventure Summary
[Brief 1–2 paragraph narrative overview of the adventure premise].

## Adventure Synopsis
- **The Situation:** [The underlying premise, hidden reality, and antagonistic conspiracy guiding the adventure].
- **The Core Arc & Objectives:** [The critical path from opening hook to the primary objective, key milestones, and climax].
- **Pressure & Clocks:** [Active timers, captive executions, villain escalations, or patrol mobilization schedules].
- **Factions & Pivot Points:** [Key neutral/rebel factions that can alter the balance of power, and critical lore/handouts].
- **Transition / The Next Link:** [How this adventure seamlessly transitions into the next chapter or module].

### Character Advancement
- **Level Range:** [Recommended party levels].
- **Milestones:** [Key narrative or tactical triggers for level advancement].
```

---

## The Master Encounter Schema

Every converted encounter must follow this Markdown structure:

```markdown
## [Number]. [Room Name]

**DM Info:**
- **Dimensions & Space:** [Horizontal bounds/approximates, ceiling height/shape, elevation changes, 3D features].
- **Terrain & Lighting:** [Footing, difficult terrain, water depth, illumination level, sensory impediments like smoke/glare].
- **Rules & Acoustics:** [Stealth penalties/disadvantage from noisy footing, whether ambient noise imposes disadvantage on hearing-based Perception checks, and alert propagation to adjacent areas].
- **Clocks & Timers:** [Specific event countdowns, drainage/collapse times, ritual clocks. Omit this bullet entirely if none].

**Audio Cues:** <a href="rpg-audio://trigger/ambient">▶ Ambience</a> | <a href="rpg-audio://trigger/fade">🔉 Fade Out</a>

> [Evocative boxed read-aloud text with integrated sensory preamble (sight, sound, smell, atmosphere) and tangible scale. Zero spoilers, secret doors, or game mechanics.]

![](https://.../download) <!-- Room image or map excerpt link -->

**_Structure Insight & Gated Observations:_**
- **[[Action]] DC [X] [Ability (Skill)]** — _[Insight Lens]:_ [Specific actionable clue, hazard, or hidden feature]
- **[[Action]] DC [X] [Ability (Skill)]** — _[Insight Lens]:_ [Arcane, mechanical, or historical insight]
- **[[Action]] DC [X] [Ability (Skill)]** — _[Insight Lens]:_ [Behavioral, emotional, or motivational clue]

**_DM Synopsis:_**
- **The Situation:** [What is actually going on in the room, including the hidden truth.]
- **How It Works:** [The core mechanic in one or two sentences: trigger, key DCs, damage, numbers.]
- **Pressure / Clock:** [What gets worse and when; who reacts; what the failure state looks like.]

**_Declaration Phase:_** _"What do you do?"_ _(If the room goes quiet: [3–4 concrete DM prompt choices based on room features])_

**_Tactical Stunts & Improvised Actions:_**
- **[Stunt 1 Name] ([Contest / Stunt / Swipe / Hazard]):** [Check DC, required skill/ability, and mechanical outcome].
- **[Stunt 2 Name] ([Stunt / Improvised Action]):** [Check DC, required skill/ability, and mechanical outcome].
- **[Stunt 3 Name] ([Stunt / Reaction]):** [Check DC, required skill/ability, and mechanical outcome].

---

**_Tactics, Reaction & Morale ([Creature Name / Group]):_** <!-- Omit if no creatures -->
- **Enhanced Profile:** [HP, AC, Ability Scores, Key Attacks / Condition Immunities if modified].
- **Mobility Stance:** [Mobile (Default: Investigates/reinforces noise in adjacent areas after [X] rounds) | Patrol (Route: [Path], converges on noise in [Sector]) | Sentry (Post: [Location], Holds post; shifts to Mobile on [Trigger / X rounds of combat]) | Fixed (Restricted to [Room] due to [Chains / Magic / Directive] — does not pursue or move for noise)].
- **Current Activity:** [Activity Name] (d8 roll: [Range]). [What the creature is doing when the party arrives].
- **Initial Reaction Roll ([🎲 2d6](http://127.0.0.1:26796/roll?d=2d6&dm=true&label=[Name]+Initial+Reaction)):**
  - Starting Attitude: [Hostile / Indifferent / Friendly].
  - **2–7 ([Immediate Attack / Hostile Display]):** [Immediate combat or aggressive posture].
  - **8–10 ([Threatening / Parley Challenge / Allure]):** [Verbal warning, deceptive lure, or conditional stance].
  - **11–12 ([Cautious / Standoff / Stalking]):** [Defensive assessment, stalking, or hesitant pause].
  - _Danger Assessment (DC 10 Wisdom (Insight)):_ If the party appears visibly stronger/weaker, shift reaction up or down one tier.
- **Social Influence Matrix (If Parley / Negotiations Occur):**
  - **[Attitude] DC 0:** [Creature opposes party actions and takes risks to do so].
  - **[Attitude] DC 10 ([Skills]):** [Creature offers no help but does no harm, or gives minor warning].
  - **[Attitude] DC 20 ([Skills / Bribes]):** [Creature does as asked without taking risks, or stands down for bribe].

**Combat Audio:** <a href="rpg-audio://trigger/combat">⚔️ Combat</a> | <a href="rpg-audio://trigger/fade">🔉 Fade Out</a>

- **Combat Start & Surprise:**
  - **Occupant Senses & Stance:** [Passive Perception, Darkvision/Blindsight/Tremorsense, active sentry stance, cover].
    - _Lighting & Vision (RAW):_ [State whether room ambient is Dim or Dark. If Pitch Dark: "Drops to **PP [X - 5]** against unlit intruders (Darkvision treats total darkness as dim light = disadvantage on sight checks). If party carries light or room has ambient dim light, full PP [X] applies."]
    - _Special Sense Exceptions:_ [Note if Blindsight, Tremorsense, or Keen Hearing/Smell negates visual darkness penalties within range].
  - **Occupant Concealment & Ambush:** [Active stealth roll/DC, False Appearance, cover bonuses, or held triggers].
  - **Surprise Adjudication:**
    - *Party Surprising Occupants:* [Benchmark required for party stealth to achieve surprise against these occupants].
    - *Occupants Surprising Party:* [Benchmark required for occupants to achieve surprise against party passive perception].
- **Combat Strategy & Synergy:**
  - _[Phase / Synergy 1]:_ [Pre-buffs, round 1 actions, spell sequencing, chokepoint management].
  - _[Target Priority]:_ [Lightly armored casters, isolated targets, whoever triggers specific hazards].
- 🩸 **Real-Time Bloodied Morale Check ([Roll 2d6](http://127.0.0.1:26796/roll?d=2d6&dm=true&label=[Name]+Bloodied+Morale) when ≤ [X] HP):**
  - _Assessment Shift:_ [Condition making them confident] = +1 tier (toward Rally) | [Condition making them panicked] = -1 tier (toward Surrender)
  - **2–7 [Rally / Spite / Berserk]:** [Fights to the death, reckless attacks, vindictive focus].
  - **8–10 [Desperate / Fallback / Flee]:** [Disengages, dashes for retreat route, triggers emergency defense].
  - **11–12 [Hesitate / Bargain / Parley]:** [Pauses attacks, yields tactical information or loot in exchange for life].
  - **13+ [Surrender]:** [Drops weapons, falls prone, begs for quarter, submits passively].

**_Interactions & Triggered Discoveries:_**
- **[Mechanism / Hazard / Puzzle / Secret Door]:**
  > _"[Sensory read-aloud response when triggered or manipulated]"_
  - [Detailed mechanical DC, saving throws, attack rolls, damage formulas, durations, and physical effects].
  - Sprung Trap Attack: [**+X to hit**](http://127.0.0.1:26796/roll?d=1d20%2BX&label=[Name]+Attack&cmd=avtt)
  - Trap/Hazard Damage: [**avg (dice) [type] damage**](http://127.0.0.1:26796/roll?d=[dice]&type=[type]&label=[Name]&cmd=dmg)
- **[Interrogating Occupants]:** [Diegetic lore revealed, memory blocks, boundaries of what they know and don't know].
- **[Room Loot & Hoards]:**
  > _"[Sensory description of the treasure]"_
  - Itemized coinage, exact gp values for art/gems, and markdown links for magic items.
```

---

## Detailed Component Reference (The Dungeon Sheet Engine)

### 1. DM Info & Boxed Text Staging
The top of every encounter is streamlined into two non-overlapping components: operational rules for the DM, followed immediately by immersive sensory description for the players.

#### **DM Info Components**:
- **Dimensions & Space**: Approximate horizontal footprint, ceiling height/shape, elevation changes, and 3D features (submerged drop-offs, ledges, balconies) to establish spell areas, movement grids, and line of sight.
- **Terrain & Lighting**: Footing conditions, difficult terrain, water depth, illumination level, and sensory impediments (smoke, glare, soot).
- **Rules & Acoustics**: Mechanically relevant check modifiers and encounter bleed dynamics:
  - Surface impact on stealth (e.g., splashing water or loose scree imposes disadvantage on Dexterity (Stealth)).
  - Ambient noise: state explicitly whether ambient noise (roaring cataracts, boiling steam, drunken banquet din) is loud enough to impose disadvantage on hearing-based Wisdom (Perception) checks or grant advantage on Dexterity (Stealth) checks; otherwise leave it out.
  - **Sound Propagation & Encounter Bleed**: State explicitly which adjacent rooms or sectors hear combat, thunder spells, battered doors, or alarm gongs from this chamber. This audio horizon directly dictates which nearby adversary groups are alerted and potentially bleed into the encounter.
- **Clocks & Timers**: Specific operational timers, drainage durations, room collapse counts, or ritual deadlines. **Omit this bullet entirely if there are no active timers or clocks** (combat rounds are tracked dynamically in the tracker and should not be estimated here).

#### **Boxed Read-Aloud Text (Style B: Integrated Sensory Preamble)**:
- Integrates observational sight, sound, smell, tactile sensations, and tangible scale into a single evocative read-aloud paragraph.
- Zero mechanics, spoilers, hidden traps, or creature motives. Gives players immediate spatial orientation without breaking narrative immersion.

### 1b. The Synopsis Hierarchy: Module vs. Room Level

The system employs two tiers of DM synopses to eliminate analysis paralysis at both macro and micro scales:

#### **Tier 1: Adventure / Module Synopsis (Preamble)**
Placed in the module frontmatter immediately after the title and interactive links, before keyed encounters. It briefs the DM on the overarching campaign arc in 4 to 5 structured bullets:
- **The Situation:** The overarching premise, hidden puppet master, and antagonistic conspiracy.
- **The Core Arc & Objectives:** The critical path from opening hook to the primary objective, key milestones, and climax.
- **Pressure & Clocks:** Active countdowns, prisoner execution timelines, or villain escalation states.
- **Factions & Pivot Points:** Key neutral or rebellious factions that players can manipulate to shift the tactical balance.
- **Transition / The Next Link:** The diegetic bridge or relic transporting the party to the next chapter.

#### **Tier 2: Encounter DM Synopsis (Room-Level)**
A short DM-only block placed right after Gated Observations and before the Declaration Phase. It is titled simply `DM Synopsis` (no "read silently" instructions, no solutions list).
- **Three bullets, one or two sentences each**, about 60–90 words total:
  - **The Situation:** What is really going on in this specific space, including hidden truths.
  - **How It Works:** The core mechanical engine: triggers, key DCs, damage formulas, and creature numbers.
  - **Pressure / Clock:** What escalates, who reacts, and what failure looks like.
- Restate information found elsewhere in the room; do not introduce new rules.
- Include it in every keyed encounter. For simple rooms, keep it to 2 bullets.
- Do not list "intended solutions"; this avoids railroading and keeps it scannable.

### 2. Structure Insight Lenses & Action Taxonomy
Gated observations must use modern action keywords paired with one of the **7 Insight Lenses**:

#### The 3 Action Types:
- **`[Search]`**: Perception, Survival, Medicine, Insight.
- **`[Study]`**: Arcana, Investigation, Nature, Religion, History.
- **`[Influence]`**: Insight, Animal Handling, Deception, Intimidation, Persuasion.

#### The 7 Insight Lenses:
1. **Architectural Intent or Mood**: Engineering purpose, load-bearing stress, intentional kill-zones, optical illusions.
2. **Residual Emotional Energy**: Haunting impressions, psychological trauma, ambient malice or despair.
3. **Patterns in Behavior or Use**: Footprint trails, grease stains, recurring patrol markers, unnatural movements.
4. **Symbolism and Motives**: Heraldry, religious iconology, psychological bait, cult allegiances.
5. **Conflict or Cooperation**: Signs of faction skirmishes, rival mercenary bodies, mercenary badges.
6. **Clues About Current Occupants**: Scent of musk/tallow, recent campfire embers, discarded rations, muffled sounds.
7. **Magical or Mystical Context**: Arcane auras, abjuration wards, planar conduits, glyph signatures.

#### Skill Domains:
- **Arcana**: Magic, planes, Aberrations, Constructs, Elementals, Fey, Monstrosities.
- **History**: Historic events, ruin origin, Giants, Humanoids.
- **Investigation**: Traps, ciphers, riddles, secret seams, mechanical gadgetry.
- **Nature**: Flora, fauna, Beasts, Dragons, Oozes, Plants, hydrothermal/volcanic hazards.
- **Religion**: Deities, cult rites, Celestials, Fiends, Undead.
- **Survival**: Tracks, foraging, natural guides, weather, environmental hazards.
- **Perception**: Anything concealed from casual sensory observation.
- **Insight**: True intentions, psychological bait, social posture.

### 3. Tactical Stunts & Improvised Actions
Every room must provide 2 to 3 pre-calculated stunts allowing players and enemies to weaponize the environment:
- **`Contest / Stunt`**: Opposed Athletics/Acrobatics (e.g., shoving someone into a submerged pit or off a ledge).
- **`Swipe / Hazard`**: Interacting with terrain to create an obstacle (e.g., kicking caltrops, splashing boiling mud).
- **`Stunt`**: Single-check physical feat (e.g., using a shield as a sled, flipping a table for half cover, vaulting a carapace).
- **`Improvised Action`**: Creative object manipulation (e.g., flinging blinding hot tallow, wrapping hands in wet cloaks to haul scorching handles).
- **`Stunt / Reaction`**: Immediate defensive or protective stunt (e.g., deflecting an errant strike away from a fragile membrane).

### 4. Behavioral & Morale Engine (Ammann's Tactical Framework)
Every adversary block must be driven by **Keith Ammann's *The Monsters Know What They're Doing*** tactical framework, pairing innate physiology and ability scores with pre-rolled behavioral tables:

#### Ammann's Ability Score & Tactical Mandate:
- **Strength & Constitution (Brutes & Juggernauts):** Low-agility, high-durability powerhouses (Golems, Umber Hulks, Centaurs) advance directly, absorb incoming burst damage, and weaponize grappling, shoving, and knocking foes prone.
- **Dexterity & Stealth (Skirmishers & Ambushers):** High-Dexterity predators (Displacer Beasts, Scouts, Assassins, Chasmes, Cloakers) never trade static blows in melee. They exploit cover (+2 to +5 AC), reach, superior speeds (fly, climb, swim), bonus action Disengage/Hide, and kite opponents.
- **Intelligence (Planners & Tacticians):**
  - *Int 12+ (Masterminds & Tacticians):* Coordinate roles, focus-fire concentrating casters or low-AC squishy targets, exploit chokepoints, bait party counter-measures, and use environmental hazards.
  - *Int 8–11 (Trained Combatants):* Standard military or pack discipline; focus closest threats, protect commanders.
  - *Int 3–7 (Predators & Constructs):* Operate on predatory instinct, hunger, or rigid programmed guard orders.
  - *Int 1–2 (Mindless):* Reflexive, driven by immediate sensory triggers (open light, loud noise, vibrations).
- **Wisdom (Perception, Insight & Self-Preservation):** High-Wisdom denizens gauge threat accurately, recognize when resources are spent, and know when to disengage. They rarely fight to the death unless trapped.
- **Action Economy & Recharge Discipline:** Creatures deploy powerful recharge features (*Breath Weapons*, *Slow*, *Haste*, top-level spells) immediately in Round 1 to maximize uses across combat, redeploying them the exact round they recharge while maneuvering to catch the most targets with minimal friendly fire.
- **Sensory Asymmetry & Illumination Warfare:** Native denizens weaponize Darkvision, Blindsight, or Tremorsense from beyond the party's light radius (30–60 ft out) and actively target player light sources on Round 1 (buffeting torches, dousing lanterns) to impose the blinded condition.
- **Tactical Analogue Mapping (For Uncovered / Sci-Fi / Unique Creatures):**
  When a creature is not covered in Ammann's published works (e.g. *Expedition to the Barrier Peaks* tech, unique aberrations, or retro-clones), map it to its closest functional 5e analogue by stat profile, ecology, and combat role:
  - *Automaton / Security Robot* $\rightarrow$ Shield Guardian / Helmed Horror (rigid target priority, protective warding).
  - *Worker Robot / Maintenance Drone* $\rightarrow$ Monodrone / Duodrone (linear directives, oblivious until provoked).
  - *Android / Synthetic* $\rightarrow$ Assassin / Mage (stealth infiltration, calculated spell/gadget sequencing).
  - *Vegepygmy / Fungal Thrall* $\rightarrow$ Kobold / Goblin (pack tactics, trap ambushes, terrain concealment).
  - *Alien AI / Supercomputer* $\rightarrow$ Lich / Beholder (lair actions, surveillance, divide-and-conquer room lockdowns).

#### Alexander's Mobility & Stance Taxonomy (Encounter Bleed & VTT Token Engine):
When combat, explosions, or alarms occur, realistic dungeons naturally "bleed" across room boundaries. The engine coordinates encounter bleed through two linked components:
1. **The Audio Horizon (`Rules & Acoustics`):** Establishes the sound physics and alert perimeter (how far noise carries and which rooms are within earshot).
2. **The Stance Resolution (`Mobility Stance`):** Adjudicates exactly how each enemy token within that audio horizon reacts. Even without maintaining an external adversary roster sheet, this classification allows the DM to manage tokens directly on the VTT during combat—knowing instantly whether to advance tokens, redirect patrol routes, hold defensive thresholds, or keep bound guardians in place:
- **Mobile (Default):** Free-roaming denizens that react dynamically to nearby noise. When combat or loud disturbances occur within their alert radius, they advance to investigate or reinforce after 1–2 rounds, retreat when bloodied to rally allies, or fall back to defensive chokepoints.
- **Patrol (Route):** Denizens with an active transit track or circuit between specified chambers or sectors. They cycle on set intervals or turn counts, but immediately break route to converge on combat or loud alarms occurring within their patrol sector.
- **Sentry (Post & Trigger):** Stationed guards tasked with holding a specific post (gate, doorway, watchtower, threshold). They hold their post under standard conditions to prevent incursions, but shift to **Mobile** upon a defined trigger (e.g., alarm horn blown, spotting intruders retreating, or hearing combat within their alert radius for 2+ rounds).
- **Fixed (Binding):** Denizens physically, magically, or hierarchically constrained to a single chamber (e.g., chained beasts, caged monsters, summoned elementals, bound undead, automatons with strict territorial geas, or rooted guardians). They never leave their keyed room to investigate noise or pursue intruders, allowing the DM to keep their tokens firmly in place regardless of dungeon alarms.

#### Pre-Rolled State & Morale Subsystem:
- **Activity Roll**:
  - `d8 (1–2)`: Lounging / Ambushing / Eating.
  - `d8 (3–6)`: Normal Activity / On Guard / Patrolling.
  - `d8 (7–8)`: Sleeping / Resting.
- **Initial Reaction (2d6)**:
  - Starting attitude set based on faction alignment (Hostile, Indifferent, Friendly).
  - Include the **Danger Assessment**: If party looks formidable (radiant magic, heavy armor, numerical superiority), reaction steps down one tier; if party looks weak/bloodied, reaction steps up.
- **Social Matrix**:
  - Exact Persuasion, Intimidation, or Bribe thresholds with concrete dialogue and terms.
- **Combat Start & Determine Surprise (RAW 5e):**
  - **Senses & Alertness**: List occupant Passive Perception and special senses (Darkvision, Blindsight, Tremorsense).
  - **Darkness & Darkvision Adjustment (RAW 5e PHB p. 183–185)**:
    - *Pitch Darkness*: Creatures with Darkvision treat total darkness as *dim light*. Dim light imposes disadvantage on sight-based Perception checks, inflicting a **-5 penalty to Passive Perception** against unlit intruders.
    - *Ambient Dim Light or Party Light*: If the room already has dim light (bioluminescent flora, embers, candles) or the party carries a light source, Darkvision elevates it to bright light—**no -5 penalty applies**.
    - *Blindsight / Tremorsense / Keen Hearing & Smell*: Bypasses visual darkness penalties within the stated range.
  - **Occupant Concealment & Ambush**: Note cover, False Appearance, camouflage, or held trigger actions.
  - **Surprise Adjudication**: Explicitly define the stealth check threshold for the party to surprise the occupants, and the conditions under which the occupants surprise the party.
- **🩸 Dynamic Bloodied Morale Check (Roll 2d6 when $\le$ 50% HP)**:
  - Assessment shift (+1 / -1 tier based on tactical balance).
  - **2–7 [Rally]**: Fight to the death, spiteful drag into hazard, berserk fury.
  - **8–10 [Desperate]**: Disengage, flee toward allies, trigger collapse.
  - **11–12 [Hesitate]**: Call cease-fire, offer parley or bypass password.
  - **13+ [Surrender]**: Drop weapons, beg for quarter, yield hoards.

### 5. Interactive Rollers & AboveVTT Chat Integration

The engine integrates with the local RPG runner (`http://127.0.0.1:26796/roll`) to provide one-click rolling that automatically copies AboveVTT chat commands or evaluated outcomes to the system clipboard for immediate pasting (`Ctrl+V`) into AboveVTT.

#### Roller Inclusion Rules:
- **Include Rollers For:**
  - Anything in the environment that can attack or damage players: mechanical/magical traps, falling hazards, scalding steam/fire pools, collapsing masonry, and sprung poison spikes.
  - Behavioral and reaction engines (`Initial Reaction` and `Bloodied Morale`).
  - Environmental hazard durations (e.g., grease fire burning for `2d4 rounds`).
- **Do NOT Include Rollers For:**
  - **Enemies / Monsters with Token Stat Blocks:** Adversaries placed on the VTT have full interactive sheets in AboveVTT; their attacks, damage, and saves roll natively from their tokens.
  - **Player Rolls:** Player saving throws, perception checks, athletics contests, and thieves' tools checks are driven and rolled by the players themselves.

#### Endpoint Parameter Standards (`http://127.0.0.1:26796/roll`):

| Roll Category | Endpoint Parameters | Example Link & Markdown | Clipboard Result & VTT Behavior |
| :--- | :--- | :--- | :--- |
| **Trap / Hazard Attack** | `cmd=avtt`<br>`d=1d20%2BX`<br>`label=[Name]` | `[**+6 to hit**](http://127.0.0.1:26796/roll?d=1d20%2B6&label=Bear+Trap+Attack&cmd=avtt)` | Copies `/r 1d20+6 Bear Trap Attack`. When pasted into AboveVTT chat, rolls a live 3D attack roll. |
| **Trap / Hazard Damage** | `cmd=dmg`<br>`d=[dice]`<br>`type=[type]`<br>`label=[Name]` | `[**12 (2d8 + 3) piercing damage**](http://127.0.0.1:26796/roll?d=2d8%2B3&type=piercing&label=Bear+Trap&cmd=dmg)` | Copies `/dmg 2d8+3 Bear Trap:piercing`. When pasted into AboveVTT chat, renders an interactive damage card applyable to tokens. |
| **Hazard Duration** | `d=[dice]`<br>`label=[Name]+Duration` | `[**2d4 rounds**](http://127.0.0.1:26796/roll?d=2d4&label=Grease+Fire+Duration)` | Evaluates duration and copies `🎲 Grease Fire Duration: X rounds` to clipboard. |
| **DM Morale / Reaction** | `dm=true`<br>`d=2d6`<br>`label=[Name]` | `[🎲 2d6](http://127.0.0.1:26796/roll?d=2d6&dm=true&label=Goblin+Bloodied+Morale)` | Evaluates 2d6, logs outcome to session ledger, and copies `🎲 [DM] Goblin Bloodied Morale: X (2d6 [...])` to clipboard. |

---

## Step-by-Step Conversion Workflow

When given a raw chapter or adventure module:

1. **Step 1: Front-Matter Extraction**:
   - Read the module's introduction, "General Features", wandering tables, and regional lore.
   - Note environmental constants (dungeon flooding, darkness, acoustic resonance, door construction).
2. **Step 2: Room Staging**:
   - Write `DM Info` with `Dimensions & Space`, `Terrain & Lighting`, `Rules & Acoustics` (only noting disadvantage on Stealth or hearing Perception if applicable, plus alert propagation), and `Clocks & Timers` (omitted if none).
   - Draft the sensory and scale-integrated `Read-Aloud Boxed Text` (Style B: Integrated sensory & spatial preamble). Never mention traps, illusions, or ambushers.
3. **Step 3: Gated Observations**:
   - Convert all passive perception or investigation triggers into 2–4 formatted `[Search]` / `[Study]` / `[Influence]` bullets using the 7 Insight Lenses.
4. **Step 4: DM Synopsis & Pacing Options**:
   - Write the `DM Synopsis` (Situation / How It Works / Pressure-Clock) after the Gated Observations.
   - Write the `Declaration Phase` prompt with 3–4 parenthetical suggestions.
5. **Step 5: Tactical Stunt Generation**:
   - Inspect the room's map and furnishings. Invent 2–3 contextual stunts with DCs 11–15.
6. **Step 6: Monster Behavioral Tuning (Ammann Framework)**:
   - Analyze each adversary's ability scores, senses, speeds, and action economy per Keith Ammann's *The Monsters Know What They're Doing* (or map uncovered/sci-fi creatures to their closest 5e functional analogue).
   - Script the pre-rolled Activity (d8), 2d6 Initial Reaction Roll with Danger Assessment, Social Influence Matrix, **Combat Start & Determine Surprise** (including the RAW Darkness/Darkvision -5 adjustment and ambush triggers), combat strategy (Round 1 openers, recharge discipline, target prioritization, illumination warfare), and clean un-nested 2d6 Dynamic Bloodied Morale Check with tactical assessment shifts.
7. **Step 7: Physical Interactions & Rewards**:
   - Script sensory feedback quotes (`> _"..."_`) for all buttons, levers, doors, and chests.
   - Embed interactive AboveVTT rollers for all trap/hazard attacks (`cmd=avtt`) and damage formulas (`cmd=dmg`).
   - Break down hoards into specific currencies, art objects, and hyperlinked magic items.
