#!/usr/bin/env python3
"""Sync custom stat blocks and token fields into an AboveVTT .abovevtt export using canonical D&D Beyond HTML.

Usage:
  avtt_tokens.py IN.abovevtt CREATURES.json [--out OUT.abovevtt] [--write]

Without --write it only prints the match table (dry run).
Rules (see SKILL.md):
- Stat blocks use canonical AboveVTT .mon-stat-block.ddbc-creature-block markup with native
  roll buttons (avtt-roll-button) and clickable dice spans (data-dicenotation).
- Token fields touched: size (to match stat block), border colour (duplicates only), border on/off (unique creatures).
- Names, images, style and positions are strictly preserved.
"""
import argparse, base64, collections, json, re, sys, uuid

SIZE = {  # name: (gridSquares, sizeId)
    "Tiny": (0.5, 2), "Small": (1, 3), "Medium": (1, 4),
    "Large": (2, 5), "Huge": (3, 6), "Gargantuan": (4, 7),
}
PALETTE = ['#FF7433', '#1A6AFF', '#E6194B', '#3CBB75', '#FFE119', '#911EB4', '#46F0F0', '#F032E6',
           '#D2F53C', '#FABEBE', '#008080', '#E6BEFF', '#AA6E28', '#800000', '#AAFFC3', '#808000',
           '#FFD8B1', '#000080', '#808080', '#FFFFFF']


def load(path):
    return json.loads(base64.b64decode(open(path).read()).decode("utf-8"))


def save(path, data):
    open(path, "w").write(base64.b64encode(json.dumps(data, indent="\t").encode("utf-8")).decode())


def mod(v):
    return (v - 10) // 2


def format_action_text(text, action_name):
    """Format attack rolls and damage dice into AboveVTT interactive data attributes."""
    def repl_hit(m):
        val = m.group(1)
        sign = val if val.startswith(("+", "-")) else f"+{val}"
        return f'<span data-dicenotation="1d20{sign}" data-rolltype="to hit" data-rollaction="{action_name}">{sign}</span> to hit'

    t = re.sub(r'([+-]\d+)\s+to\s+hit', repl_hit, text)

    def repl_dmg(m):
        dice = m.group(1)
        dtype = m.group(2) or ""
        clean_dice = dice.replace(" ", "")
        return f'<span data-dicenotation="{clean_dice}" data-rolltype="damage" data-rollaction="{action_name}" data-rolldamagetype="{dtype}">({dice})</span> {dtype} damage'

    t = re.sub(r'\((\d+d\d+(?:\s*[+-]\s*\d+)?)\)\s*([a-zA-Z]+)?\s*damage', repl_dmg, t)
    return t


