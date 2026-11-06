#!/usr/bin/env python3
"""Extract an Xbox (XDVDFS) disc image to a directory.

Xbox game discs are not ISO-9660: the filesystem is XDVDFS, described by a
"MICROSOFT*XBOX*MEDIA" volume descriptor at offset 0x10000. Tools that open
ISO-9660 images fail on them, so the roles that build a native port from an
owned disc use this instead of a packaged binary.

Usage:
    xiso-extract.py IMAGE.iso OUT_DIR

Files keep their on-disc names and layout; the extraction is verified by the
caller against a known hash of the executable it needs (default.xbe).
"""

from __future__ import annotations

import pathlib
import struct
import sys

SECTOR = 2048
MAGIC = b"MICROSOFT*XBOX*MEDIA"


def read_tree(image, root_sector: int, root_size: int):
    """Yield (name, start_sector, size, is_dir) for every entry, recursively."""
    pending = [(root_sector, root_size, "")]
    while pending:
        sector, size, prefix = pending.pop()
        image.seek(sector * SECTOR)
        table = image.read(size)
        seen: set[int] = set()
        stack = [0]
        while stack:
            off = stack.pop()
            if off in seen or off + 14 > len(table):
                continue
            seen.add(off)
            left, right = struct.unpack_from("<HH", table, off)
            start, length = struct.unpack_from("<II", table, off + 4)
            attr = table[off + 12]
            nlen = table[off + 13]
            name = table[off + 14 : off + 14 + nlen].decode("latin1")
            # Siblings are relative to the table start, in 4-byte units.
            if left:
                stack.append(left * 4)
            if right:
                stack.append(right * 4)
            if nlen == 0:
                continue
            if attr & 0x10:
                yield (prefix + name, start, length, True)
                pending.append((start, length, prefix + name + "/"))
            else:
                yield (prefix + name, start, length, False)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: xiso-extract.py IMAGE.iso OUT_DIR", file=sys.stderr)
        return 2
    image_path, out_path = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    if not image_path.is_file():
        print(f"xiso-extract: no image at {image_path}", file=sys.stderr)
        return 1
    out_path.mkdir(parents=True, exist_ok=True)

    files = 0
    with image_path.open("rb") as image:
        image.seek(0x10000)
        descriptor = image.read(28)
        if descriptor[:20] != MAGIC:
            print(f"xiso-extract: {image_path} is not an XDVDFS image", file=sys.stderr)
            return 1
        root_sector, root_size = struct.unpack_from("<II", descriptor, 20)

        for name, start, size, is_dir in read_tree(image, root_sector, root_size):
            destination = out_path / name
            if is_dir:
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.seek(start * SECTOR)
            remaining = size
            with destination.open("wb") as out:
                while remaining:
                    chunk = image.read(min(4 << 20, remaining))
                    if not chunk:
                        print(f"xiso-extract: truncated while reading {name}", file=sys.stderr)
                        return 1
                    out.write(chunk)
                    remaining -= len(chunk)
            files += 1

    print(f"xiso-extract: {files} files -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
