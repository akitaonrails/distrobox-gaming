#!/usr/bin/env python3
"""Sync emulator cheat/patch files from local community repositories.

The script is intentionally conservative: it only installs files that can be
matched to the local emulator caches or game library, and it skips ambiguous
3DS title-name matches instead of guessing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Iterable


PS2_SERIAL_RE = re.compile(
    r"\b(?:SLUS|SCUS|SLES|SCES|SLPM|SLPS|PBPX|PAPX)-?\d{5}\b", re.I
)
PS1_SERIAL_RE = re.compile(
    r"\b(?:SLUS|SCUS|SLES|SCES|SLPS|SLPM|SCPS)-?\d{5}(?:CE)?\b", re.I
)
TITLE_ID_RE = re.compile(r"^[A-Z]{4}\d{5}$")


def printable_strings(path: Path) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    return "".join(chr(b) if 32 <= b < 127 or b in (9, 10, 13) else "\n" for b in data)


def ensure_dir(path: Path, dry_run: bool) -> None:
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path, dry_run: bool) -> None:
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


PAREN_NOISE_RE = re.compile(
    r"\([^)]*(?:\b(?:en|ja|fr|de|es|it|zh|ko|rev|usa|eur|europe|japan|jpn|world|glo|gb|virtual console)\b|(?:en|ja|fr|de|es|it|zh|ko){2,})[^)]*\)",
    re.I,
)
LANG_BLOB_RE = re.compile(r"\b(?:en|ja|fr|de|es|it|zh|ko){2,}\b", re.I)


def normalized_title(value: str) -> str:
    value = PAREN_NOISE_RE.sub(" ", value)
    value = value.lower().replace("&", " and ").replace("'", "")
    value = LANG_BLOB_RE.sub(" ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(
        r"\b(the|usa|eur|europe|japan|jpn|rev|en|fr|es|de|it|ja|zh|ko|for|nintendo|edition|virtual|console)\b",
        " ",
        value,
    )
    return re.sub(r"\s+", " ", value).strip()


def region_from_name(value: str) -> str:
    if re.search(r"\((?:USA|U)\)", value, re.I):
        return "USA"
    if re.search(r"\((?:Japan|JPN)\)", value, re.I):
        return "JPN"
    if re.search(r"\((?:EUR|Europe)\)", value, re.I):
        return "EUR"
    if re.search(r"\((?:GLO|World)\)", value, re.I):
        return "GLO"
    return ""


def iter_3ds_roms(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".cci", ".3ds", ".cia", ".cxi"}
    )


def sync_azahar(ctrpf_root: Path | None, n3ds_root: Path | None, box_home: Path, dry_run: bool) -> dict:
    result = {"installed": [], "misses": [], "skipped_ambiguous": [], "skipped": None}
    if not ctrpf_root or not n3ds_root or not ctrpf_root.exists() or not n3ds_root.exists():
        result["skipped"] = "missing CTRPF cheat repo or 3DS ROM root"
        return result

    cheats_root = ctrpf_root / "Cheats" if (ctrpf_root / "Cheats").is_dir() else ctrpf_root
    entries = []
    for folder in cheats_root.iterdir():
        if not folder.is_dir():
            continue
        txts = [p for p in folder.glob("*.txt") if re.fullmatch(r"[0-9A-Fa-f]{16}\.txt", p.name)]
        if txts:
            entries.append(
                {
                    "norm": normalized_title(folder.name),
                    "region": region_from_name(folder.name),
                    "folder": folder,
                    "txts": txts,
                }
            )

    dest = box_home / ".local/share/azahar-emu/cheats"
    ensure_dir(dest, dry_run)

    for rom in iter_3ds_roms(n3ds_root):
        game_name = rom.parent.name if rom.parent != n3ds_root else rom.stem
        wanted_region = region_from_name(str(rom))
        rom_tokens = set(normalized_title(game_name).split())
        candidates = []
        for entry in entries:
            if wanted_region and entry["region"] not in {wanted_region, "GLO"}:
                continue
            entry_tokens = set(entry["norm"].split())
            if not rom_tokens or not entry_tokens:
                continue
            score = len(rom_tokens & entry_tokens) / len(rom_tokens | entry_tokens)
            if rom_tokens == entry_tokens or score >= 0.86:
                candidates.append((score, entry))
        if not candidates:
            result["misses"].append(str(rom.relative_to(n3ds_root)))
            continue
        candidates.sort(key=lambda item: (item[0], item[1]["region"] == wanted_region), reverse=True)
        if (
            len(candidates) > 1
            and abs(candidates[0][0] - candidates[1][0]) < 0.001
            and candidates[0][1]["folder"] != candidates[1][1]["folder"]
        ):
            result["skipped_ambiguous"].append(
                {
                    "rom": str(rom.relative_to(n3ds_root)),
                    "candidates": [item[1]["folder"].name for item in candidates[:3]],
                }
            )
            continue
        entry = candidates[0][1]
        for src in entry["txts"]:
            dst = dest / f"{src.stem.upper()}.txt"
            copy_file(src, dst, dry_run)
            result["installed"].append(
                {"rom": str(rom.relative_to(n3ds_root)), "source_folder": entry["folder"].name, "file": dst.name}
            )
    return result


def ps2_serials(box_home: Path) -> set[str]:
    serials = {m.group(0).replace("_", "-").upper() for m in PS2_SERIAL_RE.finditer(printable_strings(box_home / ".config/PCSX2/cache/gamelist.cache"))}
    for path in (box_home / ".config/PCSX2/gamesettings").glob("*.ini"):
        match = re.match(r"((?:SLUS|SCUS|SLES|SCES|SLPM|SLPS|PBPX|PAPX)-?\d{5})_", path.name, re.I)
        if match:
            serials.add(match.group(1).replace("_", "-").upper())
    return serials


def sync_pcsx2(repo_root: Path | None, box_home: Path, dry_run: bool) -> dict:
    result = {"installed": [], "misses": [], "skipped": None}
    if not repo_root or not repo_root.exists():
        result["skipped"] = "missing PCSX2 cheat repo"
        return result
    source_root = repo_root / "cheats" if (repo_root / "cheats").is_dir() else repo_root
    wanted = ps2_serials(box_home)
    matched = set()
    dest = box_home / ".config/PCSX2/cheats"
    ensure_dir(dest, dry_run)
    for src in sorted(source_root.glob("*.pnach")):
        match = re.match(r"((?:SLUS|SCUS|SLES|SCES|SLPM|SLPS|PBPX|PAPX)-?\d{5})_([0-9A-Fa-f]{8})\.pnach$", src.name)
        if not match:
            continue
        serial = match.group(1).replace("_", "-").upper()
        crc = match.group(2).upper()
        if serial not in wanted:
            continue
        modern = dest / f"{serial}_{crc}.pnach"
        copy_file(src, modern, dry_run)
        legacy = dest / f"{crc}.pnach"
        if dry_run or not legacy.exists():
            copy_file(src, legacy, dry_run)
        result["installed"].append({"serial": serial, "file": modern.name})
        matched.add(serial)
    result["misses"] = sorted(wanted - matched)
    return result


def ps1_serials(box_home: Path) -> set[str]:
    serials = {m.group(0).upper() for m in PS1_SERIAL_RE.finditer(printable_strings(box_home / ".config/duckstation/cache/gamelist.cache"))}
    for path in (box_home / ".config/duckstation/gamesettings").glob("*.ini"):
        serials.add(path.stem.upper())
    playtime = box_home / ".config/duckstation/playtime.dat"
    if playtime.exists():
        for line in playtime.read_text(errors="ignore").splitlines():
            parts = line.split()
            if parts and PS1_SERIAL_RE.match(parts[0]):
                serials.add(parts[0].upper())
    return serials


def sync_duckstation(repo_root: Path | None, box_home: Path, dry_run: bool) -> dict:
    result = {"installed": [], "misses": [], "skipped": None}
    if not repo_root or not repo_root.exists():
        result["skipped"] = "missing DuckStation chdtdb repo"
        return result
    source_root = repo_root / "cheats" if (repo_root / "cheats").is_dir() else repo_root
    wanted = ps1_serials(box_home)
    matched = set()
    dest = box_home / ".config/duckstation/cheats"
    ensure_dir(dest, dry_run)
    for src in sorted(source_root.glob("*.cht")):
        serial = src.stem.upper()
        if serial in wanted:
            dst = dest / src.name
            copy_file(src, dst, dry_run)
            result["installed"].append({"serial": serial, "file": dst.name})
            matched.add(serial)
    result["misses"] = sorted(wanted - matched)
    return result


def rpcs3_title_ids(box_home: Path) -> list[str]:
    games_yml = box_home / ".config/rpcs3/games.yml"
    if not games_yml.exists():
        return []
    ids = []
    for line in games_yml.read_text(errors="ignore").splitlines():
        maybe_id = line.strip().split(":", 1)[0]
        if TITLE_ID_RE.fullmatch(maybe_id):
            ids.append(maybe_id)
    return ids


def sync_rpcs3(repo_root: Path | None, box_home: Path, dry_run: bool) -> dict:
    result = {"installed": [], "misses": [], "skipped": None}
    if not repo_root or not repo_root.exists():
        result["skipped"] = "missing Artemis RPCS3 patch repo"
        return result
    title_ids = rpcs3_title_ids(box_home)
    matched = set()
    dest = box_home / ".config/rpcs3/patches"
    ensure_dir(dest, dry_run)
    for title_id in title_ids:
        matches = [p for p in sorted(repo_root.iterdir()) if p.is_file() and title_id in p.name]
        if not matches:
            continue
        chunks = []
        for src in matches:
            text = src.read_text(errors="ignore")
            text = re.sub(r"^Version:\s*1\.2\s*\n+", "", text, count=1, flags=re.M)
            chunks.append(f"\n# ---- Artemis source: {src.name} ----\n{text.rstrip()}\n")
        dst = dest / f"{title_id}_patch.yml"
        if not dry_run:
            dst.write_text("Version: 1.2\n" + "".join(chunks))
        result["installed"].append({"title_id": title_id, "files": [p.name for p in matches], "dest": dst.name})
        matched.add(title_id)
    result["misses"] = sorted(set(title_ids) - matched)
    return result


def optional_path(value: str | None) -> Path | None:
    return Path(value).expanduser() if value else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--box-home", default=os.environ.get("DG_BOX_HOME", "~/distrobox/gaming"))
    parser.add_argument("--n3ds-root", default=os.environ.get("DG_N3DS_ROOT"))
    parser.add_argument("--ctrpf", default=os.environ.get("DG_CTRPF_CHEATS_REPO"))
    parser.add_argument("--pcsx2", default=os.environ.get("DG_PCSX2_CHEATS_REPO"))
    parser.add_argument("--duckstation", default=os.environ.get("DG_DUCKSTATION_CHTDB_REPO"))
    parser.add_argument("--rpcs3-artemis", default=os.environ.get("DG_RPCS3_ARTEMIS_REPO"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    box_home = Path(args.box_home).expanduser()
    report = {
        "dry_run": args.dry_run,
        "box_home": str(box_home),
        "azahar": sync_azahar(optional_path(args.ctrpf), optional_path(args.n3ds_root), box_home, args.dry_run),
        "pcsx2": sync_pcsx2(optional_path(args.pcsx2), box_home, args.dry_run),
        "duckstation": sync_duckstation(optional_path(args.duckstation), box_home, args.dry_run),
        "rpcs3": sync_rpcs3(optional_path(args.rpcs3_artemis), box_home, args.dry_run),
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).expanduser().write_text(rendered)
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
