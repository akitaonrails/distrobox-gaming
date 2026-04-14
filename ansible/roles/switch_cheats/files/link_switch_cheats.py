#!/usr/bin/env python3
"""
Symlink Atmosphere-format Switch cheats into Eden's load path.

Cheats source layout:
  <SOURCE>/<TITLE_ID> - <Game Name>/cheats/<build_id>.txt

Eden expects:
  <EDEN_LOAD>/<TITLE_ID>/cheats/<build_id>.txt

We symlink the per-game `cheats/` subdirectory itself, not the parent
(parent often holds non-cheat files like readme.txt).

Idempotent: existing correct symlinks are left alone, broken or stale
links are replaced.
"""

import os
import re
import sys


def link_cheats(source: str, eden_load: str, dry_run: bool = False) -> dict:
    if not os.path.isdir(source):
        print(f"ERROR: cheats source not found: {source}", file=sys.stderr)
        return {"linked": 0, "skipped": 0, "errors": 1}

    os.makedirs(eden_load, exist_ok=True)

    counts = {"linked": 0, "skipped": 0, "errors": 0}
    title_re = re.compile(r"^([0-9A-Fa-f]{16})")

    for entry in sorted(os.listdir(source)):
        src_dir = os.path.join(source, entry)
        if not os.path.isdir(src_dir):
            continue

        match = title_re.match(entry)
        if not match:
            continue

        tid = match.group(1).upper()
        cheats_src = os.path.join(src_dir, "cheats")
        if not os.path.isdir(cheats_src):
            counts["skipped"] += 1
            continue

        dest_parent = os.path.join(eden_load, tid)
        dest = os.path.join(dest_parent, "cheats")

        # Idempotency: same target already in place
        if os.path.islink(dest) and os.readlink(dest) == cheats_src:
            counts["skipped"] += 1
            continue

        if dry_run:
            print(f"  WOULD LINK: {tid} -> {entry}")
            counts["linked"] += 1
            continue

        try:
            os.makedirs(dest_parent, exist_ok=True)
            if os.path.islink(dest) or os.path.exists(dest):
                os.unlink(dest)
            os.symlink(cheats_src, dest)
            counts["linked"] += 1
        except OSError as e:
            print(f"  ERROR linking {tid}: {e}", file=sys.stderr)
            counts["errors"] += 1

    return counts


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    source = sys.argv[1]
    eden_load = os.path.expanduser("~/.local/share/eden/load")
    dry_run = False

    args = sys.argv[2:]
    while args:
        if args[0] == "--dest" and len(args) > 1:
            eden_load = args[1]
            args = args[2:]
        elif args[0] == "--dry-run":
            dry_run = True
            args = args[1:]
        else:
            print(f"Unknown arg: {args[0]}", file=sys.stderr)
            sys.exit(1)

    print(f"Source:      {source}")
    print(f"Destination: {eden_load}")
    if dry_run:
        print("DRY RUN — no symlinks will be created")
    print()

    counts = link_cheats(source, eden_load, dry_run)
    print()
    print(
        f"Complete: {counts['linked']} linked, "
        f"{counts['skipped']} already in place, "
        f"{counts['errors']} errors"
    )

    sys.exit(1 if counts["errors"] else 0)


if __name__ == "__main__":
    main()
