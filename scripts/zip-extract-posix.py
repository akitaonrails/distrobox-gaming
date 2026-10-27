#!/usr/bin/env python3
"""Extract a ZIP whose entry names use Windows backslashes.

Some Windows-built release archives store entry names as
``dir\\subdir\\file`` instead of ``dir/subdir/file``. Neither
``ansible.builtin.unarchive`` (unzip) nor 7-Zip on POSIX rewrites those, so
the archive extracts into a handful of files whose *names* contain
backslashes. This extractor converts the separators before writing.

Usage:
    python3 scripts/zip-extract-posix.py ARCHIVE.zip DEST_DIR

Existing files are overwritten. The destination is created if missing.
"""

from __future__ import annotations

import pathlib
import sys
import zipfile


def safe_target(root: pathlib.Path, name: str) -> pathlib.Path:
    normalised = name.replace("\\", "/")
    target = (root / normalised).resolve()
    if not target.is_relative_to(root.resolve()):
        raise SystemExit(f"refusing path escaping the destination: {name!r}")
    return target


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    archive_path, dest = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            target = safe_target(dest, info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, open(target, "wb") as out:
                while chunk := src.read(1 << 20):
                    out.write(chunk)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
