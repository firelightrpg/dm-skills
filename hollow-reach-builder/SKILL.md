---
name: hollow-reach-builder
description: Generates high-efficiency, 2-to-4-hour West Marches adventures for the Hollow Reach campaign using the 5-Room Dungeon / Three-Act Structure framework, dynamic adversary rosters, 30/20 combat math, and tactile layered challenges.
---

# Hollow Reach Adventure Builder: Rapid West Marches One-Shot Engine

This skill automates the creation of modular, high-tension, 2-to-4-hour one-shot adventures tailored for the **Hollow Reach** West Marches campaign (centered around the hub town of **Wayfare**).

It synthesizes:
- **Johnn Four's 5-Room Dungeon** overlaid with **Syd Field's Three-Act Screenwriting Structure** and an abridged **Hero's Journey**.
- **Justin Alexander's Dynamic Dungeons**: Adversary Rosters with active mobility stances (*Patrol*, *Mobile*, *Stationary*) and 1-in-6 adjacent room alert triggers.
- **The 30/20 Combat Rule**: Hard capstone encounter CR math (CR ≤ 1.5 × APL), tactical enemy behaviors informed by `themonstersknow.com`, and a ≤ 50% HP bloodied morale parley/retreat engine.
- **Tactile Challenge Design**: Traps, locks, and secrets engineered as multi-layered, interactive physical scenes (Clue → Interaction → Teamwork/Solution) using the **3-Clue Rule**, with ability checks serving as safety nets rather than progress-blocking gates.
- **Strict Session Economy**: Designed specifically to wrap in **2 to 4 hours** with **at most 4 primary encounters** (ideally 2 combat + 2 exploration/puzzle/roleplay), plus 1 optional return ambush buffer.

---

## 1. West Marches Operational Flow (Hollow Reach Lifecycle)

```mermaid
flowchart TD
    R[Rumor on Server Board] -->|3+ Player Signups| P[Launch Prep]
    P --> G[Generate via hollow-reach-builder]
    G --> V[Import Adventure JSON to Main Campaign]
    V --> S[Run Session: 2-4 Hours strictly in media res]
    S --> W[Wrap-Up & Fast Travel Back to Wayfare]
    W --> D[Post DM Results & Rewards]
    D --> A[Players Post in after-action-reports]
    A -->|Earns Inspiration| F[AARs Spawn Next Band Rumors]
    F --> R
```

### The 6 Golden Rules of Hollow Reach Prep:
1. **Greenlit by Signups:** An adventure is only prepped after a rumor gets 3+ interested players.
2. **Fast Travel & *In Media Res*:** Assume the party fast travels from Wayfare to the adventure site. Start the session *in media res* at the entrance threshold.
3. **Pacing Guarantee:** Keep the primary adventure to **4 encounters maximum** (no more than 3 combat; target 2 combat + 2 exploration/puzzle/social).
4. **Teamwork Over Heroics:** Every puzzle, obstacle, and secret requires cooperation or pairs (e.g., hold a lever while another prying a stone; shield cover while picking a lock). Success or failure is party-wide.
5. **Emergent Server Storytelling:** Adventure outcomes must ripple into Wayfare. Player writeups in `#after-action-reports` grant inspiration and directly inspire the next band's rumors.
6. **Clean VTT Workflow:** Build in a separate blank campaign/folder → export as `.json` → import into the main campaign on game day → archive and delete the folder after the game.

---

## 2. Modes of Operation & The Map-First Principle

A great DM workflow begins with a **strong premise**, immediately followed by the **battlemap**. The map's spatial architecture (its chokepoints, elevation changes, chambers, and natural contours) leads and inspires every subsequent encounter, trap, secret, and tactical element.

```mermaid
flowchart TD
    A["1. Concept & Band Math (Rumor, Stakes, Tone)"] --> B["2. Battlemap Generation / Selection (AI or UVTT)"]
    B --> C["3. Map Vision Inspection (Read Chamber Bounds, Doors & Elevation)"]
    C --> D["4. Keyed Adventure Module Drafting (Markdown Text matches Map)"]
    C --> E["5. AboveVTT File Co-Generation (Walls, Statblock Notes, Tokens)"]
    D --> F["Turnkey Adventure Package (Markdown + .abovevtt)"]
    E --> F
```

