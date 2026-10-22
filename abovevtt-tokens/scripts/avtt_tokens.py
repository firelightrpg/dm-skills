#!/usr/bin/env python3
"""Sync custom stat blocks and a few token fields into an AboveVTT .abovevtt export.

Usage:
  avtt_tokens.py IN.abovevtt CREATURES.json [--out OUT.abovevtt] [--journal /path/to/AboveVTT/Journal.js] [--write]

Without --write it only prints the match table (dry run).
Rules (see SKILL.md): the stat block is always rewritten for tokens whose name matches a
creature; the only token fields touched are size (to match the stat block), border colour
(duplicates only) and border on/off (unique creatures). Names, images and styles are never touched.
"""
import argparse, base64, json, re, sys, uuid, collections

SIZE = {  # name: (gridSquares, sizeId)
    "Tiny": (0.5, 2), "Small": (1, 3), "Medium": (1, 4),
    "Large": (2, 5), "Huge": (3, 6), "Gargantuan": (4, 7),
}
PALETTE = ['#FF7433', '#1A6AFF', '#E6194B', '#3CBB75', '#FFE119', '#911EB4', '#46F0F0', '#F032E6',
           '#D2F53C', '#FABEBE', '#008080', '#E6BEFF', '#AA6E28', '#800000', '#AAFFC3', '#808000',
           '#FFD8B1', '#000080', '#808080', '#FFFFFF']
SEP = ('<p><img class="mon-stat-block__separator-img" '
       'src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg" alt="" /></p>')


def load(path):
    return json.loads(base64.b64decode(open(path).read()).decode("utf-8"))


def save(path, data):
    open(path, "w").write(base64.b64encode(json.dumps(data, indent="\t").encode("utf-8")).decode())


def content_styles(journal_js):
    """AboveVTT's journal template embeds this CSS in every note; extract it from Journal.js."""
    lines = open(journal_js, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "content_styles() {")
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "\t\t`")
    css = "\n".join(lines[start + 2:end])  # skip "content_styles() {" and "return `"
    return css.replace("\\`", "`")


def mod(v):
    return (v - 10) // 2


def build_html(c, css):
    ab = c["abilities"]
    h = [f"<style id='contentStyles'>{css}</style>",
         '<div class="Basic-Text-Frame stat-block-background one-column-stat" '
         "style=\"font-family: 'Scala Sans Offc', Roboto, Helvetica, sans-serif;\">",
         f'<div class="mon-stat-block__name"><span class="mon-stat-block__name-link"> {c["title"]} <br /></span></div>',
         f'<div class="mon-stat-block__meta">{c["meta"]}</div>', SEP,
         f'<p><strong>Armor Class</strong>&nbsp;{c["ac"]}&nbsp;({c["ac_note"]})<br />'
         f'<strong>Hit Points</strong>&nbsp;{c["hp"]}&nbsp;({c["hp_dice"]})<br />'
         f'<strong>Speed</strong>&nbsp;{c["speed"]}</p>', SEP,
         '<table style="height: 61px;" width="364" cellspacing="0" cellpadding="0"><tbody>',
         "<tr>" + "".join(f'<td style="text-align: center;"><strong>{x}</strong></td>'
                          for x in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]) + "</tr>",
         "<tr>" + "".join(f'<td style="text-align: center;"><span style="font-size: 10pt;">{v}&nbsp;</span></td>'
                          for v in ab) + "</tr>",
         "<tr>" + "".join(f'<td style="text-align: center;"><span style="font-size: 10pt;">({mod(v):+d})</span></td>'
                          for v in ab) + "</tr>",
         "</tbody></table>", SEP]
    det = []
    for label, key in [("Saving Throws", "saves"), ("Skills", "skills"), ("Damage Vulnerabilities", "vulnerabilities"),
                       ("Damage Resistances", "resists"), ("Damage Immunities", "immunes"),
                       ("Condition Immunities", "cond_immunes"), ("Senses", "senses"), ("Languages", "languages")]:
        if c.get(key):
            det.append(f"<strong>{label}&nbsp;</strong>{c[key]}")
    det.append(f'<strong>Challenge&nbsp;</strong>{c["cr"]} ({c["xp"]} XP)&nbsp; &nbsp;'
               f'<strong>Proficiency Bonus</strong>&nbsp;+{c["pb"]}')
    h.append("<p>" + "<br />".join(det) + '<br /><br /><img class="mon-stat-block__separator-img" '
             'src="https://www.dndbeyond.com/file-attachments/0/579/stat-block-header-bar.svg" alt="" /><br />&nbsp;</p>')
    for title in ["Traits", "Actions", "Bonus Actions", "Reactions", "Legendary Actions"]:
        items = c.get("sections", {}).get(title)
        if not items:
            continue
        h.append(f'<div class="mon-stat-block__description-block-heading">{title}</div>')
        for i, (n, t) in enumerate(items):
            h.append(f"<p>{'<br />' if i == 0 else ''}<strong><em>{n}.</em></strong>&nbsp;{t}</p>")
        h.append(SEP)
    h.append("</div>")
    return "\n".join(h)


def plain_text(html):
    html = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", html)
    t = re.sub(r"</td>", " ", t)
    t = re.sub(r"<[^>]+>", "", t).replace("&nbsp;", " ")
    return t


def upsert_note(data, c, css):
    """Overwrite the note for this creature (match by title) or create it. Returns note id."""
    html = build_html(c, css)
    notes = data["notes"]
    nid = next((k for k, v in notes.items() if v.get("statBlock") is True and
                (v.get("title") or "").strip().lower() == c["title"].strip().lower()), None)
    if nid is None:
        nid = f'{c["slug"]}-{uuid.uuid4()}'
    notes[nid] = {"title": c["title"], "text": html, "plain": plain_text(html),
                  "player": False, "statBlock": True, "id": nid}
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
    css = content_styles(args.journal)
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
            ids[c["name"]] = upsert_note(data, c, css)
        nid = ids[c["name"]]
        t.update({"statBlock": nid, "itemId": nid, "monster": "customStat", "itemType": "myToken",
                  "disablestat": False, "hidestat": False})
        t.pop("stat", None)
        t["armorClass"] = c["ac"]
        t["hitPointInfo"] = {"maximum": c["hp"], "current": c["hp"], "temp": 0}
        t["customInit"] = f"{mod(c['abilities'][1]):+d}"
        sv = c.get("save_bonus", {})
        t["customStat"] = {str(i): {"mod": f"{mod(v):+d}", "save": f"{sv.get(str(i), mod(v)):+d}"}
                           for i, v in enumerate(c["abilities"])}
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
    ap.add_argument("input"); ap.add_argument("creatures")
    ap.add_argument("--out"); ap.add_argument("--write", action="store_true")
    ap.add_argument("--journal", default="/home/grim/github/AboveVTT/Journal.js")
    a = ap.parse_args()
    if a.write and not a.out:
        sys.exit("--write needs --out")
    run(a)
