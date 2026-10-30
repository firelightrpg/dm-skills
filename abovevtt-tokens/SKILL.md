---
name: abovevtt-tokens
description: Updates placed tokens in AboveVTT (.abovevtt) exports with custom stat blocks, ability modifiers/saves, HP, AC, vision, token art, and distinct high-contrast border colors from adventure markdown files or 5e.tools data.
---

# AboveVTT Custom Token & Stat Block Injection Skill

This skill automates synchronizing placed placeholder tokens in an exported `.abovevtt` file with custom creature stat blocks from adventure notes or bestiaries, with strict guardrails to preserve all DM visual customizations.

---

## 1. File Format & Architecture

- `.abovevtt` files are **Base64-encoded UTF-8 JSON** (typically tab-indented `indent="\t"`).
- Root keys: `version`, `scenes`, `tokencustomizations`, `notes`, `journalchapters`, `soundpads`.
- Custom stat blocks reside in `notes` with `"statBlock": True` and `"player": True` (AboveVTT custom tokens).
- `notes[note_id]` contains:
  - `id`: unique UUID
  - `statBlock`: `True`
  - `player`: `True`
  - `plain` and `text`: identical canonical D&D Beyond stat block HTML (using `mon-stat-block ddbc-creature-block` classes)
  - `abilityTracker`: dict of tracked charges/spells (e.g. `{"create undead": 3}`)
- Placed tokens in `scenes[0]["tokens"]` point to these notes via `token["statBlock"] = note_id`, `token["itemId"] = note_id`, `token["itemType"] = "myToken"`, `token["listItemPath"] = "/My Tokens/<Name>"`, and `token["monster"] = "customStat"`.
- Helper script, resources and data directory:
  - Token Script: `.agents/skills/abovevtt-tokens/scripts/avtt_tokens.py`
  - UVTT Importer: `.agents/skills/abovevtt-tokens/scripts/uvtt_to_abovevtt.py`
  - Mask Importer: `.agents/skills/abovevtt-tokens/scripts/mask_to_abovevtt.py`
  - Canonical Reference Fixtures (from native AboveVTT capture):
    - `.agents/skills/abovevtt-tokens/resources/orcus_reference.json` (raw token and note dictionary)
    - `.agents/skills/abovevtt-tokens/resources/orcus_statblock.html` (standalone DDB HTML stat block)
  - Creature data: `.agents/skills/abovevtt-tokens/data/<adventure>.json`

---

## 2. Token Field Guardrails

When updating tokens, adhere to the following rules:

