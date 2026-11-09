# Super Mario All-Stars — PC port (Darhkfox)

[Darhkfox/SuperMarioAllStars](https://github.com/Darhkfox/SuperMarioAllStars) is
a native C++ port of the 1993 SNES collection (Super Mario Bros., The Lost
Levels, Super Mario Bros. 2, Super Mario Bros. 3) that runs from the owned USA
ROM. It ships a **Linux AppImage** (bundled SDL2), so there is no build and no
Wine.

```sh
cd ansible && ansible-playbook install-smas.yml     # or: site.yml --tags smas
```

| | |
|---|---|
| Release | `v1.1.1` — `SuperMarioAllStars-Linux-x86_64.AppImage` (3.2 MB, SHA256-pinned, staged in `ROMS_FINAL/PC/ports/smas-port/`) |
| ROM | `ROMS_FINAL/snes/Super Mario All-Stars.smc` — the 1993 USA dump, CRC32 `925637c7` (upstream's supported file; other dumps run with the launcher warning amber) |
| Install | `tools/smas-port/v1.1.1/` (unpacked AppImage); the ROM is linked beside the binary as `usr/bin/Super Mario All-Stars (USA).sfc` |
| State | `~/.local/share/SuperMarioAllStars/` — `smas_port.ini`, `saves/` (`smas.srm` battery + save states), `achievements.ini` |
| Launcher | `bin/smas`; entry **Super Mario All-Stars · PC Port** |

The box has no FUSE, so the AppImage is unpacked once (`--appimage-extract`) and
the launcher runs the extracted binary with the bundled SDL2 on
`LD_LIBRARY_PATH`, pinned to the NVIDIA GLX vendor. Presentation goes through
gamescope at **3840×2160 / 60 Hz**: without it the port opened on the portrait
4K output and paced against the 240 Hz mode (`0 refreshes per frame` in its
log); under gamescope it reports `3840x2160`, `60.00 Hz display, 1 refreshes
per frame`. The port only looks for the ROM beside the binary, in `roms/`
beside it and in a few parent folders — a `roms/` folder three levels up was
ignored, so the link sits in `usr/bin/`.

## What it adds over a plain emulator

- **True widescreen**: 4:3, 16:10, 16:9, 21:9 or auto, revealing more of each
  level sideways; HUDs re-anchored to the edges, the SMB2/SMB3 areas that wrap
  at the 4:3 edge dimmed, widescreen enemy spawns, and a pillarbox fill for the
  menus and 4:3 screens.
- **Simultaneous two-player co-op** — the SNES original alternates turns.
- Save states with checksums, **rewind**, fast-forward, level select, cheats,
  an achievements system, a music player and MSU-1 custom soundtracks, CRT /
  slang shader presets, screenshots.

## Settings

`dg_smas_settings` seeds `smas_port.ini` once (the game rewrites it, so later
in-game changes survive): fullscreen, 16:9-by-auto, VSync, the widescreen
HUD/enemy/dim options on, and **no per-scanline sprite limit**. The daily
GitHub update check is off; **Options › Updates** re-enables it.

## Controls

Native SDL2 gamepads (8BitDo and other controllers) for players 1 and 2, plus
keyboard. The in-game options cover pad bindings, menu button swap (Xbox /
Nintendo layout), dead zone and analog touch controls. Not exercised here: no
controller was connected during the install.

## Previous install (retired)

TanookiStudios' **recompilation** (`install_smas_recomp`) used to occupy this
entry. It had no widescreen — only aspect stretch/letterbox — and required the
2010 *25th-Anniversary* ROM from the Limited-Edition Wii disc. Its files are
left on disk, unlinked, at `tools/smas-recomp/` (no saves were created there);
delete that directory whenever you like. The recovered 25th-Anniversary ROM
stays in `roms_mid/snes/` and the recovery script in `scripts/` is untouched.

## Verified here

The launcher opens at 3840×2160 through gamescope with the dump recognised
(`✓ Super Mario All-Stars (USA).sfc`) and 60 Hz pacing; the role rerun is
`changed=0`. A full play session, two-player co-op and the shader presets were
not exercised.

## Notes

- The port's own code is MIT; librashader MPL-2.0; shader presets GPL-2.0/public
  domain. No game data is included — the ROM is your own dump.
- Battery saves and states live in the XDG data dir and are mirrored by
  `dg_save_sets` as `smas`.