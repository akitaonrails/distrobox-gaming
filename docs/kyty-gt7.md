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
`dg_kyty_launcher` (`{{ dg_box_home }}/bin/kyty-gt7`). The wrapper runs
`kyty_emulator --game <dir>` with a profile based on upstream's tests: **4K fullscreen,
Mailbox present, vblank 60, tessellation ON, bindless textures ON, shader
optimization Performance, reflections every other frame**. Tessellation is
not the emulator default; without it car bodies are drawn wrong. Red-zone
protection is on by default. Extra args pass through to `kyty_emulator`.

The host script re-enters the gaming box and runs the emulator directly there.
The older `distrobox-enter -- sh -c` form dropped the positional game path,
causing Kyty to exit with `game input must be provided with --game` when
started from Walker. Keep the script re-entrant if changing the launcher.

In-game, use the **performance (frame rate) mode**; the RT mode is not
recommended yet. Expect pop-in the first time on each track (shaders compile
while you drive, cached afterwards).

The role keeps `_ShaderCache` and `_PipelineCache` under
`dg_kyty_cache_root` and links them into the selected release. A new emulator
release therefore reuses the compiled caches rather than starting empty.
Driver or shader-translator changes may still require recompilation. These
caches are rebuildable and are not included in save backups.

The upstream guide describes drawing reflections every other frame as a small
performance adjustment (roughly 1 FPS in its race test and 4 FPS in its time
trial test) with no visible difference in its tests. The role sets the matching
`--reflections-every 2` option. Upstream also recommends 60 Hz
for GT7; 120 Hz mode did not improve its measurements. Low-VRAM environment
flags are unnecessary for the RTX 5090. The game folder resides on the NAS,
which could affect loading, though we have not measured an I/O bottleneck.

## Status and expectations

Very early: the October 28 upstream notes report **~27–28 fps in a Tokyo race
against 11 AI cars**, from about 22 in heavy spots to peaks near 40, on an
RTX 5090 in performance mode. This is an upstream measurement, not a result
measured on this machine. The emulator uses about 20–25 GB RAM in races.
Known upstream issues: Scapes drift-tutorial softlock (#19, close the emulator),
livery editor exit error CE-210717, Tokyo night green tint at some angles,
video/audio sync. The emulator never goes online (online requests fail like a
PS5 without internet). A 2026-10-30 launcher smoke test initialized Vulkan
on the RTX 5090, recognized PPSA01317 v01.710.000 and opened the GT7 window;
its window title reported 60 FPS during startup. Racing, controller input and
sustained gameplay frame rate remain unverified.

Kyty stores game saves in `_SaveData` beside the emulator. The role moves that
directory to `dg_kyty_save_dir` and links it into the selected release so
updates retain saves. `kytyps5-savedata` in `dg_save_sets` mirrors the shared
directory to the NAS; shader and pipeline caches are excluded.

Reports: GitHub issues with the zipped `_kyty.txt` log (written next to the
emulator / in its working dir).
