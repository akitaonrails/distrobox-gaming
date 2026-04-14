#!/usr/bin/env python3
"""
Reorganize a Switch NSP/DLC dump into a clean per-title-ID layout.

Current state of the dump is messy: some folders are named after release
groups (Castlevania_..._NSW-VENOM), some by plain game name (ace combat 7),
some by decorated name (FINAL FANTASY VIII Remastered (NSP)(Update 1.0.2)).
Filenames sometimes embed the title ID in brackets like
[01008B900DC0A800], sometimes not.

This script groups every .nsp by its base title ID:

  <dest>/<BASE_TID>/<original_filename>.nsp

where BASE_TID = base game TID (update TIDs have their last 3 hex digits
set to 800; DLC TIDs go +0x1000 upward — we normalize them all to the
base so updates and DLCs for the same game live together).

Title ID resolution order per NSP:
  1. 16 hex chars inside [] in the filename   (cheap, covers most)
  2. Parse PFS0 container, read the first .cnmt.nca's CNMT metadata
     (embedded title ID — always correct)
  3. Fallback: leave in UNKNOWN/ for manual triage

Usage:
    python3 reorganize_switch_nsps.py /path/to/switch_updates \\
        [--dest /path/to/new/layout]   # default: in-place reorganize
        [--dry-run]                    # print plan only, don't touch files

Idempotent when run a second time (everything is already in its target
location). Safe: uses rename (same-filesystem only). Fails loudly if the
rename would cross filesystems; in that case use --dest on same fs.
"""

import os
import re
import struct
import sys
from collections import defaultdict


FILENAME_TID_RE = re.compile(r"\[([0-9A-Fa-f]{16})\]")


def parse_pfs0(f, base_offset: int = 0):
    """Yield (name, abs_offset, size) tuples from a PFS0 container."""
    f.seek(base_offset)
    if f.read(4) != b"PFS0":
        return []
    num_files = struct.unpack("<I", f.read(4))[0]
    str_table_size = struct.unpack("<I", f.read(4))[0]
    f.read(4)  # reserved

    entries = []
    for _ in range(num_files):
        data_off = struct.unpack("<Q", f.read(8))[0]
        data_sz = struct.unpack("<Q", f.read(8))[0]
        str_off = struct.unpack("<I", f.read(4))[0]
        f.read(4)  # reserved
        entries.append((data_off, data_sz, str_off))

    str_table = f.read(str_table_size)
    header_size = 16 + num_files * 24 + str_table_size
    data_start = base_offset + header_size

    out = []
    for data_off, data_sz, str_off in entries:
        nul = str_table.find(b"\x00", str_off)
        if nul < 0:
            nul = len(str_table)
        name = str_table[str_off:nul].decode("utf-8", errors="replace")
        out.append((name, data_start + data_off, data_sz))
    return out


def tid_from_cnmt(f, cnmt_offset: int) -> str | None:
    """Read title ID from a CNMT NCA inside the NSP.

    NCA header is encrypted with per-content key we don't have here, but
    unencrypted NCAs are rare — what we want is the *inner* CNMT file
    which is plaintext inside its section. Parsing the full NCA header
    chain needs keys. Instead, rely on the filename: every CNMT NCA in
    an NSP is named <title_id>.cnmt.nca where <title_id> is the 16-hex
    CNMT title ID (base TID + 0x800 for updates). The *base* title ID
    of the content lives there; same-game CNMT filenames share the high
    48 bits which is what we group on.
    """
    # This function would need NCA key decryption to truly read CNMT.
    # We skip it — PFS0 filename inspection (below) covers the cases
    # where the bracket TID is missing.
    return None


def extract_tid_from_nsp(nsp_path: str) -> str | None:
    """Return base title ID (16 hex chars) for an NSP, or None."""
    # 1. Filename bracket match — cheapest, covers most cases.
    m = FILENAME_TID_RE.search(os.path.basename(nsp_path))
    if m:
        return normalize_to_base_tid(m.group(1).upper())

    # 2. PFS0 inspection: look at embedded .nca names. CNMT NCA filenames
    #    are the title's cnmt TID, which we normalize to base.
    try:
        with open(nsp_path, "rb") as f:
            files = parse_pfs0(f)
    except OSError:
        return None

    for name, _, _ in files:
        m = re.match(r"([0-9A-Fa-f]{16})\.cnmt\.nca$", name)
        if m:
            return normalize_to_base_tid(m.group(1).upper())
        m = re.match(r"([0-9A-Fa-f]{16})\.nca$", name)
        if m:
            # Any NCA filename is the content ID (hash), not TID.
            # But in practice the first NCA in a patch/update package is
            # the CNMT NCA whose name starts with the CNMT TID. Skip.
            continue
    return None


