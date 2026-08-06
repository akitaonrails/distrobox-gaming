#!/usr/bin/env python3
"""Download NexusMods files using the user's OWN credentials.

Two auth paths (auto-selected):
  * PREMIUM API (preferred) — env NEXUS_MODS_API_KEY generates CDN download
    links directly via the Nexus API. Requires a Premium account.
  * COOKIE session (fallback) — a browser cookies export (Netscape or the
    13-column tab format) drives the website's GenerateDownloadUrl endpoint,
    for non-premium accounts.

Metadata (game id, file lists) always comes from the API (works on any tier).
Files go to --dest and are skipped if already present (preserve/reuse). Secrets
are never printed. Used by the nexus-mod-set skill / install_<game>_mods roles.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

API = "https://api.nexusmods.com"
SITE = "https://www.nexusmods.com"
UA = "Mozilla/5.0 (distrobox-gaming nexus-download)"


def api_get(path: str) -> dict | list:
    key = os.environ.get("NEXUS_MODS_API_KEY")
    if not key:
        raise SystemExit("NEXUS_MODS_API_KEY is not set in the environment")
    req = urllib.request.Request(
        API + path,
        headers={"apikey": key, "accept": "application/json", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def api_download_link(game: str, mod: str, file_id: int) -> str | None:
    """Premium-only: return a CDN URL for a file, or None if not permitted."""
    try:
        data = api_get(f"/v1/games/{game}/mods/{mod}/files/{file_id}/download_link.json")
    except urllib.error.HTTPError as e:
        if e.code in (403, 400):  # non-premium / needs nxm key
            return None
        raise
    if isinstance(data, list) and data:
        return data[0].get("URI")
    return None


def load_nexus_cookies(path: str) -> str:
    """Return a 'name=value; ...' Cookie header for *.nexusmods.com.

    Accepts standard Netscape cookies.txt AND the 13-column tab export some
    browser extensions produce (name, value, domain, path, ...).
    """
    jar: dict[str, str] = {}
    for line in open(path, errors="replace").read().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) >= 7 and cols[1] in ("TRUE", "FALSE"):
            domain, name, value = cols[0], cols[5], cols[6]          # Netscape
        elif len(cols) >= 3:
            name, value, domain = cols[0], cols[1], cols[2]          # ext TSV
        else:
            continue
        if "nexusmods.com" in domain:
            jar[name] = value
    if not jar:
        raise SystemExit(f"no nexusmods.com cookies found in {path}")
    return "; ".join(f"{k}={v}" for k, v in jar.items())


def cookie_download_url(cookie_header: str, domain: str, game_id: int, file_id: int) -> str | None:
    data = urllib.parse.urlencode({"fid": str(file_id), "game_id": str(game_id)}).encode()
    req = urllib.request.Request(
        SITE + "/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl",
        data=data,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{SITE}/{domain}/mods/?tab=files",
            "User-Agent": UA,
            "Cookie": cookie_header,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8", "replace")
    try:
        return json.loads(body).get("url")
    except json.JSONDecodeError:
        sys.stderr.write(f"  non-JSON generate response: {body[:200]!r}\n")
        return None


def resolve_url(game, mod, file_id, via, cookie_header, game_id):
    if via in ("auto", "api"):
        url = api_download_link(game, mod, file_id)
        if url or via == "api":
            return url
    if via in ("auto", "cookie"):
        if not cookie_header:
            return None
        return cookie_download_url(cookie_header, game, game_id, file_id)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game", required=True, help="Nexus game domain, e.g. gta4")
    ap.add_argument("--mod", required=True, help="mod id, e.g. 282")
    ap.add_argument("--file", help="specific file_id; default: every MAIN file")
    ap.add_argument("--via", choices=["auto", "api", "cookie"], default="auto")
    ap.add_argument("--cookies", default="/tmp/nexus.cookies.txt")
    ap.add_argument("--dest", help="download directory (required unless --list)")
    ap.add_argument("--list", action="store_true", help="list files and exit")
    ap.add_argument("--test", action="store_true", help="resolve URL but do not download")
    a = ap.parse_args()

    meta = api_get(f"/v1/games/{a.game}/mods/{a.mod}/files.json")
    files = meta.get("files", []) if isinstance(meta, dict) else []
    if a.list:
        for f in files:
            print(f"{f['category_name']:12} id={f['file_id']:<8} v{str(f.get('version')):<10} "
                  f"{round((f.get('size_kb') or 0) / 1024, 1)}MB  {f['file_name']}")
        return 0

    if not a.dest:
        raise SystemExit("--dest is required unless --list")
    targets = [f for f in files if (str(f["file_id"]) == a.file if a.file
                                    else f["category_name"] == "MAIN")]
    if not targets:
        raise SystemExit("no matching files (check --file or MAIN category)")

    cookie_header = ""
    if a.via in ("auto", "cookie") and os.path.exists(a.cookies):
        try:
            cookie_header = load_nexus_cookies(a.cookies)
        except SystemExit:
            cookie_header = ""
    ginfo = api_get(f"/v1/games/{a.game}.json")
    game_id = ginfo["id"] if isinstance(ginfo, dict) else 0
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)

    rc = 0
    for f in targets:
        out = dest / f["file_name"]
        if out.exists() and out.stat().st_size > 0:
            print(f"reuse   {out.name}")
            continue
        url = resolve_url(a.game, a.mod, f["file_id"], a.via, cookie_header, game_id)
        if not url:
            print(f"NO-URL  mod {a.mod} file {f['file_id']} ({f['file_name']})")
            rc = 3
            continue
        print(f"fetch   {f['file_name']}  <- {urlparse(url).netloc}")
        if a.test:
            continue
        # CDN paths contain spaces (mod filenames) — percent-encode the path,
        # leave the signed query string intact.
        parts = urllib.parse.urlsplit(url)
        dl = urllib.parse.urlunsplit((parts.scheme, parts.netloc,
                                      urllib.parse.quote(parts.path, safe="/%:@"),
                                      parts.query, parts.fragment))
        tmp = out.with_suffix(out.suffix + ".part")
        with urllib.request.urlopen(urllib.request.Request(dl, headers={"User-Agent": UA}), timeout=600) as r, \
                open(tmp, "wb") as w:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                w.write(chunk)
        tmp.rename(out)
        print(f"saved   {out.name}  ({out.stat().st_size} bytes)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
