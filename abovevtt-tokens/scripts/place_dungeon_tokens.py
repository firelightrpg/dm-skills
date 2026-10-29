#!/usr/bin/env python3
"""Place room number markers and creature tokens into AboveVTT scenes with standardized styling.

Rules applied:
- Token Style: Virtual Mini w/ Round Base (tokenStyleSelect: "virtualMiniCircle", tokenBaseStyleSelect: "default")
- HP Bar: Only show HP values on hover (hidehpbar: True)
- Border: Disabled for unique creatures; enabled with distinct colors from PALETTE for multiples
- Size: Explicitly scaled to statblock grid footprint (size: gridSquares * vpps)
- Artwork: High-resolution transparent PNG / webp tokens
- Statblock: Canonical DDB stat blocks and native AboveVTT roll buttons for custom creatures;
  verified DDB monster IDs for standard creatures.

Usage:
  python place_dungeon_tokens.py --abovevtt SCENE.abovevtt [--scene "Dungeon"] [--creatures] [--write]
"""

import argparse
import base64
import collections
import json
import re
import uuid

PALETTE = [
    "#FF7433", "#1A6AFF", "#E6194B", "#3CBB75", "#FFE119", "#911EB4", "#46F0F0", "#F032E6",
    "#D2F53C", "#FABEBE", "#008080", "#E6BEFF", "#AA6E28", "#800000", "#AAFFC3", "#808000",
    "#FFD8B1", "#000080", "#808080", "#FFFFFF"
]

