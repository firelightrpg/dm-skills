#!/usr/bin/env python3
"""
Room Prompt Generator for Gemini AI Art.

Extracts adventure room descriptions (Heading, DM Info, Audio Cues, and Boxed Text)
from adventure Markdown, appends the user's art style, and copies directly to the
clipboard via xclip for instant pasting into Gemini.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_MODULE = Path("/home/grim/github/tftyp-dm/11 - Steading of the Hill Giant Chief/Steading of the Hill Giant Chief.md")
DEFAULT_STYLE = "First person, Fantasy art, hand painted"


def copy_to_clipboard(text: str, notify_title: str | None = None, notify_msg: str | None = None) -> None:
    """Copy text to X11 clipboard via xclip if available, and send desktop notification."""
    try:
        proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        proc.communicate(input=text.encode("utf-8"))
    except Exception:
        pass
    if notify_title:
        try:
            subprocess.run(["notify-send", notify_title, notify_msg or "Copied to clipboard!"], check=False)
        except Exception:
            pass


class AdventureRoomParser:
    def __init__(self, md_path: Path):
        self.md_path = md_path
        self.content = md_path.read_text(encoding="utf-8")
        self.lines = self.content.splitlines()
        self.rooms = self._parse_rooms()

    def _parse_rooms(self) -> list[dict]:
        rooms = []
        current_section = "General"
        area_re = re.compile(r"^##\s+(\d+[A-Za-z0-9–\s&]*)\.\s+(.*)")
        enc_re = re.compile(r"^##\s+(Encounter\s+\d+):\s+(.*)", re.IGNORECASE)

        for i, line in enumerate(self.lines):
            if line.startswith("## Upper Works:"):
                current_section = "Upper Works"
                continue
            elif line.startswith("## Dungeon Level:"):
                current_section = "Dungeon Level"
                continue
            elif line.startswith("## The Approach:"):
                current_section = "The Approach"
                continue

            area_match = area_re.match(line)
            enc_match = enc_re.match(line)

            if area_match or enc_match:
                code = area_match.group(1).strip() if area_match else enc_match.group(1).strip()
                title = area_match.group(2).strip() if area_match else enc_match.group(2).strip()
                rooms.append({
                    "line_idx": i,
                    "code": code,
                    "title": title,
                    "section": current_section,
                })

        # Calculate bounds and extract content
        for idx, r in enumerate(rooms):
            start = r["line_idx"]
            end = rooms[idx + 1]["line_idx"] if idx + 1 < len(rooms) else len(self.lines)
            chunk = self.lines[start:end]

            # Check if image already exists
            r["has_image"] = any("wyrmbox.com" in l and "/download" in l for l in chunk)

            # Extract snippet up to end of blockquote
            heading = f"{r['code']}. {r['title']}"
            dm_info_lines = []
            bq_lines = []
            audio_lines = []

            in_dm_info = False
            in_bq = False
            bq_finished = False

            for l in chunk[1:]:  # skip heading line
                stripped = l.strip()

                if stripped.startswith("**DM Info:**"):
                    in_dm_info = True
                    continue
                elif stripped.startswith("**Audio Cues:**"):
                    in_dm_info = False
                    # Clean up HTML links in audio cues
                    clean_audio = re.sub(r"<[^>]+>", "", stripped)
                    audio_lines.append(clean_audio)
                    continue
                elif stripped.startswith(">"):
                    in_dm_info = False
                    in_bq = True
                    # Remove leading > and leading space
                    clean_bq = re.sub(r"^>\s?", "", l)
                    bq_lines.append(clean_bq)
                    continue
                elif in_bq and not stripped.startswith(">"):
                    if stripped:  # non-empty line right after blockquote -> blockquote is done
                        bq_finished = True
                        break

                if in_dm_info:
                    dm_info_lines.append(l)

            # Clean up and reconstruct
            dm_info_text = "\n".join(dm_info_lines).strip()
            # Clean Markdown bullet bolding from DM Info if present for cleaner prompt
            dm_info_clean = re.sub(r"^\s*-\s*\*\*([^*]+)\*\*:\s*", r"\1: ", dm_info_text, flags=re.MULTILINE)
            dm_info_clean = re.sub(r"^\s*-\s*", "- ", dm_info_clean, flags=re.MULTILINE)

            audio_text = "\n".join(audio_lines).strip()
            bq_text = "\n".join(bq_lines).strip()

            r["heading_text"] = heading
            r["dm_info_text"] = dm_info_clean
            r["audio_text"] = audio_text
            r["bq_text"] = bq_text

        return rooms

    def get_room(self, query: str) -> dict | None:
        q = query.strip().lower()

        # Handle 'next' query
        if q == "next":
            for r in self.rooms:
                if not r["has_image"]:
                    return r
            return None

        # Check section-specific prefixes like 'd1', 'dungeon 1', 'u1', 'upper 1'
        sec_filter = None
        if q.startswith("d") and q[1:].isdigit():
            sec_filter = "Dungeon Level"
            q = q[1:]
        elif q.startswith("dungeon"):
            sec_filter = "Dungeon Level"
            q = q.replace("dungeon", "").strip()
        elif q.startswith("u") and q[1:].isdigit():
            sec_filter = "Upper Works"
            q = q[1:]
        elif q.startswith("upper"):
            sec_filter = "Upper Works"
            q = q.replace("upper", "").strip()

        # Exact match
        for r in self.rooms:
            if sec_filter and r["section"] != sec_filter:
                continue
            if r["code"].lower() == q:
                return r

        # Fuzzy code/title match
        for r in self.rooms:
            if sec_filter and r["section"] != sec_filter:
                continue
            if q in r["code"].lower() or q in r["title"].lower():
                return r

        return None


def format_room_prompt(room: dict, style: str) -> str:
    parts = [room["heading_text"]]
    if room["dm_info_text"]:
        parts.append(f"DM Info:\n\n{room['dm_info_text']}")
    if room["audio_text"]:
        parts.append(room["audio_text"])
    if room["bq_text"]:
        parts.append(room["bq_text"])
    if style:
        parts.append(style)

    return "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Extract room text & style for Gemini AI generation.")
    parser.add_argument("room", nargs="?", default="next", help="Room code, name, 'next', or 'd1' (default: next)")
    parser.add_argument("--module", "-m", default=str(DEFAULT_MODULE), help="Path to adventure Markdown file")
    parser.add_argument("--style", "-s", default=DEFAULT_STYLE, help="Style prompt to append")
    parser.add_argument("--no-style", action="store_true", help="Omit the style suffix")
    parser.add_argument("--list", "-l", action="store_true", help="List all rooms and image status")
    args = parser.parse_args()

    md_path = Path(args.module).resolve()
    if not md_path.exists():
        print(f"Error: Module file not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    parser_obj = AdventureRoomParser(md_path)

    if args.list:
        print(f"\nAdventure Rooms in {md_path.name}:")
        print(f"{'Section':<15} {'Code':<8} {'Status':<10} {'Title'}")
        print("-" * 65)
        for r in parser_obj.rooms:
            status = "✓ Imaged" if r["has_image"] else "○ Missing"
            print(f"{r['section']:<15} {r['code']:<8} {status:<10} {r['title']}")
        return

    room = parser_obj.get_room(args.room)
    if not room:
        print(f"Error: Room '{args.room}' not found.", file=sys.stderr)
        sys.exit(1)

    style_suffix = "" if args.no_style else args.style
    prompt = format_room_prompt(room, style_suffix)

    copy_to_clipboard(
        prompt,
        notify_title="Gemini Room Prompt Copied!",
        notify_msg=f"[{room['section']}] Area {room['code']}: {room['title']}",
    )

    print(f"\n=======================================================")
    print(f" COPIED TO CLIPBOARD: [{room['section']}] Area {room['code']}")
    print(f" Title: {room['title']}")
    print(f" Status: {'✓ Has Image' if room['has_image'] else '○ Needs Image'}")
    print(f"=======================================================\n")
    print(prompt)
    print(f"\n[!] Paste directly into Gemini (Ctrl+V)!")


if __name__ == "__main__":
    main()
