#!/usr/bin/env python3
"""
Batch-download Xbox 360 Title Updates from archive.org's
"microsoft_xbox360_title-updates" collection.

Scans a local xbox360 ROM directory, matches each game's folder/ISO name
to the matching TU filename(s) in the archive.org collection, picks the
highest-version TU per preferred region (USA > World > Europe > Japan >
other), and downloads to a destination directory using archive.org's
official `ia` CLI tool (handles auth + CDN redirects + resumes cleanly).

Prerequisites:
    1. `ia` CLI installed: `pip install internetarchive` (or Arch
       `python-internetarchive`). Confirm: `ia --version`.
    2. Configured once: `ia configure` — prompts for archive.org email
       and password, stores token at ~/.config/ia.ini.

Usage:
    python3 scripts/download-xbox360-tus.py \\
        --src /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360 \\
        --dest /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360-updates \\
        --concurrency 3 [--dry-run]

Skips downloads whose destination already exists with matching size.
"""

import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

COLLECTION = "microsoft_xbox360_title-updates"
MANIFEST_URL = f"https://archive.org/download/{COLLECTION}/{COLLECTION}_files.xml"

REGION_PRIORITY = ["USA", "World", "Europe", "Japan", "Asia"]

# Local dir names we skip at the top level (never scanned as games).
# Substring match (case-insensitive).
SKIP_LOCAL_SUBSTRINGS = (
    "RidgeRacerCollection",
    # Skip all Forza folders — user maintains those TUs manually.
    "Forza Horizon",
    "Forza Motorsport",
    "FM2 (",
    "FM3 (",
    "FM4 (",
)

# Directories whose immediate children ARE individual games. For each
# entry listed here, we descend one level and treat each subdir as its
# own game for matching purposes. XBLA-style pack dirs in particular.
RECURSE_INTO = ("xbla",)


