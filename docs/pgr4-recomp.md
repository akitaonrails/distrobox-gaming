# Project Gotham Racing 4 (Recomp) — PGR4 2026

[tazzkiller/PGR4_2026](https://github.com/tazzkiller/PGR4_2026) is a static
recompilation of **Project Gotham Racing 4** (Xbox 360, Title Update 2) built on
ReXGlue and the `pgr4-native` D3D12 renderer (with DLSS/DLAA, FSR, XeGTAO,
enhanced reflections, multithreaded rendering, optional volumetric fog, and an
optional 6.5 GB HD texture pack). It runs from the host through
**GE-Proton11-1** (VKD3D-Proton + NVAPI).

## Install

```sh
cd ansible && ansible-playbook install-pgr4-recomp.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `v1.65` (`PGR4_v1.65.zip`, SHA256-pinned in `ansible/group_vars/all/pgr4_recomp.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned ISO | `ROMS_FINAL/xbox360/Project Gotham Racing 4 [RF].iso` (extracted once via `extract-xiso` into `tools/pgr4-recomp/game/`) |
| Title Update 2 | `ROMS_FINAL/xbox360-updates/Project Gotham Racing 4/tu00000002_00000000` (XboxUnity TUID `21625`, SHA256 `9980cf82…`, symlinked into `tools/pgr4-recomp/title-update/`) |
| Optional HD Pack | `ROMS_FINAL/PC/mods/pgr4-2026/textures_hd.pak` (6.5 GB, symlinked beside `pgr4.exe` when staged) |
| Install root | `{{ dg_box_home }}/tools/pgr4-recomp/` (`releases/v1.65/PGR4/`, `current/`, shared `game/`, `title-update/`, `pgr4.toml`) |
| Saves & settings | `compatdata/pgr4-recomp/pfx/drive_c/users/steamuser/Documents/pgr4/` + `pgr4.toml` — backed up by `backup-saves` under `pgr4-recomp` |
| Launcher | `{{ dg_box_home }}/bin/pgr4-recomp` (host-side GE-Proton11-1 → `PGR4Launcher.exe`) |
| Desktop entry | **Project Gotham Racing 4 (Recomp)** (`pgr4-recomp.desktop`) |

## Graphics & Performance

- `pgr4.toml` is seeded once (`force: false`, so launcher/in-game edits survive
  reruns) for **4K** on the RTX 5090:
  - `pgr4_native_resolution_scale = 3` (1280×720 × 3 = **3840×2160** native 4K)
  - `pgr4_native_msaa = 4` (4× MSAA), `pgr4_native_anisotropy = 16` (16× AF)
  - `pgr4_native_gtao = true` (XeGTAO), `pgr4_native_enhanced_reflections = true`,
    `pgr4_native_details = 2` (Ultra), `pgr4_native_texture_hd = true`
  - `pgr4_60fps = true`, `pgr4_native_frame_latency = 3` (unlocked up to monitor
    refresh rate), `d3d12_present_vsync = true`, `fullscreen = true`
- Optional **Volumetric Effects** can be enabled in `PGR4Launcher.exe` (adds
  ~33,000 extra shaders on first preparation).
- First launch compiles shaders inside `PGR4Launcher.exe` before starting
  `pgr4.exe`.

## Gamepad Policy

A controller is required by upstream; native XInput through GE-Proton works out
of the box with the 8BitDo Ultimate 2 (`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`
is exported by the launcher).
