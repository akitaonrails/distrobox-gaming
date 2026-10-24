# Banjo-Tooie Recompiled — `install_banjotooie_recomp`

[some-scurvy-dog/banjo-tooie-scurvy-dog-port](https://github.com/some-scurvy-dog/banjo-tooie-scurvy-dog-port)
is an **N64Recomp + N64ModernRuntime + RT64 static recomp** PC port of
Banjo-Tooie (NTSC-U 1.0), built on the Banjo-Tooie decompilation. Opt-in
role; updated 2026-10-23 to `v0.1.0-alpha.4.3`. This is still an upstream
prerelease. The renamed executable is installed in a versioned folder so the
old Alpha 3 build remains available for rollback; the external profile keeps
saves, settings and the verified ROM. Alpha 4.3 fixes distant-geometry flicker
and audio clicking and adds borderless fullscreen and live resolution changes.

## Windows-only alpha → Wine (unlike CBFD/DKR-R)

Upstream ships **Windows x64 alpha builds only** (Linux/macOS "not ready"),
so — unlike the native-Linux CBFD/DKR-R/Beetle/Pilotwings recomps — this one
runs under **wine-11.8** with the established recipe: `UseEGL=N` GLX pin
(wine 11 EGL→iGPU regression), WineBus SDL registry for the 8BitDo, and
**gamescope** (`-W 3840 -H 2160 -f`) for fullscreen on DP-1. RT64 renders
through its "plume" D3D12→Vulkan layer (vkd3d) — confirmed initializing on
the RTX 5090 in the boot smoke test. The release zip is hash-pinned on the
NAS (`ROMS_FINAL/PC/banjotooie-recomp/`).

> Update-check note: upstream has **only prereleases** so far, so
> `releases/latest` is empty — query the releases list instead.

## ROM (required)

**Banjo-Tooie NTSC-U 1.0 only** — big-endian z64 sha256
`9ec37fba6890362eba86fb855697a9cff1519275531b172083a1a6a045483583`; the
launcher hard-rejects other regions/byte orders/modified ROMs. The NAS dump
`ROMS_FINAL/n64/Banjo-Tooie (USA).zip` (`Banjo-Tooie (U) [!].v64`,
byte-swapped) is normalized to `.z64`, sha256-verified and kept at
`ROMS_FINAL/PC/banjotooie-recomp/Banjo-Tooie (USA).z64`, plus a copy next to
the exe so the ROM picker defaults beside it.

**First launch is a one-time manual step**: Play → **Choose ROM...** → pick
the z64 → "Selected ROM: NTSC-U 1.0 validated" → **Start Game**. The launcher
then stores its own validated copy in the profile (integrity-checked; not
practical to pre-seed). No `--rom` CLI flag exists (checked exe strings;
only `--profile-dir`, `--run-seconds`, `--save-dir`, practice/trace flags).

## Pre-seeded graphics config

The role seeds `config/tooie_imgui.json` in the profile **only when absent**
(never clobbers user changes) with int enums from upstream
`src/frontend_config.cpp`:

- `tooie_output_mode: 1` — Borderless desktop (fills the gamescope canvas;
  default is a small window)
- `tooie_output_resolution: 5` — 3840 x 2160
- `tooie_game_widescreen: 1` — 16:9 widescreen

Pacing defaults (VSync off, Display output rate, Present Early) are written
by the app itself on first run and match upstream's recommended setup.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-banjo-tooie-recomp.yml
ansible-playbook install-banjo-tooie-recomp.yml -e dg_btooie_revert=true
```

Launcher `bin/banjotooie-recomp` (Walker: **Banjo-Tooie Recompiled**).
The profile is pinned with `--profile-dir` to
`~/.config/banjotooie-recomp` in the box (saves in its `saves/`, settings,
controller profiles, validated ROM copy, logs) so it survives reinstalls of
the install dir. Revert removes the launcher, install dir and Wine prefix but
keeps the NAS zip/z64 and the profile.

Alpha caveats (upstream): full-game completion not established; menu overlays
can glitch during entry; shadows can lose coverage on angled floors. F5 =
ordinary save from the pause menu, F6 hold = fast forward, F7 = skip
intro/title, Private Practice has one durable save-state slot (per-build).
