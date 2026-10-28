# Gravity Rush Remastered — native PC port

[LucaPazienza/gravityrush_pc](https://github.com/LucaPazienza/gravityrush_pc)
v0.1.9 is a native Windows x64 port of **Gravity Rush Remastered** (PS4): the
game's own x86-64 executable runs on the CPU, the PS4 system libraries are
reimplemented, and the graphics go through the shadPS4 Vulkan video core. No
emulator. Managed by `install_gravity_rush` / `install-gravity-rush.yml`, run
through GE-Proton like DriveClub and Azimuth.

## Game data (user-provided)

Needs the **unpacked European release `CUSA01113` v01.00** — an ISO is not
usable. On this box it already exists at
`roms_rare/ps4/CUSA01113` (9.2 GB: `eboot.bin`, `sce_module`, `sce_sys`,
`arc/*.psarc`, param.sfo `EP9000-CUSA01113_00-GRAVITYRUSHHDEU1`, 01.00). The
role refuses to install against anything else, because the port's resolution
and shadow patches are version-specific.

## Install / run

```sh
cd ansible
ansible-playbook install-gravity-rush.yml    # or site.yml --tags gravity_rush
```

Walker entry: **Gravity Rush Remastered · PC Port**; launcher
`/mnt/data/distrobox/gaming/bin/gravity-rush`. It pre-seeds the Proton
`%APPDATA%/gravityrush-launcher/settings.json` with the game folder and runs
`Gravity Rush.exe --play`, so the launcher window is skipped. Saves, screenshots
and the in-game menu settings live in `~/.local/share/gravity-rush`
(symlinked as `user/` into each release); keep that directory across updates.

## Baseline

One-time `gravityrush.ini` (marker `~/.local/share/gravity-rush/.dg-max-baseline`):
**3840×2160 output, DLSS Quality (×1.5 render scale)**, 4096 shadow map
(`shadow_quality=high`), 16× anisotropy, borderless, 60 Hz engine, unlimited
render rate with vsync, FPS counter on. The release bundles both `gow3_dlss.dll`
and `nvngx_dlss.dll`, so DLSS works under Proton; FSR 3.1
(`upscaler=fsr3`) is the one-click fallback in the launcher's Video page.
The in-game menu is **Insert** (or R3+L2): resolution, performance, FPS overlay.

## Status

Installed and configured 2026-10-24 — **not yet launched** (the operator was
using the GPU for other work). First-launch checks to do: the port prepares
`eboot.bin` and links `libc`/`libSceFios2` on first run (can take a minute),
DLSS initialises, saves work. Report problems with `user/last_run.log` and an
F12 capture.
