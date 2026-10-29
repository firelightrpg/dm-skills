#!/usr/bin/env python3
"""Convert Universal VTT (.uvtt / .dd2vtt) walls, doors, and lights into AboveVTT scene format.

AboveVTT stores drawings in scene["drawings"] as:
  - Walls: ['line', 'wall', 'rgba(0, 255, 0, 1)', x1, y1, x2, y2, 6, 1, false, '', '']
  - Doors (closed): ['line', 'wall', 'rgba(255, 100, 255, 1)', x1, y1, x2, y2, 12, 1, false, '', '']
  - Doors (open): ['line', 'wall', 'rgba(255, 100, 255, 0.5)', x1, y1, x2, y2, 12, 1, false, '', '']
  - Secret doors: ['line', 'wall', 'rgba(100, 0, 255, 1)', x1, y1, x2, y2, 12, 1, false, '', '']

Usage:
  python uvtt_to_abovevtt.py --uvtt MAP.uvtt --abovevtt SCENE.abovevtt --scene "Dungeon" [--write] [--out OUT.abovevtt]
"""

import argparse
import base64
import json
import math
import os
import sys

DOOR_COLORS = {
    0: {  # standard door
        "open": "rgba(255, 100, 255, 0.5)",
        "closed": "rgba(255, 100, 255, 1)"
    },
    1: {  # window
        "open": "rgba(255, 255, 0, 0.5)",
        "closed": "rgba(255, 255, 0, 1)"
    },
    2: {  # locked door
        "open": "rgba(150, 50, 150, 0.5)",
        "closed": "rgba(150, 50, 150, 1)"
    },
    4: {  # secret door
        "open": "rgba(100, 0, 255, 0.5)",
        "closed": "rgba(100, 0, 255, 1)"
    }
}


def load_abovevtt(path):
    raw = open(path, "r", encoding="utf-8").read().strip()
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        return json.loads(decoded), True
    except Exception:
        # Fall back to plain json
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


