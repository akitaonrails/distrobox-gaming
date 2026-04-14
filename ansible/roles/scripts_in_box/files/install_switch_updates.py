#!/usr/bin/env python3
"""
Switch NSP Update/DLC Installer for Eden (yuzu fork).

Extracts NCA files from NSP (PFS0 container) files and places them in Eden's
NAND user content directory. This bypasses Eden's GUI-only "Install Files to NAND".

NSP/PFS0 format is unencrypted at the container level. NCAs inside are
encrypted but Eden handles decryption at runtime using prod.keys.

Usage:
    python3 install_switch_updates.py /path/to/updates-folder [--dest /path/to/eden/nand]
    python3 install_switch_updates.py /path/to/single-file.nsp

Default dest: ~/.local/share/eden/nand/user/Contents/registered/
"""

import struct
import os
import sys
import glob
from pathlib import Path


DEFAULT_NAND_REGISTERED = os.path.expanduser(
    '~/.local/share/eden/nand/user/Contents/registered'
)


def parse_pfs0(f, base_offset=0):
    """Parse a PFS0 (NSP) container and return list of (name, offset, size)."""
    f.seek(base_offset)
    magic = f.read(4)
    if magic != b'PFS0':
        return None

    num_files = struct.unpack('<I', f.read(4))[0]
    str_table_size = struct.unpack('<I', f.read(4))[0]
    _padding = f.read(4)

    # Read file entries (each 24 bytes)
    entries = []
    for _ in range(num_files):
        data_offset = struct.unpack('<Q', f.read(8))[0]
        data_size = struct.unpack('<Q', f.read(8))[0]
        str_offset = struct.unpack('<I', f.read(4))[0]
        _pad = f.read(4)
        entries.append((data_offset, data_size, str_offset))

    # Read string table
    str_table = f.read(str_table_size)

    # Calculate data start (after header + entries + string table)
    header_size = 16 + (num_files * 24) + str_table_size
    data_start = base_offset + header_size

    files = []
    for data_offset, data_size, str_offset in entries:
        # Extract null-terminated filename from string table
        end = str_table.index(b'\x00', str_offset) if b'\x00' in str_table[str_offset:] else len(str_table)
        name = str_table[str_offset:end].decode('utf-8', errors='replace')
        abs_offset = data_start + data_offset
        files.append((name, abs_offset, data_size))

    return files


def extract_nsp(nsp_path: str, dest_dir: str, dry_run: bool = False) -> dict:
    """Extract NCA/ticket files from an NSP to dest_dir.

    Returns dict with counts: {'nca': N, 'tik': N, 'skipped': N, 'existing': N}
    """
    result = {'nca': 0, 'tik': 0, 'skipped': 0, 'existing': 0}
    nsp_name = os.path.basename(nsp_path)

    with open(nsp_path, 'rb') as f:
        files = parse_pfs0(f)
        if files is None:
            print(f'    SKIP: not a valid PFS0/NSP: {nsp_name}')
            result['skipped'] = 1
            return result

        for name, offset, size in files:
            ext = name.lower().rsplit('.', 1)[-1] if '.' in name else ''

            if ext in ('nca',):
                # NCA or CNMT NCA — place in registered/
                dest_path = os.path.join(dest_dir, name)

                if os.path.exists(dest_path) and os.path.getsize(dest_path) == size:
                    result['existing'] += 1
                    continue

                if dry_run:
                    result['nca'] += 1
                    continue

                f.seek(offset)
                with open(dest_path, 'wb') as out:
                    remaining = size
                    while remaining > 0:
                        chunk = min(1024 * 1024, remaining)
                        data = f.read(chunk)
                        if not data:
                            break
                        out.write(data)
                        remaining -= len(data)

                result['nca'] += 1

            elif ext == 'tik':
                # Ticket file — also place in registered/ for Eden to find
                dest_path = os.path.join(dest_dir, name)
                if os.path.exists(dest_path):
                    result['existing'] += 1
                    continue
                if not dry_run:
                    f.seek(offset)
                    with open(dest_path, 'wb') as out:
                        out.write(f.read(size))
                result['tik'] += 1

            else:
                # cert, xml, jpg, etc — skip
                result['skipped'] += 1

    return result


def find_nsps(source: str) -> list:
    """Recursively find all .nsp files under source."""
    if os.path.isfile(source) and source.lower().endswith('.nsp'):
        return [source]
    elif os.path.isdir(source):
        return sorted(glob.glob(os.path.join(source, '**', '*.nsp'), recursive=True))
    return []


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    dest = DEFAULT_NAND_REGISTERED
    dry_run = False

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

    nsps = find_nsps(source)
    if not nsps:
        print(f'No NSP files found in {source}')
        sys.exit(1)

    print(f'Found {len(nsps)} NSP files')
    print(f'Destination: {dest}')
    if dry_run:
        print('DRY RUN — no files will be extracted')
    print()

    os.makedirs(dest, exist_ok=True)

    totals = {'nca': 0, 'tik': 0, 'skipped': 0, 'existing': 0, 'errors': 0}

    for i, nsp in enumerate(nsps):
        rel = os.path.relpath(nsp, source) if os.path.isdir(source) else os.path.basename(nsp)
        print(f'[{i+1}/{len(nsps)}] {rel}')
        try:
            r = extract_nsp(nsp, dest, dry_run)
            for k in ('nca', 'tik', 'skipped', 'existing'):
                totals[k] += r[k]
            status_parts = []
            if r['nca']: status_parts.append(f"{r['nca']} NCAs")
            if r['tik']: status_parts.append(f"{r['tik']} tickets")
            if r['existing']: status_parts.append(f"{r['existing']} already exist")
            if r['skipped']: status_parts.append(f"{r['skipped']} skipped")
            if status_parts:
                print(f'    {", ".join(status_parts)}')
        except Exception as e:
            print(f'    ERROR: {e}')
            totals['errors'] += 1

    print()
    print(f'Complete: {totals["nca"]} NCAs + {totals["tik"]} tickets extracted, '
          f'{totals["existing"]} already existed, {totals["skipped"]} non-NCA files skipped, '
          f'{totals["errors"]} errors')


if __name__ == '__main__':
    main()
