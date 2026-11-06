# Project Gotham Racing 2 — Xbox recompilation (hk21x)

[hk21x/pgr2-recomp](https://github.com/hk21x/pgr2-recomp) turns the original
Xbox release of **Project Gotham Racing 2** into a native Windows program by
static recompilation (XboxXBERecomp, the same SDK family as our PGR1 and
NightFire roles). It runs here under **Wine with DXVK** on the RTX 5090.

```sh
cd ansible && ansible-playbook install-pgr2-recomp.yml
```

| | |
|---|---|
| Release | `v1.6.0` — `PGR2-package.zip` (program + compiler) and `PGR2Launcher.exe`, both SHA256-pinned |
| Disc | `EmuDeck/roms_heavy/xbox/Project Gotham Racing 2 (USA, Japan) (En,Ja,…).iso`, 5.6 GB, `default.xbe` SHA-1 `702b79fd…` = the port's "NTSC (USA), media patched" build |
| Install | `Games/pgr2/` — package, `assets/` (the disc), `compiler/`, the built `PGR2.dll`, `hdd/` (emulated disk) |
| Prefix | `wineprefixes/pgr2` (DXVK `d3d11`/`dxgi`, the package's `d3dcompiler_47.dll`, WineBus on SDL) |
| Launcher | `bin/pgr2-recomp`; entry **Project Gotham Racing 2 (Recomp)** |

## How it is installed

The v1.6.0 package is self-contained: `PGR2.exe`, `compiler/` (clang,
lld-link, xbe_recomp, the Xbox XDK and `PGR2.lib`) and the MSVC runtime DLLs.
On first start `PGR2.exe` recompiles the disc's `default.xbe` and links it into
`PGR2.dll` **on this machine** — no game code is downloaded. The role:

1. verifies the ISO's SHA-256, stages the pinned launcher and package in
   `ROMS_FINAL/PC/ports/pgr2-recomp/v1.6.0/`;
2. unpacks the package into `Games/pgr2/` and extracts the disc with
   `scripts/xiso-extract.py` (XDVDFS, not ISO-9660) into `Games/pgr2/assets/`,
   then checks the extracted `default.xbe` SHA-1;
3. creates the Wine prefix, installs DXVK, the package's shader compiler and
   the Wine DLL overrides / WineBus settings;
4. seeds `Games/pgr2/pgr2.toml` and runs the build once (headless `wine
   ./PGR2.exe`), verifying `PGR2.dll` appears.

The build took about two minutes (65 translation units, 32 at a time). It is
skipped on later runs once `PGR2.dll` exists; delete that file (or run
`bin/pgr2-recomp --build`) to rebuild.

## Settings (`Games/pgr2/pgr2.toml`)

The in-game **F1** settings window (or Options → General Options → PC Settings)
edits the same file, so the role seeds it once and later changes win. Seeded:

| Key | Value | Why |
|---|---|---|
| `renderer` | `d3d11` | DXVK path; the default `d3d12` needs vkd3d-proton, which this prefix does not carry |
| `display_mode` / `width` / `height` | `borderless` 3840×2160 | gamescope presents it fullscreen |
| `msaa` | `8x` | the port's highest; the guest frame is only 640×480, so the cost is modest |
| `anisotropic_filtering` | `16` | 16× AF |
| `render_percent` | `100` | the render scale is derived from the 4K window (≈4.5× the guest frame) |
| `race_fps` | `60` | races at 60 instead of the console's 30, in the game's own 1/60 physics steps |
| `fps_cap` | `60` | menus stay at their native 60 |
| `skip_intro` | `true` | skips the four intro movies; set false to watch them once |
| `vsync` | `true` | paced presentation |

`multiplayer`, split screen and System Link are unsupported by the port; it
fails gracefully instead of hanging.

## Controller

Native XInput through Wine's SDL-backed WineBus (`DisableHidraw/DisableInput`
on, `Enable SDL`/`Map Controllers` on — the same block the PGR1 role sets).
The 8BitDo Ultimate 2 is picked up as a controller; the port also speaks to a
wheel (FFB strength, range, deadzone keys in `pgr2.toml`).

## Saves

`Games/pgr2/hdd/` is the emulated hard disk; progress lives in
`hdd/E/UDATA/4d53004b/` and is mirrored by `dg_save_sets` (the file `pgr2.toml`
is backed up too). Deleting `hdd/` repeats the port's first start (cache
rebuild and intros); it is not needed for normal use.

## Verified

Bounded launch through the launcher: window at 3840×2160 inside gamescope,
`d3d11: drawing renderer, 640x480 guest, 3840x2160 window, render scale 4.500`,
60 fps paced, title screen reached; quitting leaves no Wine or gamescope
processes behind.
