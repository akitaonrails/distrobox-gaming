# Perfect Dark PC port

The **Perfect Dark PC port**, in the [DabDavis/perfect-dark-dabs-mod](https://github.com/DabDavis/perfect-dark-dabs-mod)
flavour — a **superset fork** of the mainline
[perfect-dark-pc-port/perfect_dark](https://github.com/perfect-dark-pc-port/perfect_dark)
(itself from the N64 decompilation). Keeps everything upstream (OpenGL 3, any
resolution/aspect, dual-analog + mouse look, configurable FOV, a `pd.ini` for
everything) and layers on **opt-in** extras: jump/roll/melee, third-person +
spectator cameras, 8→80 Combat Simulator simulants, body persistence, F12
screenshots, MP4 recording, 2×/4×/8× texture upscaling + texture-pack
auto-download, and an xdelta/bps/ips mod + stage loader. Same ROM,
`pd.ini`-compatible (the `Mod.*` keys are additive and ignored by stock builds).
Prebuilt Linux x64. Runs on the RTX. Managed by `install_perfect_dark` /
`install-perfect-dark.yml` (`site.yml --tags perfect_dark`).

_(Switched from the mainline port to this fork 2026-09-10 — strictly more
features, same base game and ROM, and it ships stable version tags instead of
the mainline's moving `ci-dev-build`. Revertible: repoint the vars back.)_

## Game data (required)

Your own **Perfect Dark NTSC-U V1.1** ROM — `ntsc-final`, md5
`e03b088b6ac9e0080440efed07c1e40f` in z64 form (US V1.0, PAL and JPN are also
supported upstream with their own executables; this role does NTSC-U). The port
expects it as `data/pd.ntsc-final.z64` next to the executable. This box's dump
`roms_mid/n64/Perfect Dark (USA) (Rev A).n64` is byte-swapped; the role converts
it to z64 and md5-verifies. Override `dg_pd_rom_src` for your rip.

## Release pinning (stable version tags)

The fork ships **stable version releases** (e.g. `v3.2.2`). The role pins the
tag + a **sha256** (`dg_pd_asset_sha256`, provenance in `dg_pd_build_ref`) and
reuses the tarball staged on the NAS at
`ROMS_FINAL/PC/perfect-dark-port/pd-dabs-mod-x86_64-linux.tar.gz`; `get_url` only
downloads when that copy is absent/corrupt and refuses a newer build until the
sha is bumped. To update: bump `dg_pd_release_tag`, download the new tarball to
that NAS path, set the new sha256 + `dg_pd_build_ref`, re-run (extract is
sha-gated, `data/` preserved).

## Install / run

```sh
cd ansible
ansible-playbook install-perfect-dark.yml
```

Installs to `tools/perfect-dark/` (`pd.x86_64` + `data/`; the fork ships a single
NTSC binary), seeds the ROM, seeds `~/.local/share/perfectdark/pd.ini` **once** with
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

**Working** 2026-09-10 — dabs-mod `v3.2.2` boots to the Perfect Dark title,
fullscreen on DP-1, on the RTX, reusing the existing ROM + saves. Mod features
are opt-in via the in-game menus / `pd.ini` `Mod.*` keys; stock play is
unchanged. (Prior mainline `port@32a1cb9f` also worked — revert by repointing
`dg_pd_repo`/tag/asset/sha back.)
