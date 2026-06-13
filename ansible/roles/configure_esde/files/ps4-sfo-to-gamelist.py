#!/usr/bin/env python3
"""Generate ES-DE gamelist.xml for the PS4 system from PARAM.SFO metadata.

For each <ps4_root>/<CUSA_xxxxx>/sce_sys/param.sfo found, parse the
TITLE field and write a <game> entry in the output gamelist.xml whose
<path> points at the eboot.bin inside the same CUSA dir. ES-DE
displays games using the <name> from gamelist.xml when present, which
is how we avoid showing every game as "eboot".

Usage: ps4-sfo-to-gamelist.py <ps4_root> <output_gamelist.xml>
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement


def parse_sfo(path: Path) -> dict[str, str | int]:
    """Parse a Sony PARAM.SFO file. Returns dict of key -> value."""
    data = path.read_bytes()
    if data[:4] != b"\x00PSF":
        raise ValueError(f"not a SFO file: {path}")
    _magic, _version, key_off, data_off, n_entries = struct.unpack_from(
        "<4sIIII", data, 0
    )
    out: dict[str, str | int] = {}
    for i in range(n_entries):
        k_off, data_fmt, used_len, _total_len, d_off = struct.unpack_from(
            "<HHIII", data, 0x14 + i * 16
        )
        key_start = key_off + k_off
        key_end = data.index(b"\x00", key_start)
        key = data[key_start:key_end].decode("utf-8", "replace")
        val_bytes = data[data_off + d_off : data_off + d_off + used_len]
        if data_fmt in (0x0404, 0x0204):
            out[key] = val_bytes.rstrip(b"\x00").decode("utf-8", "replace")
        elif data_fmt == 0x0004:
            out[key] = struct.unpack("<I", val_bytes[:4])[0]
        else:
            out[key] = val_bytes.hex()
    return out


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <ps4_root> <output_gamelist.xml>", file=sys.stderr)
        return 2

    ps4_root = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()

    if not ps4_root.is_dir():
        print(f"ps4_root does not exist: {ps4_root}", file=sys.stderr)
        return 1

    game_list = Element("gameList")
    entries: list[tuple[str, str, str]] = []  # (sort_key, name, eboot_rel)

    for cusa_dir in sorted(ps4_root.iterdir()):
        if not cusa_dir.is_dir():
            continue
        eboot = cusa_dir / "eboot.bin"
        if not eboot.is_file():
            continue
        sfo = cusa_dir / "sce_sys" / "param.sfo"

        name = cusa_dir.name  # fallback = CUSA ID
        title_id = cusa_dir.name
        version: str | None = None

        if sfo.is_file():
            try:
                meta = parse_sfo(sfo)
            except Exception as exc:
                print(f"WARN: failed to parse {sfo}: {exc}", file=sys.stderr)
            else:
                if t := meta.get("TITLE"):
                    name = str(t).strip()
                if tid := meta.get("TITLE_ID"):
                    title_id = str(tid).strip()
                if v := meta.get("VERSION"):
                    version = str(v).strip()

        # Path is relative to <system>'s configured path (ps4_root). ES-DE
        # tolerates both ./CUSA.../eboot.bin and absolute paths; relative
        # is more portable across box-home moves.
        eboot_rel = "./" + os.path.relpath(eboot, ps4_root)
        entries.append((name.lower(), name, eboot_rel))

        game = SubElement(game_list, "game")
        SubElement(game, "path").text = eboot_rel
        SubElement(game, "name").text = name
        desc_lines = [f"Title ID: {title_id}"]
        if version:
            desc_lines.append(f"App Version: {version}")
        SubElement(game, "desc").text = "\n".join(desc_lines)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Render to bytes first so we can compare against existing and only
    # write (+ report changed) on actual content drift. Without this the
    # task reports changed every run, breaking reset-configs idempotency.
    from io import BytesIO

    buf = BytesIO()
    ElementTree(game_list).write(buf, encoding="UTF-8", xml_declaration=True)
    new_bytes = buf.getvalue()

    existing = out_path.read_bytes() if out_path.exists() else b""
    if existing == new_bytes:
        print(f"unchanged: {len(entries)} PS4 entries -> {out_path}")
        return 0

    out_path.write_bytes(new_bytes)
    print(f"wrote {len(entries)} PS4 entries -> {out_path}")
    for _sort, name, eboot_rel in entries:
        print(f"  {name}  ({eboot_rel})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
