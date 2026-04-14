#!/usr/bin/env python3
"""
Check installed PS3 games against the PSN update server and (optionally)
download missing patch PKGs into the local DLC staging directory.

The downloaded PKGs are type 0x0001 (unencrypted PSN packages) so the
existing extract_ps3_dlc.py extractor will install them on the next run
of the install_dlcs Ansible role.

Usage:
    python3 check_ps3_updates.py /path/to/ps3-roms \\
        [--dlc-dir /path/to/ps3-DLC] \\
        [--list]      # only print the report, don't download
        [--download]  # download missing patches into <dlc-dir>/<title-id>/

Detect strategy:
  1. For each installed game, parse PARAM.SFO (TITLE_ID + APP_VER).
  2. Fetch https://a0.ww.np.dl.playstation.net/tpl/np/<TID>/<TID>-ver.xml
  3. Compare server's max version vs installed APP_VER.
  4. Compare existing PKGs in <dlc-dir>/<TID>/ to detect which versions
     are already locally cached (so we only download missing ones).
"""

import os
import re
import ssl
import struct
import sys
import urllib.request
from xml.etree import ElementTree as ET

PSN_URL = "https://a0.ww.np.dl.playstation.net/tpl/np/{tid}/{tid}-ver.xml"
DISC_RE = re.compile(rb"(?:^|\x00)((?:BL|BC)[A-Z]{2}[0-9]{5})")
PSN_RE = re.compile(rb"(?:^|\x00)(NP[A-Z]{2}[0-9]{5})")
DIRNAME_DISC_RE = re.compile(r"(BL|BC)([A-Z]{2})[-_]?([0-9]{5})")

# Sony's update server uses self-signed certs; verification fails.
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def extract_title_id(sfo_path: str, dir_name: str) -> str | None:
    try:
        with open(sfo_path, "rb") as f:
            data = f.read(8192)
    except OSError:
        return None

    m = DISC_RE.search(data)
    if m:
        return m.group(1).decode("ascii")
    raw = DIRNAME_DISC_RE.search(dir_name)
    if raw:
        return f"{raw.group(1)}{raw.group(2)}{raw.group(3)}"
    m = PSN_RE.search(data)
    return m.group(1).decode("ascii") if m else None


def parse_sfo(sfo_path: str) -> dict:
    """Parse PARAM.SFO and return key/value dict (string values only)."""
    try:
        with open(sfo_path, "rb") as f:
            data = f.read()
    except OSError:
        return {}
    if len(data) < 20 or data[:4] != b"\x00PSF":
        return {}
    key_table_off = struct.unpack("<I", data[8:12])[0]
    data_table_off = struct.unpack("<I", data[12:16])[0]
    num_entries = struct.unpack("<I", data[16:20])[0]
    out = {}
    for i in range(num_entries):
        idx = 20 + i * 16
        if idx + 16 > len(data):
            break
        key_off = struct.unpack("<H", data[idx:idx + 2])[0]
        data_fmt = struct.unpack("<H", data[idx + 2:idx + 4])[0]
        data_len = struct.unpack("<I", data[idx + 4:idx + 8])[0]
        data_off = struct.unpack("<I", data[idx + 12:idx + 16])[0]
        # Key is null-terminated string in key table
        kp = key_table_off + key_off
        ke = data.index(b"\x00", kp) if b"\x00" in data[kp:] else len(data)
        key = data[kp:ke].decode("utf-8", errors="replace")
        # Value: 0x0204 = utf-8 string (null-terminated within data_len)
        if data_fmt in (0x0204, 0x0004):
            raw = data[data_table_off + data_off:data_table_off + data_off + data_len]
            value = raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            out[key] = value
    return out


def extract_app_ver(sfo_path: str) -> str:
    sfo = parse_sfo(sfo_path)
    return sfo.get("APP_VER", "00.00")


def find_games(ps3_root: str) -> dict:
    """Return {title_id: (app_ver, name)} for installed games."""
    games = {}
    if not os.path.isdir(ps3_root):
        return games
    for entry in sorted(os.listdir(ps3_root)):
        sfo = os.path.join(ps3_root, entry, "PS3_GAME", "PARAM.SFO")
        if not os.path.isfile(sfo):
            continue
        tid = extract_title_id(sfo, entry)
        if not tid:
            continue
        ver = extract_app_ver(sfo)
        name = entry[:-4] if entry.endswith(".ps3") else entry
        # Keep first-seen entry (don't overwrite)
        games.setdefault(tid, (ver, name))
    return games


def fetch_psn_versions(tid: str) -> list:
    """Return list of (version, url, size, sha1) tuples available from PSN."""
    url = PSN_URL.format(tid=tid)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ansible-distrobox-gaming/1.0"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
            xml_data = resp.read()
    except Exception:
        return []
    if not xml_data.strip():
        return []
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return []
    if root.attrib.get("status") != "alive":
        return []
    out = []
    for pkg in root.iter("package"):
        ver = pkg.attrib.get("version", "")
        purl = pkg.attrib.get("url", "")
        size = int(pkg.attrib.get("size", "0"))
        sha1 = pkg.attrib.get("sha1sum", "")
        if ver and purl:
            out.append((ver, purl, size, sha1))
    return out


