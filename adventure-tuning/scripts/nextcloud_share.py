#!/usr/bin/env python3
"""
Nextcloud Public Share Generator for Adventure DM Notes.

Uses the Nextcloud OCS Share API to query or create public read-only share links
for files in your local Nextcloud mount (~/Nextcloud/...), outputting direct
download URLs formatted as Markdown images (`![](https://wyrmbox.com/s/<token>/download)`).

Credentials are automatically read from ~/.davfs2/secrets.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def get_davfs_credentials() -> list[tuple[str, str, str]]:
    """Extract list of (base_url, username, password) from ~/.davfs2/secrets in reverse order (newest first)."""
    secrets_path = Path.home() / ".davfs2" / "secrets"
    if not secrets_path.exists():
        secrets_path = Path("/etc/davfs2/secrets")

    creds: list[tuple[str, str, str]] = []
    if secrets_path.exists():
        with open(secrets_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 3 and "http" in parts[0]:
                    url, user, pwd = parts[0], parts[1], parts[2]
                    parsed = urllib.parse.urlparse(url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    creds.append((base_url, user, pwd))

    if creds:
        # Return newest (last) entries first
        return list(reversed(creds))

    # Fallback to env vars if available
    host = os.environ.get("NEXTCLOUD_HOST", "https://wyrmbox.com")
    user = os.environ.get("NEXTCLOUD_USER", "admin")
    pwd = os.environ.get("NEXTCLOUD_PASS", "")
    return [(host, user, pwd)]


def get_nextcloud_relative_path(local_path: Path) -> str:
    """Convert absolute local path to Nextcloud-relative path."""
    abs_path = local_path.resolve()
    nc_mount = Path.home() / "Nextcloud"
    try:
        rel = abs_path.relative_to(nc_mount)
        return str(rel)
    except ValueError:
        # If path is already relative or passed directly
        p_str = str(local_path)
        if "bulk-store" in p_str:
            idx = p_str.find("bulk-store")
            return p_str[idx:]
        return str(local_path).lstrip("/")


class NextcloudShareManager:
    def __init__(self, base_url: str | None = None, user: str | None = None, password: str | None = None):
        if not base_url or not user or not password:
            cred_list = get_davfs_credentials()
            # Try credentials to find the active one
            active_cred = None
            for b, u, p in cred_list:
                auth = f"Basic {base64.b64encode(f'{u}:{p}'.encode('utf-8')).decode('ascii')}"
                test_url = f"{b.rstrip('/')}/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json"
                req = urllib.request.Request(
                    test_url,
                    headers={"OCS-APIRequest": "true", "Accept": "application/json", "Authorization": auth},
                )
                try:
                    with urllib.request.urlopen(req) as resp:
                        if resp.status == 200:
                            active_cred = (b, u, p)
                            break
                except Exception:
                    continue
            if not active_cred:
                active_cred = cred_list[0]
            b, u, p = active_cred
            self.base_url = (base_url or b).rstrip("/")
            self.user = user or u
            self.password = password or p
        else:
            self.base_url = base_url.rstrip("/")
            self.user = user
            self.password = password

        auth_str = f"{self.user}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(auth_str.encode('utf-8')).decode('ascii')}"

    def get_existing_shares(self) -> dict[str, str]:
        """Return dict of {relative_path: direct_download_url} for all existing shares."""
        url = f"{self.base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json"
        req = urllib.request.Request(
            url,
            headers={
                "OCS-APIRequest": "true",
                "Accept": "application/json",
                "Authorization": self.auth_header,
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.load(resp)
            shares = data.get("ocs", {}).get("data", [])
            mapping = {}
            for s in shares:
                p = s.get("path", "").lstrip("/")
                s_url = s.get("url", "")
                if p and s_url:
                    mapping[p] = f"{s_url}/download"
            return mapping
        except Exception as e:
            print(f"[Nextcloud] Warning: Failed to fetch existing shares: {e}", file=sys.stderr)
            return {}

    def get_or_create_share(self, relative_path: str, existing_shares: dict[str, str] | None = None) -> str:
        """Return direct download URL for relative_path, creating public share if needed."""
        clean_path = relative_path.lstrip("/")
        if existing_shares is not None and clean_path in existing_shares:
            return existing_shares[clean_path]

        # Check single file share status via API query
        query_url = f"{self.base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares?path={urllib.parse.quote(clean_path)}&format=json"
        req = urllib.request.Request(
            query_url,
            headers={
                "OCS-APIRequest": "true",
                "Accept": "application/json",
                "Authorization": self.auth_header,
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.load(resp)
            data_list = data.get("ocs", {}).get("data", [])
            for s in data_list:
                if s.get("share_type") == 3 and s.get("url"):
                    return f"{s['url']}/download"
        except Exception:
            pass

        # Create public share (shareType=3, permissions=1 read-only) with retry for WebDAV sync
        post_url = f"{self.base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json"
        body = urllib.parse.urlencode({
            "path": clean_path,
            "shareType": 3,
            "permissions": 1,
        }).encode("utf-8")
        req_post = urllib.request.Request(
            post_url,
            data=body,
            headers={
                "OCS-APIRequest": "true",
                "Accept": "application/json",
                "Authorization": self.auth_header,
            },
        )
        
        import time
        last_err = None
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req_post) as resp:
                    data = json.load(resp)
                share_data = data.get("ocs", {}).get("data", {})
                if "url" in share_data:
                    return f"{share_data['url']}/download"
            except Exception as e:
                last_err = e
                time.sleep(2)

        raise RuntimeError(f"Failed to create public share for {clean_path}: {last_err}")


def copy_to_clipboard(text: str, notify_title: str | None = None) -> None:
    """Copy text to X11 clipboard via xclip if available, and send desktop notification."""
    try:
        proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        proc.communicate(input=text.encode("utf-8"))
    except Exception:
        pass
    if notify_title:
        try:
            subprocess.run(["notify-send", notify_title, "Link copied to clipboard!"], check=False)
        except Exception:
            pass


def insert_images_into_module(
    module_path: Path,
    image_dir: Path,
    mgr: NextcloudShareManager,
    section_name: str = "Upper Works",
    dry_run: bool = False,
) -> list[tuple[str, str, int]]:
    """
    Scan image_dir for area images (e.g., 1.jpeg, 1b.jpeg, 2.jpeg...) and insert
    corresponding public download share links directly into module_path Markdown file
    right after each room's read-aloud blockquote.

    Returns list of (area_code, share_url, line_number).
    """
    content = module_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Index available images
    image_exts = {".jpeg", ".jpg", ".png", ".webp"}
    image_map: dict[str, Path] = {}
    for f in image_dir.iterdir():
        if f.is_file() and f.suffix.lower() in image_exts:
            stem = f.stem.lower()
            image_map[stem] = f

    # Determine section boundaries if specified
    start_line = 0
    end_line = len(lines)
    is_dungeon = False
    if section_name:
        is_dungeon = "dungeon" in section_name.lower() or "lower" in section_name.lower()
        for i, line in enumerate(lines):
            if f"## {section_name.lower()}" in line.lower() or f"# {section_name.lower()}" in line.lower():
                start_line = i
                break
        for i in range(start_line + 1, len(lines)):
            if not is_dungeon and re.match(r"^##\s+(Dungeon\s+Level|Lower\s+Level|Level\s+2)", lines[i], re.IGNORECASE):
                end_line = i
                break

    # Locate area headings
    area_re = re.compile(r"^##\s+(\d+[A-Za-z0-9–\s&]*)\.\s+(.*)")
    enc_re = re.compile(r"^##\s+(Encounter\s+\d+):\s+(.*)", re.IGNORECASE)

    headings: list[tuple[int, str, str]] = []
    for i in range(start_line, end_line):
        m = area_re.match(lines[i])
        if m:
            clean_code = m.group(1).lower().replace("–", "-").replace(" ", "")
            headings.append((i, clean_code, m.group(2)))
        else:
            me = enc_re.match(lines[i])
            if me:
                headings.append((i, me.group(1).lower().replace(" ", "-"), me.group(2)))

    existing_shares = mgr.get_existing_shares()
    changes: list[tuple[int, str, str, str]] = []  # (insert_after_line_idx, area_code, title, url)

    for idx, (h_line, area_code, title) in enumerate(headings):
        # Match candidates: exact code, prefixed with 'd' or 'dungeon-' if dungeon section
        img_path = None
        base_m = re.search(r"^\d+", area_code)
        base = base_m.group(0) if base_m else area_code
        dash_code = area_code.replace("&", "-")
        in_dungeon_dir = "dungeon" in image_dir.name.lower()
        if is_dungeon:
            d_cands = [
                f"d{area_code}",
                f"d{dash_code}",
                f"dungeon-{area_code}",
                f"dungeon-{dash_code}",
                f"d-{area_code}",
                f"d-{dash_code}",
                f"d{base}",
                f"dungeon-{base}",
            ]
            if in_dungeon_dir:
                d_cands.extend([area_code, dash_code, base])
            candidates = d_cands
        elif "upper" in (section_name or "").lower():
            candidates = [area_code, dash_code, base, f"u{area_code}", f"u{base}", f"upper-{area_code}"]
        else:
            candidates = [area_code, dash_code, base]

        for cand in candidates:
            if cand in image_map:
                img_path = image_map[cand]
                break

        if not img_path:
            continue

        next_bound = headings[idx + 1][0] if idx + 1 < len(headings) else end_line
        section_slice = lines[h_line:next_bound]

        # Check if wyrmbox image already inserted
        if any(re.search(r"!\[.*?\]\(https://wyrmbox\.com/.*?\)", l) for l in section_slice):
            continue

        # Find blockquote end
        bq_end = None
        in_bq = False
        for j in range(h_line, next_bound):
            if lines[j].startswith(">"):
                in_bq = True
                bq_end = j
            elif in_bq and not lines[j].startswith(">"):
                break

        if bq_end is None:
            continue

        rel_path = get_nextcloud_relative_path(img_path)
        url = mgr.get_or_create_share(rel_path, existing_shares)

        changes.append((bq_end, area_code, title, url))

    if not changes:
        return []

    # Insert changes in reverse line order so line indices remain stable
    changes.sort(key=lambda x: x[0], reverse=True)
    results: list[tuple[str, str, int]] = []

    for bq_end, area_code, title, url in changes:
        check_idx = bq_end + 1
        while check_idx < len(lines) and not lines[check_idx].strip():
            check_idx += 1

        if check_idx < len(lines) and lines[check_idx].startswith("![") and "5e.tools" in lines[check_idx]:
            lines[check_idx] = f"<!-- {lines[check_idx]} -->"

        while bq_end + 1 < len(lines) and not lines[bq_end + 1].strip():
            del lines[bq_end + 1]

        lines.insert(bq_end + 1, "")
        lines.insert(bq_end + 2, f"![]({url})")
        lines.insert(bq_end + 3, "")
        results.append((area_code, url, bq_end + 2))

    if not dry_run:
        module_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return results


def main():
    parser = argparse.ArgumentParser(description="Create public Nextcloud share links for adventure images.")
    parser.add_argument("path", help="Local file or directory in ~/Nextcloud")
    parser.add_argument("--markdown", "-m", action="store_true", default=True, help="Output as Markdown image ![](url)")
    parser.add_argument("--raw", "-r", action="store_true", help="Output only the raw download URL")
    parser.add_argument("--clipboard", "-c", action="store_true", help="Copy the result to system clipboard via xclip")
    parser.add_argument("--insert", "-i", metavar="MODULE_MD", help="Path to adventure Markdown file to insert image links into")
    parser.add_argument("--section", "-s", default="Upper Works", help="Adventure section to target (default: 'Upper Works')")
    parser.add_argument("--dry-run", action="store_true", help="Simulate insertions without writing to disk")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    mgr = NextcloudShareManager()

    if args.insert:
        md_file = Path(args.insert).resolve()
        if not md_file.is_file():
            print(f"Error: Module file not found: {args.insert}", file=sys.stderr)
            sys.exit(1)
        if not target.is_dir():
            print(f"Error: Target path must be an image directory when using --insert", file=sys.stderr)
            sys.exit(1)

        results = insert_images_into_module(
            md_file,
            target,
            mgr,
            section_name=args.section,
            dry_run=args.dry_run,
        )
        action_verb = "Would insert" if args.dry_run else "Inserted"
        print(f"\n{action_verb} {len(results)} images into {md_file.name} [{args.section}]:")
        for code, url, lno in sorted(results, key=lambda x: (int(re.search(r"\d+", x[0]).group(0)), x[0])):
            print(f"  ✓ Area {code:4s} -> {url} (Line ~{lno})")
        return

    existing = mgr.get_existing_shares()

    output_lines = []
    if target.is_dir():
        image_exts = {".jpeg", ".jpg", ".png", ".webp"}
        files = sorted(
            [f for f in target.iterdir() if f.is_file() and f.suffix.lower() in image_exts],
            key=lambda x: (
                int(re.search(r"(\d+)", x.stem).group(1)) if re.search(r"(\d+)", x.stem) else 9999,
                x.name,
            ),
        )
        for f in files:
            rel = get_nextcloud_relative_path(f)
            url = mgr.get_or_create_share(rel, existing)
            if args.raw:
                line = f"{f.name}: {url}"
            else:
                line = f"<!-- {f.name} -->\n![]({url})\n"
            output_lines.append(line)
            print(line)
    elif target.is_file():
        rel = get_nextcloud_relative_path(target)
        url = mgr.get_or_create_share(rel, existing)
        line = url if args.raw else f"![]({url})"
        output_lines.append(line)
        print(line)
    else:
        print(f"File or directory not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.clipboard and output_lines:
        combined = "\n".join(output_lines).strip()
        copy_to_clipboard(combined, notify_title="Nextcloud Share")


if __name__ == "__main__":
    main()
