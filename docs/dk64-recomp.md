# Donkey Kong 64: Recompiled

**DK64 Recompiled** ("DK64 Rekongpiled",
[Rainchus/Donkey-Kong-64-Recompiled](https://github.com/Rainchus/Donkey-Kong-64-Recompiled))
is a static recompilation (N64Recomp + RT64) of the N64 *Donkey Kong 64* into a
native executable — same family as our GoldenEye recomp, but with **official
prebuilt Linux x64 releases**, so there's no source build. Runs on the RTX (RT64
Vulkan), any framerate (gameplay unaffected), widescreen, in-game config menus,
mods. Managed by `install_dk64_recomp` / `install-dk64-recomp.yml`
(`site.yml --tags dk64_recomp`).

## Game data (required)

Your own **Donkey Kong 64 (USA)** N64 ROM. It is the *only* ROM the port accepts
(any byte order; verified by hash). The correct dump is
`roms_mid/n64/originals/Donkey Kong 64 (USA).n64` — 32 MiB, byte-swapped,
z64 sha1 `cf806ff2603640a748fca5026ded28802f1f4a50`. The `roms_mid/n64/` copy is a
33.8 MB **overdump** and is rejected. Override `dg_dk64_rom_src` for your rip.

The app's ROM picker stores the chosen ROM as `<config>/<game_id>.z64` with
`game_id = "DK64"` (from `src/main/main.cpp`), i.e.
`~/.config/DK64Recompiled/DK64.z64`. The role byteswaps + sha1-verifies the
dump and **pre-seeds** that file, so the launcher goes straight into the game.

## Install / run

```sh
cd ansible
ansible-playbook install-dk64-recomp.yml
```

Pins release `1.0.2` (`DK64Recompiled-Linux-X64-Release-1-0-2.zip`, sha256-checked;
the zip wraps a `DK64Recompiled.tar.gz` → `DK64Recompiled` + `assets/` +
`recompcontrollerdb.txt`) into `tools/dk64-recomp/`, seeds the ROM, seeds
`graphics.json` to **Fullscreen + Vulkan** (first install only — in-game
changes are preserved), and installs `bin/dk64-launch` + a Walker entry
"Donkey Kong 64 · Recompiled". Saves live in `~/.config/DK64Recompiled/saves`.
Bump `dg_dk64_version` + `dg_dk64_asset_name` + sha256 to update (extract is
version-gated; saves/ROM untouched). Revert: `-e dg_dk64_revert=true`.

The launcher runs from the install root (assets are cwd-relative), pins the
NVIDIA Vulkan ICD (RT64 must not land on the AMD iGPU), and focuses DP-1 via
the Hyprland Lua `eval` API. **8BitDo** works natively (SDL2 +
`recompcontrollerdb.txt`); remap in the in-game config menu.

## Status

**Working** 2026-09-02 — v1.0.2 launches straight into the game, fullscreen on
DP-1 at 2560×1440, RT64 on `NVIDIA GeForce RTX 5090`.
