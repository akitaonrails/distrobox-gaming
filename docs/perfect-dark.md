# Perfect Dark PC port

The **Perfect Dark PC port** ([perfect-dark-pc-port/perfect_dark](https://github.com/perfect-dark-pc-port/perfect_dark),
formerly fgsfdsfgs) is a native port built from the N64 decompilation: OpenGL 3
renderer, any resolution/aspect, dual-analog controller + mouse look,
configurable FOV, and a `pd.ini` for everything. Prebuilt Linux x64 builds.
Runs on the RTX. Managed by `install_perfect_dark` / `install-perfect-dark.yml`
(`site.yml --tags perfect_dark`).

## Game data (required)

Your own **Perfect Dark NTSC-U V1.1** ROM — `ntsc-final`, md5
`e03b088b6ac9e0080440efed07c1e40f` in z64 form (US V1.0, PAL and JPN are also
supported upstream with their own executables; this role does NTSC-U). The port
expects it as `data/pd.ntsc-final.z64` next to the executable. This box's dump
`roms_mid/n64/Perfect Dark (USA) (Rev A).n64` is byte-swapped; the role converts
it to z64 and md5-verifies. Override `dg_pd_rom_src` for your rip.

## Release pinning (rolling tag)

Upstream publishes builds under one rolling tag, `ci-dev-build`, rebuilt in
place — so the URL is stable but the bytes change. The role pins a **sha256**
(`dg_pd_asset_sha256`, provenance in `dg_pd_build_ref`) and reuses the tarball
staged on the NAS at `ROMS_FINAL/PC/perfect-dark-port/pd-x86_64-linux.tar.gz`;
`get_url` only downloads when that copy is absent/corrupt and refuses a newer
upstream build until the sha is bumped. To update: download the tarball, copy
it to that NAS path, set the new sha256 + `dg_pd_build_ref`, re-run (extract is
sha-gated, `data/` preserved).

## Install / run

```sh
cd ansible
ansible-playbook install-perfect-dark.yml
```

Installs to `tools/perfect-dark/` (`pd.x86_64` + `pd.pal/jpn.x86_64` + `data/`),
seeds the ROM, seeds `~/.local/share/perfectdark/pd.ini` **once** with
`[Video] DefaultFullscreen=1, ExclusiveFullscreen=0, VSync=1,
FramerateLimit=144` (the port fills every other default and rewrites the file
on exit — later in-game changes are preserved), and installs
`bin/perfect-dark-launch` + a Walker entry "Perfect Dark · PC port".

Why those video settings: borderless fullscreen (an *exclusive* mode-switch is
exactly what crashes games on the 240 Hz DP-1 — leave the display mode alone),
and a frame cap because the port "will have issues running faster than
~165 FPS" and VSync alone on this panel would run it at 240.

The launcher pins NVIDIA GLX (OpenGL would otherwise land on the AMD
iGPU/llvmpipe), focuses DP-1 via the Hyprland Lua `eval` API, and runs from the
install root (the port finds `data/` relative to the exe). Saves + `pd.ini`
live in `~/.local/share/perfectdark`. Revert: `-e dg_pd_revert=true`.

## Controller

**8BitDo works natively** (SDL2): the log shows
`input: assigned controller '0: (8BitDo Ultimate 2 Wireless Controller)' … to player 0`.
Dual-analog (two-stick) control is enabled for player 1; rebind in `pd.ini`
`[Input]` or in-game options.

## Status

**Working** 2026-08-30 — build `port@32a1cb9f` boots straight into the game,
fullscreen on DP-1 at 2560×1440, pad assigned.