def build_ddb_html(c):
    """Build canonical D&D Beyond stat block HTML matching native AboveVTT custom tokens."""
    ab = c["abilities"]
    dex_mod = mod(ab[1])
    abbrs = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

    # Ability blocks
    ab_blocks = []
    for abbr, score in zip(abbrs, ab):
        m = mod(score)
        ab_blocks.append(f"""                          <div class="ability-block__stat ability-block__stat--{abbr.lower()} ddbc-creature-block__ability-stat">
                            <div class="ability-block__heading ddbc-creature-block__ability-heading">{abbr}</div>
                            <div class="ability-block__data">
                              <span class="ability-block__score">{score}</span>
                              <span class="ability-block__modifier ddbc-creature-block__ability-modifier"><button 
            data-exp="1d20"
            data-mod="{m:+d}"
            data-rolltype="check"
            data-actiontype="{abbr}"
            class="avtt-roll-button">({m:+d})</button></span>
                            </div>
                          </div>""")
    abilities_html = "\n".join(ab_blocks)

    # Tidbits (Saves, Skills, Resistances, Immunities, Senses, Languages, CR)
    tidbits = []

    # Saving Throws
    sv = c.get("save_bonus", {})
    if sv or c.get("saves"):
        save_buttons = []
        for i, abbr in enumerate(abbrs):
            if str(i) in sv:
                s_val = sv[str(i)]
                save_buttons.append(f'{abbr} <button data-exp="1d20" data-mod="{s_val:+d}" data-rolltype="save" data-actiontype="{abbr}" class="avtt-roll-button">{s_val:+d}</button>')
        if save_buttons:
            tidbits.append(f"""                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">Saving Throws</span>
                          <span class="mon-stat-block__tidbit-data">{", ".join(save_buttons)}</span>
                        </div>""")
        elif c.get("saves"):
            tidbits.append(f"""                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">Saving Throws</span>
                          <span class="mon-stat-block__tidbit-data">{c["saves"]}</span>
                        </div>""")

    # Skills
    if c.get("skills"):
        tidbits.append(f"""                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">Skills</span>
                          <span class="mon-stat-block__tidbit-data">{c["skills"]}</span>
                        </div>""")

    # Vulnerabilities, Resistances, Immunities, Senses, Languages
    for label, key in [
        ("Damage Vulnerabilities", "vulnerabilities"),
        ("Damage Resistances", "resists"),
        ("Damage Immunities", "immunes"),
        ("Condition Immunities", "cond_immunes"),
        ("Senses", "senses"),
        ("Languages", "languages"),
    ]:
        if c.get(key):
            tidbits.append(f"""                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">{label}</span>
                          <span class="mon-stat-block__tidbit-data">{c[key]}</span>
                        </div>""")

    # Challenge & PB
    pb = c.get("pb", 2)
    xp = c.get("xp", "")
    xp_str = f" ({xp} XP)" if xp else ""
    tidbits.append(f"""                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">Challenge</span>
                          <span class="mon-stat-block__tidbit-data">{c.get("cr", "-")}{xp_str}</span>
                        </div>
                        <div class="mon-stat-block__tidbit-spacer"></div>
                        <div class="mon-stat-block__tidbit ddbc-creature-block__tidbit">
                          <span class="mon-stat-block__tidbit-label ddbc-creature-block__tidbit-label">Proficiency Bonus</span>
                          <span class="mon-stat-block__tidbit-data">
                            <button data-exp="1d20" data-mod="+{pb}" data-rolltype="roll" data-actiontype="Proficiency Bonus" class="avtt-roll-button">+{pb}</button>
                          </span>
                        </div>""")

    tidbits_html = "\n".join(tidbits)

    # Sections (Traits, Actions, Bonus Actions, Reactions, Legendary Actions)
    sections_html = []
    sec_dict = c.get("sections", {})
    for title in ["Traits", "Actions", "Bonus Actions", "Reactions", "Legendary Actions"]:
        items = sec_dict.get(title)
        if not items:
            continue
        items_html = []
        for name, text in items:
            formatted_text = format_action_text(text, name)
            items_html.append(f"<p><em><strong>{name}.</strong></em> {formatted_text}</p>")
        sections_html.append(f"""                        <div class="mon-stat-block__description-block ddbc-creature-block__description-block">
                          <div class="mon-stat-block__description-block-heading ddbc-creature-block__description-block-heading">{title}</div>
                          <div class="mon-stat-block__description-block-content">
                            {"\n".join(items_html)}
                          </div>
                        </div>""")

    sections_rendered = "\n".join(sections_html)

    ac_note = f" ({c['ac_note']})" if c.get("ac_note") else ""
    hp_dice = f" ({c['hp_dice']})" if c.get("hp_dice") else ""

    html = f"""          <div id="content" class="main content-container" style="padding:0!important">
            <section class="primary-content" role="main">
              <div class="monster-details">
                <div class="more-info details-more-info" style="padding: 2px;">
                  <div class="detail-content">
                    <div class="mon-stat-block ddbc-creature-block" style="column-count: 1;margin:0;">
                      <div class="mon-stat-block__header ddbc-creature-block__header">
                        <div class="mon-stat-block__name ddbc-creature-block__name">
                          <a class="mon-stat-block__name-link ddbc-creature-block__name-link" href="#">
                            {c["title"]}
                          </a>
                        </div>
                        <div class="mon-stat-block__meta ddbc-creature-block__meta">{c.get("meta", "")}</div>
                      </div>
                      <div class="mon-stat-block__separator ddbc-creature-block__separator">
                        <img class="mon-stat-block__separator-img ddbc-creature-block__separator-img" alt="" src="https://media-waterdeep.cursecdn.com/file-attachments/0/579/stat-block-header-bar.svg">
                      </div>
                      <div class="mon-stat-block__attributes">
                        <div class="mon-stat-block__attribute ddbc-creature-block__attribute">
                          <span class="mon-stat-block__attribute-label ddbc-creature-block__attribute-label">Armor Class</span>
                          <span class="mon-stat-block__attribute-value">
                            <span class="mon-stat-block__attribute-data-value">{c["ac"]}</span>
                            <span class="mon-stat-block__attribute-data-extra ddbc-creature-block__attribute-data-extra">{ac_note}</span>
                          </span>
                          <span class="mon-stat-block__attribute-label ddbc-creature-block__attribute-label">Initiative</span>
                          <span class="mon-stat-block__attribute-value">
                            <span class="mon-stat-block__attribute-data-value">
                              <button 
            data-exp="1d20"
            data-mod="{dex_mod:+d}"
            data-rolltype="Check"
            data-actiontype="Initiative"
            class="avtt-roll-button">{dex_mod:+d}</button>
                            </span>
                          </span>        
                        </div>
                        <div class="mon-stat-block__attribute ddbc-creature-block__attribute">
                          <span class="mon-stat-block__attribute-label ddbc-creature-block__attribute-label">Hit Points</span>
                          <span class="mon-stat-block__attribute-data">
                            <span class="mon-stat-block__attribute-data-value">{c["hp"]}</span>
                            <span class="mon-stat-block__attribute-data-extra ddbc-creature-block__attribute-data-extra">{hp_dice}</span>
                          </span>
                        </div>
                        <div class="mon-stat-block__attribute ddbc-creature-block__attribute">
                          <span class="mon-stat-block__attribute-label">Speed</span>
                          <span class="mon-stat-block__attribute-data">
                            <span class="mon-stat-block__attribute-data-value">{c.get("speed", "30 ft.")}</span>
                          </span>
                        </div>
                      </div>
                      <div class="mon-stat-block__stat-block">
                        <div class="mon-stat-block__separator">
                          <img class="mon-stat-block__separator-img" alt="" src="https://media-waterdeep.cursecdn.com/file-attachments/0/579/stat-block-header-bar.svg">
                        </div>
                        <div class="ability-block ddbc-creature-block__abilities">
{abilities_html}
                        </div>
                        <div class="mon-stat-block__tidbits">
{tidbits_html}
                        </div>
{sections_rendered}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>"""
    return html


