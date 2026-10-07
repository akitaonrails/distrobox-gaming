#!/usr/bin/env python3
"""
SYNOPSIS
    Unpack the game data out of your own Super Mario 64 DS cartridge dump.

DESCRIPTION
    Reads a .nds file you supply and writes the game's internal filesystem next
    to this script, in the layout the port expects:

        extracted/dsd/files/<path>     every file, byte for byte as the card has it
        build/assets/files.tsv         file id -> path index, rebuilt from the dump
        build/assets/handles.tsv       game handle -> file id, read out of overlay 0
        build/assets/nitrofs.tsv       where the card's own FNT and FAT live in it
        build/assets/nitrofs_fnt.bin   the card's file name table, copied verbatim
        build/assets/nitrofs_fat.bin   the card's file allocation table, verbatim
        build/assets/romdata.bin       code-side data tables, rebuilt from the dump
        build/assets/romdata.manifest  boot-time checksum contract, copied from the kit

    romdata.recipe.tsv and romdata.manifest contain only offsets, names and hashes;
    all game bytes are rebuilt from the dump supplied by the player.

    This is the portable Python counterpart to the extract_assets.ps1 shipped
    with the official Windows build. It uses only the Python standard library
    and keeps the PowerShell script's recipe semantics for Linux compatibility.

USAGE
    python extract_assets.py
    python extract_assets.py path/to/sm64ds.nds
    python extract_assets.py -Rom path/to/sm64ds.nds -Destination path/to/build
    python extract_assets.py --ensure-current
    python extract_assets.py --apply-updates
"""

import argparse
import collections
import errno
import hashlib
import os
import re
import shutil
import stat
import struct


_doing = "starting up"
_doing_path = ""


def write_step(text):
    print(text)


def write_warn(text):
    print(f"\033[33m{text}\033[0m")


def write_prog(pct, phase):
    pct = max(0, min(100, int(pct)))
    print(f"##PROGRESS {pct} {phase}", flush=True)


def write_reason(text):
    """Emit one safe, bounded failure marker for the launcher."""
    one = re.sub(r"\s+", " ", re.sub(r"[^ -~]", " ", str(text))).strip()
    if len(one) > 400:
        one = one[:397] + "..."
    print(f"##REASON {one}", flush=True)


def set_context(doing, path=""):
    global _doing, _doing_path
    _doing = doing
    _doing_path = path


def test_cloud_placeholder(path):
    """Return whether a Windows file has an online-only attribute."""
    if not path:
        return False
    try:
        attributes = getattr(os.stat(path), "st_file_attributes", 0)
    except OSError:
        return False

    return bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_OFFLINE", 0x1000)
        or attributes & getattr(stat, "FILE_ATTRIBUTE_RECALL_ON_OPEN", 0x40000)
        or attributes & getattr(stat, "FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS", 0x400000)
    )


def _error_code(error):
    for name in ("winerror", "errno"):
        value = getattr(error, name, None)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return 0


def get_plain_reason(error, doing, path):
    """Turn an unexpected filesystem failure into a player-facing sentence."""
    ex = error
    # Keep the useful underlying error when a caller wrapped it with a cause.
    while getattr(ex, "__cause__", None) is not None:
        ex = ex.__cause__

    where = f" while {doing}" if doing else ""
    code = _error_code(ex)

    if isinstance(ex, OSError) and (
        code == getattr(errno, "ENAMETOOLONG", 36) or code == 206
    ):
        return (
            f"A file path was too long{where}. Move the kit closer to the top of the "
            "drive (for example C:\\SM64DS) and press Play again."
        )

    if isinstance(ex, PermissionError) or code == 5:
        return (
            f"Windows refused permission{where}. This usually means the kit is in a "
            "protected folder (Program Files), or security software is blocking it. "
            "Move the kit to a normal folder (your Desktop or Documents), or allow it "
            "in your antivirus, then press Play again."
        )

    if isinstance(ex, MemoryError):
        return f"Ran out of memory{where}. Close other programs and press Play again."

    if isinstance(ex, OSError):
        # ERROR_DISK_FULL (112), ERROR_HANDLE_DISK_FULL (39), and POSIX ENOSPC.
        if code in (112, 39, getattr(errno, "ENOSPC", 28)):
            return (
                f"The disk is full{where}. Free up some space (about 100 MB is plenty) "
                "and press Play again."
            )

        # ERROR_SHARING_VIOLATION (32), ERROR_LOCK_VIOLATION (33).
        if code in (32, 33):
            return (
                f"Another program is holding a file open{where}. Close the game, any "
                "antivirus scan and any open folder window, then press Play again."
            )

        # The cloud filter range (362 to 395) is what OneDrive and similar report.
        if 362 <= code <= 395 or test_cloud_placeholder(path):
            return (
                f"A file is stored online only and Windows could not download it{where}. "
                "This happens with OneDrive (or similar) when a file is not kept on "
                'this PC. Right-click the kit folder and your .nds file, choose "Always '
                'keep on this device", wait for it to finish, then press Play again.'
            )

    message = str(ex) if ex else str(error)
    return f"The unpack step failed{where}. Windows reported: {message}"


