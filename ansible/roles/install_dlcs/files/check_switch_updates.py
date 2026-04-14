#!/usr/bin/env python3
"""
Report Switch games whose available update version is newer than what
you currently have staged in the switch_updates directory.

Since Nintendo's official update CDN requires device authentication
(console certs you only get by hacking a Switch), we can't download
updates automatically. This script only LISTS games that are outdated
so you can hunt down the newer NSPs manually.

Data source for "latest version available":
  https://raw.githubusercontent.com/blawar/titledb/master/versions.txt
  (community titledb, public, 10-minute cache)

Usage:
    python3 check_switch_updates.py /path/to/switch-roms \\
        --updates-dir /path/to/switch_updates

Detect strategy:
  1. For each base game ROM folder, extract title ID (16 hex chars in
     filename brackets, or scan NSP headers).
  2. Scan switch_updates/ for NSPs of the matching update TID
     (base TID with last 3 hex digits replaced by 800).
  3. Parse [v<number>] version from NSP filenames to find the highest
     version staged locally.
  4. Compare to blawar/titledb versions.txt for latest release.
"""

import os
import re
import struct
import sys
import urllib.request

VERSIONS_URL = "https://raw.githubusercontent.com/blawar/titledb/master/versions.txt"
FILENAME_TID_RE = re.compile(r"\[([0-9A-Fa-f]{16})\]")
FILENAME_VER_RE = re.compile(r"\[v(\d+)\]")


def parse_pfs0(path: str) -> list:
    """Return first few inner filenames from an NSP (to extract CNMT TID)."""
    try:
        with open(path, "rb") as f:
            if f.read(4) != b"PFS0":
                return []
            num_files = struct.unpack("<I", f.read(4))[0]
            str_table_size = struct.unpack("<I", f.read(4))[0]
            f.read(4)
            f.seek(16 + num_files * 24, 0)
            str_table = f.read(str_table_size)
    except OSError:
        return []
    return [
        str_table[i:str_table.index(b"\x00", i)].decode("utf-8", errors="replace")
        for i in [0] + [j + 1 for j in range(len(str_table)) if str_table[j:j + 1] == b"\x00"][:-1]
    ]


def tid_from_file(path: str) -> str | None:
    fn = os.path.basename(path)
    m = FILENAME_TID_RE.search(fn)
    if m:
        return m.group(1).upper()
    # Last resort: peek inside the NSP for a cnmt.nca named with the TID
    if fn.lower().endswith(".nsp"):
        for name in parse_pfs0(path):
            m = re.match(r"([0-9A-Fa-f]{16})\.cnmt\.nca$", name)
            if m:
                return m.group(1).upper()
    return None


def tid_from_dir(dir_path: str) -> str | None:
    """Resolve base TID for a ROM directory by inspecting any file inside."""
    if not os.path.isdir(dir_path):
        return None
    for entry in os.listdir(dir_path):
        full = os.path.join(dir_path, entry)
        if os.path.isfile(full) and entry.lower().endswith((".nsp", ".xci")):
            tid = tid_from_file(full)
            if tid:
                return base_tid(tid)
    # Also check dir name itself
    m = FILENAME_TID_RE.search(os.path.basename(dir_path))
    return base_tid(m.group(1).upper()) if m else None


def base_tid(tid: str) -> str:
    """Normalize any TID (base/update/DLC) to the base game TID."""
    if len(tid) != 16:
        return tid
    return tid[:13] + "000"


def update_tid(tid: str) -> str:
    """Return the update-variant TID (...800) for a base TID."""
    if len(tid) != 16:
        return tid
    return tid[:13] + "800"


def fetch_versions() -> dict:
    """Return {update_tid: version_int} mapping from blawar titledb."""
    try:
        req = urllib.request.Request(
            VERSIONS_URL, headers={"User-Agent": "ansible-distrobox-gaming/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"ERROR fetching versions.txt: {e}", file=sys.stderr)
        return {}

    out = {}
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        tid, _rights, ver = parts[0].upper(), parts[1], parts[2]
        if len(tid) != 16 or not ver.strip().isdigit():
            continue
        out[tid] = int(ver)
    return out


def ver_to_semver(raw: int) -> str:
    """Switch raw version int to human string. raw is major * 65536 + minor."""
    return f"v{raw // 65536}.{raw % 65536}"


def max_staged_version(updates_dir: str, base_tid_: str) -> int | None:
    """Find the highest version NSP present in updates_dir for this base TID."""
    upd_tid = update_tid(base_tid_)
    best = None
    for root, _, files in os.walk(updates_dir):
        for fn in files:
            if not fn.lower().endswith(".nsp"):
                continue
            if upd_tid not in fn.upper():
                # Only consider NSPs whose filename has the update TID
                continue
            m = FILENAME_VER_RE.search(fn)
            if m:
                v = int(m.group(1))
                if best is None or v > best:
                    best = v
    return best


def game_name(dir_path: str) -> str:
    return os.path.basename(dir_path.rstrip("/"))


def main(argv: list) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 1

    rom_root = argv[0]
    updates_dir = None

    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--updates-dir" and i + 1 < len(argv):
            updates_dir = argv[i + 1]
            i += 2
        else:
            print(f"Unknown arg: {a}", file=sys.stderr)
            return 1

    if not os.path.isdir(rom_root):
        print(f"ERROR: rom_root not found: {rom_root}", file=sys.stderr)
        return 1
    if updates_dir and not os.path.isdir(updates_dir):
        print(f"WARNING: updates_dir not found: {updates_dir}", file=sys.stderr)
        updates_dir = None

    print(f"Scanning Switch ROMs in {rom_root}...")
    games = []
    for entry in sorted(os.listdir(rom_root)):
        full = os.path.join(rom_root, entry)
        if not os.path.isdir(full):
            continue
        tid = tid_from_dir(full)
        if tid:
            games.append((tid, entry, full))

    print(f"Found {len(games)} ROMs with resolvable TIDs.")
    print("Fetching latest versions from blawar/titledb...")
    versions = fetch_versions()
    print(f"Loaded {len(versions)} version entries.")
    print()

    outdated = []
    up_to_date = []
    no_info = []

    for tid, name, _ in games:
        upd_tid = update_tid(tid)
        latest = versions.get(upd_tid, 0)

        staged = max_staged_version(updates_dir, tid) if updates_dir else None

        if latest == 0:
            no_info.append((tid, name, staged))
            continue

        if staged is None:
            outdated.append((tid, name, 0, latest, "no update staged"))
        elif staged < latest:
            outdated.append((tid, name, staged, latest,
                             f"have {ver_to_semver(staged)} < {ver_to_semver(latest)}"))
        else:
            up_to_date.append((tid, name, staged, latest))

    if outdated:
        print(f"Outdated games ({len(outdated)}):")
        for tid, name, staged, latest, note in sorted(outdated, key=lambda x: -x[3]):
            print(f"  {tid}  staged={ver_to_semver(staged):<8} "
                  f"latest={ver_to_semver(latest):<8}  {name[:55]}")
        print()

    if up_to_date:
        print(f"Up to date ({len(up_to_date)}):")
        for tid, name, _, _ in up_to_date:
            print(f"  {tid}  {name[:70]}")
        print()

    if no_info:
        print(f"No version info in titledb ({len(no_info)}):")
        for tid, name, _ in no_info:
            print(f"  {tid}  {name[:70]}")
        print()

    print(f"Summary: {len(outdated)} outdated, {len(up_to_date)} current, "
          f"{len(no_info)} unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
