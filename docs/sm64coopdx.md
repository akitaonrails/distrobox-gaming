# SM64 Last Impact via Coop Deluxe (`install_sm64coopdx`)

Kaze Emanuar's **Super Mario 64: Last Impact** crashes every N64 emulator on the
box — its ~100k lines of custom assembly break Mupen64Plus-Next and ParaLLEl-N64
alike (see the parallel-n64 note). Instead of emulating the romhack, this role
runs the community **[Last Impact Port](https://github.com/ManIsCat2/last-impact-port)**,
which re-implements the hack as a **Lua mod** for
**[sm64coopdx](https://github.com/coop-deluxe/sm64coopdx)** (Super Mario 64 Coop
Deluxe), the maintained co-op fork of the SM64 PC port. Opt-in; installed
2026-08-16.

- **Form:** the **prebuilt Linux binary** of sm64coopdx `v1.5.1` (no compile) +
  the Last Impact mod `v1.0.1` dropped into its `mods/` folder. Renderer is
  **OpenGL** (SDL2); input is **native SDL** (8BitDo works out of the box).
- **Ships no game data.** On first launch it extracts assets from a US SM64
  baserom placed next to the binary as `baserom.us.z64`.

## Required baserom

The role reuses the same US SM64 dump as Render96ex
(`{{ dg_rom_mid_root }}/n64/Super Mario 64 (USA).n64`), converts it to big-endian
`.z64`, and verifies **SHA-1 `9bef1128717f958171a4afac3ed78ee2bb4e86ce`** via the
shared `n64_rom_prepare` role before placing it next to the binary. The NAS ROM
is never modified.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-sm64coopdx.yml       # or: site.yml --tags sm64coopdx
scripts/install-host-launchers.sh             # refresh the host menu entry
ansible-playbook install-sm64coopdx.yml -e dg_sm64coopdx_revert=true   # remove
```

Launcher: `{{ dg_box_home }}/bin/sm64coopdx`. It pins the RTX 5090 (GLX/PRIME —
the renderer is OpenGL), focuses DP-1, `cd`s into the install dir (the binary's
RUNPATH is CWD-relative, which is how it finds the bundled
`libdiscord_game_sdk.so` and its data), then runs the game.

## Playing Last Impact

1. Launch **SM64 Last Impact — Coop DX** (host menu / `bin/sm64coopdx`).
2. First boot extracts assets from `baserom.us.z64` (one-time, silent).
3. Open **Mods** in the menu and enable **SM64 Last Impact** (it's a
   `romhack`-class total conversion — enable it alone).
4. Start a game (single-player is fine; it's the co-op engine but plays solo).
   To play with others, host via the in-game server / CoopNet.

Config and saves live in `~/.local/share/sm64coopdx/` (box home), not the
install dir. Known gaps in the port (cutscenes/dialog limited by Coop's engine)
are listed in the mod's own `Bugs and Missing Content.txt`.

## Verified

Smoke-tested headless (`--headless --server --enable-mod last_impact_coop`): the
binary boots on the box, extracts assets from the verified baserom
(`rom_assets.c: loading asset`), and loads the Last Impact mod — all its levels,
actors, behaviours and textures — with **no Lua errors or incompatibility
warnings** on sm64coopdx v1.5.1. Actual in-level play is enabled from the Mods
menu (interactive).

## Updating

sm64coopdx and the mod are pinned by version + SHA-256 in
`group_vars/all/sm64coopdx.yml`. Bump `dg_sm64coopdx_version` /
`dg_sm64coopdx_li_version` and their checksums, then re-run — the checksum-gated
downloads pull the new builds. If a future coopdx release breaks the 2024-era
mod's Lua, pin coopdx back to a compatible tag.
