#!/usr/bin/env python3
"""Apply a BPS patch to a base ROM, verifying hashes before and after.

Mirrors apply_ips.py's contract but for the BPS format (Floating IPS / beat):
  apply_bps.py <base_rom> <patch.bps> <output_rom> <base_sha1> <out_sha1>

BPS carries its own CRC32 of the source, target and patch; we assert all three,
and additionally assert the caller-supplied SHA-1 of the base (before) and the
output (after) so a wrong-region/revision base fails loudly instead of yielding
a broken ROM. Self-contained: standard library only.
"""
import sys
import hashlib
import zlib


def read_number(buf, pos):
    """Decode a BPS variable-length number. Returns (value, new_pos)."""
    data = 0
    shift = 1
    while True:
        x = buf[pos]
        pos += 1
        data += (x & 0x7F) * shift
        if x & 0x80:
            break
        shift <<= 7
        data += shift
    return data, pos


def apply_bps(base, patch):
    if patch[:4] != b"BPS1":
        sys.exit("ERROR: not a BPS1 patch (bad magic).")

    # The last 12 bytes are three little-endian CRC32s: source, target, patch.
    src_crc = int.from_bytes(patch[-12:-8], "little")
    tgt_crc = int.from_bytes(patch[-8:-4], "little")
    patch_crc = int.from_bytes(patch[-4:], "little")

    if zlib.crc32(patch[:-4]) != patch_crc:
        sys.exit("ERROR: BPS patch is corrupt (patch CRC32 mismatch).")
    if zlib.crc32(base) != src_crc:
        sys.exit(
            "ERROR: base ROM CRC32 does not match the patch's expected source. "
            "Wrong ROM/region/revision."
        )

    pos = 4
    source_size, pos = read_number(patch, pos)
    target_size, pos = read_number(patch, pos)
    metadata_size, pos = read_number(patch, pos)
    pos += metadata_size

    if source_size != len(base):
        sys.exit(
            f"ERROR: base ROM is {len(base)} bytes; patch expects {source_size}."
        )

    out = bytearray(target_size)
    out_pos = 0
    src_rel = 0
    tgt_rel = 0
    end = len(patch) - 12

    while pos < end:
        cmd, pos = read_number(patch, pos)
        action = cmd & 3
        length = (cmd >> 2) + 1

        if action == 0:  # SourceRead
            out[out_pos:out_pos + length] = base[out_pos:out_pos + length]
            out_pos += length
        elif action == 1:  # TargetRead
            out[out_pos:out_pos + length] = patch[pos:pos + length]
            pos += length
            out_pos += length
        elif action == 2:  # SourceCopy
            data, pos = read_number(patch, pos)
            src_rel += (-1 if data & 1 else 1) * (data >> 1)
            out[out_pos:out_pos + length] = base[src_rel:src_rel + length]
            src_rel += length
            out_pos += length
        else:  # TargetCopy
            data, pos = read_number(patch, pos)
            tgt_rel += (-1 if data & 1 else 1) * (data >> 1)
            # Byte-by-byte: ranges may overlap (RLE-style back-references).
            for _ in range(length):
                out[out_pos] = out[tgt_rel]
                out_pos += 1
                tgt_rel += 1

    if zlib.crc32(out) != tgt_crc:
        sys.exit("ERROR: patched output CRC32 does not match the patch's target.")
    return bytes(out)


def main():
    if len(sys.argv) != 6:
        sys.exit(
            "usage: apply_bps.py <base_rom> <patch.bps> <output_rom> "
            "<base_sha1> <out_sha1>"
        )
    base_path, patch_path, out_path, base_sha1, out_sha1 = sys.argv[1:]

    with open(base_path, "rb") as f:
        base = f.read()
    got = hashlib.sha1(base).hexdigest()
    if got != base_sha1:
        sys.exit(f"ERROR: base SHA-1 {got} != expected {base_sha1}. Wrong ROM.")

    with open(patch_path, "rb") as f:
        patch = f.read()

    out = apply_bps(base, patch)

    got_out = hashlib.sha1(out).hexdigest()
    if got_out != out_sha1:
        sys.exit(
            f"ERROR: output SHA-1 {got_out} != expected {out_sha1}. "
            "Refusing to write a ROM that does not match the pin."
        )

    with open(out_path, "wb") as f:
        f.write(out)
    print(f"OK: wrote {out_path} ({len(out)} bytes, sha1 {got_out})")


if __name__ == "__main__":
    main()
