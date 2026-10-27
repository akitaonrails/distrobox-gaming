#!/usr/bin/env python3
"""Report new GitHub releases for the PC games in the rendered OGM catalog."""

import os
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DIR = ROOT / "config/desktop/rendered"
VARS_DIR = ROOT / "ansible/group_vars/all"
GAME_CATEGORIES = {"port", "decomp", "recomp", "fangame", "wine", "arcade"}

# Installs the sweep cannot compare against a release tag, and why. Keeping
# them visible (instead of dropping them) documents the intent.
SOURCE_PINNED = {
    # built from source at a pinned commit, not from a release asset
    "gaming-cannonball": "dg_cannonball_ref",
    "gaming-dkc1-recomp": "commit pin",
    "gaming-dkc2-recomp": "commit pin",
    "gaming-dkc3-recomp": "commit pin",
    "gaming-sonic2-2013": "source build",
    "pc-outrun-2006": "nightly.link artifact pinned by commit",
}
AUTO_LATEST = {
    # role installs whatever the API reports as latest, on purpose
    "gaming-dusk": "latest-release role",
    "gaming-unleashed-recomp": "latest-release role",
}
GONE_REPOS = {
    # upstream deleted/renamed; the installed pinned copy is kept as-is
    "gaming-rygt-gt-sport": "mlgprorektm8/RyGT is gone (HTTP 404); installed release kept",
}

# Values remain in group_vars; this only tells the sweep which pin to compare.
# Games built from a moving Git ref, or installed by a latest-release role, are
# still queried and shown as REVIEW rather than silently assumed current.
PIN_VARS = {
    "gaming-azimuth-fh2-infinity": ("azimuth.yml", "dg_azimuth_infinity_version"),
    "gaming-2ship2harkinian": ("2ship2harkinian.yml", "dg_two_ship2harkinian_version"),
    "gaming-banjotooie-recomp": ("banjotooie_recomp.yml", "dg_btooie_release_tag"),
    "gaming-beetle-recomp": ("beetle_recomp.yml", "dg_bar_version"),
    "gaming-cbfd-recomp": ("cbfd_recomp.yml", "dg_cbfd_version"),
    "gaming-dekui-mm3d": ("dekui.yml", "dg_dekui_version"),
    "gaming-dk64-recomp": ("dk64_recomp.yml", "dg_dk64_version"),
    "gaming-dkr-r": ("dkr_recomp.yml", "dg_dkr_release_tag"),
    "gaming-dude": ("dude.yml", "dg_dude_version"),
    "gaming-driveclub-recomp": ("driveclub_recomp.yml", "dg_dcr_version"),
    "gaming-fm4-recomp": ("hl360_fm4.yml", "dg_hl360_version"),
    "gaming-doa2u-re": ("doa2u_re.yml", "dg_doa2u_version"),
    "gaming-doom2-ray-traced": ("prboom_rt.yml", "dg_prboom_rt_version"),
    "gaming-ffvii-7th-heaven": ("7th_heaven.yml", "dg_7th_heaven_version"),
    "gaming-fukami-rrv": ("fukami.yml", "dg_fukami_version"),
    "gaming-fzero": ("fzero_recomp.yml", "dg_fzero_release_tag"),
    "gaming-gravity-rush": ("gravity_rush.yml", "dg_gr_version"),
    "gaming-gt2-pc-port": ("gt2_pc.yml", "dg_gt2_version"),
    "gaming-gt3-revisited": ("gt3_revisited.yml", "dg_gt3r_version"),
    "gaming-kyty-gt7": ("kyty_gt7.yml", "dg_kyty_version"),
    "gaming-sotc-pc": ("sotc_pc.yml", "dg_sotc_version"),
    "gaming-gdiffuser": ("gdiffuser.yml", "dg_gdiffuser_version"),
    "gaming-goldeneye": ("project_midas.yml", "dg_midas_version"),
    "gaming-gow3-pc": ("gow3_pc.yml", "dg_gow3_pc_release_tag"),
    "gaming-gt4-recomp": ("gt4_recomp.yml", "dg_gt4r_130_version"),
    "gaming-lighthouse": ("lighthouse.yml", "dg_lighthouse_version"),
    "gaming-midnightclubla": ("midnightclub_la.yml", "dg_mcla_release_tag"),
    "gaming-mickey-donald": ("mickey_donald.yml", "dg_mdc_version"),
    "gaming-mph-recomp": ("mph_recomp.yml", "dg_mph_version"),
    "gaming-nebula-galaxy": ("nebula.yml", "dg_nebula_version"),
    "gaming-opencmr2": ("opencmr2.yml", "dg_opencmr2_version"),
    "gaming-opensc2k": ("opensc2k.yml", "dg_opensc2k_version"),
    "gaming-perfect-dark": ("perfect_dark.yml", "dg_pd_release_tag"),
    "gaming-pilotwings-recomp": ("pilotwings_recomp.yml", "dg_pw64_version"),
    "gaming-roadrash64": ("roadrash64_recomp.yml", "dg_rr64_release_tag"),
    "gaming-rsc2": ("rsc2.yml", "dg_rsc2_version"),
    "gaming-rygt-gt-sport": ("rygt.yml", "dg_rygt_release_tag"),
    "gaming-ship-of-harkinian": ("ship_of_harkinian.yml", "dg_ship_of_harkinian_version"),
    "gaming-smas": ("smas_recomp.yml", "dg_smas_release_tag"),
    "gaming-smb-remastered": ("smb_remastered.yml", "dg_smb_remastered_version"),
    "gaming-smw-remastered": ("smw_remastered.yml", "dg_smw_remastered_version"),
    "gaming-sonic3air": ("sonic3air.yml", "dg_s3air_version"),
    "gaming-spaghettikart": ("spaghettikart.yml", "dg_spaghettikart_version"),
    "gaming-starfox-enhanced": ("starfox_enhanced.yml", "dg_sfe_version"),
    "gaming-starfox64-recomp": ("starfox64_recomp.yml", "dg_sf64_version"),
    "gaming-starship": ("starship.yml", "dg_starship_version"),
    "gaming-triaevum": ("triaevum.yml", "dg_triaevum_version"),
    "gaming-twine-007": ("twine.yml", "dg_twine_release_tag"),
    "gaming-waverace-recomp": ("waverace_recomp.yml", "dg_wr64_release_tag"),
    "gaming-wipeout-pe": ("wipeout_pe.yml", "dg_wipeout_pe_version"),
    "gaming-wwhd-recomp": ("wwhd_recomp.yml", "dg_wwhd_release_tag"),
    "gaming-vf1": ("vf1_recomp.yml", "dg_vf1_release_tag"),
    "gaming-vf3-recomp": ("vf3_recomp.yml", "dg_vf3_release_tag"),
    "ridge-racer": ("ridge_racer.yml", "dg_ridge_racer_version"),
    "sega-rally-hd": ("sega_rally.yml", "dg_sega_rally_version"),
    "virtua-fighter": ("model1.yml", "dg_model1_vf_version"),
    "virtua-racing": ("model1.yml", "dg_model1_vr_version"),
}

