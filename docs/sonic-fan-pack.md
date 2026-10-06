# Sonic fan games: S3AIR, SMS Remake, Sonic XG, Sonic Galactic, Sonic Overture, Sonic Legends, Rush Rerun, Dimensions, Moon Facility, Fallen Star (Banjo-Kazooie moved to lighthouse.md)

Three installs from the 2026-09-04 batch (`docs/dkc-recomp.md` came the same
week — it's fan-port season).

## Controller + display notes (2026-10-04)

- **Wine games** all use the same WineBus recipe (DisableHidraw=1,
  DisableInput=1, Enable SDL=1, Map Controllers=1): the 8BitDo reaches the
  game as a single SDL/XInput device. The Clickteam games (Overture,
  Dimensions, Moon Facility) only import **winmm.dll** (legacy joystick API)
  — the same pad still works through Wine's shared bus, and keyboard + pad
  are live at the same time in these games by design (prompts may show
  keyboard icons even while the pad works).
- **Clickteam games run at gamescope's 240 Hz** under Wine (their own frame
  limiter doesn't engage), which makes "button held" conditions fire
  multiple times per physical press — e.g. Dimensions' tutorial dialog
  advancing twice on one A press. Fix: `--framerate-limit 60` added to
  `dg_*_gamescope_args` for Overture, Dimensions and Moon Facility (they are
  60 fps-designed 2D games, so the cap is visually lossless). If a dialog
  still double-advances, the next lever is `Map Controllers=0` in that
  game's prefix.
- **Max-settings audit**: Dimensions and Moon Facility have no exposed
  resolution/quality config worth forcing (2D pixel games; Moon's
  `Data/Data.ini` already ships SFX/BGM at 100, and its `Fullscreen=0` +
  gamescope integer scaling is the crispest path — do NOT set
  `Fullscreen=1`). Rush Rerun (Unity) takes the gamescope 4K display
  natively and keeps quality in its in-game menu (no prefs written until
  first launch; nothing safe to pre-seed).


## Sonic 3 A.I.R. (`install_sonic3air`)

[Eukaryot/sonic3air](https://github.com/Eukaryot/sonic3air) — "Angel Island
Revisited", the definitive Sonic 3 & Knuckles remaster on the Oxygen engine.
**Official native Linux build** (`sonic3air_game.tar.gz` from the stable GitHub
release, sha256-pinned, NAS-staged under `ROMS_FINAL/PC/sonic remake/`; the
`sonic3air_game.zip` downloaded from sonic3air.org is the *Windows* package).
**Requires the original Sonic 3 & Knuckles combined ROM** — the role stages the
box's standard 4 MiB dump (`Sonic and Knuckles & Sonic 3 (JUE) [!].bin`, sha1
`cfbf98c3…`) as `Sonic_Knuckles_wSonic3.bin` beside the binary; the game
verifies it and adopts it into `~/.local/share/Sonic3AIR/`. Verified: fullscreen
DP-1 on the RTX, log shows `Controller #1: "8BitDo Ultimate 2 Wireless
Controller"` (native). Launcher `bin/sonic3air`, Walker "Sonic 3 A.I.R.".
Mods go in `~/.local/share/Sonic3AIR/mods/`.

## Sonic SMS Remake (`install_sonic_sms_remake`)

[The Creative Araya's remake](https://sonic-sms-remake.blogspot.com/) of the
Master System Sonic 1 — 5 playable characters, no original data needed.
**GameMaker Windows exe, no Linux build exists** → wine-11.8 with the standard
recipe (UseEGL=N GLX pin, WineBus SDL for the 8BitDo), running inside a **4K
Wine virtual desktop**: its exclusive fullscreen otherwise renders in the
bottom-left corner of the panel (the Sega Rally Revo lesson; observed here
too). Source = the user's NAS zip (`v1-9-rev4_Sonic_SMS_Remake.zip`, single
exe inside). Launcher `bin/sonic-sms-remake`, Walker "Sonic SMS Remake".
Sonic 2 SMS and Sonic 3 SMS remakes exist on the same site — drop their zips
next to this one and clone the role data if wanted.

## Sonic XG (`install_sonicxg`)

[Sonic eXtended Genesis](https://sonic-xg.github.io/) — ULTRA RING's fan
project (with the original 2001/2012 devs' blessing): an alternate-take
Knuckles campaign acting as an epilogue to the Death Egg Saga. Currently the
**Time Attack Preview v1.2**. **Official native Linux AppImage** (GameMaker
runner), no ROM required. Distribution is Google Drive links off the download
page (no releases API) — the user stages the zip at
`ROMS_FINAL/PC/SonicXG_TA-Preview-V1.2-Linux.zip` and the role installs from
there; bump `dg_sonicxg_version` + `dg_sonicxg_zip` on upgrades (ogm
fingerprints the download page to badge new releases). FUSE for the AppImage
is covered by `fuse2`/`fuse3` in `packages.yml`. Like the others it launches
fullscreen via gamescope integer scaling (its GameMaker window is a fixed
small size; `scale` in `~/.config/Sonic_XG/options.txt` stays at default).
Saves/replays/options live in
`~/.config/Sonic_XG/` — `uuid.bin` there owns your best times, do not lose it.
Verified 2026-10-01: boots in the box, window on DP-1. Launcher
`bin/sonicxg`, Walker "Sonic XG".

## Sonic Galactic (`install_sonic_galactic`)

[Sonic Galactic](https://sonicgalactic.github.io/) — fan-made classic-Sonic
homage on the Hatch engine, **Demo 2 patch 1**. **Windows-only build** (an M1
Mac build exists, no Linux) → wine-11.8 with the standard recipe (UseEGL=N GLX
pin, WineBus SDL for the 8BitDo) presented **fullscreen via gamescope integer
scaling** (`dg_sonicgalactic_gamescope_args`), which also subsumes the old
Wine-virtual-desktop corner-render fix. Source = the user's NAS zip
(`ROMS_FINAL/PC/sonicgalactic-demo2-patch1-win.zip`, `SonicGalactic.exe` +
`Data.hatch` inside). Bump `dg_sonicgalactic_version` + `_zip` on new demos;
ogm fingerprints the download page. Verified 2026-10-01: boots under Wine and
stays up. Launcher `bin/sonic-galactic`, Walker "Sonic Galactic".

## Sonic Overture (`install_sonic_overture`)

[Sonic Overture](https://sonic-overture-team.itch.io/sonic-overture-2023-demo)
— Sonic Overture Team's fan-made classic-Sonic game on Clickteam Fusion 2.5
(mmf2d3d9.dll, .mfx modules), **2023 demo** (`Overture95_Demo_v1`).
**Windows-only** → wine-11.8, same recipe as Galactic (UseEGL=N GLX pin,
WineBus SDL, gamescope integer-scaled fullscreen). Source = the user's NAS rar
(`ROMS_FINAL/PC/Overture95_Demo_v1.rar`; top-level `Overture95_Demo_v1/`
folder with `SonicOverture95.exe` inside). itch has no releases API — ogm
fingerprints the itch page. Verified 2026-10-01: boots and runs under Wine
(smoke-test note: `pgrep -x` can't match `SonicOverture95.exe` — Linux
`comm` truncates to 15 chars — use `pgrep -f` or the truncated name).
Launcher `bin/sonic-overture`, Walker "Sonic Overture".

## Sonic Legends (`install_sonic_legends`)

[Sonic Legends Trial Version](https://ultra-ring.itch.io/sonic-legends-trial-version)
— ULTRA RING's other fan-made classic-Sonic game (same circle as Sonic XG),
on GameMaker Studio 2 (`data.win`, `.vsh` shaders). **Windows-only** →
wine-11.8, same recipe as Galactic/Overture (UseEGL=N GLX pin, WineBus SDL,
gamescope integer-scaled fullscreen). Source = the user's NAS zip
(`ROMS_FINAL/PC/Sonic Legends.zip`, files at zip root — note the exe name has
a space). itch has no releases API — ogm fingerprints the itch page.
Verified 2026-10-01: boots and runs under Wine. Launcher
`bin/sonic-legends`, Walker "Sonic Legends".

## Sonic Rush Rerun (`install_sonic_rush_rerun`)

[Sonic Rush Rerun](https://gamejolt.com/games/sonicrushrerun/1030374)
— fan reimagining of the Nintendo DS Sonic Rush, on **Unity**
(MonoBleedingEdge + FMOD). **Anniversary Demo** (Sonic Rush 20th
anniversary, the newest demo as of 2026-10). **Windows-only** → wine-11.8,
same recipe as Galactic (UseEGL=N GLX pin, WineBus SDL, gamescope
integer-scaled fullscreen). Source = the user's NAS rar
(`ROMS_FINAL/PC/sonic-rush-rerun-anniversary-demo.rar`; top-level
`Sonic Rush Rerun/` folder, exe `Sonic Rush Rerun.exe`). GameJolt has no
releases API — ogm fingerprints the GameJolt page. Launcher
`bin/sonic-rush-rerun`, Walker "Sonic Rush Rerun".

## Sonic Dimensions (`install_sonic_dimensions`)

[Sonic Dimensions](https://www.deviantart.com/phantom-radea/art/Sonic-Dimensions-5-1-1-In-Development-5-1-0-DEMO-963814256)
— Phantom-Radea's 2D Sonic fangame on **Clickteam Fusion** (supersound.dll).
**5.1.0 demo** — the newest public build (5.1.1 in development per the same
DeviantArt post, which is the canonical distribution page). **Windows-only**
→ wine-11.8, same recipe (UseEGL=N GLX pin, WineBus SDL, gamescope
integer-scaled fullscreen). Source = the user's NAS rar
(`ROMS_FINAL/PC/Sonic Dimensions 5.1.0.rar`; top-level `Sonic Dimensions/`
folder, exe `Sonic Dimensions 5.1.0.exe` — note the exe name embeds the
version, so a future 5.1.1 update needs `dg_sonicdimensions_exe` bumped).
ogm fingerprints the DeviantArt page. Launcher `bin/sonic-dimensions`,
Walker "Sonic Dimensions".

## Sonic and the Moon Facility (`install_moon_facility`)

[Sonic and the Moon Facility](https://gamejolt.com/games/sonicmoonfacility/975042)
— StarDrop's 2D Sonic fangame on **Clickteam Fusion 2.5** (mmf2d3d9.dll,
.mfx modules). The project was **cancelled**; the ~90%-complete final build
(2025-02-10, "Final 2") is what we install — no further updates expected.
**Windows-only** → wine-11.8, same recipe (UseEGL=N GLX pin, WineBus SDL,
gamescope integer-scaled fullscreen). Source = the user's NAS zip
(`ROMS_FINAL/PC/sonic-and-the-moon-facility-last-build.zip`; top-level
`Sonic and The Moon Facility (Final 2)/` folder, exe
`Sonic and The Moon Facility.exe`). ogm fingerprints the GameJolt page.
Launcher `bin/moon-facility`, Walker "Sonic and the Moon Facility".

## Sonic and the Fallen Star (`install_sonic_fallen_star`)

[Sonic and the Fallen Star](https://stardropsmh.github.io/sonic-and-the-fallen-star/)
— StarDrop's acclaimed classic-Sonic fan game (SAGE 2022), the same dev and
engine as Moon Facility: **Clickteam Fusion 2.5** (`mmf2d3d9.dll`, `.mfx`
modules). We install the **V1.1.1 Edit 4** community build. **Windows-only** →
wine-11.8, same recipe as the other Clickteam games (UseEGL=N GLX pin, WineBus
SDL for the 8BitDo, **gamescope integer-scaled fullscreen capped at 60 fps** via
`dg_fs_gamescope_args` — the cap stops the Fusion runtime's 240 Hz held-button
double-fire). Source = the user's NAS zip
(`ROMS_FINAL/PC/Sonic and the Fallen Star (V1.1.1 Edit 4).zip`; a version-named
top-level folder holds `Sonic and the Fallen Star.exe` + `.dat` + `Modules/`).
Bump `dg_fs_version` + `_zip` (+ `_subdir`) on new builds; ogm fingerprints the
project page. Launcher `bin/sonic-fallen-star`, Walker "Sonic and the Fallen
Star". Install: `ansible-playbook install-sonic-fallen-star.yml`.

## Banjo-Kazooie

Moved to its own page — Banjo-Kazooie now runs on **Lighthouse**, HarbourMasters'
libultraship PC port (the old BanjoRecomp recompilation was replaced). See
[docs/lighthouse.md](lighthouse.md).
