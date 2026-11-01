# 007 NightFire Recomp

[hk21x/nightfire-recomp](https://github.com/hk21x/nightfire-recomp) recompiles
the original Xbox release into two Windows executables. The port does not
include game data. Our opt-in role stages the pinned v1.0.2 build launcher,
checks the owned USA Xbox image, creates a dedicated Wine prefix, publishes
the menu entry, and checks that both executables were built.

## Owned game data

The current `dg_nf_iso` is `ROMS_FINAL/xbox/007 - Nightfire (USA)/007 - Nightfire
(USA).xiso.iso`. Its SHA256 is
`732868ed01692636f189c015609c5cb4f00f985053af33755a6b1a4e081448f8`.
Inside that image, the two XBE SHA-1 values are:

| File | SHA-1 |
|---|---|
| `default.xbe` | `7e4b8f8a54bacc61a5897ba5245fdd65bddc0752` |
| `Driving.xbe` | `8d46a023dfbd5c89d4ee04fe28b24a9620de546a` |

Both match the upstream USA release. The earlier GameCube copy and incomplete
`xbox-hdd-ready` extraction cannot supply these executables. On another
machine, override `dg_nf_iso` and its ISO checksum in host vars. The upstream
build launcher also checks the XBE SHA-1 values before building.

## Install and rebuild

```sh
cd ansible
ansible-playbook install-nightfire-recomp.yml
```

The upstream launcher is a Windows GUI. Choose the XISO in its **Your game**
section, review and accept the Microsoft C++ libraries and Windows SDK terms,
then press **Build**. The first build downloads its Windows build toolchain and
can take 30–90 minutes. The role reports an explicit incomplete-build error
until both `Nightfire.exe` and `NightfireDriving.exe` exist; rerun it after the
GUI build. Run `nightfire-recomp build` to reopen the build launcher later.
The game menu runs the compiled game when it is present.

The launcher copies the image into its `NightFire/play/assets` directory and
builds under `NightFire/` beside the launcher. It keeps saves in `play/hdd`,
settings in `play/settings.toml`, and logs in `play/logs`. The role seeds the
settings file only when absent. The save backup includes only the game's
`hdd/E/UDATA/45410026` title-data directory and `settings.toml`: `hdd/Z`
contains a 784 MB logical-size disc cache, which is reproducible and excluded.
The copied image, toolchain, source checkout, shader cache, and logs are also
excluded. Rebuilding the role does not clear player data.

Wine's built-in `d3dcompiler_47` rejected a D3D11 shader and left a black
window. The role stages both checksum-pinned native DLLs used by winetricks,
installs them in this prefix, and sets the native override. A second launch
rendered the EA intro without the shader error.

WineD3D then rendered the intro at roughly 15–16 FPS despite the 5090. The
role pins DXVK v3.1.1 for this prefix, translating D3D11 to Vulkan. The log
then identified the RTX 5090 and showed 592 frames in a 10-second intro sample
with two frames over the 25 ms pacing threshold. This is a measured intro
sample, not an in-game FPS guarantee.

## Display and controller

The seeded settings request a 3840×2160 fullscreen display, 100% native render
scale, 16× anisotropic filtering, 8× MSAA, 50% sharpening, and Direct3D 11
for Wine. Exclusive fullscreen directly under Wine failed with an XRandR
`BadValue`; the game launcher therefore uses a 3840×2160 fullscreen gamescope
display. The game log confirmed a 3840×2160 window and MSAA 8×. VSync is
enabled with a 120 FPS cap; this cap does not force a higher game speed.
Upstream says the game itself paces menus at 60 FPS and races at 30 FPS.

The port has native SDL controller input, hot plugging, and rumble. It supports
Xbox, PlayStation, and Switch pads. The 8BitDo Ultimate 2 should be presented
through Wine's SDL-backed XInput path; the role enables Wine's SDL mapping and
suppresses duplicate raw devices in its dedicated prefix. The
launcher must be tested in gameplay to establish the final mapping. F1 (or
Back + Start on the pad) opens the settings overlay, including controls.

The on-foot executable reached the start screen and handed off to
`NightfireDriving.exe`, but play beyond that transition remains unverified.