def find_note_id(notes, c):
    """Find existing note ID by matching creature title/name or DDB HTML name-link."""
    c_title = c["title"].strip().lower()
    c_name = c["name"].strip().lower()
    for nid, n in notes.items():
        if not n.get("statBlock"):
            continue
        t = (n.get("title") or "").strip().lower()
        if t in (c_title, c_name):
            return nid
        m = re.search(r'class="mon-stat-block__name-link[^"]*">\s*([^<]+?)\s*</a>', n.get("plain", ""))
        if m and m.group(1).strip().lower() in (c_title, c_name):
            return nid
        if nid.startswith(f"{c['slug']}-"):
            return nid
    return f"{c['slug']}-{uuid.uuid4()}"


def upsert_note(data, c):
    """Overwrite the note for this creature with canonical DDB markup or create it."""
    html = build_ddb_html(c)
    notes = data["notes"]
    nid = find_note_id(notes, c)
    notes[nid] = {
        "id": nid,
        "title": c["title"],
        "text": html,
        "plain": html,
        "player": True,
        "statBlock": True,
        "abilityTracker": {},
    }
    return nid


def real_tokens(scene):
    for tid, t in scene["tokens"].items():
        if not isinstance(t, dict) or not t.get("name"):
            continue
        if "/numbers/" in (t.get("imgsrc") or "") or t["name"].isdigit():
            continue  # map labels
        if t.get("auraislight") and t.get("tokenStyleSelect") == "definitelyNotAToken":
            continue
        yield tid, t


def find_creature(name, creatures):
    base = re.sub(r"\s+\d+$", "", name.strip()).lower()
    for c in creatures:
        if base in [c["title"].lower(), c["name"].lower()] + [a.lower() for a in c.get("aliases", [])]:
            return c
    return None


def run(args):
    data = load(args.input)
    creatures = json.load(open(args.creatures))
    scene = data["scenes"][0]
    groups = collections.defaultdict(list)
    unmatched = []
    for tid, t in real_tokens(scene):
        c = find_creature(t["name"], creatures)
        (groups[c["name"]] if c else unmatched).append((tid, t, c) if c else (tid, t))
    print(f"{'token':28} {'creature':26} {'size now':>9} -> {'size':>6}  border")
    plan = []
    for cname, toks in groups.items():
        c = next(c for c in creatures if c["name"] == cname)
        toks.sort(key=lambda x: (float(str(x[1]["top"]).rstrip("px")), float(str(x[1]["left"]).rstrip("px"))))
        gs, sid = SIZE[c["size"]]
        used = set()
        multi = len(toks) > 1
        for tid, t, _ in toks:
            col = t.get("color")
            if multi:
                if col in used or not col:
                    col = next((p for p in PALETTE if p not in used), col)
                used.add(col)
            border = "on, " + str(col) if multi else "off"
            print(f"{t['name']:28} {cname:26} {t.get('gridSquares')!s:>9} -> {gs!s:>6}  {border}")
            plan.append((t, c, gs, sid, multi, col))
    for tid, t in unmatched:
        print(f"{t['name']:28} (no match - left untouched)")
    if not args.write:
        return
    ids = {}
    for t, c, gs, sid, multi, col in plan:
        if c["name"] not in ids:
            ids[c["name"]] = upsert_note(data, c)
        nid = ids[c["name"]]
        t.update({
            "statBlock": nid,
            "itemId": nid,
            "monster": "customStat",
            "itemType": "myToken",
            "listItemPath": f"/My Tokens/{c['name']}",
            "disablestat": False,
            "hidestat": False,
        })
        t.pop("stat", None)
        t["armorClass"] = str(c["ac"])
        t["hitPointInfo"] = {"maximum": str(c["hp"]), "current": str(c["hp"]), "temp": 0}
        t["customInit"] = f"{mod(c['abilities'][1]):+d}"
        sv = c.get("save_bonus", {})
        t["customStat"] = {
            str(i): {
                "mod": f"{mod(v):+d}",
                "save": f"{sv.get(str(i), mod(v)):+d}",
            }
            for i, v in enumerate(c["abilities"])
        }
        t["gridSquares"], t["size"] = gs, gs * 35
        if t.get("sizeId") is not None:
            t["sizeId"] = sid
        t["disableborder"] = not multi
        if multi:
            t["color"] = col
        t.pop("selected", None)
    save(args.out, data)
    print("wrote", args.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("creatures")
    ap.add_argument("--out")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.write and not a.out:
        sys.exit("--write needs --out")
    run(a)
