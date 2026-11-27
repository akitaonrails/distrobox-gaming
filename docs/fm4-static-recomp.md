# Forza Motorsport 4 — Static Recompilation (`i2kiselev/fm4-static-recomp`)

[i2kiselev/fm4-static-recomp](https://github.com/i2kiselev/fm4-static-recomp)
is a ShiftGlue + Vulkan static recompilation of **Forza Motorsport 4** (Xbox
360, supports both 1.0 and Rev 1 discs) with live 1×–4× resolution scaling,
60–240 FPS, DLSS/DLAA/FSR 2/3/4 upscaling, in-game PC OPTIONS (`BACK+START` or
`F6`), and Disc 2 / DLC support. It installs **alongside**
[hl360-forza4](fm4-hl360.md) and runs from the host through **GE-Proton11-1**.

## Install

```sh
cd ansible && ansible-playbook install-fm4-static-recomp.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `v0.3.3` (`FM4StaticRecomp-Launcher-v0.3.3.zip`, SHA256-pinned in `ansible/group_vars/all/fm4_static_recomp.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned discs | Symlinked into `tools/fm4-static-recomp/discs/` (`fm4-disc1.iso`, `fm4-disc2.iso`) from your USA Rev 1 ISOs |
| Install root | `{{ dg_box_home }}/tools/fm4-static-recomp/` (`releases/v0.3.3/`, `current/`, persistent `data/`) |
| Saves | `tools/fm4-static-recomp/data/profiles/` — backed up by `backup-saves` under `fm4-static-recomp` |
| Launcher | `{{ dg_box_home }}/bin/fm4-static-recomp` (host-side GE-Proton11-1 → `FM4StaticRecompLauncher.exe`) |
| Desktop entry | **Forza Motorsport 4 (Static Recomp)** (`fm4-static-recomp.desktop`) |

## First-Time Setup (Interactive GUI Step)

Because upstream does not redistribute translated game code or Microsoft's
compiler headers, the first launch of `FM4StaticRecompLauncher.exe` runs a
guided setup (~10 minutes):

1. Launch **Forza Motorsport 4 (Static Recomp)** (or `fm4-static-recomp`).
2. Point Setup at `Z:\mnt\data\distrobox\gaming\tools\fm4-static-recomp\discs\fm4-disc1.iso`
   (and optionally `fm4-disc2.iso` under **CONTENT** after setup).
3. Accept Microsoft's C++ runtime & Windows SDK licences so the launcher can
   download the ~300 MB toolchain and compile your `default.xex` into `data/`.
4. On the first launch of the built game, wait for **Preparing shaders** to
   finish (progress saves every 10 s).

## Graphics & Performance (RTX 5090 4K)

Settings are configured in the launcher's **SETTINGS** page or live in-game via
**BACK + START** (or **F6** → **PC OPTIONS → GRAPHICS**, then **Y** to Save &
Apply):

- **Preset**: **Ultra** (or **Experimental** for 4× Race MSAA + scenery shadows)
- **Resolution Scale**: `3x` (3840×2160 native 4K)
- **Upscaler**: **DLSS** (acts as **DLAA** at 3× on a 4K display, preset `Auto`
  or `K`) — or **Off** with 4× MSAA + 16× AF
- **Frame Rate**: `120`–`240` FPS (matching display refresh), **VSync** `Off`
  with VRR/G-Sync (or `On` if tearing appears)

## Gamepad Policy

Native XInput support works out of the box with the 8BitDo Ultimate 2; the
launcher sets `WINEDLLOVERRIDES="windows.gaming.input=d"` (avoiding Wine's
broken `Windows.Gaming.Input` enumeration) and
`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`.