### A. Protected Fields (NEVER Overwrite)
Never touch or reset the following properties:
- `name` (unless adding numeric suffixes to identical duplicate copies)
- `imgsrc` & `alternativeImages` (preserve DM's selected artwork)
- `tokenStyleSelect` (`"virtualMiniCircle"`, `"circle"`, etc.)
- `square` & `legacyaspectratio`
- `top`, `left`, `offset` (preserve map placement)
- `hidden`

### B. Size Synchronization
- Sync token grid footprint to match the stat block size category:
  - **Tiny**: `gridSquares: 0.5`, `size: 17.5`, `sizeId: 2`
  - **Small / Medium**: `gridSquares: 1`, `size: 35`, `sizeId: 3` (Small) or `4` (Medium)
  - **Large**: `gridSquares: 2`, `size: 70`, `sizeId: 5`
  - **Huge**: `gridSquares: 3`, `size: 105`, `sizeId: 6`
  - **Gargantuan**: `gridSquares: 4`, `size: 140`, `sizeId: 7`

### C. Border Management
- **Unique Creatures (single instance on scene):**
  - Set `disableborder: True`.
- **Duplicate Creatures (multiple instances on scene, e.g., minions/wights):**
  - Set `disableborder: False`.
  - Assign distinct, high-contrast hex border colors from `PALETTE` so players can target them by color (e.g., *"I attack the green one"*).
  - Number names sequentially (`<Name>`, `<Name> 2`, `<Name> 3`) sorted spatially by `(top, left)`.

### D. Visual Style & Footprint Standards
- **Token Style:** Set `tokenStyleSelect: "virtualMiniCircle"` and `tokenBaseStyleSelect: "default"` (Virtual Mini with Round Base).
- **HP Visibility:** Set `hidehpbar: True` (Only Show HP Values on Hover).
- **Footprint Scaling:** Token `size` must match `gridSquares * vpps` (e.g. for standard 70px grid: Medium = 70px, Large = 140px, Huge = 210px).

### E. 2014 vs. 2024 D&D Beyond Monster IDs & Artwork
- **2014 Monster Manual IDs:** For 2014 5e campaigns, always bind to 2014 Monster Manual IDs (16xxx/17xxx, e.g., Carrion Crawler is `17138`, Commoner is `16829`, Scout is `17007`, Bugbear is `16817`). Never use 2024 Free Rules IDs (5xxxxxx) as they enforce 2024 stat blocks and 2024 artwork.
- **Artwork Standards:**
  - `imgsrc`: High-resolution transparent PNG or webp cutout mini (e.g., `https://5e.tools/img/bestiary/tokens/MM/<Creature>.webp` or DDB `largeAvatarUrl`).
  - `alternativeImages`: Store `[transparent_token_cutout, headshot_jpeg_avatar]`.
- **Offline / Non-SRD Zero-Spinner Rule:** If a creature is non-SRD or custom, inject canonical interactive HTML stat blocks directly into `data["notes"]` and bind via `statBlock: note_id`. This prevents infinite loading spinners from unauthenticated DDB public API calls.

### F. Room Number Markers
- **Asset Source:** `https://abovevtt-assets.s3.eu-central-1.amazonaws.com/numbers/{room_num}.png`
- **Standard Properties:** `tokenStyleSelect: "circle"`, `disableborder: True`, `hidden: True`, `locked: False`, `placeType: "count"`, `hidehpbar: True`.

---

## 3. Stat Block Formatting & Idempotency

### A. Stat Block Schema (`notes`)
AboveVTT stores custom tokens as notes with identical `plain` and `text` HTML fields. To avoid creating duplicate notes across multiple runs, look up existing notes by title or header link before generating a new UUID:
```python
def find_note_id(notes, name):
    name_clean = name.strip().lower()
    for nid, n in notes.items():
        if not n.get("statBlock"):
            continue
        if n.get("title", "").strip().lower() == name_clean:
            return nid
        # Check title in DDB HTML name-link
        m = re.search(r'class="mon-stat-block__name-link[^"]*">\s*([^<]+?)\s*</a>', n.get("plain", ""))
        if m and m.group(1).strip().lower() == name_clean:
            return nid
    return str(uuid.uuid4())
```

### B. Native D&D Beyond HTML & Roll Buttons (No CSS Bloat)
AboveVTT natively injects stylesheets for standard D&D Beyond stat blocks. **Do NOT embed 50KB `<style id='contentStyles'>`**.
Use the canonical structure captured from AboveVTT tokens:
- **Root wrapper**:
  ```html
  <div id="content" class="main content-container" style="padding:0!important">
    <section class="primary-content" role="main">
      <div class="monster-details">
        <div class="more-info details-more-info" style="padding: 2px;">
          <div class="detail-content">
            <div class="mon-stat-block ddbc-creature-block" style="column-count: 1;margin:0;">
              ...
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
  ```
- **Interactive Check & Save Buttons (`avtt-roll-button`)**:
  ```html
  <button data-exp="1d20" data-mod="+2" data-rolltype="Check" data-actiontype="Initiative" class="avtt-roll-button">+2</button>
  <button data-exp="1d20" data-mod="+8" data-rolltype="check" data-actiontype="STR" class="avtt-roll-button">(+8)</button>
  <button data-exp="1d20" data-mod="+10" data-rolltype="save" data-actiontype="DEX" class="avtt-roll-button">+10</button>
  ```
- **Clickable Dice Notation Spans (`data-dicenotation`)**:
  ```html
  <span data-dicenotation="1d20+19" data-rolltype="to hit" data-rollaction="Wand of Orcus">+19</span>
  <span data-dicenotation="3d8+8" data-rolltype="damage" data-rollaction="Wand of Orcus" data-rolldamagetype="bludgeoning">(3d8 + 8)</span>
  ```
- **Note Object Properties**:
  ```python
  notes[note_id] = {
      "id": note_id,
      "player": True,
      "statBlock": True,
      "plain": html,
      "text": html,
      "abilityTracker": ability_tracker or {},
  }
  ```

### C. Token Combat Wiring
```python
token["statBlock"] = note_id
token["itemId"] = note_id
token["monster"] = "customStat"
token["itemType"] = "myToken"
token["listItemPath"] = f"/My Tokens/{creature_name}"
token.pop("stat", None)  # CRITICAL: strip DDB numeric ID to decouple vanilla sheet
token["disablestat"] = False
token["hidestat"] = False
token["armorClass"] = ac
token["hitPointInfo"] = {"maximum": hp, "current": hp, "temp": 0}
token["customInit"] = f"{(dex - 10) // 2:+d}"
token["customStat"] = {
    "0": {"mod": str_mod, "save": str_save},
    "1": {"mod": dex_mod, "save": dex_save},
    "2": {"mod": con_mod, "save": con_save},
    "3": {"mod": int_mod, "save": int_save},
    "4": {"mod": wis_mod, "save": wis_save},
    "5": {"mod": cha_mod, "save": cha_save},
}
```

---

## 4. Execution Workflow

1. **Dump / Inspect**: Decode `.abovevtt` to JSON or inspect token names, ignoring map labels (`/numbers/` images or pure digits) and lighting effect tokens.
2. **Dry Run & Match Table**:
   Run `avtt_tokens.py` without `--write` to verify token matching and size/border plans:
   ```bash
   python3 .agents/skills/abovevtt-tokens/scripts/avtt_tokens.py input.abovevtt data.json
   ```
   Confirm with the user that the matched tokens and untouched tokens look correct.
3. **Execute & Increment Export**:
   Run with `--write --out <new_export>.abovevtt` so the previous export remains intact as a fallback.
   ```bash
   python3 .agents/skills/abovevtt-tokens/scripts/avtt_tokens.py input.abovevtt data.json --write --out output.abovevtt
   ```
4. **Markdown Sync**: Ensure any custom token avatars are reflected in the corresponding adventure encounter markdown.
