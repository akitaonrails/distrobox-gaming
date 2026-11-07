# SoulCalibur (Dreamcast) — Voldorium

[enrique363/voldorium](https://github.com/enrique363/voldorium) statically
recompiles the Dreamcast **SoulCalibur** (USA T-1401N V1.000) to a native
program with a **native Linux build** (SDL2 + OpenGL, no Wine): true 16:9,
8× MSAA, a built-in VMU, and rollback netplay shared with Windows players.

```sh
cd ansible && ansible-playbook install-voldorium.yml
```

| | |
|---|---|
| Release | `v1.1.3` — `Voldorium-1.1.3-linux.tar.gz` (486 KB, SHA256-pinned; the asset name has no `v` while the tag does) |
| Disc | `ROMS_FINAL/dreamcast/Soulcalibur (USA).chd` (redump), converted once with `chdman` to `.gdi` + tracks |
| Install | `Games/voldorium/` — program, `builder/` (toolchain + work), `disc/`, `sc_game.so`, `voldorium.ini`, `vmu_a1.bin` |
| Launcher | `bin/voldorium`; entry **SoulCalibur (Voldorium)** |

## Install path

1. Stage the pinned tarball in `ROMS_FINAL/PC/ports/voldorium/v1.1.3/` and
   unpack it flat into `Games/voldorium/`.
2. Convert the library CHD to GDI with `chdman extractcd … --splitbin` (the port
   reads `.gdi` + track files, not a CHD).
3. Verify the dump identity in `IP.BIN` (`SEGA SEGAKATANA`, product `T1401N`,
   version `V1.000`) before building, so a wrong dump fails with our message.
4. Build the game module headlessly: `builder/first_run.sh <gdi> <folder>` runs
   `tools/build.py --download --only module`, which fetches Zig 0.14.1 and two
   Flycast files (each SHA-256 checked) into `builder/toolchain/`, translates the
   disc's code and compiles `sc_game.so` — about a minute here, no GUI.
5. Seed `voldorium.ini` (disc path, fullscreen, native resolution, 8× MSAA,
   stretch backgrounds, smooth text, VSync on) and publish the menu entry.

## Settings

The in-game **GRAPHICS** menu (OPTIONS) edits `voldorium.ini` and wins after the
first seed: fullscreen/window, the resolution the game is drawn at (native or a
16:9 size up to the monitor), anti-aliasing (off/2×/4×/8×), VSync, and loading
(ORIGINAL disc speed vs FAST). Input is keyboard + gamepad (left stick or
d-pad, triggers or shoulders for L/R), or a mouse-based light gun.

## Saves

`vmu_a1.bin` (the virtual memory card in controller port A) and `voldorium.ini`
are the two files to keep; `dg_save_sets` mirrors both. `.dci` cards from an
emulator can be imported with `tools/vmu_import.py` from the source repository.

## Notes

- `builder/` holds ~340 MB of toolchain (Zig + headers) and ~280 MB of work
  files; both are re-derivable and deliberately not backed up.
- Rollback netplay requires the same program version on both ends; the game
  module is byte-identical for everyone who builds from the same disc.
- Verified here: headless build produced `sc_game.so` (17 MB), and a bounded
  launch renders fullscreen at 3840×2160 through the normal menu path.
