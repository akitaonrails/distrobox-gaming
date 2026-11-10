#!/usr/bin/env python3
"""Unpack the GT4 GSdx renderer zip into <release>/game/gs, flattened.

The upstream zip is built on Windows: entry names use backslashes and its
directory entries carry no execute bit, so plain unzip cannot create files
inside them (and leaves literal `dir\\file` names behind). This writes the
tree under normal names, flattens the single version-named top folder and
makes the directories traversable.

usage: extract_gsdx.py DEST_ZIP_DIR GS_ZIP
"""
import os
import shutil
import sys
import zipfile


def make_traversable(path: str) -> None:
    """Add u+x to every directory under path, repeated for depth."""
    for _ in range(8):
        try:
            for root, dirs, _files in os.walk(path, onerror=lambda _e: None):
                for name in dirs:
                    full = os.path.join(root, name)
                    try:
                        os.chmod(full, os.stat(full).st_mode | 0o700)
                    except OSError:
                        pass
        except OSError:
            pass


def extract(archive: str, out: str) -> None:
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            target = os.path.join(out, name)
            if name.endswith("/"):
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)


def main(dest: str, archive: str) -> int:
    make_traversable(dest)
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)

    stage = dest + ".extract"
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    try:
        extract(archive, stage)
        entries = os.listdir(stage)
        src = stage
        if len(entries) == 1 and os.path.isdir(os.path.join(stage, entries[0])):
            src = os.path.join(stage, entries[0])
        for name in os.listdir(src):
            s = os.path.join(src, name)
            d = os.path.join(dest, name)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    finally:
        make_traversable(stage)
        shutil.rmtree(stage, ignore_errors=True)

    if not os.path.isfile(os.path.join(dest, "gt4-gs.exe")):
        print(f"{dest}: gt4-gs.exe missing after extraction", file=sys.stderr)
        return 1
    print(f"{dest}: GSdx renderer installed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
