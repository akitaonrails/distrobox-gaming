---
name: nexus-mod-set
description: >-
  Generate a reproducible, opt-in Ansible role that installs a curated set of
  NexusMods (or similar) game mods for one game in this distrobox-gaming repo.
  Use when the user gives a game + a list of nexusmods.com links and wants them
  installed reproducibly, in the correct order, with dependencies and game-
  version requirements handled. Triggers: "nexus mods", "mod set", "install
  these mods for <game>", or a pasted list of nexusmods.com links.
---

# nexus-mod-set

Turn "here is a game + a list of NexusMods links (+ constraints)" into a
reproducible, opt-in Ansible role, following the same MANUAL-staging pattern as
`install_re4_hd`, `metal_gear_master_collection`, and `install_gt5_master_mod`.

## Non-negotiables (learned the hard way)

1. **Version first, always.** Find the exact game version each mod requires and
   VERIFY it against the user's INSTALLED version before designing anything.
   Read the game exe's PE FileVersion:
   `scripts/pe-version.py <game.exe> --expect <version>`. Bake a hard version
   gate into the role (fail-with-guidance on mismatch). Version traps sink mod
   sets — GTA IV needs Complete Edition **1.2.0.59**; the RE4 HD Project needs
   appid **254700** (the 2005 UHD), not the 2023 remake.

2. **Nexus downloads: API for Premium, else manual.** Nexus pages 403 automated
   fetchers, and download links only generate with the user's own credentials.
   Use `scripts/nexus-download.py` (env `NEXUS_MODS_API_KEY`): file-list metadata
   works on ANY tier, but generating a CDN download link via the API requires a
   **Premium** account — free/supporter falls back to a browser cookies export
   (Netscape or the 13-column tab format), or fully-manual staging. The role
   auto-downloads when a key is present, else fails-with-manifest (mod, URL,
   target subdir). Gotchas: pick the version-appropriate `file` id per mod
   (variants exist — CE vs IV vs episode; "Fusion Fix build" vs "OIV"/RTX); CDN
   paths contain spaces, so percent-encode the path before GET. Genuinely
   hotlinkable deps (GitHub releases) auto-fetch pinned by sha256.

3. **Honor environment constraints.** EXCLUDE ReShade-required mods (hard under
   Proton — see memory `feedback_avoid_reshade_mods`) and NVIDIA RTX-Remix
   variants (heavy/finicky under Proton). Prefer ENB or native. If a candidate
   asset is found under NAS `Downloads/Hydra/`, flag it to the user first
   (memory `feedback_hydra_assets_flag_first`) — those are usually cracked
   repacks.

4. **Order is data.** Foundation (ASI loader / script hooks / bugfix framework)
   → framework mods → texture/content mods → single-owner data files
   (`handling.dat`, `weaponinfo.xml`) applied LAST with "last writer wins".
   Encode the sequence as an ordered catalog list in `group_vars`.

5. **Idempotent, reversible, documented.** `.dg-*` markers, backups before
   overlay, a `revert` path, a `docs/<game>-mods.md` write-up, and — in the
   SAME change — rows in `docs/external-installers.md` and a section in
   `ansible/host_vars/localhost.yml.example`.

6. **Preserve originals; reuse before re-downloading.** Every mod archive — the
   user's manual Nexus downloads AND auto-fetched GitHub deps — lives under
   `{{ dg_roms_final_root }}/PC/NexusMods/<game>/` (i.e.
   `/mnt/terachad/Emulators/ROMS_FINAL/PC/NexusMods/<game>/`). This is the
   canonical `dg_<game>_staging_root`. The role checks there and REUSES an
   existing archive before fetching again on a retry, and never deletes staged
   originals — they are the preserved source of truth on the NAS.

7. **Inspect archives before installing.** List each staged zip's contents and
   sanity-check it against the mod's declared type: expected file kinds (textures
   / `.rpf` / `.dat` / `.xml` for data & texture mods; `.asi` / `.dll` /
   `.net.dll` for scripts), a sane top-level structure, and NO red flags —
   unexpected bundled `.exe`/installers, `steam_api.dll` / `steam_appid.txt` /
   scene-crack markers, `autorun`, or paths escaping the intended folder. Flag
   anything suspicious to the user and do NOT install a questionable archive.

