# Forza Motorsport (Xbox, 2005) — Redline Recompiled

[DivxPlays/redline-recompiled](https://github.com/DivxPlays/redline-recompiled)
is a static recompilation of the original Xbox **Forza Motorsport** (2005):
x86-32 code lifted to C and rebuilt as a 64-bit Windows program with a new
D3D11/12 + DLSS/FSR layer, 144 fps and ultrawide support.

**Status here: installed and working (2026-11-17).** The Windows game is built
with **Linux Zig** from the owned Rev 1 disc and played through **GE-Proton**;
the live game reaches its profile-select/title screens under Wine.

```sh
cd ansible && ansible-playbook install-redline-recomp.yml   # or site.yml --tags redline
```

| | |
|---|---|
| Release | `0.3.0` source/launcher zip (SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Disc | `ROMS_FINAL/xbox/Forza Motorsport (USA) … (Rev 1)/…iso`; its `Forza.xbe` SHA-1 is `e60a968e…` |
| Install | `tools/redline/` — sources, `game/` (extracted disc), `build/redline.exe`, `forza_recomp.dll`, saves |
| Build tools | Linux Zig 0.14.1 + a Python venv with Capstone 5.0.7 (`tools/redline/.venv`, `tools/zig-linux`) |
| Proton | GE-Proton 11-5 (`wineprefixes/redline-proton`), DXVK + Microsoft's native `d3dcompiler_47.dll` |
| Launcher | `bin/redline`; entry **Forza Motorsport · Redline** |

## How it runs

The release is a Windows/MSVC project with an optional `--zig` path. Its
launcher expects Windows' `tar.exe` to unpack its tools, which Wine does not
have, so the role builds the same sources directly:

- extracts the owned Rev 1 ISO with `extract-xiso` into `game/` (the `Forza.xbe`
  SHA-1 is checked);
- runs the package's `find_functions.py`, `oovpa_pp.py`, `find_symbols.py` and
  `lift.py` with a Python venv + Capstone;
- runs `tools/build.py --zig` with **Linux** Zig 0.14.1. Two small patches make
  the source build on Linux: `ZIG` comes from `REDLINE_ZIG`, and the job count
  no longer calls `ctypes.windll`.

The game's D3D11 shaders do not compile with Wine's built-in
`d3dcompiler_47.dll`; the role installs Microsoft's native DLL into the Proton
prefix and sets the override. Proton then supplies DXVK and Vulkan.

## Settings and controls

The role seeds `build/recomp.ini` at **1080i video mode, 2× render scale**
(3840×2160 internal), borderless fullscreen, 16:9, 16× anisotropic filtering
and no upscaler (native). The in-game Recomp Settings menu rewrites the file;
later changes survive. Pads follow the Xbox layout (RT/LT throttle/brake, stick
steer, shoulders gears, Y camera); keyboard controls are in `README.md`.

On this Wayland desktop Wine still reports a 1706×960 client window and
presents 1920×1080 guest frames; the 2× render scale is applied internally.
The game's own resolution setting is at its maximum (1080i/2×); a true 4K
swapchain needs a Wine/gamescope setup that reports the 3840×2160 desktop
without Xwayland's 1.5 scale.

Saves are in `hdd/Partition1/UDATA` beside the install (backed up as
`redline-recomp`).

## Verified here

- The Rev 1 disc was extracted and `Forza.xbe` matched the expected SHA-1.
- The full lift/build completed (`build/redline.exe`, `forza_recomp.dll`,
  `SDL3.dll`, DLSS/FSR DLLs).
- A bounded launch through GE-Proton reached **Redline Recompiled 0.3.0**
  and the in-game **Player Profile / Profile Select** screen, with audio
  initialized and frames rendering.
- A race, controller input, DLSS/FSR modes and the optional 4x texture pack
  were not exercised in this install.

## Updating

Bump `dg_redline_version` and the zip SHA in
`group_vars/all/redline_recomp.yml`, then re-run. The role rebuilds only when
`build/redline.exe` is absent; to force a rebuild remove `build/redline.exe`
(or the whole `build/` directory) and re-run. Revert with
`-e dg_redline_revert=true`; the disc and `hdd/` saves are untouched.