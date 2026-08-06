#!/usr/bin/env python3
"""Toggle the LargeAddressAware (4GB) flag on a 32-bit PE executable.

Idempotent: prints ``changed: false`` when the flag is already set, otherwise
sets IMAGE_FILE_LARGE_ADDRESS_AWARE (0x20) in the COFF header Characteristics
field, backs the original up once, and prints ``changed: true``.

Used by the RE4 HD Project role (roles/install_re4_hd) to 4GB-patch the
genuine ``bio4.exe`` in place — the mod needs >2 GB of address space for the
HD assets — instead of swapping in a scene repack's pre-patched exe. This is
the same one-bit edit NTCore's "4GB Patch" performs; the PE checksum is left
alone (Windows/Proton ignore it for user-mode images).
"""

from __future__ import annotations

import argparse
import shutil
import struct
from pathlib import Path

LARGE_ADDRESS_AWARE = 0x20


def patch(path: Path, backup_suffix: str) -> bool:
    data = bytearray(path.read_bytes())
    if data[:2] != b"MZ":
        raise SystemExit(f"{path}: not a PE/MZ executable")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise SystemExit(f"{path}: no PE signature at offset {pe}")
    chars_off = pe + 0x16
    chars = struct.unpack_from("<H", data, chars_off)[0]
    if chars & LARGE_ADDRESS_AWARE:
        return False
    struct.pack_into("<H", data, chars_off, chars | LARGE_ADDRESS_AWARE)
    backup = path.with_name(path.name + backup_suffix)
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_bytes(data)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("--backup-suffix", default=".pre-laa-backup")
    args = parser.parse_args()
    changed = patch(args.exe.expanduser(), args.backup_suffix)
    print(f"changed: {str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
