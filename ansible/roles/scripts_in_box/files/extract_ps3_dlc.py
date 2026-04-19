#!/usr/bin/env python3
"""
PS3 PKG Extractor for RPCS3 DLC installation.

Decrypts and extracts PS3 PKG files directly to RPCS3's dev_hdd0/game/ directory,
bypassing RPCS3's GUI-only --installpkg limitation.

Uses the well-known PS3 free-package AES key for decryption.
Only works for unencrypted/free DLC PKGs (type 0x0001). Paid/licensed PKGs
that require RAP files are NOT supported.

Usage:
    python3 extract_ps3_dlc.py /path/to/dlc-folder [--dest /path/to/dev_hdd0/game]
    python3 extract_ps3_dlc.py /path/to/single-file.pkg

    --max-version 01.12   # for game patches, skip any PKG whose filename
                          # version exceeds this limit (useful for games
                          # where the latest patches break emulator compat)
    --dry-run             # don't write anything, print plan only

Default dest: ~/.config/rpcs3/dev_hdd0/game/
"""

import re
import struct
import os
import sys
import glob
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Well-known PS3 AES key for free (non-RAP) PKG files
PS3_PKG_AES_KEY = bytes.fromhex('2E7B71D7C9C9A14EA3221F188828B8F8')

DEFAULT_DEST = os.path.expanduser('~/.config/rpcs3/dev_hdd0/game')

# Game patch PKG filenames encode the version as -A<major><minor>- where
# both halves are zero-padded 2-digit decimal: e.g. -A0122- -> 01.22.
PATCH_VER_RE = re.compile(r'-A(\d{2})(\d{2})-V')

# Per-title upper bound on patch versions to install. Games listed here
# will NOT receive patch PKGs newer than the pinned version, even when
# staging dirs contain them. Use when newer patches introduce
# regressions under RPCS3 that downgrade the play experience.
PER_GAME_MAX_VERSION = {
    # Gran Turismo 6: v1.06+ introduces visual regressions on RPCS3
    # (issue #17453 black reflections, menu glitches, black track/car
    # surfaces). v1.05 is the community-recognized "safe stop".
    "BCES01893": "01.05",
    "BCUS98296": "01.05",  # US release of GT6
    "BCJS37016": "01.05",  # JP
    "BCAS25018": "01.05",  # Asia
    "BCES01977": "01.05",  # EU re-issue
}


def sfo_version(sfo_path: str) -> str | None:
    """Extract the VERSION field from a PS3 PARAM.SFO, if present."""
    try:
        with open(sfo_path, 'rb') as f:
            data = f.read()
    except OSError:
        return None
    if len(data) < 20 or data[:4] != b'\x00PSF':
        return None
    key_table_off = struct.unpack('<I', data[8:12])[0]
    data_table_off = struct.unpack('<I', data[12:16])[0]
    num_entries = struct.unpack('<I', data[16:20])[0]
    for i in range(num_entries):
        idx = 20 + i * 16
        if idx + 16 > len(data):
            break
        key_off = struct.unpack('<H', data[idx:idx + 2])[0]
        data_len = struct.unpack('<I', data[idx + 4:idx + 8])[0]
        data_off = struct.unpack('<I', data[idx + 12:idx + 16])[0]
        kp = key_table_off + key_off
        ke = data.index(b'\x00', kp) if b'\x00' in data[kp:] else len(data)
        key = data[kp:ke].decode('utf-8', errors='replace')
        if key == 'VERSION':
            raw = data[data_table_off + data_off:data_table_off + data_off + data_len]
            return raw.split(b'\x00', 1)[0].decode('utf-8', errors='replace')
    return None


def patch_ver_from_filename(pkg_name: str) -> str | None:
    m = PATCH_VER_RE.search(pkg_name)
    return f'{m.group(1)}.{m.group(2)}' if m else None


def ver_tuple(v: str) -> tuple:
    parts = v.split('.')
    return tuple(int(x) for x in parts) if all(p.isdigit() for p in parts) else (0,)


def increment_iv(iv_bytes: bytes, blocks: int) -> bytes:
    """Increment a 16-byte big-endian IV by a number of AES blocks."""
    iv_int = int.from_bytes(iv_bytes, 'big')
    new_iv = (iv_int + blocks) & ((1 << 128) - 1)
    return new_iv.to_bytes(16, 'big')


