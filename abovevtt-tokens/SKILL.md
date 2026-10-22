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
- Custom stat blocks reside in `notes` with `"statBlock": True` and `"player": False`.
- Placed tokens in `scenes[0]["tokens"]` point to these notes via `token["statBlock"] = note_id` and `token["monster"] = "customStat"`.
- Helper script and data directory:
  - Script: `.agents/skills/abovevtt-tokens/scripts/avtt_tokens.py`
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

---

## 3. Stat Block Formatting & Idempotency

### A. Stat Block Schema (`notes`)
To avoid creating duplicate notes across multiple runs, look up existing notes by title before generating a new UUID:
```python
note_id = next(
    (
        k
        for k, v in data["notes"].items()
        if v.get("statBlock") is True
        and v.get("title").strip().lower() == creature_title.strip().lower()
    ),
    f"{slug}-{uuid.uuid4()}",
)
```

### B. AboveVTT Journal Template Styling
Embed AboveVTT's official `content_styles` CSS in `<style id='contentStyles'>` inside the note HTML so fonts, headings, and tables match the native journal themes and interact cleanly with DM browser extensions (e.g. Stylus).

### C. Token Combat Wiring
```python
token["statBlock"] = note_id
token["itemId"] = note_id
token["monster"] = "customStat"
token["itemType"] = "myToken"
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
