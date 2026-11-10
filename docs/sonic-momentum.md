# Sonic Momentum (Beta Edition, SAGE 2024)

[Sonic Momentum](https://sonicfangameshq.com/forums/showcase/sonic-momentum-beta-edition.2324/)
is a **GameMaker Studio 2** fan game remixing Sonic Frontiers' cyberspace
stages around momentum-based movement (Sonic Advance/Rush style tricks and
boosts). It ships as a Windows x86-64 build, run here under **Wine + DXVK** in
the `gaming` box.

```sh
cd ansible && ansible-playbook install-sonic-momentum.yml    # or site.yml --tags sonic_momentum
```

| | |
|---|---|
| Source | `ROMS_FINAL/PC/games/Sonic_Momentum_Beta_Edition_m1_8.zip` (44 MB, SHA256-pinned in `dg_sm_source_sha256`) |
| Install | `Games/sonic-momentum/` — `Sonic_Momentum_Beta.exe`, `data.win`, `options.ini`, `splash.png` |
| Wine | prefix `wineprefixes/sonic-momentum` (win64), DXVK 2.7.1, `UseEGL=N` (wine 11 EGL regression) |
| Launcher | `bin/sonic-momentum`; entry **Sonic Momentum · Beta Edition** |

The launcher runs inside the box (Wine lives there), focuses DP-1 and presents
the Windows build through gamescope at **3840×2160/60**. GameMaker draws its own
426×213 canvas; gamescope scales it to the panel, so the in-game resolution
switches (if any) do not need to fight the desktop.

## Controls

GameMaker reads keyboard and XInput/DirectInput through SDL/WineBus, so the
8BitDo enumerates as an Xbox pad: left stick/d-pad move, A/B/X/Y jump and
actions, Start pauses, shoulder buttons for tricks/boost (the game's own
control screen lists the exact bindings). Keyboard works in parallel. Not
exercised here: no controller was connected during the install.

## Saves

The build writes one of `SM.sav`, `SM_SAVE.sav`, `Momentum.sav`,
`SonicMomentumData.sav` or `savedgame.sav` (GameMaker's sandboxed
`%LOCALAPPDATA%` folder is the fallback). `dg_save_sets` mirrors those five
files beside the exe plus the sandbox folder, so whichever slot the game uses is
protected once it writes one.

## Verified here

The build unpacks, the Wine prefix initialises with DXVK, and the game starts
(`Entering main loop` in its stdout, a fullscreen 4K gamescope window on DP-1).
Rendering, controller input and a play session were **not** verified — the
headless check stopped after the engine booted. Settings are the game's own
in-engine menu; there is no external config file to seed (`options.ini` only
holds GameMaker's SleepMargin and x64 flag).

## Notes

- The ZIP stays in the PC games bucket as the provenance/staged copy; the role
  verifies its SHA256 before unpacking.
- Upstream is a Sonic Fan Games HQ showcase entry (no GitHub repo/API), so ogm
  tracks that page for update badges.
- The game's own `data.win` is the whole game; no external assets or ROMs are
  needed.