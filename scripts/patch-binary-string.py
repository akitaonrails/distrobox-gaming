#!/usr/bin/env python3
"""Replace one fixed-width ASCII string inside a binary, in place.

Used by roles that have to bend a compiled-in constant (e.g. an installer's
list of accepted disc-image hashes) without patching the source. The
replacement must be the same length as the original so code offsets and any
embedded pointers stay valid.

Usage:
    patch-binary-string.py FILE OLD NEW

Prints "patched" when the file changed and "unchanged" when OLD is no longer
present (a rerun), so a role can derive changed_when from the output. Fails if
OLD appears more than once: an ambiguous patch is not worth guessing at.
"""

from __future__ import annotations

import pathlib
import sys


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: patch-binary-string.py FILE OLD NEW", file=sys.stderr)
        return 2

    path = pathlib.Path(argv[1])
    old = argv[2].encode()
    new = argv[3].encode()
    if len(old) != len(new):
        print("OLD and NEW must be the same length", file=sys.stderr)
        return 2
    if not old:
        print("OLD must not be empty", file=sys.stderr)
        return 2

    data = path.read_bytes()
    occurrences = data.count(old)
    if occurrences == 0:
        print("unchanged")
        return 0
    if occurrences > 1:
        print(f"OLD appears {occurrences} times; refusing to patch", file=sys.stderr)
        return 1

    path.write_bytes(data.replace(old, new))
    print("patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
