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

Default dest: ~/.config/rpcs3/dev_hdd0/game/
"""

import struct
import os
import sys
import glob
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Well-known PS3 AES key for free (non-RAP) PKG files
PS3_PKG_AES_KEY = bytes.fromhex('2E7B71D7C9C9A14EA3221F188828B8F8')

DEFAULT_DEST = os.path.expanduser('~/.config/rpcs3/dev_hdd0/game')


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


def extract_pkg(pkg_path: str, dest_base: str, dry_run: bool = False) -> bool:
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

        dest_dir = os.path.join(dest_base, content_id)

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
        for name, file_off, file_sz, is_dir, ctype in entries:
            if is_dir or file_sz == 0:
                continue

            file_path = os.path.join(dest_dir, name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Skip if already extracted and same size
            if os.path.exists(file_path) and os.path.getsize(file_path) == file_sz:
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

    # Parse optional args
    args = sys.argv[2:]
    while args:
        if args[0] == '--dest' and len(args) > 1:
            dest = args[1]
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
    if dry_run:
        print('DRY RUN MODE — no files will be extracted')
    print()

    os.makedirs(dest, exist_ok=True)

    success = 0
    fail = 0
    for pkg in pkg_files:
        try:
            if extract_pkg(pkg, dest, dry_run):
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
