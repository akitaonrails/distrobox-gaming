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

## Mods

The in-game **Mods** screen (main menu → Mods) installs mods from a `.zip`
(**Install from .zip**, or drop the `.zip` on the window), and toggles or
removes them. Unzipped mod folders can also be dropped straight into the
user data folder, which on this box is
`~/.local/share/GT3Revisited/GT3Revisited/mods/` (per upstream
[MODDING](https://github.com/matt-pulsipher/GT3-revisited/blob/master/docs/MODDING.md)).

What a mod can do today: **replace any file from `GT3.VOL`** (menus, models,
courses, sounds, databases, movies), **replace music tracks** (`.ads`), and
**add new cars** — small `cars/*.ini` files, optionally with their own glTF
body and a new maker/dealer page, electric drivetrains included.

Where to get mods (checked 2026-10-28): **nowhere public yet.** The project is
days old; Discussions has no mod-sharing category and no third-party mods are
posted. The one complete mod is upstream's own template,
[`examples/mods/example_coupe`](https://github.com/matt-pulsipher/GT3-revisited/tree/master/examples/mods/example_coupe)
(a Tesla Model Y Performance built as a copy-and-edit example — download the
folder, zip it, install it). When a mod scene appears it will most likely live
in that repo's Discussions.

**HD textures: not supported, and not wired here.** The port has no
hash-keyed PNG texture replacement yet — upstream lists "PNG texture
replacement packs keyed by decoded-texture hash" as *planned*, and texture
modding today means re-encoding the game's own `.img` texture files (Tex1;
a PNG import tool is also planned). PCSX2-style HD packs therefore **cannot**
be reused: the `textures/SCUS-97102` dir this box has for PCSX2 is an empty
skeleton (0 files — no GT3 pack was ever staged, unlike GT4's). Revisit when
upstream ships the PNG pack feature.

### Easy mode: the prize-multiplier mod (installed)

`dg_gt3r_prize_multiplier` (default **10**) ships a mod the role generates
itself: `gt3tool` extracts `database/paramdb_us.db` from your own disc,
`scripts/gt3r-prize-patch.py` multiplies every event's six place prizes
(`+0x1D4`) and championship bonus (`+0x1E2`) in place — same file size, clamped
to the u16 ceiling — and the result lands in
`~/.local/share/GT3Revisited/GT3Revisited/mods/dg-prize-multiplier/` as
**Prize Multiplier x10** (folder mods are enabled by default; the game log
confirms it at launch). 338 of 454 events carry prizes; a 50,000 Cr
championship first prize becomes 500,000 Cr. Changing the variable regenerates
the mod on the next run; `1` removes it. Nothing extracted from the disc is
committed — only the patch script is in the repo.

## Notes

- F11 fullscreen, F12 screenshots (into the user data folder).
- Controller support is comprehensive (analog pressure, DualSense adaptive
  triggers, FFB wheels); input untested here — first launch is the
  verification step.
- The update prompt inside the game is disabled in the seeded config; bump
  `dg_gt3r_version` in the role instead (the ogm GitHub sweep reports newer
  releases).