def stop_politely(text):
    write_reason(text)
    print("")
    print(f"\033[31m{text}\033[0m")
    print("")
    print("\033[31mThis kit contains no game data of its own, by design. It needs a dump\033[0m")
    print("\033[31mof a Super Mario 64 DS cartridge that you own. See README.txt.\033[0m")
    raise SystemExit(1)


def stop_blocked(text):
    write_reason(text)
    print("")
    print(f"\033[31m{text}\033[0m")
    print("")
    raise SystemExit(1)


def expand_blz(data: bytes) -> bytes:
    if len(data) < 8:
        return data

    footer = struct.unpack_from("<I", data, len(data) - 8)[0]
    extra_size = struct.unpack_from("<I", data, len(data) - 4)[0]
    if extra_size == 0:
        return data

    header_len = footer >> 24
    compressed_len = footer & 0xFFFFFF
    if header_len < 8 or header_len > len(data) or compressed_len > len(data):
        raise ValueError("overlay 0 has an unreadable compression header")
    if compressed_len >= len(data):
        compressed_len = len(data)

    passthrough = len(data) - compressed_len
    comp_len = compressed_len - header_len
    out_len = len(data) + extra_size - passthrough
    out = bytearray(out_len)

    read = 0
    done = 0
    flags = 0
    mask = 1

    while done < out_len:
        if mask == 1:
            if read >= compressed_len:
                raise ValueError("overlay 0 ended mid-stream")
            flags = data[passthrough + comp_len - 1 - read]
            read += 1
            mask = 0x80
        else:
            mask >>= 1

        if flags & mask:
            b1 = data[passthrough + comp_len - 1 - read]
            read += 1
            b2 = data[passthrough + comp_len - 1 - read]
            read += 1
            length = (b1 >> 4) + 3
            disp = (((b1 & 0x0F) << 8) | b2) + 3
            if disp > done:
                if done < 2:
                    raise ValueError("overlay 0 back-references data that is not there yet")
                disp = 2
            from_pos = done - disp
            for _ in range(length):
                out[out_len - 1 - done] = out[out_len - 1 - from_pos]
                from_pos += 1
                done += 1
        else:
            out[out_len - 1 - done] = data[passthrough + comp_len - 1 - read]
            read += 1
            done += 1

    result = bytearray(passthrough + out_len)
    if passthrough > 0:
        result[:passthrough] = data[:passthrough]
    result[passthrough:] = out
    return bytes(result)


def _find_nds_files(directory):
    try:
        with os.scandir(directory) as entries:
            return sorted(
                entry.path
                for entry in entries
                if entry.is_file() and entry.name.lower().endswith(".nds")
            )
    except OSError:
        return []


def _ascii_text(data):
    return data.decode("ascii", errors="replace")


def _printable(text):
    return re.sub(r"[^ -~]", ".", text)


def _drive_root(path):
    full_path = os.path.abspath(path)
    while not os.path.exists(full_path):
        parent = os.path.dirname(full_path)
        if parent == full_path:
            break
        full_path = parent
    return full_path


