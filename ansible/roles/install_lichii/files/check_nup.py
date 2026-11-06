#!/usr/bin/env python3
"""Validate the NUP container header and table of contents without unpacking it."""

import hashlib
import struct
import sys
from pathlib import Path


def main(path: Path) -> None:
    with path.open("rb") as stream:
        header = stream.read(128)
        if len(header) != 128:
            raise ValueError("NUP header is incomplete")
        magic, header_size, version, toc_offset, toc_size = struct.unpack_from(
            "<4sHHQQ", header
        )
        blob_offset, declared_size, packages, flags = struct.unpack_from(
            "<QQII", header, 0x38
        )
        actual_size = path.stat().st_size
        if not (
            magic == b"NUP\x01"
            and header_size == 128
            and version == 1
            and toc_offset == header_size
            and packages >= 1
            and flags == 0
            and blob_offset % 16 == 0
            and blob_offset >= toc_offset + toc_size
            and declared_size == actual_size
        ):
            raise ValueError("NUP header fields or file length are invalid")
        stream.seek(toc_offset)
        digest = hashlib.sha256()
        remaining = toc_size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError("NUP table of contents is incomplete")
            digest.update(chunk)
            remaining -= len(chunk)
        if digest.digest() != header[0x18:0x38]:
            raise ValueError("NUP table-of-contents SHA256 differs from header")
    print(f"NUP v1 header, {packages} packages, TOC SHA256 OK")


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except (IndexError, OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
