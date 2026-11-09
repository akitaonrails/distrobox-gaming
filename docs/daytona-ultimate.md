# Daytona USA Ultimate (Sega Saturn mod disc)

[AJBats/daytona-cce95](https://github.com/AJBats/daytona-cce95) rebuilds
**Daytona USA Circuit Edition** (Japan, GS-9100 — the release that lets you pick
the time of day) with the original **Daytona USA** inside it: its handling,
camera, car bodies, road-bank physics, engine and tyre sounds, title screen and
attract mode, while keeping Circuit Edition's five courses and two-player mode.
The disc is region free. It is a **beta**: complete and playable, but some parts
have had little testing.

```sh
cd ansible && ansible-playbook install-daytona-ultimate.yml
```

| | |
|---|---|
| Patcher | `v1.0.0-beta.1` (commit `0e8fdcc`); source tarball and the Windows builder ZIP are SHA256-pinned and staged in `ROMS_FINAL/PC/ports/daytona-ultimate/` |
| Circuit Edition input | `EmuDeck/roms/saturn/Daytona USA - Circuit Edition (Japan).chd` (SHA256 `267fea42…`), extracted with `chdman` to its 31 tracks |
| Daytona USA input | `ROMS_FINAL/saturn/Daytona USA (USA)` — tracks 1–3, checked against the exact SHA-1s the patch was made from |
| Output | `EmuDeck/roms/saturn/Daytona USA Ultimate/` — `.cue` + 33 tracks, 639 MB |
| Playing it | ES-DE → Saturn → **Daytona USA Ultimate** (Beetle Saturn core) |

## How it is built

Upstream's disc builder is a Windows GUI, and the source build (`make disc`)
needs recordings made from a debugger-driven Mednafen and Windows fonts. This
repo does neither: it uses the patcher's own Rust modules unchanged through a
small headless driver, and the **release patch** carved out of the released
`Daytona USA Ultimate Builder.exe` (the patch is compiled into that binary, not
shipped in the tree).

1. Verify both owned rips. The builder refuses anything off by a few samples,
   so the CCE CHD and the three DUSA tracks are checked against the hashes the
   patch was generated from.
2. `chdman extractcd --splitbin` turns the CCE CHD into its cue + 31 tracks.
3. `scripts/daytona_extract_patch.py` carves the embedded `ultimate.patch` out
   of the pinned builder binary.
4. The role templates a two-file Cargo crate around upstream's
   `builder/`/`cdrom/`/`disc/`/`patch/` modules and `cargo build`s it in the
   box (Rust from the Arch repo, crates from crates.io).
5. The driver verifies every track, rebuilds track 01 from the patch streams
   (ECC included) and writes the 33-track disc.
6. The disc is copied into the ES-DE Saturn library, and a `.built-<commit>`
   marker makes reruns `changed=0` until the pin, the CHD or a track changes.

No game data is downloaded: both discs are the owned rips already in the
library.

## Settings

Everything Saturn runs through the shared RetroArch/Beetle Saturn setup (the
same one ES-DE uses for the rest of the Saturn library): fullscreen, the
configured shader and audio. The core renders at the console's own resolution
and RetroArch presents it; there is no per-game 3D resolution to raise, unlike
the PC ports. The game's own options cover the Circuit Edition handling option,
sound/attract choice, automatic or manual gearbox and the usual race settings.

## Saves

Saturn saves are RetroArch's shared save directory (`.config/retroarch/saves`),
already mirrored by `dg_save_sets` as `retroarch-saves`; the disc itself is
read-only.

## Verified here

The disc builds in about a minute of patching after the one-off CHD extraction,
comes out as 33 tracks / 639 MB, and boots in RetroArch's **Beetle Saturn
1.32.1** at 2560×1440 fullscreen to the Daytona USA legal screen. Gameplay,
two-player mode and the Force Feedback wheel add-on were not exercised.

## Notes

- Beta caveats from upstream: tested on a real Saturn with a Satiator, not with
  other ODEs, the Saroo or a burned disc; it boots on a PAL Saturn but the game
  is made for 60 Hz and will probably run slow at 50 Hz.
- The patcher is Unlicense; the modded disc is built from SEGA discs and is not
  redistributed here.