# GoldenEye 007 via Project Midas

Native PC port of **GoldenEye 007 (N64)** built from the decompilation
(`murkantor/Project-Midas`), managed by `install_project_midas` /
`install-project-midas.yml`. It replaced the retired
`cblock85/GoldenEye64Recomp` static recomp on 2026-10-18 after a side-by-side
evaluation — same verified working baseline (4K, high fps), plus true mouselook,
real widescreen, in-game settings, named controller profiles, and multiplayer
extras; the recomp's RT64 renderer was its only edge. The retired role and its
build-toolchain fixes live in git history (`docs/goldeneye-recomp.md` at
commit `30fe52a`).

## Game data (user-provided)

Needs your own **stock NTSC-U GoldenEye 007 cart** (12,582,912 bytes,
content-checked at startup; z64/v64/n64 byte orders all accepted, bad dumps are
rejected with a reason in the log). On this box, `roms_mid/n64/originals/
007 - GoldenEye (USA).n64` is the good dump (v64 byteswapped); the
`roms_mid/n64/` non-originals copy is a **bad dump** — never point
`dg_midas_rom` at it. The launcher passes the cart via `--rom-file`.

## Install / run

```sh
cd ansible
ansible-playbook install-project-midas.yml   # or site.yml --tags project_midas
```

Launcher: `/mnt/data/distrobox/gaming/bin/goldeneye-midas`; the Walker menu
entry is **GoldenEye 007 · Project Midas**. Saves, profiles, weapon sets,
match settings and controller layouts live in `~/.local/share/ProjectMidas`
(`Data/`, `midas.ini`, `gamecontrolleruser.txt`) and are shared across
versions via symlinks from the versioned release dir — retain that directory
during upgrades.

## Baseline and policy

One-time baseline (marker `~/.local/share/ProjectMidas/.dg-initial-settings`):
3840×2160 borderless fullscreen, real widescreen (`widescreen=1`), 4× MSAA,
16× anisotropic filtering, `maxfps=120` (the project default; sim tick rate is
derived from it) with vsync, mouse look with `smart_mouse_lock`, rumble on.
The game rewrites `midas.ini` on exit and preserves later in-game menu
changes; delete the marker to re-apply the baseline. Authentic N64 timing is
`maxfps=-1` if ever wanted.

Controller: SDL game controllers with rumble; the 8BitDo Ultimate 2 is
recognized by name and mapped as player 1 (left stick moves, right stick
looks, right trigger fires, left trigger aims). Default layout and rebinding
live in the in-game settings (no in-game remapping limitation carried from
1.0 — Midas has full binding screens). Keyboard + mouse play player 1 by
default (`p1_hybrid`).

## Gotchas

- **The Linux build is 32-bit i386 with SDL2 bundled.** Audio goes through
  SDL's pulseaudio backend → `lib32-libpulse` is a required package (installed
  by the role); without it SDL falls back to ALSA/dummy and the game is silent
  while the log spams `snd: event queue FULL`. With it, the host PipeWire
  pulse socket is used directly (verified as a live playback stream).
- Launch from the desktop/Walker entry so the session env
  (`XDG_RUNTIME_DIR`, Wayland/X) is inherited; v1.0.1 fixed Wayland keyboard
  input and settings persistence.
- 7z extraction drops the executable bit — the role restores it; a manual
  extract needs `chmod +x ProjectMidas`.

## Status

Verified 2026-10-18 (v1.0.1): boots the stock USA cart (CRC checked in-log),
attract loop at 3840×2160 at roughly 100–120 fps on the RTX 5090, 8BitDo
recognized with rumble, settings persisted, audio streaming through PipeWire.
A player-driven mission and controller input during gameplay have **not**
been checked yet.
