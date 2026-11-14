# God of War: Ascension — GoW-Ascension-Recomp (parked)

[bc160201983/GoW-Ascension-Recomp](https://github.com/bc160201983/GoW-Ascension-Recomp)
is a Windows-only static recompilation of **God of War: Ascension** (PS3,
Europe BCES01741 v1.00). The release `0.1.31` bundles the launcher, Python,
the SDK and a Direct3D 12 runtime; the game is lifted from the player's own
disc. There is no Linux target: the CMake project and runtime use Windows
import libraries and `d3d12`.

**Status on this box: parked (2026-11-14), not installed.** Wine and Proton
both reach the renderer and then crash.

## What was tried

The owned dump is the DUPLEX Europe release:

```
ROMS_FINAL/ps3/God.of.War.Ascension.PS3-DUPLEX[rarbg]/BCES01741-[God of War Ascension EU]
```

Its `PS3_GAME/USRDIR/EBOOT.BIN` is a small loader; the disc's real encrypted
EBOOT is in `ORIG/EBOOT.BIN`. RPCS3 decryption of the ORIG file gives the exact
`4c12e201bd8579dbd4f9410b4c65af3c` decrypted ELF the port expects, and the
launcher accepts it. The launcher's `--play` path then:

- reads `PARAM.SFO` (`BCES01741`, `01.00`),
- patches the EBOOT (Disable Motion Blur, Unlock FPS, Disable SPU MLAA),
- boots the PPU/SPU guest, enters the game's own code, and opens a fullscreen
  4K window.

The renderer does not survive:

- **Wine 11 + vkd3d-proton 3.1, live-draw D3D12:** after the adapter and
  window are created, `0xC0000005` (read at address 0) in the module at
  `ydkj_boot.exe+0x165C50`; no frame is drawn. The same crash occurs at 4K and
  at 1280×720, with and without shader precompile.
- **Proton CachyOS 11 (vkd3d-proton 3.1):** the identical crash at the same
  address.
- **Wine's built-in D3D12:** the window opens but stays at `FPS 1.00, draws 0`;
  it never presents.
- Forcing `PS3_RSX=rpcs3` / `PS3_RSX_RENDERER=vulkan` has no effect: this
  build logs `[RSX null]` and always initialises the live-draw D3D12 backend,
  so there is no Vulkan-renderer fallback under Wine.

A physical Windows 10/11 machine with a D3D12 driver is the supported target.
There is no source-level Linux/D3D12 fix to apply here.

## What does work

The PS3 game is in the library and RPCS3 is installed:

```
bin/rpcs3-launch
```

(or the **PS3** system in ES-DE). Boot the Europe BCES01741 dump there; the
DUPLEX `ORIG/EBOOT.BIN` layout is understood by RPCS3. That is the supported
way to play it here until the port runs under a newer vkd3d/Proton.

## If revisiting

Re-test with a newer vkd3d-proton and Wine/Proton, or on real Windows. The
port's launcher and logs make the boundary clear: the guest runs; only the
D3D12 presenter crashes. Report the crash with
`ascension-recomp/ascension/build/logs/last_run.log` upstream.