# One repository publishes several unrelated games under separate tag prefixes.
TAG_PREFIXES = {
    "gaming-dkr-r": "Version",
    "gaming-midnightclubla": "midnightclubla-",
}
PRERELEASE_CHANNELS = {"gaming-rygt-gt-sport"}


def catalog_games():
    games = []
    for desktop in sorted(DESKTOP_DIR.glob("*.desktop")):
        fields = {}
        for line in desktop.read_text().splitlines():
            if line.startswith("X-OGM-") and "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value
        repo = fields.get("X-OGM-GitHub", "")
        if fields.get("X-OGM-Category") not in GAME_CATEGORIES or not repo:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise ValueError(f"Invalid GitHub repo in {desktop}: {repo}")
        games.append((desktop.stem, repo))
    return games


def pinned_tag(stem, var_cache):
    spec = PIN_VARS.get(stem)
    if spec is None:
        return None
    filename, key = spec
    if filename not in var_cache:
        var_cache[filename] = yaml.safe_load((VARS_DIR / filename).read_text())
    value = var_cache[filename].get(key)
    if value is None:
        raise ValueError(f"Cannot resolve {filename}:{key}")
    pin = re.sub(
        r"{{\s*(\w+)\s*}}",
        lambda match: str(var_cache[filename][match.group(1)]),
        str(value),
    )
    if "{{" in pin:
        raise ValueError(f"Cannot resolve {filename}:{key}")
    return pin


def github_token():
    token = os.environ.get("GITHUB_TOKEN", "")
    if re.fullmatch(r"(?:gh[opsur]_|github_pat_)[A-Za-z0-9_]+", token):
        return token
    if shutil.which("gh"):
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return None
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            token = lines[-1].strip() if lines else ""
            if re.fullmatch(r"(?:gh[opsur]_|github_pat_)[A-Za-z0-9_]+", token):
                return token
    return None


