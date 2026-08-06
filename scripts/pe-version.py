#!/usr/bin/env python3
"""Print the FileVersion of a Windows PE executable.

Scans for the VS_FIXEDFILEINFO signature (0xFEEF04BD) and decodes the
dwFileVersionMS / dwFileVersionLS dwords, printing "major.minor.build.revision".
No external deps (no pefile) — a raw signature scan, which is enough to read a
game exe's advertised version.

Used by the NexusMods mod-set roles (nexus-mod-set skill) to assert a modded
game is the exact version a mod set requires (e.g. GTA IV Complete Edition
1.2.0.59) BEFORE installing anything. With --expect, exits 2 on mismatch.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

SIGNATURE = b"\xbd\x04\xef\xfe"  # 0xFEEF04BD little-endian


def file_version(path: Path) -> str:
    data = path.read_bytes()
    idx = data.find(SIGNATURE)
    if idx < 0:
        raise SystemExit(f"{path}: no VS_FIXEDFILEINFO version resource found")
    # struct VS_FIXEDFILEINFO: dwSignature(4) dwStrucVersion(4)
    # dwFileVersionMS(4) dwFileVersionLS(4) ...
    ms = struct.unpack_from("<I", data, idx + 8)[0]
    ls = struct.unpack_from("<I", data, idx + 12)[0]
    return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("--expect", help="exit 2 unless the version equals this")
    args = parser.parse_args()
    version = file_version(args.exe.expanduser())
    print(version)
    if args.expect and version != args.expect:
        print(f"mismatch: expected {args.expect}, found {version}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
