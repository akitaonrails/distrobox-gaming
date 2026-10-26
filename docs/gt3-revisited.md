# Gran Turismo 3 — GT3 Revisited

[matt-pulsipher/GT3-revisited](https://github.com/matt-pulsipher/GT3-revisited)
`0.3.0` is an open-source **reimplementation of the GT3 A-Spec engine** (not an
emulator): native Linux x86_64, Vulkan through SDL_GPU, and it reads your own
disc image directly at runtime — nothing is extracted or redistributed. This
sits alongside (not replacing) the [PCSX2 setup](gt3-pcsx2.md). Managed by
`install_gt3_revisited` / `install-gt3-revisited.yml`; runs in the gaming
distrobox.

## Game data

Our `roms_heavy/ps2/Gran Turismo 3 - A-spec (USA) (v1.10).iso` is the
**PBPX-95503 v1.10 NTSC** bundle disc — one of the two verified NTSC-U
releases (the role re-verifies with `gt3tool info`, which reports
`Status: verified`). Only `.iso` is read (no CHD).

## Status: the whole game is playable

GT Mode (dealers, garage, tuning, licenses, championships, endurance with pit
stops, endings), Arcade, 2-player split screen, AI, replays with TV cameras,
Replay Theater, Analyzer, movies, music — physics verified against the
original. Extras over the PS2: **online battle up to 6 players** (i.LINK
rebuilt for the internet — session codes, no port forwarding), quick race,
time trial with saved replays, widescreen/high refresh/MSAA/dynamic
resolution, mods, and **PS2 save import/export** (title menu → Load game →
FROM A FILE accepts PCSX2 cards/.psu; `gt3tool save-import/export` on the
command line — the NTSC-U `BASCUS-97102GAMEDATA` save).

## Baseline

`~/.local/share/GT3Revisited/GT3Revisited/config.ini` seeded once (later
Settings changes win): fullscreen, vsync, **MSAA 8**, render_scale auto with
dynamic resolution, uncapped (`limit_60fps = off` — the engine paces itself;
240 Hz display), update check off (the role pins versions). Launcher
`bin/gt3-revisited` passes the disc directly. In-game: **Select** on the title
menu (or the GT3R button) opens the reimplementation's own menu — settings,
controller setup (pads/wheels, remappable, adaptive triggers), mods, jukebox,
quick race, online.

## Notes

- F11 fullscreen, F12 screenshots (into the user data folder).
- Controller support is comprehensive (analog pressure, DualSense adaptive
  triggers, FFB wheels); input untested here — first launch is the
  verification step.
- The update prompt inside the game is disabled in the seeded config; bump
  `dg_gt3r_version` in the role instead (the ogm GitHub sweep reports newer
  releases).
