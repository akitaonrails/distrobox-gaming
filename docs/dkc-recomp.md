# Donkey Kong Country SNES recompilations (DKC1 / DKC2 / DKC3)

[elliotttate](https://github.com/elliotttate)'s **DKC1Recomp** / **DKC2Recomp**
/ **DKC3Recomp** statically recompile the SNES trilogy into native widescreen
PC ports (shared `snesrecomp` engine, SDL2 hosts; days-old alphas). Upstream
ships **no Linux binaries** (macOS; Windows for DKC2 only), so
`install_dkc_recomp` (`install-dkc-recomp.yml`, `site.yml --tags dkc_recomp`)
**builds from source at pinned commits** with our small Linux-port patches.

## The Linux ports (role `files/`)

- **DKC1** (`dkc1-linux-port.patch` + `dkc1-linux_stubs.c`): the older
  `sdl_host.c` host is macOS-tied in four small ways — Mach timing (shimmed
  1:1 with `CLOCK_MONOTONIC`, 1 tick = 1 ns so the timebase math is exact),
  a cocoa native-window pointer (nulled; only consumed by stubbed functions),
  a `pthread_set_qos` call (guarded), and strict C11 hiding POSIX
  (`_GNU_SOURCE`). `linux_stubs.c` answers "not available" for the entire
  macOS Metal-presenter / file-picker / display-link API, which routes the
  host onto its portable SDL renderer + SDL timing fallbacks. A `dkc1_linux`
  CMake target mirrors the mac target minus the `.m` files.
- **DKC3** (`dkc3-linux-port.patch`): its newer desktop host (launcher UI,
  overlay) is **upstream-portable** — the patch only adds `_GNU_SOURCE`.

## Game data (revision-strict)

Sources are generated from the user's own ROM (`generate_snesrecomp.py`);
the role sha256-verifies the exact revision first:

| Game | Required dump | Our copy |
|---|---|---|
| DKC1 | USA **v1.0** (`fa8cacf5…`) | `ROMS_FINAL/snes/Donkey Kong Country.smc` ✅ (the EmuDeck **Rev 2** does *not* match) |
| DKC2 | USA **v1.0** (`35421a9a…`) | staged `ROMS_FINAL/snes/... (v1.0).sfc` (2026-09-04; the Rev 1 dumps do *not* match) ✅ |
| DKC3 | USA (En,Fr) (`2277a2d8…`) | EmuDeck `.sfc` ✅ |

**DKC2** is DKC3-shaped (only `_GNU_SOURCE` needed) with one extra wrinkle:
its snesrecomp desktop runner is gated behind `DKC2_BUILD_SNESRECOMP` (default
**OFF**) — the entry passes `-DDKC2_BUILD_SNESRECOMP=ON` via `cmake_flags`.
Its generator also builds a small Rust analyzer with the box's cargo.

## Run

`bin/dkc1-recomp` / `bin/dkc2-recomp` / `bin/dkc3-recomp`, or the Walker entries
the "Donkey Kong Country … · Recomp" entries. All open
on DP-1 on the RTX. **Gamepad (8BitDo) works in all three**: DKC1's host opens
the first SDL game controller automatically (with stomp haptics/rumble);
DKC2/DKC3 boot into their launcher UI (ROM shown as **verified**) where the
role seeds `build/linux/launcher.cfg` with **Player 1 = Gamepad** (sources:
0=None 1=Keyboard 2=Gamepad; the upstream default put the pad on Player 2) —
note the launcher persists its config BESIDE THE EXECUTABLE, not the cwd.
"Skip launcher on boot" available; DKC1's extras live in host menus/keys
(F7 pause, F8 step). Update = bump `ref`
in `dg_dkc_games` (checkout is ref-gated; the build re-runs).

## Saves, save states, and pad chords

All three keep the game's built-in saves (cartridge SRAM, e.g. Candy's in
DKC1) under their user dirs, and all three have **host save states** —
with **Select+L1 = quicksave** and **Select+R1 = quickload** chords, plus
**LT = rewind** and **RT = fast-forward**:

- **DKC1** (older SDL host): F11/F12 quicksave/load, 5 slots. The assist layer
  (rewind/FF/state) is gated behind a macOS-only menu toggle, so our
  `linux_stubs.c` enables it and binds the chords; the chord encoding itself
  (`DKC1_PAD_CHORD`) is our addition in `dkc1-linux-port.patch`.
- **DKC2/DKC3** (newer launcher host): F5/F9 save/load state, in-game overlay
  (Start+Select) with an Assist Tools page. Upstream *encodes* pad combos in
  the UI but never evaluated them at runtime, and launcher.cfg clamped
  `AssistPad*` values to 255 — both fixed in our `dkc2/dkc3-linux-port.patch`.
  The role seeds `launcher.cfg` with `AssistTools=1`, `AssistPad2=1528`
  (Select+L1), `AssistPad3=2040` (Select+R1) via lineinfile (user edits to
  other keys are preserved).

The chord buttons still pass through to the game as normal inputs (Select/L/R),
which is harmless in gameplay.