### Mode A: Interactive Co-Pilot (Default)
The agent acts as a creative partner, guiding the DM through a snappy 5-phase dialogue:
1. **Intake & Band Math:** DM provides party band/level, player count, and starting rumor/hook. Agent confirms CR caps and time budget.
2. **Concept & Dramatic Question:** Propose the 3-act narrative arc (Inciting Incident → Rising Confrontation → Resolution) and hidden conspiracy/twist.
3. **Map-First Generation / Selection:** Generate or select the top-down battlemap first (via `image-generator` or Watabou/UVTT).
4. **Visual Geometry Inspection & Keying:** Inspect the rendered map image to determine true chamber dimensions, door openings, stairs, and natural features, assigning Areas A1 through A5 to real visual spaces.
5. **Turnkey Drafting:** Draft the keyed adventure markdown module and co-generate the AboveVTT export file simultaneously against the real visual geometry.

### Mode B: Express Generator
The DM provides a single prompt:
`Generate adventure: [Band Level, e.g., Greenhorns Lvl 2], [Rumor Hook, e.g., Sunken crypt beneath Miller's Creek], [Tone/Tags, e.g., flooded, ancient, ghouls]`
The agent executes the full Map-First pipeline autonomously: generates concept → renders battlemap → inspects map geometry → drafts markdown module with scene art → compiles `.abovevtt` file.

---

## 3. Structural Mapping Blueprint

Every adventure treats its environment as a 5-room dungeon—whether it is an ancient reliquary, a flooded cavern, an abandoned surface farm, or a cursed swamp glade.

```
[Room 1: Entrance / Guardian] ─── (Threshold / Inciting Incident)
              │
              ▼
[Room 2: Puzzle / Challenge]   ─── (Crossing Threshold / 3-Clue Discovery)
              │
              ▼
[Room 3: Trick / Setback]      ─── (Rising Action / The Twist / Betrayal Revealed)
              │
              ▼
[Room 4: Climax / Big Battle]  ─── (The Ordeal / Confrontation / Dramatic Question Answered)
              │
              ▼
[Room 5: Reward / Revelation]  ─── (The Return / Layered Trapped-Locked Secret + Server Hook)
              │
              ▼ (Optional: If Session < 2 Hours)
[Bonus Buffer: Return Ambush]  ─── (Tactical transit chokepoint before Wayfare)
```

| Room | 5-Room Archetype | 3-Act Structure | Hero's Journey | Mechanical Purpose |
|---|---|---|---|---|
| **A1** | **Entrance / Guardian** | Act 1: Setup | Crossing the Threshold | Establishes atmosphere, *in media res* stakes, and tests party readiness with a low/mid combat sentry or environmental barrier. |
| **A2** | **Puzzle / Challenge** | Act 2: Rising Action | Tests & Trials | Non-combat encounter engaging the whole party (Athletics, Arcana, Social, Tools). Implements the **3-Clue Rule**. |
| **A3** | **Trick / Setback** | Act 2: Complication | The Approach / Complication | A sudden revelation, hazard, betrayal evidence, or resource drain that subverts expectations and raises the stakes for the climax. |
| **A4** | **Climax / Big Conflict** | Act 3: Confrontation | The Ordeal | The capstone battle. High tactical difficulty with terrain favoring the villain. Enemy uses `themonstersknow.com` tactics and checks bloodied morale at ≤ 50% HP. |
| **A5** | **Reward / Revelation** | Act 3: Resolution | The Return Home | Tangible loot protected by a **Layered Trapped/Locked Secret**, plus the critical evidence/item that answers the session's dramatic question and seeds future rumors. |
| **Bonus** | **Return Ambush** | Epilogue Buffer | Road Back | Optional chokepoint encounter deployed *only* if the party finishes in under 2 hours. Focuses on escape routes and tactical terrain. |

---

## 4. Encounter Mechanics & Math Standards

### 1. The 30/20 Combat Formula
```text
Max Capstone CR = 1.5 × APL (Average Party Level)
Guardian CR     = 1.0 × APL to 1.25 × APL
```

- **Greenhorns (APL 1–2):** Guardian CR 1–2; Boss CR 3–4 (accompanied by 2–3 CR 1/8 minions).
- **Adventurers (APL 3–4):** Guardian CR 2–3; Boss CR 5–6 (with tactical cover and terrain hazards).
- **Veterans (APL 5–7):** Guardian CR 5–6; Boss CR 7–9 (with dynamic lair actions or reinforcements).

### 2. Adversary Action Groups & Dynamic Checks
Adversaries are placed on a dynamic roster with explicit action stances:
- **Patrol:** Moves on a predetermined circuit between 2 rooms.
- **Mobile (Default):** Stationed in a room, but rolls a **1-in-6 check** every exploration turn to wander into adjacent corridors, and automatically moves to investigate loud combat or thunder spells after 1–2 rounds.
- **Stationary:** Bound to a specific chamber (chained beast, bound undead, automaton). Does not pursue beyond its room threshold.

