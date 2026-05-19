#!/usr/bin/env python3
"""Build a local Steam/Proton compatibility database from installed manifests."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "data" / "steam-proton-compat.json"
DEFAULT_OVERRIDES = REPO_ROOT / "data" / "steam-proton-overrides.json"

DECK_CATEGORY = {
    0: "unknown",
    1: "unsupported",
    2: "playable",
    3: "verified",
}


def load_acf(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pairs = re.findall(r'"([^"]+)"\s+"([^"]*)"', text)
    return {key: value for key, value in pairs}


def installed_apps(library_roots: list[Path]) -> list[dict[str, object]]:
    apps: dict[int, dict[str, object]] = {}
    for root in library_roots:
        if not root.exists():
            continue
        for manifest in sorted(root.glob("appmanifest_*.acf")):
            data = load_acf(manifest)
            app_id = int(data.get("appid", "0"))
            if not app_id:
                continue
            apps[app_id] = {
                "app_id": app_id,
                "name": data.get("name", ""),
                "install_dir": data.get("installdir", ""),
            }
    return [apps[app_id] for app_id in sorted(apps)]


def fetch_json(url: str, timeout: int = 20) -> tuple[dict | list | None, str | None]:
    try:
        completed = subprocess.run(
            [
                "curl",
                "-fsSL",
                "--max-time",
                str(timeout),
                "--retry",
                "2",
                "-H",
                "Accept: application/json",
                "-A",
                "distrobox-gaming-compat-db/1.0",
                url,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return json.loads(completed.stdout), None
    except (subprocess.CalledProcessError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)


def protondb_summary(app_id: int) -> dict[str, object]:
    url = f"https://www.protondb.com/api/v1/reports/summaries/{app_id}.json"
    data, error = fetch_json(url)
    result: dict[str, object] = {"url": f"https://www.protondb.com/app/{app_id}"}
    if isinstance(data, dict):
        for key in ("tier", "bestReportedTier", "trendingTier", "confidence", "score", "total"):
            if key in data:
                result[key] = data[key]
    elif error:
        result["error"] = error
    return result


def steam_deck_report(app_id: int) -> dict[str, object]:
    query = urllib.parse.urlencode({"nAppID": app_id})
    url = f"https://store.steampowered.com/saleaction/ajaxgetdeckappcompatibilityreport?{query}"
    data, error = fetch_json(url)
    result: dict[str, object] = {
        "url": "https://store.steampowered.com/steamdeck/mygames",
    }
    if isinstance(data, dict) and data.get("success") == 1:
        payload = data.get("results") or {}
        category = payload.get("resolved_category")
        steamos_category = payload.get("steamos_resolved_category")
        result["deck_category"] = DECK_CATEGORY.get(category, f"unknown:{category}")
        result["steamos_category"] = DECK_CATEGORY.get(
            steamos_category, f"unknown:{steamos_category}"
        )
    elif error:
        result["error"] = error
    return result


def steam_platforms(app_id: int) -> dict[str, object]:
    query = urllib.parse.urlencode({"appids": app_id, "filters": "platforms"})
    url = f"https://store.steampowered.com/api/appdetails?{query}"
    data, error = fetch_json(url)
    result: dict[str, object] = {
        "url": f"https://store.steampowered.com/app/{app_id}/",
    }
    if isinstance(data, dict):
        entry = data.get(str(app_id)) or {}
        platforms = (entry.get("data") or {}).get("platforms") or {}
        if platforms:
            result.update(
                {
                    "windows": bool(platforms.get("windows")),
                    "mac": bool(platforms.get("mac")),
                    "linux": bool(platforms.get("linux")),
                }
            )
    elif error:
        result["error"] = error
    return result


def app_kind(name: str) -> str:
    runtime_prefixes = (
        "Proton ",
        "Steam Linux Runtime",
        "Steamworks Common Redistributables",
    )
    if name.startswith(runtime_prefixes):
        return "runtime"
    return "game"


def policy_for(entry: dict[str, object]) -> str:
    if entry["type"] == "runtime":
        return "runtime_component"
    platforms = entry.get("store_platforms") or {}
    if isinstance(platforms, dict) and platforms.get("linux"):
        return "prefer_native_linux"
    protondb = entry.get("protondb") or {}
    if isinstance(protondb, dict):
        tier = protondb.get("tier")
        confidence = protondb.get("confidence")
        steam_deck = entry.get("steam_deck") or {}
        deck_category = steam_deck.get("deck_category") if isinstance(steam_deck, dict) else None
        if tier in ("platinum", "gold") and confidence in ("strong", "good"):
            return "steam_default_proton"
        if tier in ("platinum", "gold") and deck_category in ("verified", "playable"):
            return "steam_default_proton"
        if tier in ("platinum", "gold") and confidence == "moderate":
            return "steam_default_proton_low_confidence"
        if tier in ("silver", "bronze", "borked"):
            return "check_sources_before_testing"
    return "research_before_testing"


def merge_override(entry: dict[str, object], overrides: dict[str, object]) -> None:
    override = overrides.get(str(entry["app_id"]))
    if not isinstance(override, dict):
        return
    entry.update(override)
    entry["has_curated_override"] = True


def parse_roots(args: argparse.Namespace) -> list[Path]:
    roots: list[Path] = []
    for root in args.library_root or []:
        roots.append(Path(root).expanduser())
    env_roots = os.environ.get("DG_STEAM_LIBRARY_ROOTS")
    if env_roots:
        roots.extend(Path(part).expanduser() for part in env_roots.split(os.pathsep) if part)
    if not roots:
        roots.append(Path.home() / ".local/share/Steam/steamapps")
    return roots


def build_entry(app: dict[str, object], checked_date: str, overrides: dict[str, object]) -> dict[str, object]:
    app_id = int(app["app_id"])
    name = str(app["name"])
    entry: dict[str, object] = {
        "app_id": app_id,
        "name": name,
        "type": app_kind(name),
        "install_dir": app.get("install_dir", ""),
        "last_checked": checked_date,
        "store_platforms": steam_platforms(app_id),
        "steam_deck": steam_deck_report(app_id),
        "protondb": protondb_summary(app_id),
        "known_launch_options": [],
        "recommended_proton": None,
        "known_issues": [],
        "local_notes": [],
        "has_curated_override": False,
    }
    entry["compat_policy"] = policy_for(entry)
    merge_override(entry, overrides)
    return entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-root", action="append", help="Steam steamapps directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--checked-date", default=date.today().isoformat())
    parser.add_argument("--workers", type=int, default=8, help="Concurrent app metadata fetches")
    args = parser.parse_args()

    overrides: dict[str, object] = {}
    if args.overrides.exists():
        overrides = json.loads(args.overrides.read_text(encoding="utf-8"))

    roots = parse_roots(args)
    apps = installed_apps(roots)
    if not apps:
        print("No Steam app manifests found.", file=sys.stderr)
        return 1

    entries: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(build_entry, app, args.checked_date, overrides): app
            for app in apps
        }
        for index, future in enumerate(as_completed(futures), start=1):
            entry = future.result()
            print(
                f"[{index:03d}/{len(apps):03d}] {entry['app_id']} {entry['name']}",
                file=sys.stderr,
            )
            entries.append(entry)
    entries.sort(key=lambda item: int(item["app_id"]))

    output = {
        "schema_version": 1,
        "generated_by": "scripts/build-steam-proton-db.py",
        "generated_on": args.checked_date,
        "source_policy": [
            "ProtonDB summary is used for broad compatibility only.",
            "Valve Steam Deck compatibility is used as an official SteamOS signal.",
            "Launch options and Proton version pins must come from curated overrides with source links.",
        ],
        "apps": entries,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
