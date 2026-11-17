# Sega arcade racing series — REA launcher

[akitaonrails/rea-teknoparrot-sega-series](https://github.com/akitaonrails/rea-teknoparrot-sega-series)
is one hub for Sega's arcade racers. It uses open loaders only:
lindbergh-loader for OutRun 2 SP SDX, windowsarcadeloader for SEGA Rally 3,
SEGA Racing Classic and Daytona Championship USA, and Flycast for the linked
F355 Challenge 2 boards. No TeknoParrot.

```sh
cd ansible && ansible-playbook install-rea-sega.yml   # or site.yml --tags rea_sega
```

| | |
|---|---|
| Release | `v0.2.0` Linux tarball (731 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/rea-sega/SegaRacingLauncher-0.2.0-linux-x86_64/` |
| Data | `~/.local/share/rea-sega/` — `launcher.cfg`, `settings/`, `runtimes/` saves/logs, Wine prefix |
| Library | `EmuDeck/roms_rare/TeknoParrot` |
| BIOS | `EmuDeck/Emulation/bios` (F355's `dc/f355bios.zip`, Chihiro files) |
| Launcher | `bin/sega-racing`; entry **Sega Arcade Racing · REA** |

## What runs

| Game | Loader | State |
|---|---|---|
| OutRun 2 SP SDX | lindbergh-loader | ready |
| SEGA Rally 3 | windowsarcadeloader | ready |
| SEGA Racing Classic | windowsarcadeloader | ready |
| Daytona Championship USA | windowsarcadeloader | ready |
| F355 Challenge 2 | Flycast (two linked boards) | starts; wheels not set up |
| OutRun 2 SP Special Tours | Chihiro | not yet (emulator being brought up) |
| Crazy Taxi High Roller | Chihiro | not yet (emulator being brought up) |

`--list`/`--check` report the same. F355 can restart itself once or twice while
its two boards find each other.

## Settings

Per-game settings live in `~/.local/share/rea-sega/settings/<game>.cfg`. The
launcher offers Look (original / recommended / steam_deck), game render size,
output size, FSR/NIS/linear/nearest upscaling, sharpness, fullscreen, steering
lock (270° default), force feedback and stick dead zone. Pads: left stick
steers, triggers are pedals, shoulders shift, Y changes view, B is the SEGA
Rally 3 handbrake, Start/A start, Back coins.

## Verified here

- `sega-launcher --list` finds all seven dumps: four ready, F355 starts, the
  two Chihiro titles are explicitly not yet.
- The hub opens (window class `rea-sega`) and the role reruns `changed=0`.
- A race was not driven during this install; upstream records full races for
  OutRun 2 SP SDX, SEGA Rally 3, SEGA Racing Classic and Daytona on Linux.
  Wheel force feedback and F355 controls remain unverified here.

## Updating

Bump `dg_sega_version`, asset and SHA256 in `group_vars/all/rea_sega.yml`, then
re-run. `launcher.cfg`, settings and `runtimes/` saves are kept. Revert with
`-e dg_sega_revert=true`.