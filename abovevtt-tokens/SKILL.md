---
name: abovevtt-tokens
description: Updates placed tokens in AboveVTT (.abovevtt) exports with custom stat blocks, ability modifiers/saves, HP, AC, vision, token art, and distinct high-contrast border colors from adventure markdown files or 5e.tools data.
---

# AboveVTT Custom Token & Stat Block Injection Skill

This skill captures the workflow for updating placed placeholder tokens in an exported `.abovevtt` file with custom monster stat blocks (either tuned profiles in local adventure `.md` files or 5e.tools bestiary JSON data).

---

## 1. File Format & Encoding

- `.abovevtt` files are **Base64-encoded UTF-8 JSON** (typically tab-indented `indent="\t"`).
- Root keys: `version`, `scenes`, `tokencustomizations`, `notes`, `journalchapters`, `soundpads`.
- Always decode via `json.loads(base64.b64decode(raw).decode("utf-8"))` and re-encode via `base64.b64encode(json.dumps(data, indent="\t").encode("utf-8"))`.
- Filter out hidden lighting/effect tokens when scanning `scene["tokens"]` by checking `not token.get("auraislight") or bool(token.get("name"))` (light tokens typically have `name: ""` and `tokenStyleSelect: "definitelyNotAToken"`).

---

## 2. Creating the Custom Stat Block Note (`data["notes"]`)

AboveVTT stores custom monster stat blocks in the root `notes` dictionary with `"statBlock": True`. When a user clicks the stat block button on a token in AboveVTT, it renders `note["text"]` and parses rollable dice/attack syntax (`+X to hit`, `XdY + Z`) directly from the HTML.

---

<img width="5120" height="2880" alt="image" src="https://github.com/user-attachments/assets/4b315511-899b-4ae7-a688-784c24c97a76" />

---


### Note Object Schema

```python
note_id = f"{slug}-{uuid.uuid4()}"
data["notes"][note_id] = {
    "title": name,
    "text": html_stat,
    "plain": plain_stat,
    "player": False,
    "statBlock": True,
    "id": note_id,
}
```

### HTML & Plain-Text Generators

```python
def make_html_stat(
    name,
    meta,
    ac,
    ac_note,
    hp,
    hp_dice,
    speed,
    s,
    d,
    c,
    i,
    w,
    ch,
    saves,
    skills,
    resists,
    immunes,
    cond_immunes,
    senses,
    langs,
    cr,
    xp,
    pb,
    traits,
    actions,
    bonus,
    reactions,
):
  lines = [
      (
          '<div style="font-family: \'Scala Sans Offc\', Roboto, Helvetica,'
          ' sans-serif;" class="Basic-Text-Frame stat-block-background'
          ' one-column-stat">'
      ),
      (
          '<div class="mon-stat-block__name"><span'
          f' class="mon-stat-block__name-link">{name}<br></span></div>'
      ),
      f'<div class="mon-stat-block__meta">{meta}</div>',
      (
          '<p><img alt=""'
          ' src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg"'
          ' class="mon-stat-block__separator-img"></p>'
      ),
      (
          f"<p><strong>Armor Class</strong>&nbsp;{ac}&nbsp;({ac_note})"
          f"<br><strong>Hit Points</strong>&nbsp;{hp}&nbsp;({hp_dice})"
          f"<br><strong>Speed</strong>&nbsp;{speed}</p>"
      ),
      (
          '<p><img alt=""'
          ' src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg"'
          ' class="mon-stat-block__separator-img"></p>'
      ),
      (
          '<table cellpadding="0" cellspacing="0" width="364" style="height:'
          ' 61px;"><tbody>'
      ),
      (
          "<tr>"
          + "".join(
              f'<td style="text-align: center;"><strong>{x}</strong></td>'
              for x in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
          )
          + "</tr>"
      ),
      (
          "<tr>"
          + "".join(
              '<td style="text-align: center;"><span style="font-size:'
              f' 10pt;">{v}&nbsp;</span></td>'
              for v in [s, d, c, i, w, ch]
          )
          + "</tr>"
      ),
      (
          "<tr>"
          + "".join(
              '<td style="text-align: center;"><span style="font-size:'
              f' 10pt;">({(v-10)//2:+d})</span></td>'
              for v in [s, d, c, i, w, ch]
          )
          + "</tr>"
      ),
      "</tbody></table>",
      (
          '<p><img alt=""'
          ' src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg"'
          ' class="mon-stat-block__separator-img"></p>'
      ),
  ]
  det = []
  if saves:
    det.append(f"<strong>Saving Throws&nbsp;</strong>{saves}")
  if skills:
    det.append(f"<strong>Skills&nbsp;</strong>{skills}")
  if resists:
    det.append(f"<strong>Damage Resistances&nbsp;</strong>{resists}")
  if immunes:
    det.append(f"<strong>Damage Immunities&nbsp;</strong>{immunes}")
  if cond_immunes:
    det.append(f"<strong>Condition Immunities&nbsp;</strong>{cond_immunes}")
  if senses:
    det.append(f"<strong>Senses&nbsp;</strong>{senses}")
  if langs:
    det.append(f"<strong>Languages&nbsp;</strong>{langs}")
  det.append(
      f"<strong>Challenge&nbsp;</strong>{cr} ({xp} XP)&nbsp;"
      f" &nbsp;<strong>Proficiency Bonus</strong>&nbsp;+{pb}"
  )
  lines.append(
      "<p>"
      + "<br>".join(det)
      + '<br><br><img alt=""'
      ' src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg"'
      ' class="mon-stat-block__separator-img"><br>&nbsp;</p>'
  )

  for section_title, items in [
      ("Traits", traits),
      ("Actions", actions),
      ("Bonus Actions", bonus),
      ("Reactions", reactions),
  ]:
    if items:
      lines.append(
          f'<div class="mon-stat-block__description-block-heading">'
          f"{section_title}</div>"
      )
      for item_name, item_desc in items:
        lines.append(f"<p><br><strong>{item_name}.</strong>&nbsp;{item_desc}</p>")
      lines.append(
          '<p><img alt=""'
          ' src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg"'
          ' class="mon-stat-block__separator-img"></p>'
      )

  lines.append("</div>")
  return "\n".join(lines)
```