def local_versions(dlc_dir: str, tid: str) -> set:
    """Return set of patch versions already in local DLC dir."""
    p = os.path.join(dlc_dir, tid)
    if not os.path.isdir(p):
        return set()
    versions = set()
    # Filenames look like ...-A0117-V0100-PE.pkg → "A0117" → "01.17"
    pat = re.compile(r"-A(\d{2})(\d{2})-V")
    for fn in os.listdir(p):
        m = pat.search(fn)
        if m:
            versions.add(f"{m.group(1)}.{m.group(2)}")
    return versions


def ver_tuple(v: str) -> tuple:
    parts = v.split(".")
    return tuple(int(x) for x in parts) if all(p.isdigit() for p in parts) else (0,)


def download(url: str, dest: str, expected_size: int) -> bool:
    if os.path.exists(dest) and os.path.getsize(dest) == expected_size:
        return True
    try:
        with urllib.request.urlopen(url, context=SSL_CTX, timeout=60) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        return os.path.getsize(dest) == expected_size
    except Exception as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        if os.path.exists(dest):
            os.unlink(dest)
        return False


def main(argv: list) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 1

    ps3_root = argv[0]
    dlc_dir = None
    download_dir = None
    do_download = False

    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--dlc-dir" and i + 1 < len(argv):
            dlc_dir = argv[i + 1]
            i += 2
        elif a == "--download-dir" and i + 1 < len(argv):
            download_dir = argv[i + 1]
            i += 2
        elif a == "--download":
            do_download = True
            i += 1
        elif a == "--list":
            do_download = False
            i += 1
        else:
            print(f"Unknown arg: {a}", file=sys.stderr)
            return 1

    if dlc_dir is None:
        print("--dlc-dir is required", file=sys.stderr)
        return 1
    if download_dir is None:
        download_dir = dlc_dir

    games = find_games(ps3_root)
    if not games:
        print(f"No PS3 games found in {ps3_root}", file=sys.stderr)
        return 1

    if do_download:
        os.makedirs(download_dir, exist_ok=True)

    print(f"Checking {len(games)} installed PS3 games against PSN updates...")
    print(f"Existing cache: {dlc_dir}")
    print(f"Download dir:   {download_dir}")
    print(f"Mode:           {'download missing patches' if do_download else 'list only'}")
    print()

    total_missing = 0
    total_downloaded = 0
    games_with_updates = []

    for tid, (installed_ver, name) in sorted(games.items()):
        psn = fetch_psn_versions(tid)
        if not psn:
            continue
        psn_versions = sorted({v for v, *_ in psn}, key=ver_tuple)
        latest = psn_versions[-1]
        if ver_tuple(latest) <= ver_tuple(installed_ver):
            continue

        cached = local_versions(dlc_dir, tid)
        # All PSN versions newer than installed AND not already cached locally.
        needed = [
            (v, u, s) for (v, u, s, _h) in psn
            if ver_tuple(v) > ver_tuple(installed_ver) and v not in cached
        ]
        # Deduplicate by version (some XML tags repeat)
        seen = set()
        needed = [(v, u, s) for (v, u, s) in needed if v not in seen and not seen.add(v)]

        games_with_updates.append((tid, name, installed_ver, latest, len(needed)))

        if not needed:
            continue

        total_missing += len(needed)
        size_mb = sum(s for _, _, s in needed) / (1024 * 1024)
        print(f"  {tid}  installed={installed_ver}  latest={latest}  "
              f"missing={len(needed)} patches ({size_mb:.0f} MB)  {name[:50]}")

        if not do_download:
            continue

        os.makedirs(os.path.join(download_dir, tid), exist_ok=True)
        for ver, url, size in needed:
            fn = url.rsplit("/", 1)[-1]
            dest = os.path.join(download_dir, tid, fn)
            print(f"    -> {ver}: {fn}")
            if download(url, dest, size):
                total_downloaded += 1
            else:
                print(f"       FAILED")

    print()
    print(f"Summary: {len(games_with_updates)} games have updates available; "
          f"{total_missing} patches missing locally")
    if do_download:
        print(f"Downloaded: {total_downloaded}/{total_missing}")
        if total_downloaded and download_dir != dlc_dir:
            print(f"\nDownloaded to {download_dir}.")
            print(f"Move/copy to {dlc_dir} when ready, then re-run install_dlcs role.")
        elif total_downloaded:
            print(f"\nNext: re-run install_dlcs role to extract them into RPCS3.")
    else:
        print(f"\nRe-run with --download (and optional --download-dir <path>) to fetch them.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
