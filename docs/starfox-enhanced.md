# Star Fox Enhanced (SNES Star Fox source port)

**Star Fox Enhanced** ([kandowontu2/starfox-enhanced](https://github.com/kandowontu2/starfox-enhanced))
is a source port of the **SNES Star Fox** (1993, SuperFX) built on the
open-source **UltraStarFox** codebase — selectable **20–480 FPS** with the
original deterministic 20 Hz game logic, widescreen, HUD editor, GPU/software
renderers, controller rumble, an embedded **Star Fox EX** campaign, and
optional **MSU-1 orchestral music**. Managed by `install_starfox_enhanced` /
`install-starfox-enhanced.yml` (`site.yml --tags starfox_enhanced`).

> This is **not** our *Star Fox 64* port — that's **Starship** (native N64
> port). Different games (SNES vs N64); both coexist.

## Native since v0.0.3

Upstream now publishes official release binaries **including a native
linux-x64 build**, so the old run-the-Windows-exe-under-Wine setup (needed
when only a `dist/` Windows nightly existed and the native external-ROM loader
was broken) is **gone** — the role migrated away from it (removed the Wine
prefix + old exe). The release zip is pinned by sha256 (verified against the
release `SHA256SUMS.txt`) and staged on the NAS at
`ROMS_FINAL/PC/ports/starfox-enhanced/` for rebuilds.

## Game data

Your own **Star Fox (USA) (Rev 2)** ROM (v1.2 — the only revision the port
accepts), staged beside the executable. On **first launch** the game validates
it, reconstructs the runtime data, and writes a version-bound
`Starfox-Assets.BIN` companion — after that the ROM is no longer read (the
role leaves it staged; a version bump deletes the companion so it rebuilds).

**MSU-1 music:** `Starfox-MSU1.PAK` (226 MB, sha-verified) is staged from the
NAS beside the exe; enable it in the pre-game setup (off by default — without
the PAK the option reads `NOT FOUND`).

## Run

`/mnt/data/distrobox/gaming/bin/starfox-enhanced` or **"Star Fox Enhanced"**
in Walker. Opens on DP-1 on the RTX (GLX/nvidia pinned). The pre-game setup
selects `EXPERIENCE` (Original / Star Fox EX), pace, render FPS, display mode,
renderer (GPU default), MSU-1, rumble, and controller remapping. **8BitDo
works natively** (SDL, with rumble). **Select+Start exits.**

Saves live **beside the executable** — this is the native build, not the old
Wine one, so `Documents/Star Fox Enhanced/` no longer exists. EX SRAM is written
to `tools/starfox-enhanced/game/starfox-ex.srm`, and `backup_saves` mirrors that
file.

`ansible-playbook configure-pc-ports.yml` applies the one-time baseline to the
port's own setup file (`pregame.cfg`, space-separated `KEY VALUE`): fullscreen,
120 FPS presentation, AA level 3, enhanced graphics on, render scale 3 (this
release's 4× maximum), RTX lighting on, model smoothing 2 (medium), rumble on,
MSU-1 off. The effect toggles (bloom, HDR,
enhanced shadows, chromatic aberration) are deliberately **off** — they are
stylistic post effects this port adds, not higher-fidelity rendering. The file
is the port's own settings surface: change it in the setup screen or edit the
keys directly.

Updated to `v0.0.8.8.1` on 2026-10-23. Updating: bump `dg_sfe_version` + `dg_sfe_asset_sha256` (from the release
`SHA256SUMS.txt`), stage the new zip on the NAS, re-run (extract is
version-gated). Revert: `-e dg_sfe_revert=true`.
