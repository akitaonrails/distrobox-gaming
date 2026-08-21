# GoldenEye 007: Recompiled

Native static recompilation of **GoldenEye 007 (N64)** — `github.com/cblock85/
GoldenEye64Recomp`, using **N64Recomp** (MIPS→native) + **RT64** (Vulkan renderer,
enhanced N64 graphics). Built natively, runs on the RTX 5090. Managed by
`install_goldeneye_recomp` / `install-goldeneye-recomp.yml`.

## Game data (user-provided)

Needs your own **NTSC-U GoldenEye 007** ROM whose z64 (big-endian) form has sha1
`abe01e4aeb033b6c0836819f549c791b26cfde83`. On this box, `roms_mid/n64/originals/
007 - GoldenEye (USA).n64` is the correct dump (it's v64/byteswapped, the role
converts it); the `roms_mid/n64/` copy is a **bad dump** (different hash) — don't
use it. The role byteswaps + verifies the ROM to `baserom.u.z64`, then xdelta-patches
it to the TLB-free ROM the recompiler consumes.

## Build

Native build in the box. Deps: cmake, ninja, clang, lld, python, sdl2, freetype2,
gtk3, **xdelta3** (the only one that was missing).

```sh
cd ansible
ansible-playbook install-goldeneye-recomp.yml
```

**Fixes the role encodes** (the upstream `build_linux.sh` alone fails on the current
Arch toolchain — CMake 4 / GCC 15):
- `CMAKE_POLICY_VERSION_MINIMUM=3.5` — lunasvg/zstd declare `cmake_minimum < 3.5`.
- `CFLAGS=-Wno-incompatible-pointer-types` — the N64Recomp-generated `patches.c` has
  `sprintf(rdram, ctx)` mismatches (a warning on old compilers, now an error).
- `CXXFLAGS=-include cstdint` — RmlUi's `robin_hood.h` uses `uint32_t`/`uint64_t`
  without including `<cstdint>` (newer libstdc++ dropped the transitive include).
- Generates `rsp/aspMain.cpp` (the recompiled audio microcode) before the main
  CMake — upstream only does this in the "clean" build path, but the standard
  build's `CMakeLists` needs it too.

## Run

```sh
/mnt/data/distrobox/gaming/bin/goldeneye-launch
```

**Must run from the source root** (`tools/ge64-src`) — GoldenRecomp loads `assets/`
(RmlUi fonts) relative to cwd and **segfaults** if they're missing; the launcher
handles this. Pins the nvidia Vulkan ICD + focuses DP-1. On first run RT64 opens a
**ROM picker** — select your NTSC-U GoldenEye ROM (it stores the path afterwards).

## Status

Engine **built + launches** (RT64 window "Goldeneye 007: Recompiled", Vulkan, fonts
loaded, stable) 2026-08-20. The `Failed to preload executable!` message is benign —
it's an mlock stutter-optimization that the container's 8 MB memlock cap blocks; the
game runs without it. 8BitDo works via SDL2. Pick the ROM on first launch to load
the game.
