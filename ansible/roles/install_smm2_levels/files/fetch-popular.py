#!/usr/bin/env python3
"""Fetch the most-liked SMM2 courses compatible with the local game version.

Queries the tgrcode.com MariOver API's search_popular endpoint (overall +
each difficulty bucket) to build a candidate pool, filters out courses
uploaded after the local game version's release cutoff (courses saved on
newer game versions refuse to load on older games), ranks by likes, and
downloads level data (.bcd) + thumbnail (.jpg) for the top N.

Outputs into --dest:
    001.bcd, 001.jpg, 002.bcd, ...   (rank-ordered)
    manifest.json                     (rank -> course metadata)

Usage: fetch-popular.py --dest courses/ --count 60 \
           [--max-uploaded 2019-10-01] [--base https://tgrcode.com/mm2]
"""

import argparse
import datetime
import json
import sys
import time
import urllib.request

DIFFICULTIES = [None, "e", "n", "ex", "sex"]  # overall + per-difficulty buckets


def get(url: str, retries: int = 3) -> bytes:
    # tgrcode.com 403s the default Python-urllib User-Agent.
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as exc:
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt + 1} after error: {exc}", file=sys.stderr)
            time.sleep(3)
    raise RuntimeError("unreachable")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True)
    ap.add_argument("--count", type=int, default=60)
    ap.add_argument(
        "--max-uploaded",
        default="2019-10-01",
        help="only courses uploaded before this date (game-version compat); "
        "empty string disables the filter",
    )
    ap.add_argument("--base", default="https://tgrcode.com/mm2")
    args = ap.parse_args()

    from pathlib import Path

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    cutoff = None
    if args.max_uploaded:
        cutoff = datetime.datetime.fromisoformat(args.max_uploaded).timestamp()

    pool: dict[str, dict] = {}
    for diff in DIFFICULTIES:
        url = f"{args.base}/search_popular?count=100"
        if diff:
            url += f"&difficulty={diff}"
        print(f"query: {url}")
        try:
            data = json.loads(get(url))
        except Exception as exc:
            print(f"  bucket failed, continuing: {exc}", file=sys.stderr)
            continue
        for c in data.get("courses", []):
            pool[c["course_id"]] = c

    print(f"candidate pool: {len(pool)} unique courses")
    candidates = list(pool.values())
    if cutoff:
        candidates = [c for c in candidates if c["uploaded"] < cutoff]
        print(f"after {args.max_uploaded} version-compat filter: {len(candidates)}")

    candidates.sort(key=lambda c: -c["likes"])
    top = candidates[: args.count]
    if len(top) < args.count:
        print(
            f"WARNING: only {len(top)} courses available after filtering "
            f"(requested {args.count})",
            file=sys.stderr,
        )

    manifest = {}
    for rank, c in enumerate(top, start=1):
        cid = c["course_id"]
        print(
            f"[{rank:>3}/{len(top)}] {c['likes']:>7} likes  {cid}  "
            f"[{c['game_style_name']}] {c['name'][:44]}"
        )
        (dest / f"{rank:03}.bcd").write_bytes(get(f"{args.base}/level_data/{cid}"))
        try:
            (dest / f"{rank:03}.jpg").write_bytes(
                get(f"{args.base}/level_thumbnail/{cid}")
            )
        except Exception as exc:
            print(f"  thumbnail failed (non-fatal): {exc}", file=sys.stderr)
        manifest[f"{rank:03}"] = {
            "course_id": cid,
            "name": c["name"],
            "likes": c["likes"],
            "game_style": c["game_style_name"],
            "theme": c["theme_name"],
            "difficulty": c["difficulty_name"],
            "clear_rate": c["clear_rate_pretty"],
            "uploaded": c["uploaded_pretty"],
        }
        time.sleep(0.5)  # be polite to the mirror

    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {len(top)} courses + manifest to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
