#!/usr/bin/env python3
"""Extract the release patch embedded in Daytona USA Ultimate Builder.exe.

The patcher compiles `build/release/ultimate.patch` into the Windows binary
(`include_bytes!` in patcher/src-tauri/src/patch.rs), and the source tree does
not ship that file. The blob is found by its magic, its header JSON then gives
the length of the zlib stream area, so we can carve out exactly one patch.

usage: daytona_extract_patch.py BUILDER.exe OUT.patch
"""
import json
import struct
import sys

MAGIC = b"DUSAULT\x02"


def main(exe_path: str, out_path: str) -> int:
    data = open(exe_path, "rb").read()
    at = data.find(MAGIC)
    if at < 0:
        print(f"{exe_path}: no {MAGIC!r} patch inside", file=sys.stderr)
        return 1
    header_len = struct.unpack_from("<I", data, at + 8)[0]
    header = json.loads(data[at + 12:at + 12 + header_len])
    if header.get("format") != 2:
        print(f"{exe_path}: patch format {header.get('format')}, expected 2", file=sys.stderr)
        return 1
    # The stream area ends where its last [offset, length] does.
    end = sum(header["track01"]["ops"])
    for game in header["dusa"]:
        fixup = game.get("fixup")
        if fixup:
            end = max(end, sum(fixup["ops"]))
    blob = data[at:at + 12 + header_len + end]
    with open(out_path, "wb") as f:
        f.write(blob)
    print(f"{out_path}: {len(blob)} bytes ({header['cce']['name']} + "
          f"{len(header['dusa'])} Daytona USA dumps)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))