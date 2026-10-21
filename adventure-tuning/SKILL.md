---
name: adventure-tuning
description: Transforms raw published D&D adventures into high-efficiency, DM-ready tactical encounter writeups with localized acoustics, gated observations, interactive stunts, and pre-rolled behavioral/morale engines based on the Dungeon Sheet system.
---

# Adventure Tuning Skill: The Dungeon Sheet In-Situ Engine

This skill guides the transformation of raw, narrative-heavy, or fragmented adventure modules (such as standard TSR/WotC 5e publications) into **operational, modular, table-ready encounter writeups**.

Instead of requiring the Dungeon Master to juggle rules from front-matter or roll multiple tables during play (from `Dungeon Sheet.pdf`), this system **pre-rolls, contextualizes, and bakes the entire Dungeon Turn engine directly into every keyed encounter**.

---

## The Core Design Philosophy

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

## The Master Encounter Schema

Every converted encounter must follow this Markdown structure:

```markdown
## [Number]. [Room Name]

**Turn Cadence & Acoustics:**
- **Time Budget:** 1 Dungeon Turn (10 min) [exploration/investigation/puzzle] | Combat: 1–2 minutes.
- **Audible Range:** Quiet 30 ft (6 sq) | Normal 60 ft (12 sq) | Loud 300 ft (60 sq).
- **Acoustic Environment:** [Specific sound physics, dampening from doors/water, ambient drone, stealth modifiers].
- **Alert Radius:** [Exact sound propagation and cause-and-effect to adjacent numbered areas].

**Dungeon Features:**
- **Ceilings:** [Height, shape, material, moisture, features].
- **Water & Footing / Terrain:** [Depth, difficult terrain, stealth penalties, ripple visibility, footing hazards].
- **Lighting:** [Illumination level, sources, sensory impediments like smoke, soot, or glare].
- **Atmosphere & Sounds:** [Olfactory (smell) and auditory (sound) sensory details].
- **[Doors / Fortifications]:** [Dimensions, materials, hinges/flanges, AC/HP, DC to force or bypass].

> [Evocative boxed read-aloud text strictly limited to immediately perceivable sensory facts]

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

**_Tactics, Reaction & Morale ([Creature Name / Group]):_** <!-- Omit if no creatures -->
- **Enhanced Profile:** [HP, AC, Ability Scores, Key Attacks / Condition Immunities if modified].
- **Current Activity:** [Activity Name] (d8 roll: [Range]). [What the creature is doing when the party arrives].
- **Initial Reaction Roll (2d6):**
  - Starting Attitude: [Hostile / Indifferent / Friendly].
  - **2–7 ([Immediate Attack / Hostile Display]):** [Immediate combat or aggressive posture].
  - **8–10 ([Threatening / Parley Challenge / Allure]):** [Verbal warning, deceptive lure, or conditional stance].
  - **11–12 ([Cautious / Standoff / Stalking]):** [Defensive assessment, stalking, or hesitant pause].
  - _Danger Assessment (DC 10 Wisdom (Insight)):_ If the party appears visibly stronger/weaker, shift reaction up or down one tier.
- **Social Influence Matrix (If Parley / Negotiations Occur):**
  - **[Attitude] DC 0:** [Creature opposes party actions and takes risks to do so].
  - **[Attitude] DC 10 ([Skills]):** [Creature offers no help but does no harm, or gives minor warning].
  - **[Attitude] DC 20 ([Skills / Bribes]):** [Creature does as asked without taking risks, or stands down for bribe].
- **Combat Strategy & Synergy:**
  - _[Phase / Synergy 1]:_ [Pre-buffs, round 1 actions, spell sequencing, chokepoint management].
  - _[Target Priority]:_ [Lightly armored casters, isolated targets, whoever triggers specific hazards].
  - > 🩸 **Real-Time Bloodied Morale Check (Roll 2d6 when ≤ 50% HP):**
    > _Assessment Shift: [Condition making them confident] = +1 tier (toward Rally) | [Condition making them panicked] = -1 tier (toward Surrender)_
    >
    > - **2–7 [Rally / Spite / Berserk]:** [Fights to the death, reckless attacks, vindictive focus].
    > - **8–10 [Desperate / Fallback / Flee]:** [Disengages, dashes for retreat route, triggers emergency defense].
    > - **11–12 [Hesitate / Bargain / Parley]:** [Pauses attacks, yields tactical information or loot in exchange for life].
    > - **13+ [Surrender]:** [Drops weapons, falls prone, begs for quarter, submits passively].

**_Interactions & Triggered Discoveries:_**
- **[Mechanism / Hazard / Puzzle / Secret Door]:**
  > _"[Sensory read-aloud response when triggered or manipulated]"_
  - [Detailed mechanical DC, saving throws, damage formulas, durations, and physical effects].
- **[Interrogating Occupants]:** [Diegetic lore revealed, memory blocks, boundaries of what they know and don't know].
- **[Room Loot & Hoards]:**
  > _"[Sensory description of the treasure]"_
  - Itemized coinage, exact gp values for art/gems, and markdown links for magic items.
```

