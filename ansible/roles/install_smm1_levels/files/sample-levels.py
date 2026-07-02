#!/usr/bin/env python3
"""Sample the SMM1 archive metadata API and keep the highest-starred levels.

smmdb.net (the curated archive) is dead and the bobac-analytics metadata
API has no global top-by-stars endpoint, so we approximate "best": sample
random levels broadly, rank by stars, keep the top N as candidates.

Writes candidates.json: a list of {levelid, name, creator, stars, url}
sorted by stars desc, sized count * oversample to survive Wayback 404s
during the download stage.

Usage: sample-levels.py --out candidates.json [--count 60] [--samples 600]
"""

import argparse
import json
import random
import sys
import time
import urllib.request

API = "https://api.bobac-analytics.com/smm1"
UA = {"User-Agent": "curl/8.7.1"}


def get_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--count", type=int, default=60)
    ap.add_argument("--samples", type=int, default=600)
    ap.add_argument("--oversample", type=float, default=2.0)
    args = ap.parse_args()

    seen: dict[int, dict] = {}
    hits = misses = 0
    # levelids observed in the wild are ~8-digit; sample the id space and
    # tolerate misses (the endpoint returns an error for unmapped seeds).
    while hits < args.samples and (hits + misses) < args.samples * 12:
        seed = random.randint(1, 80_000_000)
        try:
            d = get_json(f"{API}/searchRandomLevels/{seed}")
        except Exception:
            misses += 1
            time.sleep(1)
            continue
        if isinstance(d, list) and d:
            for c in d:
                if c.get("levelid") and c.get("url"):
                    seen[c["levelid"]] = c
            hits += 1
        else:
            misses += 1
        if (hits + misses) % 50 == 0:
            print(f"  sampled: {hits} hits / {misses} misses, "
                  f"unique: {len(seen)}", file=sys.stderr)
        time.sleep(0.2)

    levels = sorted(seen.values(), key=lambda c: -(c.get("stars") or 0))
    keep = levels[: int(args.count * args.oversample)]
    print(f"kept top {len(keep)} of {len(seen)} sampled; star range: "
          f"{keep[0].get('stars')} .. {keep[-1].get('stars')}" if keep else "no levels!")
    with open(args.out, "w") as f:
        json.dump(
            [
                {k: c.get(k) for k in ("levelid", "name", "creator", "stars", "url", "clearrate")}
                for c in keep
            ],
            f,
            indent=1,
        )
    return 0 if keep else 1


if __name__ == "__main__":
    sys.exit(main())
