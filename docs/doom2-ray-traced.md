# Doom II: Ray Traced

The supported Linux setup uses the native
[PrBoom-Plus-RT fork](https://github.com/tomboylover93/prboom-plus-rt), not
GZDoom-RT under Proton. Install or refresh it with:

```sh
cd ansible
ansible-playbook install-prboom-plus-rt.yml
```

The focused playbook ensures the box and writable Steam-library mount, downloads
the pinned renderer, installs its runtime libraries inside the `gaming`
distrobox, builds a Doom II-specific RT data tree, seeds a persistent config,
installs controller translation, and publishes the `Doom II: Ray Traced`
desktop entry. It is also available from `site.yml` as the opt-in tags
`prboom_rt` and `doom_rt`.

## Why this is not GZDoom-RT

GZDoom-RT 1.0.2a reaches RTGL1 under Proton but then requires the Win32-only
Vulkan extension `VK_KHR_external_fence_win32`. The local test failed with
`RG_RESULT_ERROR_NO_VULKAN_EXTENSION`, and upstream's open Linux issue confirms
there is no supported native build. Keep that launcher retired.

PrBoom-Plus-RT `v2.6.1-rt1.0.7` is a native Linux Vulkan build. The playbook
pins `prboom-rt-1.0.7.tar.gz` to SHA256
`3a76049219a8c1e1c24ca1ae4f50dc4b885e63e4397536bb1aa91dfdae81e14b`
and never runs upstream's interactive root installer.

## Required owned data

The renderer does not include commercial Doom data. The role searches for
`DOOM2.WAD` below the Steam libraries derived from `dg_steam_root`,
`dg_external_usb_games_root`, and `dg_box_home`. An explicit legal copy can be
selected with `dg_prboom_rt_doom2_wad_source`; the role accepts different
legitimate IWAD revisions, verifies the `IWAD` header, and copies it into
persistent local data. It never downloads or commits an IWAD.

For the normal Steam layout, install or restore app 2280 (`DOOM + DOOM II`) in
the library at `dg_steam_root` or `dg_external_usb_games_root`, then rerun the
playbook. A library directory can be correctly mounted yet still contain no
`steamapps` data, so use the status command below rather than treating mount
visibility as proof that Doom is installed.

If Steam says the game is installed on a drive that is not connected, its
library metadata still assigns app 2280 to an absent old library. Either
reconnect that library and configure `dg_external_usb_games_root`, point
`dg_prboom_rt_doom2_wad_source` at its owned IWAD, or use Steam's Manage Storage
flow to remove the stale install record and install app 2280 into
`dg_steam_root`.

Doom II also needs rellik66's Creative Commons
[Doom II Lights 0.9 addon](https://www.moddb.com/mods/doom-lights-for-raytraced-prboom/addons/doom2-lights-for-prboomraytracing).
ModDB identifies `doom2rt-0.9.zip` as 285,803 bytes with MD5
`064349e6810812957d33009f67ab8b46`. The role additionally pins the verified
SHA256 `732c05a87b6dcf7ec73fee74871ac3e2f9b3770436df2c27abc00a8e5557bb9d`.
If the persistent cache is empty, put the official zip at
`dg_prboom_rt_addon_source`; the role fails closed on any mismatch.

## Display: gamescope is required (audio-but-no-window fix)

The launcher runs the renderer **nested in gamescope** (`gamescope -f -w W -h H
-- prboom-plus-rt … -window`), and focuses DP-1 first. This is not optional on
this Hyprland/NVIDIA host: launched directly, PrBoom-Plus-RT's game loop and
audio run but its Vulkan surface **never commits a frame to Hyprland's Wayland
WSI**, so no window ever maps — you hear the game but see nothing (it is *not*
off-screen; `hyprctl clients` shows no toplevel at all). Nested in gamescope the
renderer gets a real swapchain and presents into a normal Hyprland window.

gamescope inherits the desktop-entry's forced NVIDIA ICD
(`VK_ICD_FILENAMES=…/nvidia_icd.json`), so it renders on the RTX 5090 — the same
GPU Hyprland's compositor uses (`AQ_DRM_DEVICES=/dev/dri/card1`). That's why it
does **not** hit the iGPU-grab problem that forces Supermodel onto the native
path: here both the compositor and the game are already on the discrete GPU.
The launcher falls back to the native `-fullscreen` path only if `gamescope` is
missing (which won't present — install gamescope).

## Controller policy

PrBoom's built-in SDL joystick path only reads two axes and eight buttons, so it
cannot provide modern twin-stick controls or dependable trigger handling.
The launcher disables that legacy path and starts a per-game AntiMicroX uinput
profile instead:

- Left stick: WASD movement; right stick: mouse look.
- RT: fire; LT: walk while autorun is enabled.
- A: use/select; B and Start: menu/back; Y: RT flashlight.
- LB/RB: previous/next weapon; Back: automap.
- X: quicksave; L3: quickload; R3: fists/chainsaw.
- D-pad: menu arrows and classic movement/turning.
- Select+Start: clean exit through an evsieve Alt+F4 chord.

The default allowlist is inherited from `dg_pc_racing_gamepad_only`. The 8BitDo
Ultimate 2 must be connected in its 2.4 GHz/XInput mode so Linux exposes an
`event-joystick`; Bluetooth/HID-only mode is not sufficient. The remapper and
exit hook exist only for the lifetime of this game and do not alter global
desktop input.

## State and diagnostics

Versioned renderer files and generated override data live below
`dg_prboom_rt_root`. Config, saves, screenshots, the owned IWAD copy, and the
verified addon cache are separate persistent paths. Ansible seeds the config
only when absent because PrBoom rewrites it on a clean exit.

Run the live diagnostic inside the box:

```sh
doom2-rt status
```

It reports the renderer, Doom II metadata, owned IWAD checksum, Vulkan GPU, and
visible supported controllers. A complete launch requires all three readiness
lines plus a controller only if keyboard/mouse fallback is not desired.