---

## Detailed Component Reference (The Dungeon Sheet Engine)

### 1. Turn Cadence & Acoustics
Derived directly from the standard Dungeon Turn:
- **1 Dungeon Turn = 10 minutes** of exploration, thorough searching, ritual casting, or spatial navigation.
- **Combat = 1 minute** (including post-fight breath catching).
- **Audible Ranges**:
  - `Quiet`: 30 ft (6 squares) — whispered speech, gentle wading, cautious creeping.
  - `Normal`: 60 ft (12 squares) — speaking cadence, metal armor clinking, walking through ankle water.
  - `Loud`: 300 ft (60 squares) — shouting, combat clatter, explosive spells, breaching doors.
- **Acoustic Dampening**:
  - Closed heavy oak doors reduce sound range by **half to three-quarters**.
  - Ambient noise (boiling lake roar, geyser thrum, howling wind) sets a background threshold where stealth checks against sound succeed automatically or audible range is slashed.
  - Thick stone walls block noise completely.

### 1b. DM Synopsis
A DM-only block placed right after Gated Observations and before the Declaration Phase. It is titled simply `DM Synopsis` (no "read silently" instructions, no solutions list).
- **Three bullets, one or two sentences each**, about 60–90 words total:
  - **The Situation:** what is really going on, including hidden truths.
  - **How It Works:** the core mechanic: trigger, key DCs, damage, numbers.
  - **Pressure / Clock:** what escalates, who reacts, what failure looks like.
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
- **🩸 Dynamic Bloodied Morale Check (Roll 2d6 when $\le$ 50% HP)**:
  - Assessment shift (+1 / -1 tier based on tactical balance).
  - **2–7 [Rally]**: Fight to the death, spiteful drag into hazard, berserk fury.
  - **8–10 [Desperate]**: Disengage, flee toward allies, trigger collapse.
  - **11–12 [Hesitate]**: Call cease-fire, offer parley or bypass password.
  - **13+ [Surrender]**: Drop weapons, beg for quarter, yield hoards.

---

## Step-by-Step Conversion Workflow

When given a raw chapter or adventure module:

1. **Step 1: Front-Matter Extraction**:
   - Read the module's introduction, "General Features", wandering tables, and regional lore.
   - Note environmental constants (dungeon flooding, darkness, acoustic resonance, door construction).
2. **Step 2: Room Staging**:
   - Write `Turn Cadence & Acoustics` for the specific room dimensions, acoustics, and alert radii to neighbors.
   - Write `Dungeon Features`, pulling the relevant global traits into this room.
   - Draft the sensory-only `Read-Aloud Boxed Text`. Never mention traps, illusions, or ambushers.
3. **Step 3: Gated Observations**:
   - Convert all passive perception or investigation triggers into 2–4 formatted `[Search]` / `[Study]` / `[Influence]` bullets using the 7 Insight Lenses.
4. **Step 4: DM Synopsis & Pacing Options**:
   - Write the `DM Synopsis` (Situation / How It Works / Pressure-Clock) after the Gated Observations.
   - Write the `Declaration Phase` prompt with 3–4 parenthetical suggestions.
5. **Step 5: Tactical Stunt Generation**:
   - Inspect the room's map and furnishings. Invent 2–3 contextual stunts with DCs 11–15.
6. **Step 6: Monster Behavioral Tuning (Ammann Framework)**:
   - Analyze each adversary's ability scores, senses, speeds, and action economy per Keith Ammann's *The Monsters Know What They're Doing* (or map uncovered/sci-fi creatures to their closest 5e functional analogue).
   - Script the pre-rolled Activity (d8), 2d6 Initial Reaction Roll with Danger Assessment, Social Influence Matrix, combat strategy (Round 1 openers, recharge discipline, target prioritization, illumination warfare), and 2d6 Dynamic Bloodied Morale Check with tactical assessment shifts.
7. **Step 7: Physical Interactions & Rewards**:
   - Script sensory feedback quotes (`> _"..."_`) for all buttons, levers, doors, and chests.
   - Break down hoards into specific currencies, art objects, and hyperlinked magic items.
