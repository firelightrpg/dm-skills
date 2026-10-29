#!/usr/bin/env python3
"""Place room number markers and creature tokens into AboveVTT scenes with standardized styling.

Rules applied:
- Token Style: Virtual Mini w/ Round Base (tokenStyleSelect: "virtualMiniCircle", tokenBaseStyleSelect: "default")
- HP Bar: Only show HP values on hover (hidehpbar: True)
- Border: Disabled for unique creatures; enabled with distinct colors from PALETTE for multiples
- Size: Explicitly scaled to statblock grid footprint (size: gridSquares * vpps)
- Artwork: If DDB alternativeImages has a transparent .png, prefer it over the cropped avatar

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

DUNGEON_ROOMS = {
    1: {"name": "Marshaling Area", "grid": (44, 20), "creatures": []},
    2: {"name": "Chamber of the Keeper", "grid": (38, 20), "creatures": [
        {"name": "The Keeper", "size": "Huge", "img": "https://wyrmbox.com/s/z9BwK8y6X3z4PqA/download"},
        {"name": "Carnivorous Ape", "size": "Medium", "count": 2}
    ]},
    3: {"name": "Cell Block", "grid": (44, 28), "creatures": []},
    4: {"name": "Bugbear Overseers", "grid": (32, 22), "creatures": [
        {"name": "Bugbear", "size": "Medium", "count": 6}
    ]},
    5: {"name": "Bugbear Barracks", "grid": (26, 22), "creatures": [
        {"name": "Bugbear", "size": "Medium", "count": 12}
    ]},
    6: {"name": "Bugbear Officers", "grid": (26, 28), "creatures": [
        {"name": "Bugbear Chief", "size": "Medium", "count": 3}
    ]},
    7: {"name": "Bugbear Armory", "grid": (32, 28), "creatures": []},
    8: {"name": "Bugbear Mess", "grid": (38, 28), "creatures": []},
    9: {"name": "Slave Pens", "grid": (50, 24), "creatures": [
        {"name": "Orc Slave", "size": "Medium", "count": 10}
    ]},
    10: {"name": "Torture Chamber", "grid": (56, 24), "creatures": [
        {"name": "Hill Giant Torturer", "size": "Huge", "count": 1}
    ]},
    11: {"name": "Armory & Smithy", "grid": (62, 24), "creatures": [
        {"name": "Fire Giant Smith", "size": "Huge", "count": 2}
    ]},
    12: {"name": "Weird Abandoned Temple", "grid": (50, 36), "creatures": []},
    15: {"name": "Subterranean Cistern", "grid": (44, 40), "creatures": [
        {"name": "Water Weird", "size": "Large", "count": 1}
    ]},
    16: {"name": "Stone Giant Miners", "grid": (32, 42), "creatures": [
        {"name": "Stone Giant", "size": "Huge", "count": 3}
    ]},
    21: {"name": "Manticore Pen", "grid": (60, 42), "creatures": [
        {"name": "Manticore", "size": "Large", "count": 2}
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


def format_scene_tokens(tokens_dict, vpps=70):
    """Enforce token standards across all creature tokens in a scene."""
    groups = collections.defaultdict(list)
    for tid, t in tokens_dict.items():
        if not isinstance(t, dict):
            continue
        name = t.get("name", "")
        if not name or name.isdigit() or "/numbers/" in (t.get("imgsrc") or ""):
            continue
        # Base creature name
        base = re.sub(r"\s+\d+$", "", name.strip())
        groups[base].append((tid, t))

    modified = 0
    for base, toks in groups.items():
        multi = len(toks) > 1
        used_colors = set()

        # Sort spatially (top, left)
        toks.sort(key=lambda item: (
            float(str(item[1].get("top", 0)).replace("px", "") or 0),
            float(str(item[1].get("left", 0)).replace("px", "") or 0)
        ))

        for idx, (tid, t) in enumerate(toks):
            # 1. Token style: Virtual Mini w/ Round Base
            t["tokenStyleSelect"] = "virtualMiniCircle"
            t["tokenBaseStyleSelect"] = "default"

            # 2. HP values: Only show on hover
            t["hidehpbar"] = True

            # 3. Size: ensure size matches gridSquares * vpps
            gs = t.get("gridSquares") or 1
            t["size"] = int(round(gs * vpps))

            # 4. Artwork: If DDB avatar and alternativeImages contains a .png, upgrade to .png
            curr_img = t.get("imgsrc") or ""
            alts = t.get("alternativeImages") or []
            if "dndbeyond.com/avatars/" in curr_img and not curr_img.lower().endswith(".png"):
                png_alts = [a for a in alts if a.lower().endswith(".png")]
                if png_alts:
                    t["imgsrc"] = png_alts[0]

            # 5. Border: disabled for unique creatures; enabled with distinct colors for multiples
            if multi:
                t["disableborder"] = False
                # Pick unique color
                col = t.get("color")
                if not col or col in used_colors or col == "#1A6AFF":
                    col = next((p for p in PALETTE if p not in used_colors), PALETTE[idx % len(PALETTE)])
                used_colors.add(col)
                t["color"] = col
            else:
                t["disableborder"] = True

            modified += 1

    return modified


def populate_and_format_scene(abovevtt_path, scene_name="Dungeon", add_creatures=False, format_all=False, write=False, out_path=None):
    data, is_base64 = load_abovevtt(abovevtt_path)

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

        # If populating Dungeon, add room numbers & encounter starter tokens
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
                        size_name = c.get("size", "Medium")
                        grid_sq, size_id = SIZE_LOOKUP.get(size_name, (1, 4))
                        px_size = int(round(grid_sq * vpps))
                        count = c.get("count", 1)
                        img = c.get("img", "")

                        for i in range(count):
                            cid = str(uuid.uuid4())
                            suffix = f" {i+1}" if count > 1 else ""
                            c_name = f"{name}{suffix}"
                            c_x = px + (i + 1) * vpps
                            c_y = py
                            col = PALETTE[i % len(PALETTE)] if count > 1 else "#1A6AFF"

                            tokens_dict[cid] = {
                                "id": cid,
                                "name": c_name,
                                "left": f"{c_x:.1f}px",
                                "top": f"{c_y:.1f}px",
                                "size": px_size,
                                "sizeId": size_id,
                                "gridSquares": grid_sq,
                                "imgsrc": img,
                                "color": col,
                                "hidden": False,
                                "locked": False,
                                "itemType": "myToken",
                                "placeType": "count",
                                "monster": "customStat" if img else "1",
                                "tokenStyleSelect": "virtualMiniCircle",
                                "tokenBaseStyleSelect": "default",
                                "hidehpbar": True,
                                "disableborder": count == 1
                            }
                            added_creatures += 1

        # Enforce styling standards
        formatted_count = format_scene_tokens(tokens_dict, vpps=vpps)
        target_scene["tokens"] = tokens_dict

        print(f"Scene '{s_title}': added {added_numbers} numbers, {added_creatures} creatures; styled {formatted_count} tokens.")

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
