#!/usr/bin/env python3
"""Delete an install path while keeping the save data registered in dg_save_sets.

Revert tasks must never destroy a player's saves. This removes an install
directory (or launcher/desktop file) but walks around every path listed as a
save source in `ansible/group_vars/all/backups.yml`: save files and their
parent directories survive in place, so a reinstall finds them again.

usage: dg-revert-clean.py --backups-file FILE --box-home DIR --user NAME --path P
"""
import argparse
import os
import shutil
import sys

import yaml


def resolve(src, box_home, user):
    src = str(src)
    if src.startswith("file:"):
        src = src[5:]
    src = src.replace("{{ ansible_facts.user_id }}", user)
    src = src.replace("{{ ansible_facts.env.HOME }}", box_home)
    if src.startswith("/"):
        return os.path.normpath(src)
    return os.path.normpath(os.path.join(box_home, src))


def load_saves(backups_file, box_home, user):
    with open(backups_file) as f:
        data = yaml.safe_load(f) or {}
    out = []
    for entry in data.get("dg_save_sets", []) or []:
        src = entry.get("src")
        srcs = src if isinstance(src, list) else [src]
        for item in srcs:
            if item is None:
                continue
            path = resolve(item, box_home, user)
            if "*" in path:
                continue  # globs are resolved by backup-saves, not here
            out.append(path)
    return out


def is_save_or_inside(path, saves):
    return any(path == s or path.startswith(s + os.sep) for s in saves)


def is_ancestor_of_save(path, saves):
    return any(s.startswith(path + os.sep) for s in saves)


def clean(path, saves):
    """Delete path, keeping saves and their parent directories. Returns kept paths."""
    if not os.path.exists(path):
        return []
    if is_save_or_inside(path, saves):
        return [path]
    if not is_ancestor_of_save(path, saves) and not is_save_or_inside(path, saves):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)
        print(f"removed {path}")
        return []

    kept = []
    for name in sorted(os.listdir(path)):
        child = os.path.join(path, name)
        if is_save_or_inside(child, saves) or is_ancestor_of_save(child, saves):
            if os.path.isdir(child):
                kept.extend(clean(child, saves))
            else:
                kept.append(child)
        else:
            if os.path.isdir(child):
                shutil.rmtree(child)
            else:
                os.unlink(child)
            print(f"removed {child}")
    if not kept and os.path.isdir(path):
        try:
            os.rmdir(path)
            print(f"removed {path}")
        except OSError:
            pass
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backups-file", required=True)
    ap.add_argument("--box-home", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--path", action="append", required=True)
    args = ap.parse_args()

    saves = load_saves(args.backups_file, args.box_home, args.user)
    all_kept = []
    for path in args.path:
        kept = clean(path, saves)
        all_kept.extend(kept)
    for path in all_kept:
        print(f"kept save {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
