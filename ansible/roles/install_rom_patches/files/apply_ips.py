#!/usr/bin/env python3
"""Apply an IPS patch to a base ROM (strict, hash-verified).

Usage: apply_ips.py <base_rom> <patch.ips> <output_rom> <base_sha1> <out_sha1>

Verifies the base ROM matches <base_sha1> before patching and the result
matches <out_sha1> after, so a wrong-region base or a corrupt patch fails
loudly instead of writing a broken ROM. Called by the
install_dkc_gba_restoration role; not a standalone CLI.
"""
import hashlib
import sys


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_ips(base, ips, out):
    data = bytearray(open(base, "rb").read())
    p = open(ips, "rb").read()
    if p[:5] != b"PATCH":
        raise SystemExit("not an IPS file (missing PATCH header)")
    i = 5
    records = 0
    while True:
        if p[i:i + 3] == b"EOF":
            break
        off = int.from_bytes(p[i:i + 3], "big"); i += 3
        length = int.from_bytes(p[i:i + 2], "big"); i += 2
        if length == 0:  # RLE record
            run = int.from_bytes(p[i:i + 2], "big"); i += 2
            chunk = p[i:i + 1] * run; i += 1
        else:
            chunk = p[i:i + length]; i += length
        end = off + len(chunk)
        if end > len(data):
            data.extend(b"\x00" * (end - len(data)))
        data[off:end] = chunk
        records += 1
    with open(out, "wb") as fh:
        fh.write(data)
    return records


def main():
    base, ips, out, base_sha1, out_sha1 = sys.argv[1:6]
    got = sha1(base)
    if got != base_sha1:
        raise SystemExit(
            "base ROM sha1 mismatch: got %s, expected %s (wrong region/revision)"
            % (got, base_sha1))
    records = apply_ips(base, ips, out)
    got_out = sha1(out)
    if got_out != out_sha1:
        raise SystemExit(
            "patched ROM sha1 mismatch: got %s, expected %s" % (got_out, out_sha1))
    print("applied %d records; %s verified (%s)" % (records, out, out_sha1))


if __name__ == "__main__":
    main()
