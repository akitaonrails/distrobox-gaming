# Colin McRae Rally (1998) — Modern Reconstruction (Recomp)

[akitaonrails/rea-colin-mcrae-recomp](https://github.com/akitaonrails/rea-colin-mcrae-recomp)
is a clean-room native Rust reconstruction of the 1998 EU PC release of
*Colin McRae Rally* using SDL3 (windowing, audio, gamepad) and a hardware
`wgpu` renderer (with a bit-exact software C3D reference rasterizer as
fallback). It installs **alongside** the Wine-based
[REA Colin McRae Rally launcher](colin-mcrae-rally-1.md) without modifying it or
the read-only game source.

## Install

```sh
cd ansible && ansible-playbook install-rea-colin-mcrae-recomp.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `v0.1.8` (`Colin-McRae-Rally-Modern-v0.1.8-x86_64.AppImage`, SHA256-pinned in `ansible/group_vars/all/rea_colin_mcrae_recomp.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/CMRally` (`Rally.exe` SHA256 `46500c8e…`, read-only) |
| Install root | `{{ dg_box_home }}/tools/rea-colin-mcrae-recomp/` |
| Imported runtime data | `{{ dg_box_home }}/tools/rea-colin-mcrae-recomp/runtime-data/installed-eu-derived-assets-v2/` plus all 11 sibling `official-eu-*` executable-backed table stores |
| Saves & settings | `runtime-data/installed-eu-derived-assets-v2/save/` (`cmRally.cfg`, `modern.cfg`, championship slots) — backed up by `backup-saves` under `rea-colin-mcrae-recomp` |
| Launcher | `{{ dg_box_home }}/bin/rea-colin-mcrae-recomp` (re-entrant into the `gaming` box with `APPIMAGE_EXTRACT_AND_RUN=1`) |
| Desktop entry | **Colin McRae Rally Modern (Recomp)** (`rea-colin-mcrae-recomp.desktop`) |

## Graphics & Performance

The role seeds `save/modern.cfg` once (`force: false`, so in-game edits survive
reruns) to the **Ultra 4K** preset:

- **Resolution / Aspect**: `3840×2160` (`resolution=6`), `16:9 WIDE` (`aspect_ratio=1`)
- **Frame rate & pacing**: `144 FPS` cap (`fps_limit=4`, decoupled from the 25 Hz
  fixed-point physics tick via continuous Q16 sub-tick pose interpolation) with
  `vsync=1` so presentation paces cleanly to the display refresh rate
- **Draw distance**: `3.0× Ultra` (`draw_distance=4`)
- **Texture filtering**: `Anisotropic 16×` (`texture_filter=4`)
- **Anti-aliasing**: `MSAA 4×` (`msaa=2` — the highest MSAA sample count
  supported by `wgpu`)
- **Upscaling**: `CAS Sharpening` (`upscaling=4`, 1.0× native render scale)
- **Renderer**: `--renderer auto` with the NVIDIA Vulkan ICD pinned via
  `VK_ICD_FILENAMES`
- **Fullscreen**: Press **F11** in-game to toggle fullscreen (not a CLI flag).

### Optional HD Art Pack

When the sibling `rea-colin-mcrae` HD texture pack (`hd/pack.txt`) is already
extracted under `dg_cmr1_release_dir`, the role symlinks it to
`runtime-data/installed-eu-derived-assets-v2/hd-pack` (otherwise it unpacks
`hd/` from the staged `CMRLauncher` archive if present) and enables `hd_art=1`
in `save/modern.cfg`. At resolutions above 1080p the engine automatically
selects the `x4` textures. You can toggle it in-game under
**Options → Graphics → Advanced → HD ART PACK**.

## Gamepad Policy

Native SDL3 gamepad support is enabled by default (`modern_gamepad=1`,
`rumble=1`), and the launcher sets `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`.
Both gamepad and keyboard remain active simultaneously in menus and on stage
(8BitDo Ultimate 2 works out of the box without any bridge or DLL override):

- **Menus**: D-Pad / Left Stick to navigate, `A` or `Start` to confirm, `B` or
  `Back` to cancel
- **Driving**: Left Stick / D-Pad to steer, `RT` accelerate, `LT` brake/reverse,
  `B` handbrake, `RB`/`LB` shift up/down, `Y` camera, `Start`/`Back` pause

## CLI Helpers

```sh
rea-colin-mcrae-recomp --version          # verify AppImage binary inside the box
rea-colin-mcrae-recomp                    # launch the game
```