8. **Map install paths from inspection; don't fake the un-automatable.** Mod
   archives are heterogeneously rooted — some `update/`-rooted for a loader's
   overloader, some wrapped in a named folder, some loose files, some OpenIV
   `.oiv` packages. Inspect each and encode explicit per-mod copy rules
   (src-inside-archive → dest-in-game) rather than one blind extract. Some mods
   genuinely need a GUI/manual step — e.g. GTA IV's **OpenIV** to import into a
   `.rpf`, or a mod's own add-on framework (Liberty's Legacy) — which cannot be
   done or verified headlessly. Install the automatable parts, and FLAG the rest
   at runtime + in docs. Never pretend an OpenIV/`.rpf` import happened. And say
   plainly that final rendering can only be confirmed by the user in-game.

## Workflow

### 1. Research each link (delegate to a research subagent)
Nexus pages 403 automated fetchers, so a subagent should combine WebFetch with
WebSearch of indexed titles + authoritative guides. For each mod capture: name/
author, type (ENB / ASI / .NET script / OpenIV `.rpf` / texture / data / trainer
/ tool), **game version required**, **dependencies** (Nexus + off-site: ASI
loader, ScriptHook(.NET), xliveless, ENB, OpenIV), install method, and download
file(s). Also capture fundamentals: the version/downgrade landscape, the
foundational load order, Proton specifics (`WINEDLLOVERRIDES`, `protontricks`
verbs, DXVK), a recommended install order, and conflicts. Explicitly flag any
ReShade / RTX-Remix dependency to drop.

### 2. Verify the installed game
Parse `steamapps/libraryfolders.vdf` + `appmanifest_<appid>.acf` to find the
install, and confirm the exe version with `pe-version.py`. Determine the true
game root (mind subfolders — e.g. GTA IV CE puts everything under `GTAIV/`).

### 3. Design the role (data-driven)
- `group_vars/all/<game>_mods.yml`: `appid`, `required_version`, game_dir
  discovery, `staging_root`, launch_options, an ORDERED `dg_<game>_mods` catalog
  (per mod: id, name, type, staging subdir OR github source, any config-file
  edits), and the pinned foundation download.
- `roles/install_<game>_mods/tasks/main.yml`: preflight (game present + version
  assert + sources staged under the NexusMods preserve dir) → install the
  foundation (auto GitHub, cached in the preserve dir, reused if present) →
  inspect + install each mod in catalog order (list archive contents, flag red
  flags, extract → place into the mod loader's folder; `community.general.ini_file`
  for config edits) → Steam launch options
  (reuse `scripts/set-steam-launch-options.py`, guard against a running Steam) →
  `protontricks` reminder for runtime deps → completion report.
- `revert.yml`: restore backups, remove added files, clear launch options.

### 4. Wire it in
`site.yml` opt-in `{ role: install_<game>_mods, tags: [<game>_mods, never] }`;
`ansible/install-<game>-mods.yml`; `docs/<game>-mods.md`;
`docs/external-installers.md` rows (GitHub deps = AUTO, Nexus = MANUAL);
`ansible/host_vars/localhost.yml.example` section.

### 5. Be honest about post-staging unknowns
Each Nexus archive's internal structure, the exact mod-loader folder name, and
config keys are only knowable once the user stages the (gated) downloads. Set
documented defaults, expose them as `confirm once staged` role variables, and
say so in the docs — never fake certainty about a file you haven't seen.

## Reference exemplars in this repo
- Steam-game mod overlay + launch options + Steam-running guard:
  `roles/install_re4_hd`, `roles/metal_gear_master_collection`.
- Pinned GitHub-release fetch (URL + sha256): `roles/metal_gear_master_collection`,
  `roles/refresh_shadps4`.
- Extract-once + backup + marker + rollback report: `roles/install_gt5_master_mod`.
- PE version gate / 4GB-patch helpers: `scripts/pe-version.py`,
  `scripts/patch-laa.py`.
- Nexus downloader (Premium API + cookie fallback): `scripts/nexus-download.py`.
- Steam VDF / game-INI editors: `scripts/set-steam-launch-options.py`,
  `scripts/set-ini-options.py`.
- Worked example (this skill's first output): `roles/install_gta4_mods` +
  `group_vars/all/gta4_mods.yml` (ordered catalog, per-mod copy rules, manual
  flags for OpenIV/framework mods).
