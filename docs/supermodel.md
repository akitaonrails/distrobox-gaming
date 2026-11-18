# Supermodel (Sega Model 3)

Supermodel emulates the Sega Model 3 arcade platform (and, since 0.4, Model 1
and 2). This repo installs **trzy/Supermodel's pinned Linux release** as a
self-contained tree inside the box and points its ROM directory at the NAS
Model 3 sets.

```sh
cd ansible && ansible-playbook install-supermodel.yml   # or site.yml --tags supermodel
```

| | |
|---|---|
| Version | `0.4-20261116-git-0b82a98` (official Linux tarball, SHA256-pinned, staged in `ROMS_FINAL/PC/releases/`) |
| Install | `tools/supermodel/` — `supermodel` binary, `Config/Games.xml` + `Music.xml`, `Assets/`, `NVRAM/`, `Saves/` |
| ROM sets | `roms_rare/model3` on the NAS (`dg_supermodel_roms_dir`), read in place |
| Launcher | `bin/supermodel-launch`; ES-DE **Sega Model 3 → Supermodel (Standalone)** |
| Old install | the AUR `supermodel` snapshot package is removed by the role |

## Why not the AUR package

The AUR `supermodel` snapshot was at `0.4_20261108_git_239a77b` while upstream
had already published `0.4-20261116-git-0b82a98`, and its packaging wrapper
(`/usr/bin/supermodel`) drops its arguments, so a frontend could never pass a
ROM. The release tarball is a complete tree with the same layout the binary
expects, so the role owns it: no package version drift, a pinned SHA256, and
`/usr/bin/supermodel` no longer shadows anything. Runtime dependencies
(`sdl2`, `sdl2_net`, `glu`) are installed explicitly.

## ROM directory

Two things point at `dg_supermodel_roms_dir` (default
`{{ dg_emudeck_root }}/roms_rare/model3`):

- `Config/Supermodel.ini` → `ROMDirectory`, the path the settings GUI lists
  ROM sets from.
- `tools/supermodel/ROMs` → a symlink to that folder, which is where the
  binary looks when it resolves the default `ROMs` path relative to its working
  directory.

Nothing is copied into the box; the ES-DE entry passes the ROM's absolute NAS
path on the command line. If you ever drop `.zip` sets into
`tools/supermodel/ROMs`, the role leaves that directory alone (and says so)
instead of replacing it with the link.

## Graphics: at the ceiling

The wrapper launches 4K exclusive fullscreen with the quality flags this build
documents:

| Flag | Why |
|---|---|
| `-res=3840,2160 -fullscreen` | native 4K output |
| `-wide-screen -wide-bg` | true 16:9 FOV with the 2D backgrounds extended to match (Model 3 has a real widescreen mode) |
| `-new3d` | Ian Curtis' 3D engine (the accurate one) |
| `-vsync` | locked to the panel's refresh |
| `-ss=2` | 2×2 supersampling (drop to `-ss=1` if a particular game ever dips) |
| `-upscalemode=3` | bicubic, the sharpest of the four 2D-layer upscale filters (default is bilinear) |

Fullscreen needs the window created on one output. Xwayland's screen here is
the **union of both monitors** (6000×3840), so SDL's default centred window
straddles them and `-fullscreen` dies with *"Couldn't find any matching video
modes"*. The wrapper reads `DP-1`'s offset from `xrandr` and passes
`-window-pos`, which pins the video mode to that output. It also focuses
`DG_MAIN_OUTPUT` (default `DP-1`) and re-asserts
`xwayland:force_zero_scaling=true` through Hyprland's Lua IPC before launching,
so the 4K surface is 1:1 pixels on the 1.5-scaled panel. There is no
gamescope: the iGPU/RADV problems documented in [sega-arcade.md](sega-arcade.md)
made it strictly worse than native XWayland.

OpenGL is hard-pinned to the RTX 5090 (`__GLX_VENDOR_LIBRARY_NAME=nvidia`,
`__NV_PRIME_RENDER_OFFLOAD=1`); the log reports
`Renderer: NVIDIA GeForce RTX 5090/PCIe/SSE2`.

## Controls

Pad mapping is managed in `Config/Supermodel.ini` (`dg_supermodel_settings`),
because Supermodel's defaults assume a different button order (Start on Guide,
Coin on L3, acceleration on the d-pad):

| Action | Pad | Keyboard |
|---|---|---|
| Start | Start | `1` |
| Coin | Back | `3` |
| Accelerate / brake | RT / LT | ↑ / ↓ |
| Shift up / down | RB / LB | `Y` / `H` |
| 4-way shifter | — (keyboard only) | `Q` `W` `E` `R` |
| Quit | Select+Start | `Esc` |

`Select+Start` is an `evsieve` bridge that injects Escape (Supermodel's UIExit)
when the chord fires, so the pad can always leave a game.

## NVRAM, saves and backups

- Per-game Test/Service-menu settings (Free Play, difficulty, …) live in
  `tools/supermodel/NVRAM/<romset>.nv`; save states go to `Saves/`.
- On first install the role **migrates** the old `~/.supermodel/NVRAM` (the
  AUR layout) with `rsync --ignore-existing`, so existing Free Play settings
  carry over, and then seeds the pre-configured pack from the NAS once.
  `~/.supermodel` is left in place, untouched, as the pre-0.4 leftover.
- Both directories are the `supermodel-nvram` set in `dg_save_sets`, so the
  nightly backup covers them and a revert keeps them.
- After tuning a game's Test menu, `ansible-playbook sync-arcade-nvram.yml`
  pushes the box's NVRAM back up to the NAS seed pack.

## Verified here

- `supermodel -version` reports `0.4-20261116-git-0b82a98` from the tree.
- A launch through `bin/supermodel-launch` opens the NAS `daytona2.zip`, logs
  `ROMDirectory=/mnt/terachad/…/roms_rare/model3`, `Supersampling=2`,
  `UpscaleMode=3`, `VSync=1`, the managed input mappings and
  `Renderer: NVIDIA GeForce RTX 5090`, and holds a fullscreen 3840×2160 window
  on DP-1 with no fullscreen mode error.
- Per-game frame rate was not measured: a direct shell launch lands on the
  workspace Hyprland picks, which was not the visible one during the test.
  Launching from ES-DE (workspace 7) is the path the family uses.

## Updating and reverting

Bump `dg_supermodel_version` + `dg_supermodel_asset_sha256` in
`group_vars/all/supermodel.yml` and re-run; the role re-unpacks when
`.dg-version` changes and leaves `NVRAM/`, `Saves/` and the managed INI keys in
place. Revert with `-e dg_supermodel_revert=true` — the wrapper and tree go,
your ROMs and NVRAM stay.