def fetch_manifest(manifest_cache: str) -> list:
    """Download (or reuse) the collection manifest and return .zip filenames.

    Manifest is public (no auth needed); stored next to the downloads dir.
    """
    if not os.path.exists(manifest_cache) or os.path.getsize(manifest_cache) < 1024:
        print(f"Fetching manifest from {MANIFEST_URL}")
        req = urllib.request.Request(MANIFEST_URL,
                                     headers={"User-Agent": "distrobox-gaming/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(manifest_cache, "wb") as f:
                f.write(resp.read())
    tree = ET.parse(manifest_cache)
    files = []
    for f in tree.getroot().findall("file"):
        name = f.get("name") or ""
        if name.endswith(".zip"):
            size = f.findtext("size")
            files.append((name, int(size) if size and size.isdigit() else 0))
    print(f"Manifest has {len(files)} TU zip files")
    return files


def game_basename(entry_name: str) -> str:
    """Strip region/version/extension noise from a local game dir or ISO name.

    Input:  "Forza Motorsport 4 (USA) (En,Ja,Fr,...) (Disc 1).iso"
    Output: "Forza Motorsport 4"
    """
    name = entry_name
    name = re.sub(r"\.(iso|chd|bin|xex|zip)$", "", name, flags=re.IGNORECASE)
    # Drop everything from the first ( or [ onward
    name = re.sub(r"\s*[\(\[].*$", "", name)
    # Drop " - Disc N", "Disc N", " CD1"
    name = re.sub(r"\s*-?\s*(Disc|CD)\s*\d+\b.*$", "", name, flags=re.IGNORECASE)
    # PFP modded-dir naming: "FM4 (Project Forza Plus Modded)" → "FM4"
    return name.strip()


def parse_tu_name(tu_zip: str) -> dict | None:
    """Parse a TU zip filename into game + region + version.

    Examples matched:
      "Forza Motorsport 3 (USA) (v4).zip"
      "Forza Horizon (World) (v4) (4000D145) (Title Update).zip"
      "Halo 3 (USA) (Rev 1) (v4).zip"
    """
    m = re.match(r"^(.+?)\s*\(([^)]+)\)(?:\s*\([^)]+\))*\s*\(v(\d+)\)", tu_zip)
    if not m:
        return None
    game = m.group(1).strip()
    region_raw = m.group(2).strip()
    version = int(m.group(3))
    # Region can be "USA", "World", "Europe", "Japan", etc. or language codes
    region = "Other"
    for r in REGION_PRIORITY:
        if r.lower() in region_raw.lower():
            region = r
            break
    return {"game": game, "region": region, "version": version, "filename": tu_zip}


def choose_best_tu(tus: list[dict]) -> dict | None:
    """From candidate TUs for a game, pick (region, version) by preference."""
    if not tus:
        return None
    # Sort by (region priority, -version) — lower priority index + higher version wins
    def key(t):
        try:
            rprio = REGION_PRIORITY.index(t["region"])
        except ValueError:
            rprio = len(REGION_PRIORITY)
        return (rprio, -t["version"])
    return sorted(tus, key=key)[0]


def match_games_to_tus(game_names: list[str], all_tus: list[tuple]) -> dict:
    """Return {game_basename: best_tu_dict} for games with matches."""
    parsed_tus = [t for t in (parse_tu_name(n) for n, _ in all_tus) if t]
    # Index TUs by lowercased game name for fast lookup
    tus_by_game = {}
    for t in parsed_tus:
        tus_by_game.setdefault(t["game"].lower(), []).append(t)
    matched = {}
    for g in game_names:
        candidates = tus_by_game.get(g.lower(), [])
        if candidates:
            best = choose_best_tu(candidates)
            matched[g] = best
    return matched


def download_one(filename: str, dest_dir: str, expected_size: int) -> bool:
    """Download a single TU zip via `ia download`.

    Skips if dest already exists at expected_size.
    """
    final_path = os.path.join(dest_dir, filename)
    if os.path.exists(final_path) and os.path.getsize(final_path) == expected_size:
        print(f"  SKIP (exists): {filename}")
        return True
    os.makedirs(dest_dir, exist_ok=True)
    # `ia download` downloads into <destdir>/<item>/<file>. We want it
    # flat under dest_dir/<game>/<file>, so use --no-directories to
    # strip the item-name wrapper dir.
    cmd = [
        "ia", "download",
        COLLECTION, filename,
        "--destdir", dest_dir,
        "--no-directories",
        "--checksum",
        "--retries", "3",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0 and os.path.exists(final_path):
            print(f"  OK: {filename} ({os.path.getsize(final_path)} bytes)")
            return True
        else:
            tail = (result.stderr or result.stdout).strip().splitlines()[-2:]
            print(f"  FAIL: {filename} — {' | '.join(tail)}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {filename}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--src", required=True, help="xbox360 ROM dir to scan")
    ap.add_argument("--dest", required=True, help="output dir for TU zips")
    ap.add_argument("--concurrency", type=int, default=3, help="parallel downloads (default 3)")
    ap.add_argument("--dry-run", action="store_true", help="list matches, don't download")
    args = ap.parse_args()

    if not shutil.which("ia"):
        print("ERROR: `ia` CLI not found in PATH. Install: "
              "`pip install internetarchive` (or pacman `python-internetarchive`).",
              file=sys.stderr)
        print("Then run `ia configure` once with your archive.org credentials.",
              file=sys.stderr)
        return 1

    os.makedirs(args.dest, exist_ok=True)
    all_tus = fetch_manifest(os.path.join(args.dest, "_manifest.xml"))

    # Collect game names from dirs and ISOs, applying skip list + one-
    # level recursion into RECURSE_INTO container dirs (xbla etc.).
    game_names = set()
    for entry in os.listdir(args.src):
        p = os.path.join(args.src, entry)
        # Descend one level into known container dirs
        if os.path.isdir(p) and entry.lower() in (r.lower() for r in RECURSE_INTO):
            for sub in os.listdir(p):
                sp = os.path.join(p, sub)
                if os.path.isdir(sp) or sub.lower().endswith((".iso", ".chd")):
                    if not any(s.lower() in sub.lower() for s in SKIP_LOCAL_SUBSTRINGS):
                        game_names.add(game_basename(sub))
            continue
        if any(s.lower() in entry.lower() for s in SKIP_LOCAL_SUBSTRINGS):
            continue
        if os.path.isdir(p) or entry.lower().endswith((".iso", ".chd")):
            game_names.add(game_basename(entry))
    game_names.discard("")
    print(f"\nFound {len(game_names)} distinct games in {args.src}")
    for g in sorted(game_names):
        print(f"  - {g}")

    print()
    matched = match_games_to_tus(list(game_names), all_tus)
    print(f"Matched {len(matched)} games to TUs:")
    for g, t in sorted(matched.items()):
        print(f"  {g}  →  {t['filename']}  ({t['region']} v{t['version']})")

    unmatched = sorted(g for g in game_names if g not in matched)
    if unmatched:
        print(f"\nNo TU found (or none exists) for {len(unmatched)} games:")
        for g in unmatched:
            print(f"  - {g}")

    if args.dry_run:
        print("\nDRY RUN — exiting without downloading.")
        return 0

    # Download best TU for each matched game into <dest>/<game>/<filename>
    size_by_name = dict(all_tus)
    jobs = []
    for g, t in matched.items():
        dest_dir = os.path.join(args.dest, g)
        jobs.append((t["filename"], dest_dir, size_by_name.get(t["filename"], 0)))

    print(f"\nDownloading {len(jobs)} TUs with concurrency={args.concurrency}...")
    ok = fail = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futs = {pool.submit(download_one, fn, dd, sz): fn for fn, dd, sz in jobs}
        for fut in concurrent.futures.as_completed(futs):
            if fut.result():
                ok += 1
            else:
                fail += 1

    print(f"\nComplete: {ok} downloaded, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
