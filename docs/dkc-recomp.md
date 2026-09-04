# Donkey Kong Country SNES recompilations (DKC1 / DKC3)

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
| DKC2 | USA **v1.0** (`35421a9a…`) | **not owned** — only Rev 1 dumps ❌ |
| DKC3 | USA (En,Fr) (`2277a2d8…`) | EmuDeck `.sfc` ✅ |

**DKC2 is therefore not installed.** When a USA v1.0 dump exists, add an entry
to `dg_dkc_games` (its host is DKC3-shaped, so likely just `_GNU_SOURCE`).

## Run

`bin/dkc1-recomp` / `bin/dkc3-recomp`, or the Walker entries
"Donkey Kong Country · Recomp" / "Donkey Kong Country 3 · Recomp". Both open
on DP-1 on the RTX. DKC3 boots into its launcher UI (ROM shown as
**verified**, per-player input pickers — the 8BitDo shows **connected**;
"Skip launcher on boot" available). DKC1 boots straight in (Rareware logo);
its extras live in host menus/keys (F7 pause, F8 step). Update = bump `ref`
in `dg_dkc_games` (checkout is ref-gated; the build re-runs).
