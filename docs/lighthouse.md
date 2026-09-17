# Lighthouse — Banjo-Kazooie PC port (`install_lighthouse`)

[HarbourMasters/Lighthouse](https://github.com/HarbourMasters/Lighthouse) is the
native PC port of **Banjo-Kazooie**, built on **libultraship** — the same engine
family as [Ship of Harkinian](ship-of-harkinian.md), Starship and
[SpaghettiKart](spaghettikart.md). It replaced the old `BanjoRecomp`
recompilation because the LUS port is the stronger base: internal resolution
scaling, widescreen, a built-in controller mapper, in-game romhack extraction,
and language packs — all the shared SoH UX.

Runs natively on the RTX (OpenGL/libultraship, no Wine), opens on DP-1, 8BitDo
works out of the box via SDL2 and the bundled `gamecontrollerdb.txt`.

## Install

```sh
cd ansible
ansible-playbook install-lighthouse.yml          # or: site.yml --tags lighthouse
scripts/install-host-launchers.sh                # refresh the host menu entry
```

Launcher `bin/lighthouse`; Walker/host entry **"Banjo-Kazooie · Lighthouse"**;
`ogm` catalog id `lighthouse`. Revert with `-e dg_lighthouse_revert=true` (removes
the launcher, desktop entry and install dir; your ROM is untouched).

## How it works

The role (see `group_vars/all/lighthouse.yml`):

- downloads the pinned release zip (`1.1.0`, sha256-pinned) into
  `tools/lighthouse/cache/` and extracts `lighthouse.appimage` +
  `gamecontrollerdb.txt` into `tools/lighthouse/current/`;
- seeds the **baserom next to the appimage** as `baserom.us.v10.z64`, extracted
  from `ROMS_FINAL/n64/Banjo-Kazooie (USA).zip` and byteswapped to big-endian
  `.z64`, verifying its SHA-1;
- deploys the launcher, which `cd`s into the install dir and runs the appimage.

On **first launch**, libultraship finds the baserom in its working directory and
**generates `bk.o2r`** (the asset archive) automatically — no ROM picker, same as
the SoH role. Saves, `bk.o2r` and `lighthouse.cfg.json` all live in
`tools/lighthouse/current/`.

> If a version bump wipes the install dir, the baserom is re-seeded and `bk.o2r`
> regenerates on the next launch. If Lighthouse ever *does* show a ROM picker
> (e.g. it stops auto-detecting), point it at `baserom.us.v10.z64` in that dir.

## ROM requirement

**Banjo-Kazooie (USA) v1.0** — z64 SHA-1 `1fe1632098865f639e22c11b9a81ee8f29c75d7a`
(the dump inside `ROMS_FINAL/n64/Banjo-Kazooie (USA).zip`). Lighthouse also
supports US v1.1 (`ded6ee16…`), JP (`90726d7e…`) and PAL (`bb359a75…`); to switch
region, change `dg_lighthouse_rom_zip` / `dg_lighthouse_rom_name` /
`dg_lighthouse_rom_sha1_z64`. Extra regions can be added in-game as **language
packs** (Settings → General → Languages).

## Romhacks

Lighthouse extracts many Banjo-Kazooie romhacks from a patched ROM (Settings →
Romhacks in the menubar), or boot one directly:

```sh
lighthouse -hack <slug>
```

## Updating

Bump `dg_lighthouse_version` + `dg_lighthouse_asset_name` to the new release, set
the new `dg_lighthouse_asset_sha256`, and re-run the playbook. The install is
version-gated by `.dg-installed-ref`, so it only re-extracts when the pin
changes.

Keybinds (default): A=X B=C L=E R=R Z=Z Start=Space, analog=WASD, C=arrows,
D-pad=TFGH, F11 fullscreen, ESC menubar.
