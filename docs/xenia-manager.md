# Xenia Manager in the Gaming Box

This repo treats Xbox 360 support as an optional Wine-managed toolchain.

## Installation

```sh
cd ansible
ansible-playbook install-xenia.yml
```

What the playbook does:

- enables `[multilib]` inside the distrobox if needed
- installs `wine` and `winetricks`
- creates the prefix at `$DG_XENIA_PREFIX`
- installs the Windows runtimes Xenia Manager requires:
  - `.NET 10 Desktop Runtime`
  - `Visual C++ Redistributable`
- downloads the latest Xenia Manager ZIP release
- extracts it into `$DG_XENIA_MANAGER_RELEASES_DIR`
- points `$DG_XENIA_MANAGER_CURRENT` at the active release
- writes the stable launcher wrapper to `$DG_XENIA_MANAGER_BIN`
- renders the desktop entry under `config/desktop/rendered/`

Install or refresh the host menu entry from the host after the playbook:

```sh
scripts/install-host-launchers.sh
```

The manager and the Canary builds it downloads stay in the same prefix. That
is the cleanest maintenance model on Linux because Xenia Manager expects a
Windows-style environment and already owns Canary download/update logic.

## Post-install setup

1. Launch `Xenia Manager (on gaming)` from the host menu.
2. Go to `Manage`.
3. Install `Xenia Canary`.
4. Point the library scanner at `Z:\mnt\...` or the `G:` drive link if
   `$DG_XENIA_GAME_DIR` exists.

## Game library location

`dg_xenia_game_dir` defaults to `{{ dg_rom_heavy_root }}/xbox360` — the
`roms_heavy` tree is where large Xbox 360 titles live (including the
`Project Forza Plus Modded` game dirs). The role symlinks that path as
the Wine prefix's `G:` drive so Xenia Manager's library scanner can reach
it without a long UNC path.

If your Xbox 360 ROMs live elsewhere, override in
`host_vars/localhost.yml`:

```yaml
dg_xenia_game_dir: /your/path/xbox360
```

## Adding games to the catalog

Xenia Manager keeps its catalog in `Config/games.json` and populates it through
its **GUI only** — *Library → Add Games → scan a folder* points it at
`dg_xenia_game_dir`, boots each title to read its title-ID/media-ID, and
downloads artwork + compatibility ratings. There is no import CLI, so add games
through the GUI (the scan skips titles already added). Re-run the scan whenever
you drop new ISOs into `roms_heavy/xbox360`. Hand-editing `games.json` is not
recommended — a malformed entry can drop the whole catalog, and entries added
that way have no artwork.

If the same game gets imported twice you get a duplicate entry (Xenia Manager
renames the second `… (1)`); remove the redundant entry from `games.json` (and
its `GameData/<title>/` artwork dir + `…/config/<title>.config.toml`) with
Xenia closed.

## Unlocking XBLA (Arcade) games

XBLA titles ship as a **trial** that checks whether you own the full-game
license — on real hardware that comes from your Xbox Live account. Xenia has no
real Live, so it reports ownership through each game's **`license_mask`** config
setting (default `0` = own nothing → the game shows locked and nags you to "go
online"). Setting it to `1` (own the first license = full game) unlocks the
title **offline**.

The helper **`bin/xenia-unlock-xbla`** (deployed by `scripts_in_box`) does this
in bulk: it reads the Xenia Manager catalog, finds every XBLA title (content
type `000D0000`), sets `license_mask = 1` in each one's config (backing up
`.bak`), and bumps the global `xenia-canary.config.toml` default so
freshly-imported games start unlocked. Run it after importing new XBLA games,
with **Xenia closed** (Xenia rewrites its configs on exit; the helper refuses if
Xenia or the Manager is running):

```sh
distrobox enter gaming -- xenia-unlock-xbla
```

Notes:

- A few titles with multiple entitlements want `license_mask = -1` (own **all**
  licenses) rather than `1` — set those by hand in the game's config (or via
  Xenia Manager → the game → Xenia settings).
- `license_mask` unlocks only the local trial→full / DLC entitlement. It does
  **not** provide real online multiplayer or leaderboards (no actual Live;
  Xenia's netplay is separate and experimental).

## Why `pacman -Sy` and not `-Syu`

This role installs `wine` + `winetricks` with `pacman -Sy --needed` (sync
DB, no full upgrade). Full system upgrades live in `bootstrap_packages`
and are not coupled to this role — otherwise an unrelated pending
conflict (for example `sfml` rolling forward past `dolphin-emu`'s pinned
`libsfml-network.so`) would abort `install-xenia.yml` even though wine
itself installs cleanly.
