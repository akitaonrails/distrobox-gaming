# Super Hang-On Ultimate

[chaotix359/Super-Hang-On-Ultimate](https://github.com/chaotix359/Super-Hang-On-Ultimate)
is a native recompilation of the arcade **Super Hang-On** (System 16) with the
Mega Drive **Original Mode** modded in. One C source tree builds the Windows,
macOS and Linux versions; Linux uses SDL2 and is built here from the pinned tag
(the DKC / F-Zero pattern), because upstream publishes installers for Windows
and macOS only.

```sh
cd ansible && ansible-playbook install-super-hang-on-ultimate.yml   # or site.yml --tags super_hang_on
```

| | |
|---|---|
| Source | `v0.9.32`, commit `e1258f7e…` |
| Build | `~/.cache/super-hang-on-ultimate-build/src` (reused on version bumps) |
| Install | `tools/super-hang-on-ultimate/` — `SuperHangOn`, both ROMs, manuals, icon |
| Arcade ROM | `ROMS_FINAL/arcade/fbneo/shangon.zip` (MAME `shangon`, unprotected), sha256 `5e2f962b…` |
| Mega Drive ROM | `ROMS_FINAL/genesis_2/Super Hang-On/Super Hang-On (W) (REV01) [!].gen` (World Rev A), sha256 `005979c7…` |
| Launcher | `bin/superhangon`; entry **Super Hang-On · Ultimate** |

## Build

The role clones the pinned tag, runs `setup.py` to translate the arcade program
ROM into C, then `build.sh linux`. `setup.py` ends with `SUCCESS` (1200 frames
matched against the reference), and the Linux build repeats the 1200-frame
self-test and prints `Self-test PASSED`. The ROM stays in the build tree as
`shangon.zip` and is copied into the game folder for the port to verify and
load at run time.

No recompiled game code is committed: it is generated from the owned ROM on
this machine and kept private.

## Game folder and settings

`tools/super-hang-on-ultimate/` is the game folder. It holds `shangon.zip`, the
Mega Drive ROM, `shangon.ini`, `shangon.nv` (the arcade EEPROM and high scores),
the Original Mode saves and the optional `music/` folder for arranged MP3s.
Everything is written next to the binary, so backups and updates are stable.

The role seeds `shangon.ini` once with:

- **fullscreen=1**, **16:9**, sharp-bilinear filtering, vsync on, no stretch;
- **Mega Drive enhancements=1**, so **ORIGINAL MODE** appears on the title
  screen (the Mega Drive ROM supplies its screens, courses and rival data);
- the settings screen skipped (`show=0`); the launcher passes `-play`.

The in-game settings screen and the launcher's options rewrite the file; later
changes survive role reruns. F9 cycles fit/16:9/4:3, F8 cycles the filter,
F11/Alt+Enter toggles fullscreen.

## Controls

Steer with the left stick or D-pad (arcade steering), A/RT accelerate, B/LT
brake, X/LB or Space turbo, Start for coin/start, Back for pause. F3 returns to
the title, F2/9 open test/service. The Mega Drive "controls" option can switch
both modes to the virtual handlebar; the seeded value keeps the arcade's own
steering. SDL handles Xbox, PlayStation, Switch Pro, 8BitDo and similar pads;
an unknown pad can use `gamecontrollerdb.txt` in the game folder or a
`[pad] map=` entry.

## Verified here

- `setup.py`: `SUCCESS` (1200 frames identical to the reference).
- `build.sh linux`: `Self-test PASSED: 1200 frames identical to the reference`.
- Bounded `bin/superhangon` launch: borderless fullscreen at 3840×2160, **16:9**
  (`16:9 428`), sharp-bilinear, **MD Enhancements** active, title/attract
  running on the RTX.
- Role rerun `changed=0`; OGM, launcher-wrapper, desktop-file and PC-layout
  checks clean.
- Physical pad input, a full race, Original Mode progression, arranged MP3s
  and the test/service menus were not exercised during this install.

## Updating

Bump `dg_sho_version` and `dg_sho_commit` in
`group_vars/all/super_hang_on_ultimate.yml`, then re-run. The build script runs
`setup.py` and the self-test again; `shangon.ini`, the EEPROM and the saves are
preserved. Revert with `-e dg_sho_revert=true`.