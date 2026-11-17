# Nintendo arcade series — REA launcher

[akitaonrails/rea-teknoparrot-nintendo-series](https://github.com/akitaonrails/rea-teknoparrot-nintendo-series)
is one hub for Nintendo's arcade games: **F-Zero AX Monster Ride** and
**Mario Kart Arcade GP 2** on Sega Triforce (Dolphin), **Mario Kart Arcade GP
DX** and **Luigi's Mansion Arcade** through windowsarcadeloader. No
TeknoParrot.

```sh
cd ansible && ansible-playbook install-rea-nintendo.yml   # or site.yml --tags rea_nintendo
```

| | |
|---|---|
| Release | `v0.1.0` Linux tarball (614 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/rea-nintendo/NintendoArcadeLauncher-0.1.0-linux-x86_64/` |
| Data | `~/.local/share/rea-nintendo/` — `launcher.cfg`, `settings/`, `runtimes/` (Dolphin user folder/saves, WAL Wine prefix) |
| Library | `EmuDeck/roms_rare/TeknoParrot` |
| Launcher | `bin/nintendo-arcade`; entry **Nintendo Arcade · REA** |

## What runs

`--list` finds all four owned dumps:

- **F-Zero AX Monster Ride** (Japan, SBHA6W) — Dolphin 2609b
- **Mario Kart Arcade GP 2** (MK21 Ver. A) — Dolphin 2609b
- **Mario Kart Arcade GP DX** (1.18.16 English mod) — windowsarcadeloader
- **Luigi's Mansion Arcade** (SDCF) — windowsarcadeloader

Each is identified by its disc image or program hash. The hub shows "starts;
not yet raced through the launcher" until a run is recorded, which is the
launcher's normal ready state for a known build.

## Settings

Per-game settings live in `~/.local/share/rea-nintendo/settings/<game>.cfg`:
render size (Triforce games up to 8× 480 lines), output size, FSR/NIS/linear/
nearest upscaling, sharpness, optional CRT shader, fullscreen and dead zone.
Pads: left stick steers (and tilts the Monster Ride handle), RT/LT gas/brake,
A item/boost, B Mario/view, LB/RB paddles or menu, Start/Back. Luigi's Mansion
uses the left stick for the crosshair; a Linux mouse/lightgun can aim too if
`/dev/input` is readable.

The optional Triforce test menu (`segaboot.gcm`) is not configured; the games
do not need it to play.

## Verified here

- `nintendo-launcher --list` finds all four games; the hub opens fullscreen at
  3840×2160 (window class `rea-nintendo`) and the role reruns `changed=0`.
- A race was not driven during this install. Upstream records races for all
  four; the first Mario Kart DX/Luigi start also installs Microsoft runtimes
  through winetricks and needs the network once.

## Updating

Bump `dg_nintendo_version`, asset and SHA256 in
`group_vars/all/rea_nintendo.yml`, then re-run. `launcher.cfg`, settings and
`runtimes/` saves are kept. Revert with `-e dg_nintendo_revert=true`.