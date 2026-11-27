# R4: Ridge Racer Type 4 (Remix)

[i5han/R4-remix](https://github.com/i5han/R4-remix) is a PC port of **R4: Ridge
Racer Type 4** (PS1, USA `SLUS-00797`) with three rendering modes (**Original**,
**Clean**, and **Remaster** with path-traced lighting), widescreen/ultrawide,
unlocked frame rates + VRR, NVIDIA Reflex, and DLSS 4.5 + Ray Reconstruction.
It runs from the host via **GE-Proton11-1** with VKD3D-Proton DXR + NVAPI
enabled.

## Install

```sh
cd ansible && ansible-playbook install-r4-remix.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `0.1.0` (`r4r-cadc145.zip`, SHA256-pinned in `ansible/group_vars/all/r4_remix.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned disc | `ROMS_FINAL/psx-usa/R4 Ridge Racer Type 4 (US)/R4 Ridge Racer Type 4 (US).img` (Redump MD5 `bf1d92037b1b2be83b459c11f0b89eb6`, symlinked as `.bin` with a generated `.cue` next to `r4r.exe`) |
| Install root | `{{ dg_box_home }}/tools/r4-remix/` (`releases/0.1.0-cadc145/`, `current/`) |
| Saves & settings | `compatdata/r4-remix/pfx/drive_c/users/steamuser/Documents/R4R/` (`save.bin`, `settings.ini`) — backed up by `backup-saves` under `r4-remix` |
| Launcher | `{{ dg_box_home }}/bin/r4-remix` (host-side GE-Proton11-1; pass `--settings` to open `settings.exe`) |
| Desktop entry | **R4: Ridge Racer Type 4 (Remix)** (`r4-remix.desktop`) |

## Graphics & Performance

- `Documents/R4R/settings.ini` is seeded once (`force: false`, so `settings.exe`
  edits survive reruns) with `mode = advanced` (**Remaster**: path tracing, ray
  tracing, DLSS Ray Reconstruction, 16× anisotropic filtering), `backend = d3d12`,
  `fullscreen = borderless`, `vrr = auto`, `max_fps = auto`.
- The launcher exports `PROTON_ENABLE_NVAPI=1`, `DXVK_ENABLE_NVAPI=1`,
  `PROTON_HIDE_NVIDIA_GPU=0`, `VKD3D_CONFIG=dxr,dxr11`, and
  `VKD3D_FEATURE_LEVEL=12_2` with the NVIDIA Vulkan ICD pinned.
- Press **`~`** in-game to cycle between Original, Clean, and Remaster modes,
  and **F11** to toggle fullscreen. (Per upstream, Remaster path tracing
  currently covers Helter Skelter, Wonderhill, Out of Blue, and ~10 cars.)

## Gamepad Policy

Native XInput + DualShock 4/DualSense support (`gamepad = true`, `rumble = 100`
in `settings.ini`, `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1` in the launcher)
works out of the box with the 8BitDo Ultimate 2.