def load_uvtt(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_uvtt_to_drawings(uvtt_data, grid_size=70, door_type=0, door_hidden=False):
    resolution = uvtt_data.get("resolution", {})
    map_origin_x = resolution.get("map_origin", {}).get("x", 0) or 0
    map_origin_y = resolution.get("map_origin", {}).get("y", 0) or 0
    map_size_x = resolution.get("map_size", {}).get("x", 0)
    map_size_y = resolution.get("map_size", {}).get("y", 0)

    # Pixels per grid from UVTT if available and reasonable
    uvtt_ppg = resolution.get("pixels_per_grid", 70)
    if grid_size is None or grid_size <= 0:
        grid_size = uvtt_ppg or 70

    drawings = []
    wall_count = 0
    door_count = 0

    # Line of sight (walls)
    for chain in uvtt_data.get("line_of_sight", []):
        for j in range(1, len(chain)):
            p1 = chain[j - 1]
            p2 = chain[j]

            # In grid units: convert to pixels
            x1 = round((p1["x"] - map_origin_x) * grid_size, 2)
            y1 = round((p1["y"] - map_origin_y) * grid_size, 2)
            x2 = round((p2["x"] - map_origin_x) * grid_size, 2)
            y2 = round((p2["y"] - map_origin_y) * grid_size, 2)

            # Avoid 0-length walls
            if math.isclose(x1, x2, abs_tol=1e-3) and math.isclose(y1, y2, abs_tol=1e-3):
                continue

            drawings.append([
                "line",
                "wall",
                "rgba(0, 255, 0, 1)",
                x1,
                y1,
                x2,
                y2,
                6,
                1,
                False,
                "",
                ""
            ])
            wall_count += 1

    # Portals (doors & windows)
    for portal in uvtt_data.get("portals", []):
        bounds = portal.get("bounds", [])
        if len(bounds) < 2:
            continue

        closed = "closed" if portal.get("closed", True) else "open"
        portal_type = portal.get("type", door_type)
        if portal_type not in DOOR_COLORS:
            portal_type = 0
        color = DOOR_COLORS[portal_type][closed]

        x1 = round((bounds[0]["x"] - map_origin_x) * grid_size, 2)
        y1 = round((bounds[0]["y"] - map_origin_y) * grid_size, 2)
        x2 = round((bounds[1]["x"] - map_origin_x) * grid_size, 2)
        y2 = round((bounds[1]["y"] - map_origin_y) * grid_size, 2)

        drawings.append([
            "line",
            "wall",
            color,
            x1,
            y1,
            x2,
            y2,
            12,
            1,
            door_hidden,
            "",
            ""
        ])
        door_count += 1

    # Ensure wallsChanged is present
    if drawings:
        drawings.append("wallsChanged")

    calc_width = int(round(map_size_x * grid_size)) if map_size_x else None
    calc_height = int(round(map_size_y * grid_size)) if map_size_y else None

    return drawings, wall_count, door_count, calc_width, calc_height


def apply_uvtt_to_scene(abovevtt_path, uvtt_path, scene_name="Dungeon", out_path=None, write=False, append=False):
    avtt_data, is_base64 = load_abovevtt(abovevtt_path)
    uvtt_data = load_uvtt(uvtt_path)

    # Locate target scene
    scenes = avtt_data.get("scenes", [])
    target_scene = None
    target_idx = None
    for idx, s in enumerate(scenes):
        if s.get("itemType") == "scene" and (s.get("title", "").strip().lower() == scene_name.strip().lower() or s.get("name", "").strip().lower() == scene_name.strip().lower()):
            target_scene = s
            target_idx = idx
            break

    if target_scene is None:
        avail = [f"[{i}] {s.get('title') or s.get('name')}" for i, s in enumerate(scenes) if s.get("itemType") == "scene"]
        raise ValueError(f"Scene '{scene_name}' not found. Available scenes: {', '.join(avail)}")

    # Grid size from scene
    vpps = int(target_scene.get("vpps") or 70)
    drawings, wall_count, door_count, w, h = convert_uvtt_to_drawings(uvtt_data, grid_size=vpps)

    print(f"Loaded UVTT: {uvtt_path}")
    print(f"Target Scene: [{target_idx}] '{target_scene.get('title')}' (grid={vpps}px)")
    print(f"Generated: {wall_count} wall segments, {door_count} doors")
    if w and h:
        print(f"Calculated dimensions: {w} x {h} px")

    existing_drawings = target_scene.get("drawings", [])
    if append:
        # Keep non-wallsChanged items, append new drawings
        cleaned = [d for d in existing_drawings if d != "wallsChanged"]
        cleaned.extend(drawings)
        target_scene["drawings"] = cleaned
    else:
        # Keep non-wall drawings (e.g. lights, fog buckets) if any
        non_walls = [
            d for d in existing_drawings
            if isinstance(d, list) and len(d) > 1 and d[1] not in ("wall",) and d != "wallsChanged"
        ]
        non_walls.extend(drawings)
        target_scene["drawings"] = non_walls

    if w and h:
        target_scene["width"] = w
        target_scene["height"] = h
    target_scene["hpps"] = str(vpps)
    target_scene["vpps"] = str(vpps)

    dest = out_path or abovevtt_path
    if write:
        save_abovevtt(dest, avtt_data, is_base64=is_base64)
        print(f"Successfully saved to: {dest} (base64={is_base64})")
    else:
        print(f"[DRY RUN] Run with --write to save changes to {dest}")


def main():
    parser = argparse.ArgumentParser(description="Convert UVTT walls/doors to AboveVTT format.")
    parser.add_argument("--uvtt", required=True, help="Path to input .uvtt / .dd2vtt file")
    parser.add_argument("--abovevtt", required=True, help="Path to .abovevtt export file")
    parser.add_argument("--scene", default="Dungeon", help="Title of target scene (default: Dungeon)")
    parser.add_argument("--out", help="Path to output file (default: overwrite input)")
    parser.add_argument("--append", action="store_true", help="Append walls instead of replacing existing walls")
    parser.add_argument("--write", action="store_true", help="Write changes to output file")

    args = parser.parse_args()
    apply_uvtt_to_scene(
        abovevtt_path=args.abovevtt,
        uvtt_path=args.uvtt,
        scene_name=args.scene,
        out_path=args.out,
        write=args.write,
        append=args.append
    )


if __name__ == "__main__":
    main()