def load_romdata_contract(destination):
    """Load and cross-check the recipe and manifest shipped by this port version."""
    assets_dir = os.path.join(destination, "build", "assets")
    recipe_candidates = [
        os.path.join(destination, "romdata.recipe.tsv"),
        os.path.join(assets_dir, "romdata.recipe.tsv"),
    ]
    manifest_candidates = [
        os.path.join(destination, "romdata.manifest"),
        os.path.join(assets_dir, "romdata.manifest"),
    ]
    recipe_path = next(
        (candidate for candidate in recipe_candidates if os.path.isfile(candidate)),
        None,
    )
    manifest_path = next(
        (candidate for candidate in manifest_candidates if os.path.isfile(candidate)),
        None,
    )

    if not recipe_path:
        raise ValueError(
            "This kit is incomplete: romdata.recipe.tsv is missing, so the game data "
            "cannot be rebuilt. Download the kit again and unpack the whole zip into "
            "one folder (keep the files together)."
        )
    if not manifest_path:
        raise ValueError(
            "This kit is incomplete: romdata.manifest is missing, so the game would "
            "refuse to start. Download the kit again and unpack the whole zip into "
            "one folder (keep the files together)."
        )

    with open(recipe_path, "r", encoding="utf-8-sig") as recipe_file:
        recipe_lines = recipe_file.read().splitlines()
    with open(manifest_path, "r", encoding="utf-8-sig") as manifest_file:
        manifest_lines = manifest_file.read().splitlines()

    recipe_header = (
        re.fullmatch(r"# romdata-recipe v1 ([0-9a-f]{64}) (\d+)", recipe_lines[0])
        if recipe_lines
        else None
    )
    manifest_header = (
        re.fullmatch(r"# romdata-manifest v1 ([0-9a-f]{64}) (\d+)", manifest_lines[0])
        if manifest_lines
        else None
    )
    if len(recipe_lines) < 2 or recipe_header is None:
        raise ValueError(
            "This kit's romdata.recipe.tsv is damaged, so the game data cannot be "
            "rebuilt. Download the kit again."
        )
    if manifest_header is None:
        raise ValueError(
            "This kit's romdata.manifest is damaged, so the game data cannot be "
            "verified. Download the kit again."
        )

    recipe_identity = (recipe_header.group(1), int(recipe_header.group(2)))
    manifest_identity = (manifest_header.group(1), int(manifest_header.group(2)))
    if recipe_identity != manifest_identity:
        raise ValueError(
            "This kit's romdata.recipe.tsv and romdata.manifest are from different "
            "versions. Download the current kit again and keep its files together."
        )

    want_sha, blob_total = recipe_identity
    rows = []
    for line_number, line in enumerate(recipe_lines[1:], start=2):
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        # The official PowerShell extractor consumes the first four columns and
        # permits later metadata columns. Keep that contract here so the Linux
        # path accepts every recipe the shipped extractor accepts.
        if len(fields) < 4:
            raise ValueError(
                f"This kit's romdata.recipe.tsv is damaged at line {line_number}. "
                "Download the kit again."
            )
        try:
            offset = int(fields[0])
            size = int(fields[1])
            source_offset = int(fields[3])
        except ValueError as ex:
            raise ValueError(
                f"This kit's romdata.recipe.tsv is damaged at line {line_number}. "
                "Download the kit again."
            ) from ex

        source = fields[2]
        if (
            offset < 0
            or size < 0
            or source_offset < 0
            or offset + size > blob_total
            or not source
        ):
            raise ValueError(
                f"This kit's romdata.recipe.tsv is damaged at line {line_number}. "
                "Download the kit again."
            )
        rows.append((offset, size, source, source_offset))

    if not rows:
        raise ValueError(
            "This kit's romdata.recipe.tsv has no data rows, so the game data cannot "
            "be rebuilt. Download the kit again."
        )

    return {
        "sha256": want_sha,
        "size": blob_total,
        "rows": rows,
        "recipe_path": recipe_path,
        "manifest_path": manifest_path,
    }