def latest_release(repo, stem, pin, token):
    releases = None
    if shutil.which("gh"):
        env = os.environ.copy()
        env["MISE_QUIET"] = "1"
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/releases?per_page=100"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        if result.returncode == 0:
            # Mise shims may prepend setup text; the API payload starts at '['.
            payload_start = result.stdout.find("[")
            if payload_start >= 0:
                try:
                    releases = json.loads(result.stdout[payload_start:])
                except json.JSONDecodeError:
                    pass
    if releases is None:
        url = f"https://api.github.com/repos/{repo}/releases?per_page=100"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "distrobox-gaming-game-sweep"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        with urlopen(Request(url, headers=headers), timeout=25) as response:
            releases = json.load(response)
    if not isinstance(releases, list):
        raise ValueError(f"Unexpected GitHub response for {repo}")
    prefix = TAG_PREFIXES.get(stem, "")
    matching = [r for r in releases if not r.get("draft") and r.get("tag_name", "").lower().startswith(prefix.lower())]
    if pin and re.match(r"^[vV]?\d", pin):
        matching = [r for r in matching if re.match(r"^[vV]?\d", r["tag_name"])]
    # A rolling nightly, devel, or test channel is not the successor to a
    # stable pin. Keep it visible through GitHub, but compare like with like.
    if pin and not any(word in pin.lower() for word in ("nightly", "devel", "test")):
        matching = [r for r in matching if not any(word in r["tag_name"].lower() for word in ("nightly", "devel", "test"))]
    # A stable installation should not silently switch to an alpha/RC build.
    if pin and stem not in PRERELEASE_CHANNELS and not re.search(r"(?:alpha|beta|rc\d|pre(?:view|release))", pin, re.I):
        matching = [r for r in matching if not r.get("prerelease")]
    return max(matching, key=lambda r: r.get("published_at") or "", default=None)


def same_tag(pinned, latest):
    left, right = pinned.lstrip("vV").lower(), latest.lstrip("vV").lower()
    if left == right:
        return True
    # Pins may carry the asset's own suffix ("0.1.6-Alpha", "1.3.0-rc6") while
    # the tag is the bare version; treat a suffixed pin as the same release.
    return left.startswith(right) or right.startswith(left)


def main():
    games = catalog_games()
    if not games:
        print("No GitHub-backed PC games found in rendered desktop entries.", file=sys.stderr)
        return 2
    counts = Counter()
    token = github_token()
    print(f"GitHub PC game releases ({len(games)} catalog entries):")

    def check_game(game):
        stem, repo = game
        if stem in GONE_REPOS:
            return stem, "GONE", GONE_REPOS[stem]
        if stem in AUTO_LATEST:
            return stem, "AUTO", AUTO_LATEST[stem]
        if stem in SOURCE_PINNED:
            return stem, "SOURCE", SOURCE_PINNED[stem]
        try:
            pin = pinned_tag(stem, {})
            release = latest_release(repo, stem, pin, token)
            if release is None:
                status, detail = "NO_RELEASE", repo
            else:
                tag = release["tag_name"]
                if pin is None:
                    status, detail = "REVIEW", f"{tag} (no release pin in group_vars)"
                elif same_tag(pin, tag):
                    status, detail = "CURRENT", tag
                else:
                    status, detail = "CANDIDATE", f"{pin} -> {tag}"
                detail += f"  {release.get('html_url') or 'https://github.com/' + repo + '/releases'}"
        except (HTTPError, URLError, HTTPException, OSError, TimeoutError, ValueError, KeyError) as exc:
            # Never format raw exceptions: urllib can include Authorization
            # header values in a malformed-header error.
            reason = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
            status, detail = "ERROR", f"{repo}: {reason}"
        return stem, status, detail

    with ThreadPoolExecutor(max_workers=5) as pool:
        for stem, status, detail in pool.map(check_game, games):
            counts[status] += 1
            print(f"  {status:10} {stem:30} {detail}", flush=True)
    print("  " + ", ".join(
        f"{key.lower()}={counts[key]}"
        for key in ("CURRENT", "CANDIDATE", "REVIEW", "SOURCE", "AUTO", "GONE", "NO_RELEASE", "ERROR")
    ))
    return 1 if counts["CANDIDATE"] or counts["REVIEW"] or counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
