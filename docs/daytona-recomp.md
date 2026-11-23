# Daytona USA (Xbox 360 / XBLA, 2011) — ReXGlue Recompilation

[springah/daytona_recomp](https://github.com/springah/daytona_recomp) is a
native static recompilation of the 2011 Xbox 360 / XBLA release of **Daytona
USA** built on ReXGlue and the native Vulkan `plume` renderer (instead of Xenos
GPU emulation).

## Install

```sh
cd ansible && ansible-playbook install-daytona-recomp.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `v1.1.7` (`Daytona-USA-Deck-v1.1.7.tar.gz`, SHA256-pinned in `ansible/group_vars/all/daytona_recomp.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/xboxlivearcade/DAYTONA USA/58410B1D/000D0000/80B8DCD51DE8B34C1513FFB1C66F3BE73B74823958` (XBLA `LIVE`/STFS package, SHA256 `db238145…`, read-only) |
| Install root | `{{ dg_box_home }}/tools/daytona-recomp/` (`v1.1.7/`, shared `assets/`, `daytona.ini`, `cache/`, `save/`) |
| Saves | `{{ dg_box_home }}/tools/daytona-recomp/save/` + `daytona.ini` — backed up by `backup-saves` under `daytona-recomp` |
| Launcher | `{{ dg_box_home }}/bin/daytona-recomp` (re-entrant into the `gaming` box; Vulkan NVIDIA ICD + `SDL_VIDEODRIVER=x11`) |
| Desktop entry | **Daytona USA (Recomp)** (`daytona-recomp.desktop`) |

## Graphics & Performance

`daytona.ini` is seeded once (`force: false`, so in-game **F4** / **Start+Select**
overlay edits survive reruns) and symlinked into the active release directory:

- **Output / Guest resolution**: `resolution = 3840x2160`, `fullscreen = true`,
  `game_resolution = 1280x720` (kept at 720p per upstream guidance), and
  `internal_resolution_scale = 3` (1280×720 × 3 = **3840×2160** native 4K).
- **Texture filtering**: `anisotropic_filtering = 16` (16× AF).
- **Frame rate & pacing**: `vsync = true`. The guest runs at a fixed **60 Hz**
  internal tick (`refresh_rate = 60` is ignored by upstream on purpose because
  changing it alters game speed).
- **Upscaler**: `bilinear` (at 3× internal scale on a 4K display, rendering is
  already 1:1 native 4K).
- **First launch**: upstream notes the first boot after a reboot can take up to
  a minute before the SEGA logo while assets stream in; subsequent starts take
  ~20 s.

## Gamepad Policy

Native SDL gamepad support works out of the box (including the 8BitDo Ultimate
2); the launcher exports `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`. Press
**Start + Select** (or **F4** on keyboard) in-game to open the settings overlay
and rebind controls or adjust display options.