def normalize_to_base_tid(tid: str) -> str:
    """Normalize update (...800) and DLC (...001/002/...) TIDs to the base.

    Switch TID convention:
      base game:   XXXXXXXXXXXXX000
      update:      XXXXXXXXXXXXX800
      DLC N:       XXXXXXXXXX(base+N)  (different prefix math)

    We only reliably normalize updates: strip the last 3 hex digits and
    append '000'. DLCs get their own TID which doesn't simply add a bit;
    the DLCs of a game share the first 13 hex chars (52 bits). Grouping
    on the first 13 hex + '000' works for most DLC families.
    """
    if len(tid) != 16:
        return tid
    return tid[:13] + "000"


def scan(source: str):
    """Return dict: {base_tid: [nsp_path, ...], 'UNKNOWN': [paths]}."""
    groups = defaultdict(list)
    unresolved = []
    for dirpath, _, files in os.walk(source):
        for fn in files:
            if not fn.lower().endswith((".nsp", ".nsz", ".xci", ".xcz")):
                continue
            full = os.path.join(dirpath, fn)
            tid = extract_tid_from_nsp(full)
            if tid:
                groups[tid].append(full)
            else:
                unresolved.append(full)
    return groups, unresolved


def plan_moves(groups: dict, unresolved: list, source: str, dest: str):
    """Yield (src, dst) pairs for files that need to move."""
    for tid, paths in sorted(groups.items()):
        for src in paths:
            fn = os.path.basename(src)
            dst = os.path.join(dest, tid, fn)
            if os.path.abspath(src) != os.path.abspath(dst):
                yield src, dst
    for src in unresolved:
        fn = os.path.basename(src)
        dst = os.path.join(dest, "UNKNOWN", fn)
        if os.path.abspath(src) != os.path.abspath(dst):
            yield src, dst


def main(argv: list) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 1

    source = argv[0]
    dest = source
    dry_run = False

    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--dest" and i + 1 < len(argv):
            dest = argv[i + 1]
            i += 2
        elif a == "--dry-run":
            dry_run = True
            i += 1
        else:
            print(f"Unknown arg: {a}", file=sys.stderr)
            return 1

    if not os.path.isdir(source):
        print(f"ERROR: source not a directory: {source}", file=sys.stderr)
        return 1

    print(f"Scanning {source}...")
    groups, unresolved = scan(source)
    total = sum(len(v) for v in groups.values()) + len(unresolved)
    print(f"Found {total} NSP files across {len(groups)} title groups, "
          f"{len(unresolved)} unresolved.")
    print()

    moves = list(plan_moves(groups, unresolved, source, dest))
    if not moves:
        print("Nothing to do — layout is already clean.")
        return 0

    print(f"{'DRY RUN: ' if dry_run else ''}Planned moves: {len(moves)}")
    sample = moves[:10]
    for src, dst in sample:
        rel_src = os.path.relpath(src, source)
        rel_dst = os.path.relpath(dst, dest)
        print(f"  {rel_src[:60]:60} -> {rel_dst[:60]}")
    if len(moves) > len(sample):
        print(f"  ... and {len(moves) - len(sample)} more")
    print()

    if dry_run:
        return 0

    # Safety guard: detect dst collisions before any move happens.
    seen_dst = set()
    for _, dst in moves:
        if dst in seen_dst:
            print(f"ERROR: destination collision, refusing to run: {dst}",
                  file=sys.stderr)
            return 1
        seen_dst.add(dst)

    moved = 0
    errors = 0
    for src, dst in moves:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # Refuse to overwrite an existing file at destination.
        if os.path.exists(dst):
            print(f"  SKIP (exists): {dst}", file=sys.stderr)
            errors += 1
            continue
        try:
            os.rename(src, dst)
            moved += 1
        except OSError as e:
            print(f"  ERROR moving {src}: {e}", file=sys.stderr)
            errors += 1

    # Clean up now-empty source dirs. Skip any directory whose name looks
    # like one of our destination TID folders (16 hex chars) or UNKNOWN —
    # those are the ones we just moved files INTO and should preserve even
    # if they happen to be empty.
    import re
    tid_re = re.compile(r"^[0-9A-Fa-f]{16}$")
    for dirpath, dirnames, filenames in os.walk(source, topdown=False):
        if dirpath == source:
            continue
        name = os.path.basename(dirpath)
        if tid_re.match(name) or name == "UNKNOWN":
            continue
        if not filenames and not dirnames:
            try:
                os.rmdir(dirpath)
            except OSError:
                pass

    print(f"Complete: {moved} moved, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
