# Resident Evil 4 HD Project (2005 Ultimate HD Edition)

Reproducibly overlays the fan-made [RE4 HD Project](https://www.re4hd.com/)
remaster onto a legitimately-owned Steam copy of the classic Resident Evil 4,
running under Proton in the box.

Role: `install_re4_hd` · vars: `group_vars/all/re4_hd.yml` · playbook:
`ansible/install-re4-hd.yml` · tag: `re4_hd` (opt-in / `never`).

## Which game (this trips everyone up)

The HD Project **only** works on the **2014 PC port**, Steam **appid 254700**.
Capcom renamed that store page to **"Resident Evil 4 (2005)"** in December 2022
— same game, same appid, no separate "lesser" edition exists. It is *not* the
2023 remake (**appid 2050650**, "RESIDENT EVIL 4  BIOHAZARD RE4"), which this
mod cannot touch.

- Buy/verify ownership: <https://store.steampowered.com/app/254700/> — if you
  own it the page says **Play**, otherwise **Buy**. In your library, search
  `2005`.
- Install it into the in-box Steam library (default
  `…/gaming/.local/share/Steam/steamapps/common/Resident Evil 4`).

## Get the mod (MANUAL — you download it)

The download is ~34 GB and has no pinned/checksummed release URL, so it is a
MANUAL asset (see `external-installers.md`).

**Use the OFFICIAL package, not a scene "repack".** Repacks (e.g. 3DMGAME)
bundle a Steam emulator — a fake `steam_api.dll`, `steam_appid.txt`,
`3DMGAME.ini`, and a pre-cracked `bio4.exe` — which would break real Steam on a
game you legitimately own. Sources, in order of preference:

1. **re4hd.com** — the authors' own installer (Mega / MediaFire / torrent).
   Archive password: `re4hdproject`.
2. **Internet Archive** — crack-free mirror uploaded for the authors:
   <https://archive.org/details/re4HDProject.7z> (checksummable).

### Stage it for Ansible

Extract/produce a directory that contains `BIO4/` and `Bin32/`, and point
`dg_re4_hd_source` at it (default `{{ dg_external_games_root }}/mods/re4-hd-project`):

```
<dg_re4_hd_source>/
├── BIO4/                     # the ~38 GB of HD assets
└── Bin32/
    ├── dinput8.dll           # re4_tweaks (mod loader)
    ├── dinput8.ini           # re4_tweaks config, tuned for the HD Project
    └── re4_tweaks/           # setting_overrides/ + sideloaded op/event
```

Ways to produce that layout from the official download:
- The **manual** mirror already ships `BIO4/` + `Bin32/` — just extract.
- From `re4HDProject.7z`: `7z x re4HDProject.7z` (password `re4hdproject`).
- From `re4HDProject-setup.exe`: run it once under Wine and point it at a
  *scratch* folder (not the game), then stage that folder — or `innoextract`
  it if it's an Inno Setup build.

The role only ever **reads** the source and copies out of it; it never writes
back, so the staged copy is safe to keep on the NAS.

> **Note on the maintainer's NAS:** a copy already exists under
> `…/Downloads/Hydra/…`, but that one is a 3DMGAME **repack** (cracked). The
> role deliberately does not point there — stage the official package instead.

## What the role does

Overlays **only** the genuine HD Project onto the owned copy:

1. **Preflight** — confirms appid 254700 is installed; fails with guidance if
   the game or the staged source is missing.
2. **Backup** — tars the pristine `Bin32/` (small: stock `bio4.exe` +
   genuine `steam_api.dll`) to `dg_re4_hd_backup_dir` for revert. BIO4 is *not*
   tar'd (13 GB) — Steam re-verify is the revert path for it.
3. **4GB patch** — sets LargeAddressAware on the **genuine** `bio4.exe` in
   place (`scripts/patch-laa.py`, idempotent). The mod needs >2 GB address
   space; we patch your real exe rather than install the repack's.
4. **re4_tweaks** — copies `dinput8.dll` + `dinput8.ini` + `re4_tweaks/` into
   `Bin32/` (allow-list; the genuine `steam_api.dll` is left untouched).
5. **BIO4** — full replace (`rsync --delete`) with the HD assets, excluding
   `steam_appid.txt` (marker-gated `.dg-re4-hd-bio4-installed`).
6. **Launch options** — sets `WINEDLLOVERRIDES="dinput8=n,b" %command%` for
   appid 254700 (Proton must load the native mod `dinput8.dll` for re4_tweaks
   to init). Auto-discovers the single in-box `localconfig.vdf`; set
   `dg_re4_hd_steam_localconfig` to override. Refuses to edit while Steam runs.

**Crack files always filtered out**, whatever the source ships:
`steam_api.dll`, `steam_api.dll.orig`, `3DMGAME.ini`, the repack `bio4.exe` and
`.bak` (never in the Bin32 allow-list), and `steam_appid.txt` (BIO4 exclude).

## Run it

```sh
cd ansible
# after installing RE4 (2005) and staging the source:
ansible-playbook install-re4-hd.yml
# or as part of a bigger run:
ansible-playbook site.yml --tags re4_hd
```

Close Steam first (or pass `-e dg_re4_hd_stop_steam=true`) so the launch-option
edit isn't clobbered. Then launch **Resident Evil 4 (2005)** from Steam.

## Revert

```sh
ansible-playbook install-re4-hd.yml -e dg_re4_hd_revert=true
```

Restores the stock `Bin32/` (un-patched exe), removes the re4_tweaks files, and
clears the launch option. **BIO4 is not restored automatically** — afterwards
run Steam → *Resident Evil 4 (2005)* → Properties → Installed Files → **Verify
integrity of game files** to re-download the stock assets.

## Troubleshooting

- **Black screen on launch** — re4_tweaks `dinput8.ini` already sets
  `FixDisplayMode = true` for this. Confirm the launch option is present
  (Steam → Properties → Launch Options).
- **No re4_tweaks overlay (F1/config) in-game** — the `WINEDLLOVERRIDES`
  launch option is missing or Proton isn't loading the native `dinput8.dll`.
- **Steam overlay / achievements broken** — a crack leaked in. Revert, confirm
  the genuine `Bin32/steam_api.dll` (≈106 KB, not ≈260 KB) is in place, and
  re-run from an official source.
- **re4_tweaks upstream** (reference only; the mod bundles a matched build):
  <https://github.com/nipkownix/re4_tweaks>.