def romdata_blob_status(path, expected_sha, expected_size):
    """Return missing, stale or current for a generated romdata.bin."""
    if not os.path.isfile(path):
        return "missing"
    if os.path.getsize(path) != expected_size:
        return "stale"

    digest = hashlib.sha256()
    with open(path, "rb") as blob_file:
        for chunk in iter(lambda: blob_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return "current" if digest.hexdigest().lower() == expected_sha else "stale"


def installed_assets_status(destination, contract):
    """Return missing, stale or current for the complete installed asset contract."""
    assets_dir = os.path.join(destination, "build", "assets")
    blob_status = romdata_blob_status(
        os.path.join(assets_dir, "romdata.bin"),
        contract["sha256"],
        contract["size"],
    )
    if blob_status != "current":
        return blob_status

    required = (
        "files.tsv",
        "handles.tsv",
        "nitrofs.tsv",
        "nitrofs_fnt.bin",
        "nitrofs_fat.bin",
        "romdata.manifest",
    )
    if any(not os.path.isfile(os.path.join(assets_dir, name)) for name in required):
        return "missing"

    manifest_target = os.path.join(assets_dir, "romdata.manifest")
    manifest_source = contract["manifest_path"]
    if os.path.abspath(manifest_source) != os.path.abspath(manifest_target):
        if os.path.getsize(manifest_source) != os.path.getsize(manifest_target):
            return "stale"
        with open(manifest_source, "rb") as source_file:
            source_bytes = source_file.read()
        with open(manifest_target, "rb") as target_file:
            if target_file.read() != source_bytes:
                return "stale"

    return "current"


def apply_staged_updates(destination: str) -> bool:
    """Check for staged launcher updates (launcher_new.exe / launcher_update.flag) and apply them cleanly."""
    staged_exe = os.path.join(destination, "launcher_new.exe")
    flag_file = os.path.join(destination, "launcher_update.flag")

    had_staged = False
    if os.path.isfile(staged_exe) or os.path.isfile(flag_file):
        target_name = "SM64DSLauncher.exe"
        if os.path.isfile(flag_file):
            try:
                with open(flag_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        target_name = content
            except Exception:
                pass

        target_path = os.path.join(destination, target_name)

        if os.path.isfile(staged_exe):
            had_staged = True
            write_step(f"Applying staged launcher update: {os.path.basename(staged_exe)} -> {target_name}")
            try:
                old_backup = os.path.join(destination, target_name + ".old")
                if os.path.isfile(target_path):
                    try:
                        if os.path.isfile(old_backup):
                            os.remove(old_backup)
                        shutil.move(target_path, old_backup)
                    except Exception:
                        pass
                shutil.move(staged_exe, target_path)
                if os.name != "nt":
                    try:
                        os.chmod(
                            target_path,
                            os.stat(target_path).st_mode
                            | stat.S_IXUSR
                            | stat.S_IXGRP
                            | stat.S_IXOTH,
                        )
                    except Exception:
                        pass
                write_step(f"    Successfully updated {target_name}")
            except Exception as ex:
                write_warn(f"    Could not swap {staged_exe} -> {target_path}: {ex}")

        if os.path.isfile(flag_file):
            try:
                os.remove(flag_file)
            except Exception:
                pass

    return had_staged


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="Unpack Super Mario 64 DS game data.", add_help=False
    )
    parser.add_argument(
        "-Rom", "-rom", "--rom", "-r", dest="rom", default=None, help="Path to .nds file"
    )
    parser.add_argument(
        "-Destination",
        "-destination",
        "--destination",
        "-d",
        dest="destination",
        default=None,
        help="Destination directory",
    )
    parser.add_argument(
        "--ensure-current",
        dest="ensure_current",
        action="store_true",
        help="Extract only when installed assets are missing or from another version",
    )
    parser.add_argument(
        "-ApplyUpdate",
        "-apply-update",
        "--apply-update",
        "--apply-updates",
        "-u",
        dest="apply_update_only",
        action="store_true",
        help="Apply any staged launcher updates (launcher_new.exe) and exit",
    )

    args, unknown = parser.parse_known_args()

    rom_arg = args.rom
    dest_arg = args.destination

    for arg in unknown:
        if not arg.startswith("-"):
            if rom_arg is None:
                rom_arg = arg
            elif dest_arg is None:
                dest_arg = arg

    destination = os.path.abspath(dest_arg) if dest_arg else script_dir

    # Automatically check and apply any staged launcher update
    had_update = apply_staged_updates(destination)
    if getattr(args, "apply_update_only", False):
        if not had_update:
            write_step("No staged launcher updates found.")
        return

    # ------------------------------------------------------ can we write here at all
    set_context("checking that the kit folder can be written to", destination)
    probe = os.path.join(destination, f".write-probe-{os.getpid()}")
    try:
        os.makedirs(destination, exist_ok=True)
        with open(probe, "wb") as probe_file:
            probe_file.write(b"\x00")
        os.remove(probe)
    except Exception as ex:
        stop_blocked(
            get_plain_reason(
                ex, "checking that the kit folder can be written to", destination
            )
        )

    # The recipe and manifest form the version contract for romdata.bin. Read
    # both before touching extracted files, so a partial update cannot spend a
    # minute unpacking the ROM only to leave an asset blob the game will reject.
    set_context("reading this version's game-data contract", destination)
    try:
        romdata_contract = load_romdata_contract(destination)
    except ValueError as ex:
        stop_blocked(str(ex))
    except Exception as ex:
        stop_blocked(
            get_plain_reason(ex, "reading this version's game-data contract", destination)
        )

    current_blob_path = os.path.join(destination, "build", "assets", "romdata.bin")
    set_context("checking the installed game-data version", current_blob_path)
    try:
        asset_status = installed_assets_status(destination, romdata_contract)
    except Exception as ex:
        stop_blocked(
            get_plain_reason(ex, "checking the installed game-data version", current_blob_path)
        )
    if args.ensure_current and asset_status == "current":
        write_step("Game assets already match this port version.")
        return
    if asset_status == "stale":
        write_step("The installed game data is from a different port version; rebuilding it.")
    elif asset_status == "missing" and args.ensure_current:
        write_step("Required game assets are missing; extracting them.")

    # ---------------------------------------------------------------- find the rom
    if not rom_arg:
        # Prefer the current bundle name, but retain the older layout.
        drop_names = ["PLACE YOUR ROM HERE", "PLACE EU ROM HERE"]
        drop_dir = None
        found = []

        for name in drop_names:
            candidate = os.path.join(destination, name)
            if os.path.isdir(candidate):
                if not drop_dir:
                    drop_dir = candidate
                hits = _find_nds_files(candidate)
                if hits:
                    found = hits
                    break

        if not drop_dir:
            drop_dir = os.path.join(destination, drop_names[0])

        if not found:
            found = _find_nds_files(destination)

        if not found:
            stop_politely(f"No .nds file found in '{drop_dir}' or next to this script.")

        if len(found) > 1:
            print("")
            print("\033[31mMore than one .nds file is sitting here:\033[0m")
            for found_path in found:
                print(f"    {os.path.basename(found_path)}")
            stop_politely(
                "Leave only the Super Mario 64 DS one, or name it: "
                "python extract_assets.py -Rom <file>"
            )

        rom_arg = found[0]

    if not os.path.isfile(rom_arg):
        stop_politely(
            f"The .nds file is not there any more: {rom_arg}. Put your Super Mario 64 DS "
            "dump back in the folder next to the launcher and press Play again."
        )

    rom_path = os.path.realpath(rom_arg)
    write_step(f"Reading {os.path.basename(rom_path)}")
    set_context("reading your .nds file", rom_path)
    try:
        with open(rom_path, "rb") as rom_file:
            rom_bytes = rom_file.read()
    except Exception as ex:
        stop_politely(get_plain_reason(ex, "reading your .nds file", rom_path))

    # ------------------------------------------------------- check it is the game
    if len(rom_bytes) < 0x4000:
        stop_politely(
            f"That file is only {len(rom_bytes)} bytes, too small to be a DS cartridge dump."
        )

    title = _ascii_text(rom_bytes[0x00:0x0C]).rstrip("\x00")
    code = _ascii_text(rom_bytes[0x0C:0x10])
    if title != "S.MARIO64DS" or re.fullmatch(r"ASM.", code) is None:
        stop_politely(
            f"That is not a Super Mario 64 DS dump (it says title '{_printable(title)}', "
            f"game code '{_printable(code)}'). Use a dump of a Super Mario 64 DS cartridge."
        )

    regions = {
        "E": "North America",
        "P": "Europe",
        "J": "Japan",
        "K": "Korea",
        "C": "China",
        "U": "Australia",
    }
    region_letter = code[3]
    region = regions.get(region_letter, f"region '{region_letter}'")

    if code != "ASMP":
        stop_politely(
            f"This is the {region} ROM (game code {code}). This port is built from the "
            f"European ROM (ASMP), so its data will not come out of a {region} cartridge."
        )

    fnt_offset = struct.unpack_from("<I", rom_bytes, 0x40)[0]
    fnt_size = struct.unpack_from("<I", rom_bytes, 0x44)[0]
    fat_offset = struct.unpack_from("<I", rom_bytes, 0x48)[0]
    fat_size = struct.unpack_from("<I", rom_bytes, 0x4C)[0]
    ovt_offset = struct.unpack_from("<I", rom_bytes, 0x50)[0]
    ovt_size = struct.unpack_from("<I", rom_bytes, 0x54)[0]
    used_size = struct.unpack_from("<I", rom_bytes, 0x80)[0]

    for name, offset, size in (
        ("file name table", fnt_offset, fnt_size),
        ("file allocation table", fat_offset, fat_size),
        ("overlay table", ovt_offset, ovt_size),
    ):
        if offset == 0 or offset + size > len(rom_bytes):
            stop_politely(
                f"This dump is truncated: its {name} runs past the end of the file. "
                "Re-dump the cartridge."
            )

    if used_size > len(rom_bytes):
        stop_politely(
            f"This dump is incomplete: the header says the cartridge holds {used_size} bytes "
            f"but the file is only {len(rom_bytes)}. Re-dump the cartridge."
        )

    write_step(
        f"Super Mario 64 DS ({code}, {region}), {round(len(rom_bytes) / (1024 * 1024))} MB"
    )
    write_prog(2, "Reading the file tables")

    # ------------------------------------------------------------- the file tables
    fat_count = fat_size // 8
    fat_start = []
    fat_end = []
    for i in range(fat_count):
        fat_start.append(struct.unpack_from("<I", rom_bytes, fat_offset + i * 8)[0])
        fat_end.append(struct.unpack_from("<I", rom_bytes, fat_offset + i * 8 + 4)[0])

    paths = {}
    queue = collections.deque([(0, "")])
    visited = {0}
    while queue:
        dir_id, base = queue.popleft()
        entry = fnt_offset + dir_id * 8
        if entry + 8 > len(rom_bytes):
            stop_politely("This dump's file name table is damaged. Re-dump the cartridge.")

        o = fnt_offset + struct.unpack_from("<I", rom_bytes, entry)[0]
        file_id = struct.unpack_from("<H", rom_bytes, entry + 4)[0]

        while True:
            if o >= len(rom_bytes):
                stop_politely("This dump's file name table is damaged. Re-dump the cartridge.")
            entry_type = rom_bytes[o]
            o += 1
            if entry_type == 0:
                break

            name_len = entry_type & 0x7F
            needs = name_len + (2 if entry_type & 0x80 else 0)
            if o + needs > len(rom_bytes):
                stop_politely("This dump's file name table is damaged. Re-dump the cartridge.")

            name = _ascii_text(rom_bytes[o:o + name_len])
            o += name_len
            if entry_type & 0x80:
                sub = struct.unpack_from("<H", rom_bytes, o)[0] & 0x0FFF
                o += 2
                if sub not in visited:
                    visited.add(sub)
                    sub_path = f"{base}/{name}" if base else name
                    queue.append((sub, sub_path))
            else:
                paths[file_id] = f"{base}/{name}" if base else name
                file_id += 1

    if not paths:
        stop_politely("This dump has no named files in it. Re-dump the cartridge.")

    # ------------------------------------------------------ validate before writing
    set_context("checking the dump's file table", rom_path)
    need_bytes = 0
    for fid in sorted(paths):
        relative = paths[fid]
        if fid < 0 or fid >= fat_count:
            stop_politely(
                f"This dump is damaged: its file name table names a file ({relative}) "
                "that its file allocation table does not have. Re-dump the cartridge."
            )

        length = fat_end[fid] - fat_start[fid]
        if length < 0 or fat_start[fid] + length > len(rom_bytes):
            stop_politely(
                f"This dump is damaged: its file table points at data past the end of the "
                f"file (file {fid}, '{relative}'). Re-dump the cartridge."
            )
        need_bytes += length

    # Free-space checks are best effort on network and substituted drives.
    set_context("checking free disk space", destination)
    try:
        root = _drive_root(destination)
        free = shutil.disk_usage(root).free
        want_bytes = need_bytes + 16 * 1024 * 1024
        if free < want_bytes:
            stop_blocked(
                f"There is not enough free space on {root} to unpack the game data. "
                f"About {round(want_bytes / (1024 * 1024))} MB is needed and "
                f"{round(free / (1024 * 1024))} MB is free. Free up some space and "
                "press Play again."
            )
    except (OSError, ValueError):
        write_warn("    (could not measure free disk space here; carrying on)")

    # --------------------------------------------------------------- write them out
    files_root = os.path.join(destination, "extracted", "dsd", "files")
    write_step(f"Writing {len(paths)} files to {files_root}")
    set_context("writing the unpacked files", "")
    made_dirs = set()
    written = 0
    total_bytes = 0
    total_files = len(paths)

    for fid in sorted(paths):
        relative = paths[fid]
        target = os.path.join(files_root, *relative.split("/"))
        set_context("writing the unpacked files", target)
        directory = os.path.dirname(target)
        if directory not in made_dirs:
            os.makedirs(directory, exist_ok=True)
            made_dirs.add(directory)

        length = fat_end[fid] - fat_start[fid]
        data = rom_bytes[fat_start[fid]:fat_start[fid] + length]
        with open(target, "wb") as output_file:
            output_file.write(data)

        written += 1
        total_bytes += length
        if written % 500 == 0:
            write_step(f"    {written} of {total_files}")
            write_prog(
                2 + int(68 * written / total_files),
                f"Unpacking file {written} of {total_files}",
            )

    write_step(f"    {written} files, {round(total_bytes / (1024 * 1024), 1)} MB")
    write_prog(70, f"Unpacked {written} files")

    # ------------------------------------------------------------ overlay 0 for the
    # handle table. Overlays are stored back-to-front LZ compressed (BLZ).
    if ovt_size < 32:
        stop_politely("This dump has no ARM9 overlays. Re-dump the cartridge.")

    ov0_ram = struct.unpack_from("<I", rom_bytes, ovt_offset + 4)[0]
    ov0_file_id = struct.unpack_from("<I", rom_bytes, ovt_offset + 24)[0]
    ov0_flags = struct.unpack_from("<I", rom_bytes, ovt_offset + 28)[0] >> 24
    set_context("reading overlay 0 out of the dump", rom_path)
    if ov0_file_id < 0 or ov0_file_id >= fat_count:
        stop_politely(
            "This dump is damaged: its overlay table points at a file its file "
            "allocation table does not have. Re-dump the cartridge."
        )

    ov0_length = fat_end[ov0_file_id] - fat_start[ov0_file_id]
    if ov0_length < 0 or fat_start[ov0_file_id] + ov0_length > len(rom_bytes):
        stop_politely("This dump is damaged: overlay 0 runs past the end of the file. Re-dump the cartridge.")
    ov0 = rom_bytes[fat_start[ov0_file_id]:fat_start[ov0_file_id] + ov0_length]

    write_prog(71, "Decompressing overlay 0")
    if ov0_flags & 1:
        try:
            ov0 = expand_blz(ov0)
        except Exception as ex:
            stop_politely(f"Could not read overlay 0 of this dump ({ex}). Re-dump the cartridge.")

    handle_table_address = 0x020BD4B8
    handle_count = 0x80A
    table_offset = handle_table_address - ov0_ram
    if table_offset < 0 or table_offset + handle_count * 4 > len(ov0):
        stop_politely(
            "This dump is Super Mario 64 DS but not a revision this build knows: "
            "its overlay 0 has no asset-handle table where one is expected."
        )

    id_by_path = {value: key for key, value in paths.items()}
    kinds = {
        ".bca": "animation",
        ".bmd": "model",
        ".btp": "texture-sequence",
        ".kcl": "collision",
        ".narc": "archive",
        ".sdat": "sound-archive",
        ".bin": "data",
    }

    def get_kind(path):
        suffix = os.path.splitext(path)[1].lower()
        return kinds.get(suffix, "file")

    write_step("Reading the asset-handle table out of overlay 0")
    write_prog(72, "Reading the asset-handle table")
    handle_rows = ["handle\thex_handle\tfile_id\thex_file_id\tpath\tkind\tsize\n"]
    for handle in range(handle_count):
        if handle % 400 == 0 and handle > 0:
            write_prog(
                72 + int(8 * handle / handle_count),
                f"Cataloguing asset handle {handle} of {handle_count}",
            )

        pointer = struct.unpack_from("<I", ov0, table_offset + handle * 4)[0]
        string_offset = pointer - ov0_ram
        if string_offset < 0 or string_offset >= len(ov0):
            stop_politely(
                "This dump is Super Mario 64 DS but not a revision this build knows: "
                f"asset handle {handle} points outside overlay 0."
            )

        end = string_offset
        while end < len(ov0) and ov0[end] != 0:
            end += 1
        asset_path = _ascii_text(ov0[string_offset:end])
        if asset_path not in id_by_path:
            stop_politely(
                "This dump is Super Mario 64 DS but not a revision this build knows: "
                f"asset handle {handle} names '{asset_path}', which its filesystem does not have."
            )

        fid = id_by_path[asset_path]
        size = fat_end[fid] - fat_start[fid]
        handle_rows.append(
            f"{handle}\t0x{handle:04x}\t{fid}\t0x{fid:04x}\t{asset_path}\t"
            f"{get_kind(asset_path)}\t{size}\n"
        )

    file_rows = ["file_id\thex_id\tpath\tkind\tsize\n"]
    for fid in sorted(paths):
        path = paths[fid]
        size = fat_end[fid] - fat_start[fid]
        file_rows.append(f"{fid}\t0x{fid:04x}\t{path}\t{get_kind(path)}\t{size}\n")

    assets_dir = os.path.join(destination, "build", "assets")
    set_context("writing the asset catalogue", assets_dir)
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "files.tsv"), "w", encoding="utf-8", newline="") as output_file:
        output_file.write("".join(file_rows))
    with open(os.path.join(assets_dir, "handles.tsv"), "w", encoding="utf-8", newline="") as output_file:
        output_file.write("".join(handle_rows))

    write_step(f"    {len(paths)} files and {handle_count} handles catalogued")

    # ------------------------------------------------------------ the NitroFS tables
    set_context("writing the NitroFS name and allocation tables", assets_dir)
    for name, offset, size in (
        ("file name table", fnt_offset, fnt_size),
        ("file allocation table", fat_offset, fat_size),
    ):
        if size == 0:
            stop_politely(
                f"This dump has an empty {name}, so the game could not look up "
                "any of its files. Re-dump the cartridge."
            )

    fnt_bytes = rom_bytes[fnt_offset:fnt_offset + fnt_size]
    with open(os.path.join(assets_dir, "nitrofs_fnt.bin"), "wb") as output_file:
        output_file.write(fnt_bytes)

    fat_bytes = rom_bytes[fat_offset:fat_offset + fat_size]
    with open(os.path.join(assets_dir, "nitrofs_fat.bin"), "wb") as output_file:
        output_file.write(fat_bytes)

    nitro_rows = [
        "key\tvalue\n",
        f"fnt_offset\t{fnt_offset}\n",
        f"fnt_size\t{fnt_size}\n",
        f"fat_offset\t{fat_offset}\n",
        f"fat_size\t{fat_size}\n",
    ]
    with open(os.path.join(assets_dir, "nitrofs.tsv"), "w", encoding="utf-8", newline="") as output_file:
        output_file.write("".join(nitro_rows))

    write_step(f"    name table {fnt_size} bytes, allocation table {fat_size} bytes")
    write_prog(80, "Rebuilding romdata.bin")

    # ------------------------------------------------------------ romdata.bin
    want_sha = romdata_contract["sha256"]
    blob_total = romdata_contract["size"]
    recipe_rows = romdata_contract["rows"]
    needed = {row[2] for row in recipe_rows}

    ov_by_name = {}
    for i in range(ovt_size // 32):
        entry = ovt_offset + i * 32
        ov_id = struct.unpack_from("<I", rom_bytes, entry)[0]
        ov_file_id = struct.unpack_from("<I", rom_bytes, entry + 24)[0]
        ov_flags = struct.unpack_from("<I", rom_bytes, entry + 28)[0] >> 24
        ov_by_name[f"ov{ov_id:03d}"] = (ov_file_id, ov_flags)

    write_step(
        f"Rebuilding romdata.bin ({len(needed)} images to decompress, the slow part, please wait)"
    )
    set_context("rebuilding the game data from the dump", rom_path)
    images = {}
    img_done = 0
    img_total = len(needed)
    for source in needed:
        progress = 80 + int(17 * img_done / img_total) if img_total else 80
        write_prog(progress, f"Decompressing {source} ({img_done + 1} of {img_total})")
        if source == "arm9":
            a9_offset = struct.unpack_from("<I", rom_bytes, 0x20)[0]
            a9_size = struct.unpack_from("<I", rom_bytes, 0x2C)[0]
            if a9_offset + a9_size > len(rom_bytes):
                stop_politely(
                    "Could not read this dump's program data (it runs past the end of "
                    "the file). Re-dump the cartridge."
                )
            a9 = rom_bytes[a9_offset:a9_offset + a9_size]
            try:
                images[source] = expand_blz(a9)
            except Exception as ex:
                stop_politely(f"Could not read this dump's program data ({ex}). Re-dump the cartridge.")
        else:
            if source not in ov_by_name:
                stop_politely(
                    "This dump is Super Mario 64 DS but not a revision this build knows: "
                    f"it has no overlay '{source}'."
                )

            file_id, flags = ov_by_name[source]
            if file_id < 0 or file_id >= fat_count:
                stop_politely(
                    "This dump is damaged: its overlay table points at a file its file "
                    f"allocation table does not have (overlay '{source}'). Re-dump the cartridge."
                )
            length = fat_end[file_id] - fat_start[file_id]
            if length < 0 or fat_start[file_id] + length > len(rom_bytes):
                stop_politely(
                    f"This dump is damaged: overlay '{source}' runs past the end of the file. "
                    "Re-dump the cartridge."
                )

            raw = rom_bytes[fat_start[file_id]:fat_start[file_id] + length]
            if flags & 1:
                try:
                    raw = expand_blz(raw)
                except Exception as ex:
                    stop_politely(
                        f"Could not read overlay '{source}' of this dump ({ex}). Re-dump the cartridge."
                    )
            images[source] = raw

        write_step(f"    {source} ({round(len(images[source]) / 1024)} KB)")
        img_done += 1

    write_prog(98, "Assembling and checking romdata.bin")
    set_context("assembling romdata.bin", "")
    blob = bytearray(blob_total)
    for offset, size, source, source_offset in recipe_rows:
        image = images[source]
        have = min(size, max(0, len(image) - source_offset))
        if have > 0:
            blob[offset:offset + have] = image[source_offset:source_offset + have]

    sha = hashlib.sha256(blob).hexdigest().lower()
    if sha != want_sha:
        stop_politely(
            f"This is a European dump (game code {code}), but its contents do not "
            "match the cartridge this build was made from. That usually means the "
            "file has been modified (a patch, a translation or a trimmed dump) or "
            "the dump is faulty. Use an untouched dump of your own retail "
            "cartridge, then press Play again."
        )

    romdata_target = os.path.join(assets_dir, "romdata.bin")
    set_context("writing the rebuilt game data", romdata_target)
    with open(romdata_target, "wb") as output_file:
        output_file.write(blob)
    if romdata_blob_status(romdata_target, want_sha, blob_total) != "current":
        stop_blocked(
            "The rebuilt game data did not verify after it was written. Check the disk "
            "for errors and press Play again."
        )
    write_step(f"    romdata.bin verified ({blob_total} bytes, checksum OK)")

    # The game verifies this sidecar at boot, so a missing copy is fatal.
    set_context("copying romdata.manifest into place", "")
    manifest_src = romdata_contract["manifest_path"]
    set_context("copying romdata.manifest into place", manifest_src)
    manifest_target = os.path.join(assets_dir, "romdata.manifest")
    if os.path.abspath(manifest_src) != os.path.abspath(manifest_target):
        shutil.copyfile(manifest_src, manifest_target)

    write_prog(100, "Done")
    print("")
    print(f"\033[32mDone. The game data is ready in {destination}\033[0m")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as ex:
        reason = get_plain_reason(ex, _doing, _doing_path)
        write_reason(reason)
        print("")
        print(f"\033[31m{reason}\033[0m")
        print("")
        print(f"Technical detail: {ex}")
        raise SystemExit(1)
