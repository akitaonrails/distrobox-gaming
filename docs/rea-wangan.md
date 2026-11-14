# Wangan Midnight arcade series — REA launcher

[akitaonrails/rea-teknoparrot-wangan-series](https://github.com/akitaonrails/rea-teknoparrot-wangan-series)
is one hub for the Wangan Midnight arcade games. It uses no TeknoParrot:
OpenParrot / OpenParrot_WMMT run the ES3B titles, WanganArcadeLoader the N2
titles natively, and the package bundles Wine/DXVK for the Windows-built games.
Your dumps stay untouched.

```sh
cd ansible && ansible-playbook install-rea-wangan.yml   # or site.yml --tags rea_wangan
```

| | |
|---|---|
| Release | `v0.1.0` Linux tarball (198 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/rea-wangan/WanganLauncher-0.1.0-linux-x86_64/` |
| Data | `~/.local/share/rea-wangan/` — `launcher.cfg`, `settings/`, `runtimes/` saves, Wine prefix |
| Library | `EmuDeck/roms_rare/TeknoParrot` |
| Launcher | `bin/wangan`; entry **Wangan Midnight · Arcade Series** |

## What runs

| Game | Board | State |
|---|---|---|
| Maximum Tune 3 | Namco N2 | ready |
| Maximum Tune 3DX+ | Namco N2 | ready |
| Maximum Tune 5 | Namco ES3B | ready |
| Maximum Tune 5DX+ | Namco ES3B | ready |
| Maximum Tune 6 | Namco ES3B | ready |
| Maximum Tune 6R | Namco ES3B | ready |
| Maximum Tune 6RR | Namco ES3B | ready |
| Maximum Tune 3.07 Rev B | Sega Chihiro | **blocked** in this release |
| Wangan Midnight R | Namco System 246 | **blocked** in this release |

`wangan-launcher --list` reports the first seven `ready` and the last two
`not yet`, with the same reasons shown in the app.

## The supplied BIOS files

The NAS has:

- `EmuDeck/Emulation/bios/sys246/r27v1602f.7d` — System 246 PS2 BIOS
- `EmuDeck/Emulation/bios/chihiro/` — a Chihiro/Xbox BIOS set

The **current launcher release does not read either one**. Its catalogue
hard-codes the Chihiro and System 246 routes as blocked, and the launcher's
library scanner only accepts `library` folders; there is no BIOS path option
or BIOS-consuming loader in v0.1.0. The Chihiro set it documents also expects
four media-board files (`ic10_g24lc64.bin`, `pc20_g24lc64.bin`,
`ic11_24lc024.bin`, `fpr21042_m29w160et.bin`), which are not the files in this
folder. Wiring the paths into `launcher.cfg` would have no effect, so they are
recorded in `group_vars/all/rea_wangan.yml` for the eventual loaders instead.

## Settings and controls

Per-game settings live in `~/.local/share/rea-wangan/settings/<game>.cfg`, with
4K output and gamescope FSR/NIS defaults. Pad: left stick steers, RT/LT
accelerate/brake, RB/LB shift, Y view, X intrude, Back insert card, Start coin,
A test menu. The first start of an MT5/MT6 game builds the Wine prefix and
takes a minute.

## Verified here

- `wangan-launcher --list` finds all nine dumps; seven are `ready`, the two
  BIOS-dependent titles are listed as blocked.
- The hub opens fullscreen at 3840×2160 (window class `rea-wangan`).
- A race was not driven during this install; the launcher's own release notes
  record MT3/3DX+/MT5/5DX+/6/6R/6RR played on Linux. Wheel feedback, audio and
  4K FSR output were not verified here.

## Updating

Bump `dg_wangan_version`, asset name and SHA256 in
`group_vars/all/rea_wangan.yml`, then re-run. `launcher.cfg`, settings and
`runtimes/` saves are kept. Revert with `-e dg_wangan_revert=true`.