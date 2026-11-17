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
| Release | `v0.2.0` Linux tarball (271 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/rea-wangan/WanganLauncher-0.2.0-linux-x86_64/` |
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
| Maximum Tune 3.07 Rev B | Sega Chihiro | board files accepted; Chihiro still freezes under Wine in most runs |
| Wangan Midnight R | Namco System 246 | ready (pcsx2x6, board files added) |

`wangan-launcher --list` reports Wangan R and the seven ES3B/N2 games ready;
Maximum Tune has its board files in but stays `not yet` because the Chihiro
emulator freezes under Wine in most runs.

## The supplied BIOS files

The NAS has:

- `EmuDeck/Emulation/bios/sys246/r27v1602f.7d` — System 246 PS2 BIOS
- `EmuDeck/Emulation/bios/chihiro/` — a Chihiro/Xbox BIOS set

v0.2.0 accepts them through **Settings → Add files** (or
`--add-files <folder>`): it scans the folder and keeps files whose size and
SHA-1 match MAME's records, under any name. The role runs that against
`EmuDeck/Emulation/bios`; it added `r27v1602f.7d` and the four Chihiro files
(`ic10_g24lc64.bin`, `pc20_g24lc64.bin`, `ic11_24lc024.bin`,
`fpr21042_m29w160et.bin`), so Wangan R is ready. Maximum Tune finds its board
files too, but the bundled Chihiro emulator freezes under Wine in most runs and
the launcher keeps Play off.

## Settings and controls

Per-game settings live in `~/.local/share/rea-wangan/settings/<game>.cfg`, with
4K output and gamescope FSR/NIS defaults. Pad: left stick steers, RT/LT
accelerate/brake, RB/LB shift, Y view, X intrude, Back insert card, Start coin,
A test menu. The first start of an MT5/MT6 game builds the Wine prefix and
takes a minute.

## Verified here

- `wangan-launcher --list` finds all nine dumps: the seven ES3B/N2 games and
  Wangan Midnight R are ready; Maximum Tune is `not yet` because Chihiro freezes
  under Wine.
- The hub opens fullscreen at 3840×2160 (window class `rea-wangan`).
- A race was not driven during this install; the launcher's own release notes
  record MT3/3DX+/MT5/5DX+/6/6R/6RR played on Linux. Wheel feedback, audio and
  4K FSR output were not verified here.

## Updating

Bump `dg_wangan_version`, asset name and SHA256 in
`group_vars/all/rea_wangan.yml`, then re-run. `launcher.cfg`, settings and
`runtimes/` saves are kept. Revert with `-e dg_wangan_revert=true`.