# Star Fox Enhanced (SNES Star Fox source port)

**Star Fox Enhanced** ([kandowontu/starfox-enhanced](https://github.com/kandowontu/starfox-enhanced))
is a hybrid **source port of the SNES Star Fox** (1993, SuperFX) — a from-scratch
SDL3 C++ engine (its own 65C816 core + SPC700 audio + software renderer) built on
the open-source **UltraStarFox** codebase. It adds selectable **20–360 FPS**,
**widescreen up to 32:9**, a customizable HUD, mouse camera, and a God Mode,
while keeping the deterministic 20 Hz game logic.

> This is **not** our *Star Fox 64* port. That's **Starship** (`starship`, a
> native N64 port) — a different game (N64 vs SNES). Both can coexist.

## How it's installed

The engine *is* portable SDL3 and builds natively on Linux, **but** the runtime
only exercises the **embedded-ROM** path — its external `SF.SFC`/`SYMBOLS.TXT`
loader mis-reads the ROM (`LoROM address … outside the cartridge window`). So we
run the upstream **prebuilt exe**, a single self-contained file with the
assembled UltraStarFox ROM + symbol map embedded, **under Wine**. It's SDL3, so
it runs cleanly under Wine, GLX-pinned to the RTX. Managed by
`install_starfox_enhanced` / `install-starfox-enhanced.yml`
(`site.yml --tags starfox_enhanced`).

The exe is pinned by commit + sha256 (no GitHub release exists) and downloaded
from the repo's `dist/`. No ROM to supply — it's embedded. The Wine prefix gets
`UseEGL=N` (wine 11's EGL backend otherwise renders on the AMD iGPU) and the
WineBus SDL controller policy so the 8BitDo reaches the game's SDL3.

## Run

```sh
/mnt/data/distrobox/gaming/bin/starfox-enhanced      # or "Star Fox Enhanced" in Walker
```

Opens on DP-1. In the pre-game setup pick **display mode** (4:3 / 16:9 / 16:10 /
21:9 / 32:9), **render FPS**, God Mode, crosshair colour, etc. `CUSTOMIZE SCREEN`
drag-positions HUD elements (saved to `Documents/Star Fox Enhanced/`).
**Select+Start exits.** Hold **Tab** = 2× fast-forward; right-mouse-drag =
free camera.

## Controls (8BitDo)

Gamepad is auto-detected (XInput/SDL). Default: **dpad/stick** = move, **South**
= B (shoot), **East** = A (boost/brake), **West** = Y, **North** = X, shoulders =
L/R. Remap in-game via **CONTROLLER REMAP**.

## Native build (future)

`starfox_pc` compiles natively (SDL3 3.4 + CMake + gcc in the box) — the blocker
is only the external asset loader. If upstream fixes it (or one builds
UltraStarFox at the pinned rev `270e959a` for matching `SF.SFC`/`SYMBOLS.TXT`),
this could drop Wine entirely. The embedded ROM/symbols can be carved from the
prebuilt exe's RCDATA resources 101/102.