---

## 3. Wiring Placed Tokens (`scene["tokens"]`)

When a user drops placeholder tokens in AboveVTT (either blank tokens or existing D&D Beyond monsters renamed on the map), update each matching token as follows:

1. **Link Custom Note & Clear Base Monster Stat ID:**
   - `token["statBlock"] = note_id`
   - `token["itemId"] = note_id`
   - `token["monster"] = "customStat"`
   - `token["itemType"] = "myToken"`
   - `token.pop("stat", None)` *(critical: remove numeric D&D Beyond monster `stat` ID so AboveVTT opens the custom note instead of the base D&D Beyond monster sheet)*
   - `token["disablestat"] = False`
   - `token["hidestat"] = False`
2. **Sync Combat Stats:**
   - `token["armorClass"] = ac`
   - `token["hitPointInfo"] = {"maximum": hp, "current": hp, "temp": 0}`
   - `token["customInit"] = f"{(dex - 10) // 2:+d}"`
   - `token["customStat"]`:
     ```python
     token["customStat"] = {
         "0": {"mod": str_mod, "save": str_save},
         "1": {"mod": dex_mod, "save": dex_save},
         "2": {"mod": con_mod, "save": con_save},
         "3": {"mod": int_mod, "save": int_save},
         "4": {"mod": wis_mod, "save": wis_save},
         "5": {"mod": cha_mod, "save": cha_save},
     }
```
3. **Token Image & Style Preservation (`imgsrc` & `tokenStyleSelect`):**
   - The user typically sets the token image (`imgsrc`) and token style (`tokenStyleSelect`) on at least one placed token first:
     - `"virtualMiniCircle"` ("virtual mini with round base", paired with `"square": True` and `"legacyaspectratio": False`) when using a transparent PNG.
     - `"circle"` (default circular border) when using a non-transparent image.
   - Always preserve `imgsrc`, `alternativeImages`, `tokenStyleSelect`, `square`, and `legacyaspectratio` on placed tokens.
   - If multiple tokens of the same creature exist and only one was configured with the custom image/style, sync `imgsrc`, `alternativeImages`, `tokenStyleSelect`, `square`, and `legacyaspectratio` to all tokens of that creature.
   - Include the token's custom image (`![](<imgsrc>)`) in the monster's description section (`**_Tactics, Reaction & Morale (...):_**`) in the corresponding adventure `.md` file if not already present (note: AboveVTT also automatically renders `token.options.imgsrc` at the bottom of the stat block window with a "Send to Players" button).
4. **Numbering & Distinct Border Colors:**
   - Sort tokens of the same creature spatially by `(top, left)` pixel coordinates.
   - Number multiple tokens sequentially (`<Name>`, `<Name> 2`, `<Name> 3`, ...), especially when tokens were duplicated in AboveVTT (which copies the same name and border color).
   - Remove transient UI state like `token.pop("selected", None)`.
   - Assign distinct high-contrast hex colors to `token["color"]` so players who only see `???` can call out targets by border color:
     ```python
     PALETTE = [
         '#FF7433',
         '#1A6AFF',
         '#E6194B',
         '#3CBB75',
         '#FFE119',
         '#911EB4',
         '#46F0F0',
         '#F032E6',
         '#D2F53C',
         '#FABEBE',
         '#008080',
         '#E6BEFF',
         '#AA6E28',
         '#800000',
         '#AAFFC3',
         '#808000',
         '#FFD8B1',
         '#000080',
         '#808080',
         '#FFFFFF',
     ]
```
5. **Preserve Map Placement & Sizing:**
   - Never overwrite `top`, `left`, `size`, or `gridSquares` unless explicitly requested.
