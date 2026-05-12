# Azahar — Nintendo 3DS emulator

[Azahar](https://azahar-emu.org/) is an open-source 3DS emulator,
[forked from Citra](https://github.com/azahar-emu/azahar) after Citra
was discontinued in 2024. Installed inside the gaming distrobox from
AUR (same pattern as Dolphin / PCSX2 / RPCS3 / etc.).

This entry is **optional** — not in `site.yml`. Install:

```sh
cd /mnt/data/Projects/distrobox-gaming/ansible
ansible-playbook install-azahar.yml
```

## What the playbook does

1. `yay -S --needed azahar` inside the gaming distrobox (the upstream
   AUR package builds Azahar from source; ~10–15 min on a fresh box,
   no-op on re-runs).
2. Ensures `~/.config/azahar-emu/qt-config.ini` exists.
3. Applies project-standard defaults via `community.general.ini_file`
   so only the listed keys are managed — anything else the user
   toggles in the Azahar GUI stays untouched on re-runs.
4. Ensures `~/.local/share/azahar-emu/load/textures/` is present so
   the HD textures role (separate playbook) can drop symlinks into it.
5. Renders + installs a host-side launcher via `dg_emulator_launchers`
   in `launchers.yml` (just one new entry; the generic
   `emulator-launcher.desktop.j2` template handles the rest).
6. Adds an `n3ds` system to ES-DE pointing at `dg_azahar_game_dir`.

## Defaults applied to qt-config.ini

| Section | Key | Value | Why |
|---|---|---|---|
| Renderer | `backend` | `2` | Vulkan — faster than OpenGL on NVIDIA at 4K |
| Renderer | `resolution_factor` | `4` | 4× native (3DS is 400×240) → ~1600×960, clean upscale to G8 |
| Renderer | `anisotropic_filtering` | `5` | 16× AF — sharper textures at oblique angles |
| Renderer | `texture_filter` | `2` | anime4k filter — good for 3DS sprites/UI |
| Renderer | `use_asynchronous_gpu_emulation` | `true` | smoother frametimes |
| Renderer | `async_custom_loading` | `true` | required when HD packs are present |
| Renderer | `spirv_shader_gen` | `true` | newer shader gen path |
| Renderer | `use_vsync_new` | `true` | tear-free |
| System | `is_new_3ds` | `true` | New 3DS family (Smash, MM3D, Xenoblade need this) |
| System | `region_value` | `-1` | auto-detect from ROM |
| UI | `fullscreen` | `true` | gaming flow |
| UI | `confirmClose` | `false` | gaming flow |
| WebService | `enable_telemetry` | `false` | privacy |
| Paths | `romsPath` + `gamedirs\1\path` | `dg_azahar_game_dir` | single library |

Unmanaged keys (controller bindings, save-state slots, layout
preferences) are left to the GUI.

## Library

ROMs live at:

```
{{ dg_rom_heavy_root }}/n3ds
```

(Default: `/mnt/terachad/Emulators/EmuDeck/roms_heavy/n3ds`.) Both the
direct Azahar library scan (`Paths.gamedirs\1\path`) and ES-DE's
n3ds system point at this directory, so one place to maintain.

## Launch

Three ways:

```sh
# CLI (with optional ROM path):
distrobox enter gaming -- azahar [/path/to/game.3ds]

# Walker / desktop launcher:
#   "Azahar (on gaming)"

# ES-DE:
#   Pick an entry in the n3ds system list.
```

## HD textures

Handled by a separate playbook (`install-hd-textures.yml` — coming
next). Azahar reuses Citra's HiResTexture format
(`load/textures/<TitleID>/`) so existing Citra HD packs slot in
unchanged. The role symlinks per-title directories from the
NAS-stored extracted packs into
`{{ dg_azahar_textures_dir }}` and flips `custom_textures = true` in
`qt-config.ini` automatically.
