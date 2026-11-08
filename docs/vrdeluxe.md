# Virtua Racing Deluxe Enhanced (Sega 32X)

[PokaMilkTea/VirtuaRacingDeluxeEnhanced](https://github.com/PokaMilkTea/VirtuaRacingDeluxeEnhanced)
runs the original Sega 32X **Virtua Racing Deluxe** in PicoDrive and rebuilds
the 3D scene on the GPU from what the 68000 sends the SH2s (HLE): higher
resolution with MSAA, 16:9, longer draw distance with haze, detailed opponents,
analog steering and pedals, and a frame rate above the console's 20. Upstream
ships Windows and macOS binaries only; on Linux it is built from source.

```sh
cd ansible && ansible-playbook install-vrdeluxe.yml
```

| | |
|---|---|
| Release | `v1.2.2` (commit `99b5ff9`), source tarball SHA256-pinned and staged in `ROMS_FINAL/PC/ports/vrdeluxe/` |
| ROM | `ROMS_FINAL/sega32x/Virtua Racing Deluxe (USA).zip` — inner file SHA-1 `18dfdeb50780c2623e60a6587d7ed701a1cf81f1` (upstream's supported dump) |
| Build | `tools/vrdeluxe/v1.2.2/src`, `make -j 30` inside the box (SDL2 + GL + zlib), under a minute |
| Install | `Games/vrdeluxe/` — `vrde`, a link to the library ROM, `vrde.ini`, `vrde.mds` (save state) |
| Launcher | `bin/vrdeluxe`; entry **Virtua Racing Deluxe · Enhanced** |

The launcher runs inside the `gaming` box (gamescope lives there) and re-enters
itself, so the desktop entry points straight at the script. The port reads the
library ZIP directly through PicoDrive's own zip support, so the owned ROM stays
where it is and is never copied or modified.

## Settings

`vrde.ini` is seeded once with the enhanced maximum and is rewritten by the
game whenever the in-game menu (Esc) or keys 1–9 change something; later changes
survive role reruns.

| Setting | Value | Meaning |
|---|---|---|
| `resolution` | `0` | render the HLE 3D at the window's pixels (4K), not 1×/2×/4× |
| `msaa` | `1` | 4× MSAA (fewer samples if the GL offers fewer) |
| `smooth` | `3` | interpolate to 60 images/s (the game's own tick is 20) |
| `widescreen` | `1` | 16:9 (21:9 and window-shaped are also available) |
| `far_view` | `1` | twice the draw distance, with haze |
| `detailed_opponents` | `1` | near-model opponents everywhere |
| `exact_vertices` | `1` | floating-point projection (no high-res jitter) |
| `blend_dither` | `1` | blended dithered shadows/smoke and sky |
| `analog` | `1` | left stick steers, triggers work throttle/brake by travel |
| `fullscreen` | `0` | gamescope owns fullscreen; the game's own stays off |

Presentation is gamescope `-W 3840 -H 2160 -r 60 -f`. That is deliberate: the
port's own fullscreen on this box's 250 Hz output measured a 15 ms average swap
with **413 missed vsyncs of 1412**, while the gamescope 4K60 path measured
**2328 vsyncs / 2327 frames, 0 missed vsyncs, 0 audio underruns, 59.9 fps** over
a 40-second bounded run (`emulate 3.1 ms`, `draw 0.24 ms`, `swap 13.2 ms`).

## Controls

Keyboard: arrows d-pad, A/S/D = pad A/B/C (B throttles), Z/X/C = six-button
X/Y/Z (Z changes view), F start, Esc menu. Keys 1–9 and O/P are debugging,
view-mode, resolution, MSAA, dither, frame rate, aspect, far view, level of
detail, and save/load state.

Controllers are native SDL and mapped by physical position to the six-button
pad: d-pad or left stick steers (analog), A/□/Y = pad A, bottom button = pad B
(throttle), right button = pad C, top button = six-button Z, triggers = analog
brake/throttle, LB/RB = X/Y, Start, Back/Guide = menu, L3+R3 toggles the debug
overlay. **Not verified here**: no controller was connected during the install
(the 8BitDo was off), so the mapping is upstream's documented layout and the
analog path still needs a hands-on check.

## Notes

- Settings and the single save state (`vrde.mds`, key O writes it, P loads it)
  live in the game folder and are mirrored by `dg_save_sets`.
- The project's own code and PicoDrive are **non-commercial use only**; the ROM
  is not included and must be your own dump.
- Upstream's Windows/macOS release bundles SDL2; the Linux build links the
  box's SDL2 2.32, GL and zlib, which is why `zlib` is not in the package list
  (this box has `zlib-ng-compat`, which provides the same headers and library).