def decrypt_at_offset(f, data_offset: int, base_iv: bytes, offset: int, size: int) -> bytes:
    """Decrypt `size` bytes from the PKG data section at a given offset.

    AES-CTR allows random access by computing the correct counter for any block.
    """
    if size == 0:
        return b''

    abs_offset = data_offset + offset
    block_num = offset // 16
    block_offset = offset % 16

    # Position to the start of the block containing our data
    f.seek(abs_offset - block_offset)
    read_size = size + block_offset
    # Align to 16-byte boundary for full blocks
    read_size = ((read_size + 15) // 16) * 16
    encrypted = f.read(read_size)

    iv = increment_iv(base_iv, block_num)
    cipher = Cipher(algorithms.AES(PS3_PKG_AES_KEY), modes.CTR(iv))
    dec = cipher.decryptor()
    decrypted = dec.update(encrypted) + dec.finalize()

    return decrypted[block_offset:block_offset + size]


def extract_pkg(pkg_path: str, dest_base: str, dry_run: bool = False,
                max_version: str | None = None) -> bool:
    """Extract a single PS3 PKG file to dest_base/<content_id>/."""
    pkg_name = os.path.basename(pkg_path)

    with open(pkg_path, 'rb') as f:
        # Validate magic
        magic = f.read(4)
        if magic != b'\x7fPKG':
            print(f'  SKIP {pkg_name}: not a valid PKG (magic={magic.hex()})')
            return False

        f.seek(0x06)
        pkg_type = struct.unpack('>H', f.read(2))[0]

        f.seek(0x14)
        item_count = struct.unpack('>I', f.read(4))[0]

        f.seek(0x18)
        total_size = struct.unpack('>Q', f.read(8))[0]

        f.seek(0x20)
        data_offset = struct.unpack('>Q', f.read(8))[0]
        data_size = struct.unpack('>Q', f.read(8))[0]

        f.seek(0x30)
        content_id = f.read(36).split(b'\x00')[0].decode('ascii')

        f.seek(0x70)
        base_iv = f.read(16)

        # Determine destination.
        #
        # - Game patches (filename -A<ver>-V<ver>-): extract into the base
        #   game's TID dir (e.g. /dev_hdd0/game/BCES01893/). RPCS3 loads
        #   base game + patches from /<TID>/; a patch at /<CONTENT_ID>/
        #   is read as unrelated DLC and never applied. Result is the
        #   game runs at disc version forever.
        # - DLC / standalone: extract into the content_id dir as before.
        #
        # TID extraction from content_id format "EP9001-BCES01893_00-..."
        patch_ver = patch_ver_from_filename(pkg_name)
        tid_match = re.match(r'^[A-Z0-9]{4,}-([A-Z]{4}\d{5})(?:_|$)', content_id)
        if patch_ver and tid_match:
            dest_dir = os.path.join(dest_base, tid_match.group(1))
        else:
            dest_dir = os.path.join(dest_base, content_id)

        # Patch-version idempotency + per-game cap.
        # - --max-version caps every game to a common ceiling.
        # - PER_GAME_MAX_VERSION caps specific titles where newer patches
        #   cause regressions under RPCS3. The stricter of the two applies.
        # - If the destination already has an equal-or-newer PARAM.SFO
        #   VERSION, skip (file-size checks alone don't catch patch diffs
        #   cleanly; different patch versions often share file sizes).
        if patch_ver:
            per_game_cap = tid_match and PER_GAME_MAX_VERSION.get(tid_match.group(1))
            effective_max = None
            if max_version and per_game_cap:
                effective_max = max_version if ver_tuple(max_version) < ver_tuple(per_game_cap) else per_game_cap
            else:
                effective_max = max_version or per_game_cap
            if effective_max and ver_tuple(patch_ver) > ver_tuple(effective_max):
                label = 'per-game cap' if per_game_cap and effective_max == per_game_cap else '--max-version'
                print(f'  SKIP {pkg_name}: version {patch_ver} exceeds {label} {effective_max}')
                return True
            existing_ver = sfo_version(os.path.join(dest_dir, 'PARAM.SFO'))
            if existing_ver and ver_tuple(existing_ver) >= ver_tuple(patch_ver):
                print(f'  SKIP {pkg_name}: existing {os.path.basename(dest_dir)} already at version {existing_ver}')
                return True

        if dry_run:
            print(f'  DRY RUN: {pkg_name} -> {dest_dir} ({item_count} items)')
            return True

        print(f'  Extracting: {pkg_name}')
        print(f'    Content ID: {content_id}')
        print(f'    Items: {item_count}, Size: {total_size:,d} bytes')

        # Decrypt file table + names
        # File table = item_count * 32 bytes
        # Names follow immediately after
        table_size = item_count * 32
        # Read enough for table + all possible name data (estimate ~64 bytes per name)
        metadata_size = table_size + item_count * 64
        metadata_size = min(metadata_size, data_size)  # don't read past data section

        metadata = decrypt_at_offset(f, data_offset, base_iv, 0, metadata_size)

        # Parse entries
        entries = []
        for i in range(item_count):
            off = i * 32
            name_off = struct.unpack('>I', metadata[off:off+4])[0]
            name_sz = struct.unpack('>I', metadata[off+4:off+8])[0]
            file_off = struct.unpack('>Q', metadata[off+8:off+16])[0]
            file_sz = struct.unpack('>Q', metadata[off+16:off+24])[0]
            ctype = struct.unpack('>I', metadata[off+24:off+28])[0]

            # Read name
            if name_off + name_sz <= len(metadata):
                name = metadata[name_off:name_off+name_sz].decode('utf-8', errors='replace').rstrip('\x00')
            else:
                # Name is beyond our metadata buffer — need to decrypt more
                name_data = decrypt_at_offset(f, data_offset, base_iv, name_off, name_sz)
                name = name_data.decode('utf-8', errors='replace').rstrip('\x00')

            is_dir = file_sz == 0 and (ctype & 0xFF) in (0x04, 0x12)
            entries.append((name, file_off, file_sz, is_dir, ctype))

        # Create directories first
        os.makedirs(dest_dir, exist_ok=True)
        for name, _, _, is_dir, _ in entries:
            if is_dir or name.endswith('/'):
                dir_path = os.path.join(dest_dir, name)
                os.makedirs(dir_path, exist_ok=True)

        # Extract files
        extracted = 0
        skipped = 0
        # Patch PKGs must overwrite even when sizes match (different content);
        # for DLC PKGs (no patch_ver) the size check is a safe idempotency hint.
        is_patch = patch_ver is not None
        for name, file_off, file_sz, is_dir, ctype in entries:
            if is_dir or file_sz == 0:
                continue

            file_path = os.path.join(dest_dir, name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Skip if already extracted and same size (DLCs only)
            if not is_patch and os.path.exists(file_path) and os.path.getsize(file_path) == file_sz:
                skipped += 1
                continue

            # Decrypt and write file data in chunks (handles large files)
            chunk_size = 1024 * 1024  # 1 MB chunks
            remaining = file_sz
            offset = file_off

            with open(file_path, 'wb') as out:
                while remaining > 0:
                    read_sz = min(chunk_size, remaining)
                    chunk = decrypt_at_offset(f, data_offset, base_iv, offset, read_sz)
                    out.write(chunk)
                    offset += read_sz
                    remaining -= read_sz

            extracted += 1

        print(f'    Done: {extracted} files extracted, {skipped} skipped (already exist)')
        return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    dest = DEFAULT_DEST
    dry_run = False
    max_version = None

    # Parse optional args
    args = sys.argv[2:]
    while args:
        if args[0] == '--dest' and len(args) > 1:
            dest = args[1]
            args = args[2:]
        elif args[0] == '--max-version' and len(args) > 1:
            max_version = args[1]
            args = args[2:]
        elif args[0] == '--dry-run':
            dry_run = True
            args = args[1:]
        else:
            print(f'Unknown arg: {args[0]}')
            sys.exit(1)

    # Find PKG files
    if os.path.isfile(source) and source.endswith('.pkg'):
        pkg_files = [source]
    elif os.path.isdir(source):
        pkg_files = sorted(glob.glob(os.path.join(source, '**', '*.pkg'), recursive=True))
    else:
        print(f'Error: {source} is not a PKG file or directory')
        sys.exit(1)

    if not pkg_files:
        print(f'No PKG files found in {source}')
        sys.exit(1)

    print(f'Found {len(pkg_files)} PKG files')
    print(f'Destination: {dest}')
    if max_version:
        print(f'Max patch version: {max_version}')
    if dry_run:
        print('DRY RUN MODE — no files will be extracted')
    print()

    os.makedirs(dest, exist_ok=True)

    success = 0
    fail = 0
    for pkg in pkg_files:
        try:
            if extract_pkg(pkg, dest, dry_run, max_version):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f'  ERROR: {os.path.basename(pkg)}: {e}')
            fail += 1

    print()
    print(f'Complete: {success} succeeded, {fail} failed out of {len(pkg_files)} total')


if __name__ == '__main__':
    main()
