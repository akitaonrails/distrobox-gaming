# GTA IV (Complete Edition) curated mod set

Reproducibly installs a curated NexusMods set onto Steam **GTA IV: The Complete
Edition** under Proton. First output of the `nexus-mod-set` skill.

Role: `install_gta4_mods` · vars: `group_vars/all/gta4_mods.yml` · playbook:
`ansible/install-gta4-mods.yml` · tag: `gta4_mods` (opt-in / `never`).

## Version requirement (hard gate)

Requires **Complete Edition, appid 12210, `GTAIV.exe` = 1.2.0.59**. The role
reads the exe's PE FileVersion (`scripts/pe-version.py`) and **refuses to run**
on anything else. **Do not downgrade** — every mod here is FusionFix-based and
targets CE; the classic 1.0.7.0/1.0.8.0 + xliveless + ScriptHook stack is *not*
used. (Verified installed here: 1.2.0.59, GFWL already stripped.)

## The mod set (install order)

FusionFix is the foundation; the rest install into its `update/` overloader (no
OpenIV / `.rpf` editing). Single-owner data files go last.

| Order | # | Mod | Type |
|---|---|---|---|
| 1 | 716 | **Fusion Fix** — ASI loader (`dinput8.dll`) + Overloader + bugfixes | foundation (auto GitHub) |
| 2 | 282 | Higher Resolution Vehicle Pack | texture → `update/` |
| 3 | 357 | Higher Resolution Miscellaneous Pack | texture → `update/` |
| 4 | 311 | Higher Resolution Radio Logos | texture → `update/` |
| 5 | 258 | HD Upscaled Protagonists | texture → `update/` |
| 6 | 263 | Rivers of Blood v9.1 HD (plain build) | texture/FX → `update/` |
| 7 | 702 | 200+ Add-On Vehicles in Traffic | overloader + `FusionFix.ini` edits |
| 8 | 272 | Realistic Weapon Overhaul (`weaponinfo.xml`) | data → `update/` |
| 9 | 195 | Realistic Handling & Physics (`handling.dat`) | data → `update/` — **LAST** |

**Decisions baked in:**
- **195 handling wins** — applied last so all cars (incl. 702's add-ons) use the
  realistic physics (`dg_gta4_handling_priority`).
- **263: plain FusionFix build only**, never the RTX-Remix variant (NVIDIA
  path-tracer, unusable under Proton).
- **No ReShade** anywhere in this set (per environment constraint).
- ScriptHook / ScriptHookDotNet **not installed** — this set's FusionFix-native
  flow doesn't need them.

## Sourcing — download & preserve on the NAS

Everything lives under **`{{ dg_roms_final_root }}/PC/NexusMods/gta4/`**
(`/mnt/terachad/Emulators/ROMS_FINAL/PC/NexusMods/gta4/`). The role reuses
anything already there before downloading again, and never deletes it.

- **FusionFix (716)** — auto-downloaded from GitHub (pinned `v5.0.1`, sha256
  verified). Content-checked legit (loader DLLs + `plugins/` + `update/`).
- **The 8 Nexus mods** — auto-downloaded via `scripts/nexus-download.py` when
  `NEXUS_MODS_API_KEY` is exported (a **Premium** account; the script generates
  CDN links via the Nexus API). Free/Supporter accounts fall back to a browser
  cookies export, or manual staging — the role prints an exact
  download-manifest (mod, URL, target subdir) if anything is missing. The
  catalog pins the CE-appropriate `file` id per mod (e.g. 282 → the *Complete
  Edition* vehicle pack, 263 → the *Fusion Fix* build not the OIV/RTX variant).

On each staged archive the role runs a **legitimacy inspection** (fails on
`steam_api.dll` / `steam_appid.txt` / scene-crack markers). All 8 were verified
clean on 2026-08-06.

## Run it

```sh
cd ansible
ansible-playbook install-gta4-mods.yml            # or: site.yml --tags gta4_mods
```

Close Steam first (or `-e dg_gta4_stop_steam=true`). After it runs, apply the
one manual runtime dep to the GTA IV Proton prefix:

```sh
protontricks 12210 d3dx9_43     # or: flatpak run com.github.Matoking.protontricks 12210 d3dx9_43
```

Then launch GTA IV from Steam (the role sets `WINEDLLOVERRIDES="dinput8=n,b"`
so Proton loads FusionFix).

## Per-mod install (mapped from archive inspection)

Each archive was inspected; the catalog encodes explicit copy rules
(`installs: src -> dest`) that map files into the `update/` overloader:

- **282 / 357 / 311** — `update/`-rooted → copied straight into `update/`.
- **258** — its `GTAIV/{pc,TBoGT,TLAD}` → `update/` (overloader paths).
- **263** — its `.../update/` → `update/`.
- **195** — its `common/` + `pc/` → `update/common/` + `update/pc/`, applied
  **last** so `handling.dat` wins any overlap with 702.

### Two mods need a manual step (NOT auto-installed — flagged at runtime)

- **272 Realistic Weapon Overhaul** — the role installs the overloader-able
  parts (`WeaponInfo.xml`, `weapons.img`, `anim.img`). Its readme also imports a
  `WEAPONS` audio folder into `pc/audio/Sfx/resident.rpf` **with OpenIV** — a
  Windows GUI step that can't be done headlessly. Do that part by hand in OpenIV
  for the new weapon sounds; the stats/models work without it.
- **702 over 200 Add-On Vehicles** — uses the **Liberty's Legacy** add-on
  framework (vehicle models + Lists) and ships a full `FusionFix.ini`. Install
  it by hand from the archive's `GTAIV - manual install/` folder and merge its
  `plugins/FusionFix.ini` keys. Too multi-step to verify headlessly.

Texture placement assumes FusionFix-overloader semantics; **verify in-game**
after installing (the role can't launch GTA IV to confirm rendering).

## Revert

```sh
ansible-playbook install-gta4-mods.yml -e dg_gta4_revert=true
```

Removes FusionFix + the `update/` tree, clears the launch option, leaves your
preserved NAS archives intact. Then run Steam → **Verify integrity of game
files** as a backstop.
