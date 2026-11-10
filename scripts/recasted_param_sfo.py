#!/usr/bin/env python3
"""Write a minimal PS4 param.sfo for a PKG extraction that lacks one.

shadpkg drops the game files but not `sce_sys/param.sfo`; ReCasted reads the
title id and app version from it (without it the dump is "UNKNOWN"). This
writes the keys the loader needs, in the PSF (SFO) container format.

usage: recasted_param_sfo.py OUT.sfo TITLE_ID APP_VER [TITLE]
"""
import struct
import sys


def build(entries):
    keys = sorted(entries)
    key_table = b""
    key_off = {}
    for key in keys:
        key_off[key] = len(key_table)
        key_table += key.encode() + b"\0"
    key_table += b"\0" * ((-len(key_table)) % 4)

    data_table = b""
    data_off = {}
    for key in keys:
        value = entries[key]
        data_off[key] = len(data_table)
        data_table += value + b"\0"
        data_table += b"\0" * ((-len(data_table)) % 4)

    header_len = 20 + 16 * len(keys)
    out = struct.pack("<IIIII", 0x46535000, 0x00000101, header_len,
                      header_len + len(key_table), len(keys))
    for key in keys:
        value = entries[key]
        out += struct.pack("<HHIII", key_off[key], 0x0404, len(value) + 1,
                           len(value) + 1, data_off[key])
    return out + key_table + data_table


def main(out_path, title_id, app_ver, title="Ratchet & Clank"):
    entries = {
        "APP_VER": app_ver.encode(),
        "CATEGORY": b"gd",
        "TITLE": title.encode(),
        "TITLE_ID": title_id.encode(),
        "VERSION": app_ver.encode(),
    }
    blob = build(entries)
    with open(out_path, "wb") as f:
        f.write(blob)
    print(f"{out_path}: {len(blob)} bytes (TITLE_ID={title_id}, APP_VER={app_ver})")


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        sys.exit(2)
    main(*sys.argv[1:])
