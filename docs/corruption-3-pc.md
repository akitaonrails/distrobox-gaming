# Metroid Prime 3: Corruption — Corruption_3 PC (parked)

[bonllavier/Corruption_3-PC](https://github.com/bonllavier/Corruption_3-PC) is a
**Windows-only static recompilation** of Metroid Prime 3 (Wii USA, `RM3E01`):
the game's code runs natively, with Aurora/WebGPU rendering (per-pixel lighting,
enhanced materials, ambient occlusion, reflections, MSAA), keyboard/mouse and
gamepad control, RetroAchievements and save states.

**Status on this box: parked (2026-11-11), not installed.** The prebuilt
`v0.1.6` Windows ZIP unpacks and starts under Wine, but cannot render:

- With `graphics_api = "auto"` (and `"vulkan"`), Dawn falls back to the **Null
  backend** and aborts on `Surface.Configure()`:
  `Usages requested … not supported by the adapter ([Adapter "Null backend"])`.
- With `graphics_api = "d3d12"` plus **vkd3d-proton 3.1** installed in the
  prefix, the port gets further — it opens the ISO (`RM3E01`), publishes the
  FST, installs the DXGI frame-latency hook — then crashes with an SEH in the
  recompiled runtime (`reason: seh`, zero guest registers).

The release contains no source (the repository has only docs and a release
workflow), so there is no Linux build to make; and the Windows executable needs
a real Windows 10/11 D3D12/Vulkan stack, not Wine's.

## What does work

The owned disc image is in the library and **Dolphin** is installed:

```
EmuDeck/roms_heavy/wii/Metroid Prime 3 - Corruption (USA)/Metroid Prime 3 - Corruption (USA).iso
```

ES-DE → Wii plays it with the shared Dolphin setup, including gamepad and the
emulator's own enhancements. That is the supported path here until the port
runs under Wine or a Linux build appears.

## If revisiting

Re-test with a newer Dawn/vkd3d-proton and Wine, or on real Windows. The
renderer must create a non-Null adapter for either backend; the save/config
layout (`UserData/Config.toml`, `[paths] iso_path`) is documented in the
upstream `Config.default.toml` and `docs/`.