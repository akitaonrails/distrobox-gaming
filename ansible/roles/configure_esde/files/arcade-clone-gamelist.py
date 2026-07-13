#!/usr/bin/env python3
"""Generate an ES-DE gamelist.xml from a Skraper gamelist, hiding
MAME-style clone sets.

Skraper scrapes every clone zip to the same display name, so ES-DE
shows "Daytona USA" four times (daytona, daytonam, daytonase,
daytonata). ES-DE ignores the in-ROM-dir gamelist entirely, so without
this the games also display as raw MAME filenames.

For each group of entries sharing a display <name>, the one with the
shortest filename is kept visible (in MAME-style sets the parent is a
prefix of its clones) and the rest are marked <hidden>true</hidden>.
Ties break alphabetically. Names, descriptions and release dates are
carried over; media is resolved separately via the downloaded_media
symlinks.

Usage: arcade-clone-gamelist.py <skraper-gamelist.xml> <out-gamelist.xml>
"""

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 64
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.is_file():
        print(f"skipping: no source gamelist at {src}")
        return 0

    tree = ET.parse(src)
    games = []
    for g in tree.getroot().iter("game"):
        path = (g.findtext("path") or "").strip()
        name = (g.findtext("name") or "").strip()
        if not path or not name:
            continue
        games.append({
            "path": path,
            "name": name,
            "desc": (g.findtext("desc") or "").strip(),
            "releasedate": (g.findtext("releasedate") or "").strip(),
        })

    by_name = defaultdict(list)
    for g in games:
        by_name[g["name"]].append(g)
    for group in by_name.values():
        group.sort(key=lambda g: (len(Path(g["path"]).name), g["path"]))
        for clone in group[1:]:
            clone["hidden"] = True

    root = ET.Element("gameList")
    for g in sorted(games, key=lambda g: g["path"]):
        e = ET.SubElement(root, "game")
        ET.SubElement(e, "path").text = g["path"]
        ET.SubElement(e, "name").text = g["name"]
        if g["desc"]:
            ET.SubElement(e, "desc").text = g["desc"]
        if g["releasedate"]:
            ET.SubElement(e, "releasedate").text = g["releasedate"]
        if g.get("hidden"):
            ET.SubElement(e, "hidden").text = "true"

    ET.indent(root)
    new = ET.tostring(root, encoding="unicode") + "\n"
    old = dst.read_text() if dst.is_file() else None
    if new == old:
        print(f"unchanged: {dst}")
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new)
    hidden = sum(1 for g in games if g.get("hidden"))
    print(f"wrote {dst}: {len(games)} games, {hidden} clones hidden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