### 3. Bloodied Morale Engine (≤ 50% HP)
*No intelligent creature wants to die.* When an intelligent foe drops below 50% HP:
- It uses its turn to parley, surrender, or negotiate (offering loot, secrets, or defection).
- If cornered with no way out, it seeks a desperate tactical withdrawal or uses environmental hazards (dropping portcullises, kicking over oil slicks).

### 4. Tactile Layered Secret, Lock & Trap Architecture
Avoid flat, single-roll DC checks. Every significant obstacle uses the **3-part physical challenge model**:
- **Layered Secret:** Clue (visible scuff marks or mortar gaps) → Interaction (recessed stud or counterweight) → Solution (two characters acting simultaneously).
- **Layered Lock:** Clue (smudges on specific rivets or tactile hinge play) → Interaction (testing pressure points) → Solution (tactile sequence requiring two hands or multiple tools).
- **Layered Trap:** Descriptive Clue (giving paving stone, slit in ceiling) → Trigger Condition (releasing weight triggers spears) → Player Agency Choices (counterweight, wedge, dodge dive, jump clear).
- *Rule for Dice Rolls:* Player character ability checks are **lifelines** for when players are stuck, not prerequisite gates to interact.

### 5. Mandatory Room Dressing (3+ Interactive Items)
Every keyed room must include at least three tactile objects from the [Dressing & Tactics Toolkit](file:///home/grim/github/dm-skills/hollow-reach-builder/resources/dressing-and-tactics.md) (e.g., barrels, sacks of flour, lantern oil jugs, chains, cauldrons, heavy furniture, mirrors, brazier coals).

---

## 5. Master Output Format

When generating an adventure document, use this standardized Markdown schema:

```markdown
---
audio:
  ambient: "ambient dark"
  combat: "battle"
  triumph: "triumph"
---

# [Adventure Title]

**Location:** [Sub-region west/east/south of Wayfare]  
**Band & Level:** [e.g. Greenhorns (APL 2)] | **Estimated Play Time:** 2–4 Hours  
**Audio Control:** [▶ Ambient](http://localhost:26796/trigger?playlist=ambient+dark) | [⚔ Combat](http://localhost:26796/trigger?playlist=battle) | [🏆 Triumph](http://localhost:26796/trigger?playlist=triumph)  
**Map Link:** [Wyrmbox direct download URL or seed tags]  

---

## Adventure Synopsis & Narrative Arc
- **The Hook & Inciting Incident:** [The public rumor posted in Wayfare and why players signed up].
- **The Hidden Truth:** [The underlying conspiracy, crime, or forgotten history causing the crisis].
- **The Dramatic Question:** [The core question answered at the climax: e.g. "Can the party seal the reliquary before the shade awakens?"]
- **Pacing & Encounter Budget:** 4 primary rooms (2 combat, 2 non-combat) + 1 optional return ambush.

---

## In Media Res Opening
> [2–3 evocative, scripted sentences placing the party directly at the threshold of the site, already geared up after fast traveling from Wayfare.]

---

## Keyed Encounter Areas

### [Area Code, e.g. A1]. [Room Name] — [Role, e.g. Guardian / Threshold]
**DM Info:**
- **Dimensions & Space:** [Footprint, ceiling height, elevation, exits].
- **Terrain & Lighting:** [Footing, light level, difficult terrain, water depth].
- **Acoustics & Bleed:** [Ambient sound, propagation to adjacent rooms, stealth modifiers].

> **Read-Aloud:**
> [Scripted, flowing narrative prose in complete sentences (following the TSR / WotC gold-standard like White Plume Mountain). Naturally integrate the chamber dimensions and architectural footprint into the first sentence—e.g. "This long stone chamber stretches 30 feet wide and 70 feet south beneath a heavy 15-foot vaulted ceiling..." Weave sight, sound, smell, and temperature directly into the description without bulleted lists or spoilers.]

![](https://wyrmbox.com/s/<token>/download)

**Gated Observations:**
- **Passive Perception [DC]:** [Tangible clue or subtle sensory warning].
- **Investigation / Arcana / History [DC]:** [Deduction regarding recent events, traps, or lore].
- **Insight [DC]:** [Motive or emotional state of occupants or dead figures].

**Interactive Dressing (3+ Objects):**
1. **[Object 1]:** [Tactile description and improvised combat/utility stunt].
2. **[Object 2]:** [Tactile description and improvised combat/utility stunt].
3. **[Object 3]:** [Tactile description and improvised combat/utility stunt].

**Adversary Roster & Tactics:** *(Omit if non-combat)*
- **Creature(s):** [Name, CR, Count, Action Group: Patrol / Mobile / Stationary].
- **Tactics:** [Home-turf advantage, target priority from themonstersknow.com].
- **Morale Engine (50% HP):** [Parley offer, surrender condition, or tactical retreat].

**Layered Challenge / Secret:** *(If present)*
- **Clue:** [Visible hint].
- **Interaction:** [Physical testing].
- **Solution:** [Tactile or teamwork resolution].

---

[Repeat for A2: Puzzle/Challenge, A3: Trick/Setback, A4: Climax/Conflict, A5: Reward/Revelation]

---

## Buffer Ambush: [Encounter Name]
*(Deploy only if session wraps in under 2 hours)*
- **Trigger & Locale:** [Transit chokepoint between the dungeon and Wayfare].
- **Enemies:** [Adversaries sent to erase evidence or claim the bounty].
- **Tactical Terrain:** [3+ terrain features: felled trees, high ground, bridge railings, overhead rocks].
- **Alternate Win Conditions:** [Fleeing to Wayfare, causing a rockslide, capturing the leader].

---

## Post-Adventure Server Pack (Wayfare Echoes)

### 1. DM Session Log & Rewards
- **Base Coin & Magic Items:** [Itemized rewards].
- **Civic Favor / Faction Standings:** [Reputation changes with Mayor Andrel, Guilds, or Wayfare factions].

### 2. Player After-Action Report (AAR) Prompt
> *"Post your character's perspective in `#after-action-reports` to earn 1 Inspiration for your next expedition! Tell Wayfare what you saw beneath Stillwater Hollow..."*

### 3. Server Rumor Ripple Effects (Seeds for Next Sessions)
1. **[Rumor Seed 1]:** [Immediate local consequence of their success/failure].
2. **[Rumor Seed 2]:** [Conspiracy ripple involving authorities or rival factions].
3. **[Rumor Seed 3]:** [An intact sister site discovered elsewhere on the map].
```

---

## 6. VTT Integration & AboveVTT Schema Compliance

When generating or preparing `.abovevtt` export files programmatically:
1. **Base64 Encoding:** The `.abovevtt` file must be a base64-encoded UTF-8 string containing the root campaign JSON.
2. **Pure 90° Orthogonal Cartography & Strict Uniform Grid Tiling:**
   - Always prompt battlemaps as **strictly 90-degree orthogonal overhead bird's-eye view** on a pure black exterior void (zero isometric tilt or vertical perspective).
   - Reserve 3D perspective / 2.5D isometric rendering exclusively for narrative scene handouts and chat splash art.
   - **Visual Style Benchmark ("Neutral Party" Aesthetic):**
     - Aim for a grounded, hand-painted tabletop cartography style inspired by **Neutral Party**: earthy, naturalistic color palettes (mossy slate, dark mud, weathered timbers), subtle atmospheric lighting and weather sheen (rain puddles, soft fog, cold stone), and organic environmental storytelling props (fallen logs, crooked headstones, rusted ironwork).
     - Keep textures painterly and clean, avoiding hyper-saturated glows or visual clutter that obscures tokens or conflicts with the AboveVTT digital grid.
   - **Strict Uniform Integer Grid Tiling Rule ($X \times X$ Snapping):**
     - Organic AI-generated dungeon maps naturally exhibit fractional scaling drift from chamber to chamber (e.g. a room rendering at 5.1 squares wide or 6.9 squares tall), causing VTT grids to drift out of sync across different sections of the dungeon.
     - To eliminate drift and ensure zero offset `(0, 0)` across the entire map, **normalize each room independently** before assembling the composite: crop each chamber and resample/scale its dimensions to exact integer multiples of the chosen grid pitch $X \times X$ (e.g., 50 px or 70 px per 5-ft square).
     - Composite all chambers, corridors, and stairs onto the canvas snapped strictly to exact integer grid line boundaries (`x % X == 0`, `y % X == 0`).
     - Always include an exterior staging space (such as a 10-ft wide descending staircase and surface mausoleum landing, at least 2 × 3 or 2 × 4 squares) so the DM can comfortably drop 5–6 player tokens before entering the first subterranean chamber.
     - **Recommended Grid Pitch (50 px Standard vs 70–90 px):**
      - While physical tabletop displays and 1:1 monitor zoom often target 70–90 px (~1 physical inch), **50 px per 5-ft square is the recommended gold-standard default for browser VTT play**.
      - In remote browser sessions, players rarely view at 1:1 zoom—they zoom out to 40%–60% to view entire tactical encounter spaces and line-of-sight cones at a glance.
      - A 50 px grid pitch keeps a complete 30 × 20 room complex at a lightweight 1500 × 1000 px (< 400 KB), ensuring instant WebDAV asset streaming, zero WebGL canvas memory spikes or rendering stutter, and maximum tactical clarity.
    - Set AboveVTT scene parameters to match the exact integer grid pitch with `offsetx: "0"` and `offsety: "0"`, ensuring instant, flawless grid alignment without manual wizard adjustments.
3. **Gridline-Centered Wall Drawing (Dungeondraft Style):**
   - Walls must be drawn **centered directly over the grid boundary lines**, straddling half-stone into the wall.
   - This ensures line-of-sight rays stop halfway through the masonry, illuminating the stone face for players while completely preventing tokens from clipping into the walls.
4. **Schema Integrity:**
   - `tokencustomizations` **MUST** be an array `[]`, not a dict `{}` (a dictionary crashes AboveVTT's `Settings.js` `forEach` call).
   - `soundpads` **MUST** be an empty dict `{}`.
   - `notes` is a dictionary of statblock notes keyed by UUID, containing valid D&D Beyond HTML creature statblocks equipped with AboveVTT roll attributes (`data-exp`, `data-mod`, `data-rolltype`, `data-actiontype`).
   - `scenes` must contain a folder object (`itemType: "folder"`, `parentId: "scenesFolder"`) and scenes assigned to `parentId: folder.id`.
5. **Asset Reachability:**
   - `player_map` must be a live, reachable direct-download URL (e.g. hosted on Wyrmbox via Nextcloud public share). A 404 or dead link causes AboveVTT's `load_scenemap` to hang permanently on an infinite spinner.
   - Built-in number tokens (`https://abovevtt-assets.s3.eu-central-1.amazonaws.com/numbers/{n}.png`) require single digits without leading zeroes (`1.png`, `2.png`, not `01.png`), otherwise Amazon S3 returns 403 Forbidden.
6. **Drawings Layer Syntax:**
   - Walls: `['line', 'wall', 'rgba(0, 255, 0, 1)', x1, y1, x2, y2, 6, 1, false, '', '']`
   - Closed Doors: `['line', 'wall', 'rgba(255, 100, 255, 1)', x1, y1, x2, y2, 12, 1, false, '', '']`
   - Secret Doors: `['line', 'wall', 'rgba(100, 0, 255, 1)', x1, y1, x2, y2, 12, 1, false, '', '']`
   - All drawing coordinates `(x, y)` must be in pixel space (`grid_square * VPPS`).

---

## 7. Automated Scene Art & Nextcloud Image Injection Workflow

When generating adventures with visual scene art:

1. **Prompt Formulation:**
   - Extract the room's boxed read-aloud text, spatial scale, and lighting.
   - Format prompt: `First person view, Fantasy art, hand painted, atmospheric lighting, moody. [Sensory read-aloud details + architectural features + lighting]`.
2. **Subagent Generation:**
   - Launch `image-generator` subagents across missing room prompts in parallel.
3. **Bulk-Store Storage & WebDAV Sync Standard:**
   - Always move/copy rendered artifacts and battlemap images to the **bulk store**: `~/Nextcloud/bulk-store/gaming/DnD/5e/Adventures/Hollow Reach/<Adventure Name>/[cover|battlemap|a1|a2...].jpg`.
   - **Do NOT store large battlemaps or high-resolution scene art in the primary Nextcloud store** (`~/Nextcloud/DnD/...`); the bulk-store (`~/Nextcloud/bulk-store/gaming/DnD/...`) has abundant capacity and is fully backed up.
   - Call `sync` and allow a brief pause (2–5 seconds) to ensure local `davfs2` caches flush to the Nextcloud server before querying shares.
4. **Public Share Generation & Insertion:**
   - Run `python3 /home/grim/github/dm-skills/adventure-tuning/scripts/nextcloud_share.py <path_to_image>` to query or create public direct-download URLs via the Nextcloud OCS API.
   - Embed the direct links (`![](https://wyrmbox.com/s/<token>/download)`) immediately below each area's read-aloud blockquote and at the top of the adventure module.

---

## 8. Reference Files

- [Canonical Gold-Standard Example: The Dry Well](file:///home/grim/github/dm-skills/hollow-reach-builder/resources/the-dry-well.md)
- [Dressing, Tactile Mechanics & Adversary Tactics Toolkit](file:///home/grim/github/dm-skills/hollow-reach-builder/resources/dressing-and-tactics.md)