SIZE_LOOKUP = {
    "Tiny": (0.5, 2),
    "Small": (1, 3),
    "Medium": (1, 4),
    "Large": (2, 5),
    "Huge": (3, 6),
    "Gargantuan": (4, 7)
}


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

    tidbits = []
    sv = c.get("save_bonus", {})
    if sv:
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

    for label, key in [
        ("Skills", "skills"),
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

    return f"""          <div id="content" class="main content-container" style="padding:0!important">
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


CUSTOM_CREATURE_DATA = {
    "the keeper": {
        "slug": "the-keeper",
        "title": "The Keeper",
        "meta": "Huge Giant, Chaotic Evil",
        "ac": "17",
        "ac_note": "chain mail",
        "hp": "170",
        "hp_dice": "15d12 + 75",
        "speed": "40 ft.",
        "abilities": [23, 15, 20, 10, 12, 9],
        "save_bonus": {"1": 5, "2": 8, "4": 4},
        "skills": "Athletics +12, Perception +4",
        "senses": "Darkvision 60 ft., passive Perception 14",
        "languages": "Giant",
        "cr": "7",
        "xp": "2,900",
        "pb": 3,
        "sections": {
            "Actions": [
                ("Multiattack", "The Keeper makes two greataxe attacks."),
                ("Greataxe +1", "Melee Weapon Attack: +10 to hit, reach 15 ft., one target. Hit: 20 (3d8 + 7) slashing damage."),
                ("Rock", "Ranged Weapon Attack: +9 to hit, range 60/240 ft., one target. Hit: 28 (4d10 + 6) bludgeoning damage.")
            ],
            "Reactions": [
                ("Rock Catching", "If a rock or similar object is hurled at the giant, the giant can, with a successful DC 10 Dexterity saving throw, catch the missile and take no bludgeoning damage from it.")
            ]
        }
    },
    "bugbear chief": {
        "slug": "bugbear-chief",
        "title": "Bugbear Chief",
        "meta": "Medium Humanoid (Goblinoid), Chaotic Evil",
        "ac": "17",
        "ac_note": "chain shirt, shield",
        "hp": "65",
        "hp_dice": "10d8 + 20",
        "speed": "30 ft.",
        "abilities": [17, 14, 14, 11, 12, 11],
        "skills": "Stealth +6, Survival +3",
        "senses": "Darkvision 60 ft., passive Perception 11",
        "languages": "Common, Goblin",
        "cr": "3",
        "xp": "700",
        "pb": 2,
        "sections": {
            "Traits": [
                ("Brute", "A melee weapon deals one extra die of its damage when the bugbear hits with it (included in the attack)."),
                ("Heart of Hruggek", "The bugbear has advantage on saving throws against being charmed, frightened, paralyzed, poisoned, stunned, or put to sleep."),
                ("Surprise Attack", "If the bugbear surprises a creature and hits it with an attack during the first round of combat, the target takes an extra 7 (2d6) damage from the attack.")
            ],
            "Actions": [
                ("Multiattack", "The bugbear makes two melee attacks."),
                ("Longsword", "Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 11 (2d8 + 2) slashing damage, or 13 (2d10 + 2) slashing damage if used with two hands."),
                ("Morningstar", "Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 11 (2d8 + 2) piercing damage."),
                ("Javelin", "Melee or Ranged Weapon Attack: +5 to hit, reach 5 ft. or range 30/120 ft., one target. Hit: 9 (2d6 + 2) piercing damage in melee or 5 (1d6 + 2) piercing damage at range.")
            ]
        }
    },
    "water weird": {
        "slug": "water-weird",
        "title": "Water Weird",
        "meta": "Large Elemental, Neutral",
        "ac": "13",
        "hp": "58",
        "hp_dice": "9d10 + 9",
        "speed": "0 ft., swim 60 ft.",
        "abilities": [17, 16, 13, 11, 10, 10],
        "resists": "fire; bludgeoning, piercing, and slashing from nonmagical attacks",
        "immunes": "poison",
        "cond_immunes": "charmed, exhaustion, grappled, paralyzed, petrified, poisoned, prone, restrained, unconscious",
        "senses": "Blindsight 30 ft., passive Perception 10",
        "languages": "understands Aquan but can't speak",
        "cr": "3",
        "xp": "700",
        "pb": 2,
        "sections": {
            "Traits": [
                ("Invisible in Water", "The water weird is invisible while fully immersed in water."),
                ("Water Bound", "The water weird dies if it leaves the water to which it is bound or if that water is destroyed.")
            ],
            "Actions": [
                ("Constrict", "Melee Weapon Attack: +5 to hit, reach 10 ft., one creature. Hit: 13 (3d6 + 3) bludgeoning damage. If the target is Medium or smaller, it is grappled (escape DC 13) and pulled 5 feet toward the water weird. Until this grapple ends, the target is restrained, the water weird tries to drown it, and the water weird can't constrict another target.")
            ]
        }
    }
}


CREATURE_BLUEPRINTS = {
    "the keeper": {
        "custom": True,
        "title": "The Keeper",
        "size": "Huge",
        "ac": 17,
        "hp": 170,
        "imgsrc": "https://5e.tools/img/bestiary/tokens/TftYP/The%20Keeper.webp",
        "alts": ["https://5e.tools/img/bestiary/tokens/TftYP/The%20Keeper.webp"],
        "listItemPath": "/My Tokens/The Keeper",
        "abilities": [23, 15, 20, 10, 12, 9],
        "saves": {"1": 5, "2": 8, "4": 4}
    },
    "carnivorous ape": {
        "custom": False,
        "title": "Carnivorous Ape",
        "size": "Medium",
        "ac": 12,
        "hp": 30,
        "stat": 16788,
        "imgsrc": "https://www.dndbeyond.com/avatars/43938/889/638607408673681530.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/4675/664/636747837303835953.jpeg",
            "https://www.dndbeyond.com/avatars/43938/889/638607408673681530.png"
        ],
        "listItemPath": "/Monsters/Ape"
    },
    "bugbear": {
        "custom": False,
        "title": "Bugbear",
        "size": "Medium",
        "ac": 16,
        "hp": 27,
        "stat": 16817,
        "imgsrc": "https://www.dndbeyond.com/avatars/31312/871/638084425511165687.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/31312/870/638084425509823947.jpeg",
            "https://www.dndbeyond.com/avatars/31312/871/638084425511165687.png"
        ],
        "listItemPath": "/Monsters/Bugbear"
    },
    "bugbear chief": {
        "custom": True,
        "title": "Bugbear Chief",
        "size": "Medium",
        "ac": 17,
        "hp": 65,
        "imgsrc": "https://www.dndbeyond.com/avatars/47144/717/638742157685478339.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/4675/675/636747837794884984.jpeg",
            "https://www.dndbeyond.com/avatars/47144/717/638742157685478339.png",
            "https://5e.tools/img/bestiary/tokens/MM/Bugbear%20Chief.webp"
        ],
        "listItemPath": "/My Tokens/Bugbear Chief",
        "abilities": [17, 14, 14, 11, 12, 11],
        "saves": {}
    },
    "orc slave": {
        "custom": False,
        "title": "Orc Slave",
        "size": "Medium",
        "ac": 13,
        "hp": 15,
        "stat": 16972,
        "imgsrc": "https://www.dndbeyond.com/avatars/30834/160/638063882785865067.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/0/300/636252771690760688.jpeg",
            "https://www.dndbeyond.com/avatars/30834/160/638063882785865067.png"
        ],
        "listItemPath": "/Monsters/Orc"
    },
    "hill giant torturer": {
        "custom": False,
        "title": "Hill Giant Torturer",
        "size": "Huge",
        "ac": 13,
        "hp": 105,
        "stat": 16923,
        "imgsrc": "https://www.dndbeyond.com/avatars/30783/933/638062024048160808.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/0/330/636252776195489562.jpeg",
            "https://www.dndbeyond.com/avatars/30783/933/638062024048160808.png"
        ],
        "listItemPath": "/Monsters/Hill Giant"
    },
    "fire giant smith": {
        "custom": False,
        "title": "Fire Giant Smith",
        "size": "Huge",
        "ac": 18,
        "hp": 162,
        "stat": 16862,
        "imgsrc": "https://www.dndbeyond.com/avatars/30783/927/638062023828890799.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/0/356/636252778143474597.jpeg",
            "https://www.dndbeyond.com/avatars/30783/927/638062023828890799.png"
        ],
        "listItemPath": "/Monsters/Fire Giant"
    },
    "water weird": {
        "custom": True,
        "title": "Water Weird",
        "size": "Large",
        "ac": 13,
        "hp": 58,
        "imgsrc": "https://5e.tools/img/bestiary/tokens/MM/Water%20Weird.webp",
        "alts": [
            "https://www.dndbeyond.com/avatars/16/591/636376367493746277.jpeg",
            "https://5e.tools/img/bestiary/tokens/MM/Water%20Weird.webp"
        ],
        "listItemPath": "/My Tokens/Water Weird",
        "abilities": [17, 16, 13, 11, 10, 10],
        "saves": {}
    },
    "stone giant": {
        "custom": False,
        "title": "Stone Giant",
        "size": "Huge",
        "ac": 17,
        "hp": 126,
        "stat": 17024,
        "imgsrc": "https://www.dndbeyond.com/avatars/30783/942/638062024167770799.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/0/108/636252744518262589.jpeg",
            "https://www.dndbeyond.com/avatars/30783/942/638062024167770799.png"
        ],
        "listItemPath": "/Monsters/Stone Giant"
    },
    "manticore": {
        "custom": False,
        "title": "Manticore",
        "size": "Large",
        "ac": 14,
        "hp": 68,
        "stat": 16951,
        "imgsrc": "https://www.dndbeyond.com/avatars/30833/344/638063861715070425.png",
        "alts": [
            "https://www.dndbeyond.com/avatars/0/186/636252762622641747.jpeg",
            "https://www.dndbeyond.com/avatars/30833/344/638063861715070425.png"
        ],
        "listItemPath": "/Monsters/Manticore"
    },
    "carrion crawler": {
        "custom": False,
        "title": "Carrion Crawler",
        "size": "Large",
        "ac": 13,
        "hp": 51,
        "stat": 17138,
        "imgsrc": "https://5e.tools/img/bestiary/tokens/MM/Carrion%20Crawler.webp",
        "alts": [
            "https://5e.tools/img/bestiary/tokens/MM/Carrion%20Crawler.webp",
            "https://www.dndbeyond.com/avatars/8/803/636319242379639973.jpeg"
        ],
        "listItemPath": "/Monsters/Carrion Crawler"
    },
    "commoner": {
        "custom": False,
        "title": "Commoner",
        "size": "Medium",
        "ac": 10,
        "hp": 4,
        "stat": 16829,
        "imgsrc": "https://5e.tools/img/bestiary/tokens/MM/Commoner.webp",
        "alts": [
            "https://5e.tools/img/bestiary/tokens/MM/Commoner.webp",
            "https://www.dndbeyond.com/avatars/4675/675/636747837794884984.jpeg"
        ],
        "listItemPath": "/Monsters/Commoner"
    },
    "captive villager": {
        "custom": False,
        "title": "Captive Villager",
        "size": "Medium",
        "ac": 10,
        "hp": 4,
        "stat": 16829,
        "imgsrc": "https://5e.tools/img/bestiary/tokens/MM/Commoner.webp",
        "alts": [
            "https://5e.tools/img/bestiary/tokens/MM/Commoner.webp",
            "https://www.dndbeyond.com/avatars/4675/675/636747837794884984.jpeg"
        ],
        "listItemPath": "/Monsters/Commoner"
    }
}

DUNGEON_ROOMS = {
    1: {"name": "Marshaling Area", "grid": (44, 20), "creatures": []},
    2: {"name": "Chamber of the Keeper", "grid": (38, 20), "creatures": [
        {"name": "The Keeper", "count": 1},
        {"name": "Carnivorous Ape", "count": 2}
    ]},
    3: {"name": "Cell Block", "grid": (44, 28), "creatures": []},
    4: {"name": "Bugbear Overseers", "grid": (32, 22), "creatures": [
        {"name": "Bugbear", "count": 6}
    ]},
    5: {"name": "Bugbear Barracks", "grid": (26, 22), "creatures": [
        {"name": "Bugbear", "count": 12}
    ]},
    6: {"name": "Bugbear Officers", "grid": (26, 28), "creatures": [
        {"name": "Bugbear Chief", "count": 3}
    ]},
    7: {"name": "Bugbear Armory", "grid": (32, 28), "creatures": []},
    8: {"name": "Bugbear Mess", "grid": (38, 28), "creatures": []},
    9: {"name": "Slave Pens", "grid": (50, 24), "creatures": [
        {"name": "Orc Slave", "count": 10}
    ]},
    10: {"name": "Torture Chamber", "grid": (56, 24), "creatures": [
        {"name": "Hill Giant Torturer", "count": 1}
    ]},
    11: {"name": "Armory & Smithy", "grid": (62, 24), "creatures": [
        {"name": "Fire Giant Smith", "count": 2}
    ]},
    12: {"name": "Weird Abandoned Temple", "grid": (50, 36), "creatures": []},
    15: {"name": "Subterranean Cistern", "grid": (44, 40), "creatures": [
        {"name": "Water Weird", "count": 1}
    ]},
    16: {"name": "Stone Giant Miners", "grid": (32, 42), "creatures": [
        {"name": "Stone Giant", "count": 3}
    ]},
    21: {"name": "Manticore Pen", "grid": (60, 42), "creatures": [
        {"name": "Manticore", "count": 2}
    ]},
    31: {"name": "Minor Treasure Room", "grid": (68, 48), "creatures": []},
    32: {"name": "Secret Room", "grid": (72, 48), "creatures": []},
    33: {"name": "Chief's Secret Vault", "grid": (76, 48), "creatures": []}
}


def load_abovevtt(path):
    raw = open(path, "r", encoding="utf-8").read().strip()
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        return json.loads(decoded), True
    except Exception:
        return json.loads(raw), False


def save_abovevtt(path, data, is_base64=True):
    text = json.dumps(data, indent="\t")
    if is_base64:
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        with open(path, "w", encoding="utf-8") as f:
            f.write(encoded)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def create_room_number_token(room_num, x_px, y_px, vpps=70):
    tid = str(uuid.uuid4())
    return tid, {
        "id": tid,
        "name": f"{room_num:02d}",
        "left": f"{x_px:.1f}px",
        "top": f"{y_px:.1f}px",
        "size": vpps,
        "sizeId": None,
        "gridSquares": 1,
        "imgsrc": f"https://abovevtt-assets.s3.eu-central-1.amazonaws.com/numbers/{room_num}.png",
        "color": "#1A6AFF",
        "hidden": True,
        "locked": False,
        "itemType": "builtinToken",
        "placeType": "count",
        "vision": "0",
        "disableborder": True,
        "tokenStyleSelect": "circle",
        "hidehpbar": True
    }


def upsert_custom_notes(data):
    """Ensure custom stat block notes exist in data['notes']."""
    if "notes" not in data or not isinstance(data["notes"], dict):
        data["notes"] = {}
    notes = data["notes"]

    note_map = {}
    for key, cdata in CUSTOM_CREATURE_DATA.items():
        slug = cdata["slug"]
        found_id = None
        for nid, n in notes.items():
            if not isinstance(n, dict):
                continue
            if nid.startswith(f"{slug}-") or (n.get("title") or "").strip().lower() == cdata["title"].lower():
                found_id = nid
                break

        if not found_id:
            found_id = f"{slug}-{uuid.uuid4()}"

        html = build_ddb_html(cdata)
        notes[found_id] = {
            "id": found_id,
            "title": cdata["title"],
            "text": html,
            "plain": html,
            "player": True,
            "statBlock": True,
            "abilityTracker": {}
        }
        note_map[key] = found_id

    return note_map


def build_custom_stat_dict(blueprint):
    """Build the customStat object on token."""
    ab = blueprint.get("abilities", [10, 10, 10, 10, 10, 10])
    saves = blueprint.get("saves", {})
    cs = {}
    for i, score in enumerate(ab):
        m = mod(score)
        s_val = saves.get(str(i), m)
        cs[str(i)] = {
            "save": f"{s_val:+d}",
            "mod": f"{m:+d}"
        }
    return cs


def configure_creature_token(token, blueprint, note_id=None, vpps=70):
    """Apply full standard properties to a creature token."""
    size_name = blueprint["size"]
    grid_sq, size_id = SIZE_LOOKUP.get(size_name, (1, 4))
    token["gridSquares"] = grid_sq
    token["sizeId"] = size_id
    token["size"] = int(round(grid_sq * vpps))
    token["imgsrc"] = blueprint["imgsrc"]
    token["alternativeImages"] = list(blueprint.get("alts", [blueprint["imgsrc"]]))
    token["tokenStyleSelect"] = "virtualMiniCircle"
    token["tokenBaseStyleSelect"] = "default"
    token["hidehpbar"] = True
    token["armorClass"] = blueprint.get("ac", 10)
    token["hitPointInfo"] = {
        "maximum": blueprint.get("hp", 10),
        "current": blueprint.get("hp", 10),
        "temp": 0
    }
    token["hidden"] = False
    token["locked"] = False
    token["placeType"] = "count"

    if blueprint.get("custom"):
        token["itemType"] = "myToken"
        token["monster"] = "customStat"
        token["statBlock"] = note_id
        token["itemId"] = note_id
        token["listItemPath"] = blueprint.get("listItemPath", f"/My Tokens/{token.get('name')}")
        token["customStat"] = build_custom_stat_dict(blueprint)
    else:
        st = blueprint.get("stat")
        token["itemType"] = "monster"
        token["monster"] = st
        token["stat"] = st
        token["itemId"] = st
        token["listItemPath"] = blueprint.get("listItemPath", f"/Monsters/{token.get('name')}")
        if "statBlock" in token:
            del token["statBlock"]


def populate_and_format_scene(abovevtt_path, scene_name="Dungeon", add_creatures=False, format_all=False, write=False, out_path=None):
    data, is_base64 = load_abovevtt(abovevtt_path)

    note_map = upsert_custom_notes(data)

    scenes_to_process = []
    for s in data.get("scenes", []):
        if s.get("itemType") == "scene":
            title = s.get("title", "").strip().lower()
            if format_all or title == scene_name.strip().lower():
                scenes_to_process.append(s)

    if not scenes_to_process:
        raise ValueError(f"No matching scene found for '{scene_name}'.")

    for target_scene in scenes_to_process:
        s_title = target_scene.get("title")
        vpps = int(target_scene.get("vpps") or 70)
        tokens_dict = target_scene.get("tokens", {})
        if isinstance(tokens_dict, list):
            tokens_dict = {t["id"]: t for t in tokens_dict if "id" in t}

        added_numbers = 0
        added_creatures = 0

        # If populating Dungeon, add missing room numbers or creatures
        if s_title.strip().lower() == "dungeon":
            for room_num, info in DUNGEON_ROOMS.items():
                gx, gy = info["grid"]
                px = gx * vpps
                py = gy * vpps

                exists = any(t.get("name") == f"{room_num:02d}" for t in tokens_dict.values())
                if not exists:
                    tid, tok = create_room_number_token(room_num, px, py, vpps=vpps)
                    tokens_dict[tid] = tok
                    added_numbers += 1

                if add_creatures:
                    for c in info.get("creatures", []):
                        name = c["name"]
                        base_key = name.strip().lower()
                        blueprint = CREATURE_BLUEPRINTS.get(base_key)
                        if not blueprint:
                            continue

                        count = c.get("count", 1)
                        # Check how many of this creature type currently exist in tokens_dict
                        curr_existing = [
                            t for t in tokens_dict.values()
                            if re.sub(r"\s+\d+$", "", t.get("name", "").strip()).lower() == base_key
                        ]

                        needed = count - len(curr_existing)
                        for i in range(max(0, needed)):
                            cid = str(uuid.uuid4())
                            c_x = px + (i + 1) * vpps
                            c_y = py

                            tok = {
                                "id": cid,
                                "name": name,
                                "left": f"{c_x:.1f}px",
                                "top": f"{c_y:.1f}px",
                            }
                            nid = note_map.get(base_key)
                            configure_creature_token(tok, blueprint, note_id=nid, vpps=vpps)
                            tokens_dict[cid] = tok
                            added_creatures += 1

        # Now group, renumber, style and set borders
        groups = collections.defaultdict(list)
        for tid, t in tokens_dict.items():
            if not isinstance(t, dict):
                continue
            name = t.get("name", "")
            if not name or name.isdigit() or "/numbers/" in (t.get("imgsrc") or ""):
                continue
            base = re.sub(r"\s+\d+$", "", name.strip()).lower()
            groups[base].append((tid, t))

        modified = 0
        for base_key, toks in groups.items():
            blueprint = CREATURE_BLUEPRINTS.get(base_key)
            multi = len(toks) > 1

            # Sort spatially (top, left)
            toks.sort(key=lambda item: (
                float(str(item[1].get("top", 0)).replace("px", "") or 0),
                float(str(item[1].get("left", 0)).replace("px", "") or 0)
            ))

            for idx, (tid, t) in enumerate(toks):
                display_name = blueprint["title"] if (blueprint and "title" in blueprint) else base_key.title()
                if multi:
                    t["name"] = f"{display_name} {idx + 1}"
                    t["disableborder"] = False
                    col = PALETTE[idx % len(PALETTE)]
                    t["color"] = col
                else:
                    t["name"] = display_name
                    t["disableborder"] = True
                    t["color"] = "#1A6AFF"

                if blueprint:
                    nid = note_map.get(base_key)
                    configure_creature_token(t, blueprint, note_id=nid, vpps=vpps)

                modified += 1

        target_scene["tokens"] = tokens_dict
        print(f"Scene '{s_title}': added {added_numbers} numbers, {added_creatures} creatures; updated/styled {modified} tokens.")

    dest = out_path or abovevtt_path
    if write:
        save_abovevtt(dest, data, is_base64=is_base64)
        print(f"Successfully saved to: {dest}")
    else:
        print(f"[DRY RUN] Would write changes to {dest}. Pass --write to apply.")


def main():
    parser = argparse.ArgumentParser(description="Place and format AboveVTT tokens.")
    parser.add_argument("--abovevtt", required=True, help="AboveVTT export file")
    parser.add_argument("--scene", default="Dungeon", help="Scene name (default: Dungeon)")
    parser.add_argument("--creatures", action="store_true", help="Add starter creature tokens to Dungeon")
    parser.add_argument("--format-all", action="store_true", help="Apply styling standards across all scenes (Upper Works + Dungeon)")
    parser.add_argument("--write", action="store_true", help="Write changes to file")
    parser.add_argument("--out", help="Output path (default: overwrite)")

    args = parser.parse_args()
    populate_and_format_scene(
        abovevtt_path=args.abovevtt,
        scene_name=args.scene,
        add_creatures=args.creatures,
        format_all=args.format_all,
        write=args.write,
        out_path=args.out
    )


if __name__ == "__main__":
    main()
