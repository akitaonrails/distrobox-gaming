# Gran Turismo 7 via KytyPS5-GT7

[usa-ratt/KytyPS5-GT7](https://github.com/usa-ratt/KytyPS5-GT7) (the
`gt7-eqaa` branch of KytyPS5) is a PS5 **emulator** with a native Linux x86_64
build, tuned specifically for Gran Turismo 7 (PPSA01317, version **01.710** —
the exact version our dump is). Managed by `install_kyty_gt7` /
`install-kyty-gt7.yml`; runs inside the gaming distrobox on the RTX 5090, no
Wine. Release cadence is roughly daily — the GitHub sweep bumps the pin often.
The current pinned build is
[KytyPS5-2026-10-28-f908636](https://github.com/usa-ratt/KytyPS5-GT7/releases/tag/KytyPS5-2026-10-28-f908636).
It includes the prior GT Sophy custom-race crash fix and moves GPU buffer
cleanup off the graphics thread. The previous October 27 release remains
installed for rollback. The new release tarball is staged in
`ROMS_FINAL/PC/releases/` and checked against its GitHub SHA256 digest.

## Game data (one-time extraction, already done)

KytyPS5 loads a **game folder** (`eboot.bin`, `sce_module`, …) or a ZArchive —
it cannot read a PKG. The library's 134 GB
`ROMS_FINAL/ps5/Gran.Turismo.7.PS5-PPSA01317[FPKG]/UP9000-PPSA01317_00-GRANTURISMO70000.pkg`
is an FIH-format backport FPKG (magic `\x7FFIH`, unencrypted filesystem,
`01.710.000`) — extractable with
[pkg-to-anyps5](https://github.com/awake-devel/pkg-to-anyps5) v0.2.5
(`~/tools/pkg-to-anyps5` in the box):

```sh
pkg-to-anyps5 <pkg> <out> --jobs 16 --verbose   # ~30-60 min for 282 GiB / 95,387 files
```

The Kyty game folder is then assembled from the two output halves (executables
are unwrapped to ELF in `source/`, everything else is in `app0/`):

```sh
gt7-kyty/            # = dg_kyty_game_dir
  eboot.bin          # from extracted/source/eboot.bin (plain ELF — Kyty accepts it)
  sce_module/*.prx   # from extracted/source/sce_module/
  …                  # moved from extracted/app0/
```

The original FPKG stays as the canonical source; `backport (4.xx to 11.xx)/`
and `_SHA256/` beside it are console-install artifacts.

## Run

Walker entry: **Gran Turismo 7 · KytyPS5**; launcher
`/mnt/data/distrobox/gaming/bin/kyty-gt7`. The wrapper runs
`kyty_emulator --game <dir>` with the upstream-tested profile: **4K fullscreen,
Mailbox present, vblank 60, tessellation ON, bindless textures ON, shader
optimization Performance** (tessellation is not the emulator default — without
it car bodies are drawn wrong; red-zone protection is on by default). Extra
args pass through to `kyty_emulator`.

In-game, use the **performance (frame rate) mode**; the RT mode is not
recommended yet. Expect pop-in the first time on each track (shaders compile
while you drive, cached afterwards).

## Status and expectations

Very early: the October 28 upstream notes report **~27–28 fps in a Tokyo race
against 11 AI cars**, from about 22 in heavy spots to peaks near 40, on an
RTX 5090 in performance mode. This is an upstream measurement, not a result
measured on this machine. The emulator uses about 20–25 GB RAM in races.
Known upstream issues: Scapes drift-tutorial softlock (#19, close the emulator),
livery editor exit error CE-210717, Tokyo night green tint at some angles,
video/audio sync. The emulator never goes online (online requests fail like a
PS5 without internet). Not yet launched on this box — first boot is the
verification step.

Reports: GitHub issues with the zipped `_kyty.txt` log (written next to the
emulator / in its working dir).
