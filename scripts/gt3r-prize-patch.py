#!/usr/bin/env python3
"""Multiply Gran Turismo 3 race prizes in a paramdb extracted from a disc.

GT3 Revisited (matt-pulsipher/GT3-revisited) loads database/paramdb_us.db
through its mod VFS: a mod that ships the same file under files/ overrides
the disc's copy. Event records (table 32, 504 bytes each) keep the prize
money for places 1-6 at +0x1D4 and the championship bonus at +0x1E2, six
u16s / one u16 in units of 100 credits, so a multiplier is an in-place edit
that never changes the file size.

Usage:
  gt3r-prize-patch.py <paramdb_us.db> <multiplier> [out.db]

The input is produced by `gt3tool extract <disc.iso> database/paramdb_us.db
<outdir>` from the user's own disc; nothing extracted is ever committed.
"""
import argparse
import struct
import sys
from pathlib import Path

EVENT_TABLE = 32
EVENT_RECORD = 504
PRIZES_OFF = 0x1D4          # 6 x u16: prizes for places 1st-6th, x100 Cr
CHAMPIONSHIP_OFF = 0x1E2    # u16: championship bonus, x100 Cr
U16_MAX = 0xFFFF


def patch(path: Path, multiplier: int, out: Path) -> int:
    data = bytearray(path.read_bytes())
    if data[:4] != b"GTAR":
        raise SystemExit(f"{path}: not a GTAR paramdb container")
    table_count, data_offset = struct.unpack_from("<II", data, 4)
    patched_events = 0
    changed_fields = 0
    samples = []
    for i in range(table_count):
        (offset,) = struct.unpack_from("<I", data, 0x10 + 4 * i)
        start = data_offset + offset
        magic, _version, index, records, rec_size, _byte_size = (
            struct.unpack_from("<4sHHHHI", data, start))
        if magic != b"GTDT":
            raise SystemExit(f"{path}: table {i} is not GTDT")
        if index != EVENT_TABLE:
            continue
        if rec_size != EVENT_RECORD:
            raise SystemExit(
                f"{path}: event table has {rec_size}-byte records, expected {EVENT_RECORD}")
        for r in range(records):
            base = start + 16 + r * rec_size
            fields = struct.unpack_from("<6H", data, base + PRIZES_OFF) \
                + struct.unpack_from("<H", data, base + CHAMPIONSHIP_OFF)
            if not any(fields):
                continue                      # license tests, demos: no prize
            patched_events += 1
            new = list(fields)
            for n, value in enumerate(fields):
                if value:
                    new[n] = min(value * multiplier, U16_MAX)
                    if new[n] != value:
                        changed_fields += 1
            struct.pack_into("<6H", data, base + PRIZES_OFF, *new[:6])
            struct.pack_into("<H", data, base + CHAMPIONSHIP_OFF, new[6])
            if len(samples) < 3:
                samples.append((r, fields[0], new[0]))
    if patched_events == 0:
        raise SystemExit(f"{path}: no event records with prizes found")
    out.write_bytes(data)
    print(f"events with prizes: {patched_events}, fields changed: {changed_fields}")
    for index, before, after in samples:
        print(f"  event {index}: 1st prize {before * 100:,} Cr -> {after * 100:,} Cr")
    return patched_events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paramdb", type=Path, help="extracted database/paramdb_us.db")
    parser.add_argument("multiplier", type=int, help="prize multiplier (>= 1)")
    parser.add_argument("out", type=Path, nargs="?", help="output file (default: in place)")
    args = parser.parse_args()
    if args.multiplier < 1:
        raise SystemExit("multiplier must be >= 1")
    patch(args.paramdb, args.multiplier, args.out or args.paramdb)


if __name__ == "__main__":
    try:
        main()
    except (OSError, struct.error) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
