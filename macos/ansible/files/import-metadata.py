#!/usr/bin/env python3
"""Import existing names/descriptions and cover links; never modify source ROMs."""
import sys
from pathlib import Path
import xml.etree.ElementTree as E
import shutil
import time

library, home, system = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
source = library / 'gamelist.xml'
if not source.exists():
    raise SystemExit(0)
tree = E.parse(source)
root = tree.getroot()
changed = False
for game in list(root):
    rom = (library / game.findtext('path', '')).resolve()
    if not rom.is_file() or not rom.is_relative_to(library.resolve()):
        root.remove(game)
        continue
    game.find('path').text = str(rom)
    image = game.find('image')
    if image is not None and image.text:
        cover = (library / image.text).resolve()
        if cover.is_file() and cover.is_relative_to(library.resolve()):
            target = home / 'downloaded_media' / system / 'covers' / rom.relative_to(library.resolve()).with_suffix(cover.suffix)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() and not target.is_symlink():
                target.symlink_to(cover)
                changed = True
        game.remove(image)
target = home / 'gamelists' / system / 'gamelist.xml'
data = E.tostring(root, encoding='utf-8', xml_declaration=True)
if not target.exists() or target.read_bytes() != data:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.copy2(target, str(target) + '.' + str(time.time_ns()) + '.bak')
    target.write_bytes(data)
    changed = True
print('changed' if changed else 'unchanged')
