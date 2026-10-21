# Star Fox 64: Recompiled (`install_starfox64_recomp`)

[sonicdcer/Starfox64Recomp](https://github.com/sonicdcer/Starfox64Recomp) is a
native PC port of **Star Fox 64**, produced by statically recompiling the N64
ROM with [N64: Recompiled](https://github.com/N64Recomp/N64Recomp) and rendering
through **RT64** (Vulkan on the RTX). It is the "Recompiled" sibling to
HarbourMasters' **Starship** (the libultraship decomp port) and **supersedes it**
on this box — the `install_starship` role has been retired in favour of this one.

Upstream ships an **official native Linux x64 release**, so this is a
prebuilt-release role (no source build) — the DK64 / GoldenEye recomp pattern.
Features: widescreen + ultrawide, high framerate (monitor refresh by default),
a mod menu with drag-and-drop installs, and full controller/keyboard/mouse
remapping. (Ray tracing via RT64 is an upstream *planned* feature, not yet
available.)

## Install

```sh
cd ansible
ansible-playbook install-starfox64-recomp.yml   # or: site.yml --tags starfox64_recomp
scripts/install-host-launchers.sh               # refresh the host menu entry
```

Launcher `bin/starfox64-recomp`; host/Walker entry **"Star Fox 64 · Recompiled"**;
`ogm` id `starfox64-recomp`. Revert with `-e dg_sf64_revert=true` (removes the
launcher + install dir; `~/.config/Starfox64Recompiled` — config, saves and the
stored ROM — and your NAS ROM are untouched).

## ROM

The US **v1.1 (Rev A)** ROM, the same dump Starship used, staged on the NAS at
`{{ dg_rom_mid_root }}/n64/Star Fox 64 (USA) (Rev A).n64` (`dg_sf64_rom_src`,
z64 sha1 `09f0d105f476b00efa5303a3ebc42e60a7753b7a`). Override `dg_sf64_rom_src`
/ `dg_sf64_rom_sha1_z64` in `host_vars/localhost.yml` if yours lives elsewhere.

The recomp stores a validated ROM in its app folder as
`~/.config/Starfox64Recompiled/sf64.n64.us.1.1.z64`. The role **pre-seeds** that
file — converting the NAS dump to big-endian z64 and verifying the sha1 — so the
first-run ROM picker is skipped and the launcher boots straight into the game.
(If you ever point it at a different dump via the launcher's own picker, it
converts and stores it there itself.)

## How it works

- Downloads the pinned `Starfox64Recompiled-v1.0.3-Linux-X64-Release.zip` (the
  zip wraps a tar.gz; sha256 in `group_vars/all/starfox64_recomp.yml`) to
  `cache/starfox64-recomp/` and unpacks the `Starfox64Recompiled` binary +
  `assets/` + `recompcontrollerdb.txt` into `tools/starfox64-recomp/`. The role
  asserts `ldd` is clean inside the box.
- Extraction is version-gated on `.dg-installed-ref` and extracts over the top,
  so a version bump never wipes the config dir.
- `graphics.json` is seeded on first install (Vulkan + fullscreen + widescreen
  "Expand", HUD clamped to 16:9); in-game changes made afterwards are preserved.
- The launcher focuses **DP-1** (Hyprland Lua IPC) and pins the nvidia Vulkan ICD
  (`VK_ICD_FILENAMES` + PRIME offload) so RT64 runs on the RTX, not the AMD iGPU.
  8BitDo works out of the box via the bundled SDL (`recompcontrollerdb.txt`);
  all controls are remappable in the in-game config menu.
- Config + saves live in `~/.config/Starfox64Recompiled`; the EEPROM saves under
  `saves/` are registered in `dg_save_sets` (`starfox64-recomp`). Note these are
  **not** compatible with the retired Starship port's saves.

## Updating

Bump `dg_sf64_version` / `dg_sf64_asset_name` / `dg_sf64_asset_sha256` (from the
[releases](https://github.com/sonicdcer/Starfox64Recomp/releases)) and re-run.
The version gate re-extracts over the top; your config, saves and stored ROM
survive.
