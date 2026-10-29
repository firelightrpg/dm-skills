#!/usr/bin/env python3
"""Convert a GIMP battle map wall mask directly into clean AboveVTT vector walls.

Bypasses AboveVTT's buggy client-side marching squares and destructive smoothing passes,
vectorizing the user's exact GIMP selection lines into clean, straight, grid-aligned walls.

Usage:
  python mask_to_abovevtt.py --mask MASK.png --abovevtt SCENE.abovevtt --scene "Dungeon" [--write] [--out OUT.abovevtt]
"""

import argparse
import base64
import json
import os
import sys
import cv2
import numpy as np


def extract_walls_from_user_mask(mask_path, grid=35, snap_tol=8, min_len=8, approx_eps=6.0):
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"Mask file not found: {mask_path}")

    print(f"Loading user mask: {mask_path}")
    img = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read mask image: {mask_path}")

    h, w = img.shape[:2]
    print(f"Mask dimensions: {w}x{h} px")

    # In user GIMP mask, walls are opaque (alpha > 128)
    if len(img.shape) == 3 and img.shape[2] == 4:
        binary_walls = (img[:, :, 3] > 128).astype(np.uint8) * 255
    else:
        # Fall back to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        binary_walls = (gray > 128).astype(np.uint8) * 255

    print(f"Wall stroke pixels: {cv2.countNonZero(binary_walls)}")

    # Close micro-gaps (1-3px) in the user's hand/fuzzy selection
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(binary_walls, cv2.MORPH_CLOSE, kernel3)

    # Invert: rooms become solid white regions, outer unexcavated void is also a region
    rooms = cv2.bitwise_not(closed)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(rooms, connectivity=8)

    # Identify the outer border void (touches corner (0,0))
    outer_label = labels[0, 0]
    print(f"Outer void component ID: {outer_label} ({stats[outer_label, cv2.CC_STAT_AREA]} px)")

    # Keep only the true playable rooms and corridors (discarding outer void and tiny noise)
    room_mask = np.zeros_like(rooms)
    kept_rooms = 0
    for i in range(1, num_labels):
        if i != outer_label and stats[i, cv2.CC_STAT_AREA] >= 500:
            room_mask[labels == i] = 255
            kept_rooms += 1

    print(f"Identified {kept_rooms} distinct room & corridor areas.")

    # Find the room perimeters and interior pillars with RETR_CCOMP
    cnts, hierarchy = cv2.findContours(room_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Extracted {len(cnts)} room perimeter and pillar contours.")

    def snap_coordinate(val):
        if grid <= 0:
            return float(val)
        r = round(val / grid) * grid
        return float(r if abs(val - r) <= snap_tol else val)

    drawings = []
    wall_count = 0

    for cnt in cnts:
        # Douglas-Peucker polygon approximation on the room perimeter
        approx = cv2.approxPolyDP(cnt, approx_eps, True)
        pts = approx.reshape(-1, 2)
        if len(pts) < 3:
            continue

        # Snap vertices to grid where close
        snapped = []
        for p in pts:
            snapped.append([snap_coordinate(p[0]), snap_coordinate(p[1])])

        # Orthogonal snap for nearly horizontal / vertical segments
        n = len(snapped)
        for j in range(n):
            p1 = snapped[j]
            p2 = snapped[(j + 1) % n]
            if abs(p1[1] - p2[1]) <= 5:
                avg_y = float(round((p1[1] + p2[1]) / 2))
                p1[1] = avg_y
                p2[1] = avg_y
            elif abs(p1[0] - p2[0]) <= 5:
                avg_x = float(round((p1[0] + p2[0]) / 2))
                p1[0] = avg_x
                p2[0] = avg_x

        # Collinear segment merging
        merged = []
        i = 0
        while i < n:
            start_pt = snapped[i]
            curr_pt = snapped[(i + 1) % n]
            while (i + 2) <= n:
                next_pt = snapped[(i + 2) % n]
                dx1, dy1 = curr_pt[0] - start_pt[0], curr_pt[1] - start_pt[1]
                dx2, dy2 = next_pt[0] - curr_pt[0], next_pt[1] - curr_pt[1]
                cross = dx1 * dy2 - dy1 * dx2
                if abs(cross) < 1e-3 and (dx1 * dx2 >= 0) and (dy1 * dy2 >= 0):
                    curr_pt = next_pt
                    i += 1
                else:
                    break
            merged.append((start_pt, curr_pt))
            i += 1

        for p1, p2 in merged:
            length = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
            if length < min_len:
                continue

            drawings.append([
                "line",
                "wall",
                "rgba(0, 255, 0, 1)",
                round(p1[0], 1),
                round(p1[1], 1),
                round(p2[0], 1),
                round(p2[1], 1),
                6,
                1,
                False,
                "",
                ""
            ])
            wall_count += 1

    if drawings:
        drawings.append("wallsChanged")

    print(f"Generated {wall_count} crisp, straight AboveVTT vector walls.")
    return drawings, wall_count, w, h


def apply_to_abovevtt(abovevtt_path, drawings, scene_name="Dungeon", write=False, out_path=None, w=None, h=None):
    raw = open(abovevtt_path, "r", encoding="utf-8").read().strip()
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        data = json.loads(decoded)
        is_b64 = True
    except Exception:
        data = json.loads(raw)
        is_b64 = False

    target_scene = None
    for s in data.get("scenes", []):
        if s.get("itemType") == "scene" and s.get("title", "").strip().lower() == scene_name.strip().lower():
            target_scene = s
            break

    if target_scene is None:
        raise ValueError(f"Scene '{scene_name}' not found.")

    target_scene["drawings"] = drawings
    if w and h:
        target_scene["width"] = w
        target_scene["height"] = h

    dest = out_path or abovevtt_path
    if write:
        text = json.dumps(data, indent="\t")
        if is_b64:
            encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            with open(dest, "w", encoding="utf-8") as f:
                f.write(encoded)
        else:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"Successfully saved {len(drawings)-1} walls directly to: {dest}")
    else:
        print(f"[DRY RUN] Would save {len(drawings)-1} walls to {dest}. Pass --write to apply.")


def main():
    parser = argparse.ArgumentParser(description="Convert GIMP wall mask directly into AboveVTT JSON walls.")
    parser.add_argument("--mask", required=True, help="Path to GIMP mask PNG")
    parser.add_argument("--abovevtt", required=True, help="Path to .abovevtt export file")
    parser.add_argument("--scene", default="Dungeon", help="Scene title (default: Dungeon)")
    parser.add_argument("--grid", type=int, default=35, help="Snap grid spacing (default: 35 for half-grid, 70 for full)")
    parser.add_argument("--write", action="store_true", help="Write changes to the .abovevtt file")
    parser.add_argument("--out", help="Output path (default: overwrite input)")

    args = parser.parse_args()
    drawings, count, w, h = extract_walls_from_user_mask(args.mask, grid=args.grid)
    apply_to_abovevtt(args.abovevtt, drawings, scene_name=args.scene, write=args.write, out_path=args.out, w=w, h=h)


if __name__ == "__main__":
    main()
