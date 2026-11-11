# Sega Rally 2 Native (Sega Model 3)

[snicolast/SegaRally2Native](https://github.com/snicolast/SegaRally2Native) is a
static recompilation of the 1998 Model 3 arcade game: the original code
recompiled to C++ with a Vulkan renderer — ray-traced sun shadows, GI and car
reflections, true widescreen with corner HUDs, HD liveries, real dust, DLAA/DLSS
or MSAA, 120+ Hz, arcade sound, gamepad/wheel input and achievements.

Upstream is **Windows-only** (MSVC, Win32, Media Foundation, WIC, WinHTTP, Win32
Vulkan surface) and ships no binaries, so this role cross-builds it with
MinGW-w64 and runs the result under Wine.

```sh
cd ansible && ansible-playbook install-sega-rally-2-native.yml   # or site.yml --tags sega_rally_2_native
```

| | |
|---|---|
| Source | commit `05dd362`, SHA256-pinned tarball in `ROMS_FINAL/PC/ports/sega-rally-2-native/` |
| ROM | `ROMS_FINAL/arcade/model3/srally2.zip` (Model 3 Step 2.0 World, with `epr-20512.bin`), SHA256-pinned |
| Build | `tools/sega-rally-2-native/05dd362/` — ROM extraction + PowerPC recomp (Python), host glslang/m68kmake, MinGW cross build |
| Install | `Games/sega-rally-2-native/` — `SegaRally2.exe`, `data/`, `textures/` |
| State | `Games/sega-rally-2-native/save/` (`eeprom.bin`, `settings.ini`) |
| Launcher | `bin/sega-rally-2-native`; entry **Sega Rally 2 · Native** |

## The cross-build

The repository's `build.bat` drives MSVC. The role reproduces the same steps on
Linux with MinGW-w64:

1. `tools/romtool.py` extracts the ROM into `data/`; `tools/recomp.py` turns the
   PowerPC code into `build/gen/` (1,651 functions, 42 files).
2. Two host tools are built natively because the cross-built Windows versions
   cannot execute during the build: **glslang** (compiles the GLSL shaders to
   SPIR-V) and **m68kmake** (Musashi's 68000 opcode tables).
3. CMake configures with `CMAKE_SYSTEM_NAME=Windows`, the MinGW compilers and
   `-static -static-libgcc -static-libstdc++` (otherwise the exe needs the
   MinGW runtime DLLs), passing the host tool paths.
4. `files/cross-build.patch` is ours, not upstream's: it selects the host tools
   when cross-compiling and replaces two MSVC intrinsics (`_BitScanReverse`,
   `__popcnt`) with GCC builtins.

## Running it

The launcher runs inside the box, focuses DP-1 and starts the exe under a
dedicated win64 Wine prefix with the NVIDIA Vulkan ICD. Settings and the arcade
EEPROM live in `save/` beside the exe and are mirrored by `dg_save_sets`.

The port's own menu covers resolution (up to 4K), true widescreen, ray tracing,
DLAA/DLSS/MSAA, 120/144 Hz, sound modes and the arcade options; the game's
in-engine options hold the display size and controller bindings. The first
start is slower while shaders and the recompiled code warm up.

## Verified here

The cross-build completes (glslang + m68kmake host tools, 371-target MinGW
build, statically linked exe), the role rerun is `changed=0`, and a bounded
launch reaches the in-game menu ("SELECT GAME") at 240 Hz with the timing log
showing ~0.08 ms render / ~4 ms GPU wait per frame. Gameplay, wheel force
feedback and the ray-traced options were not exercised.

## Notes

- Other Model 3 sets (`srally2x`, `srally2p`, `srally2pa`) are not accepted by
  the port; only the World `srally2` set is.
- The original PC release remains available through `install_sega_rally_2`
  (sr2-patcher) and Model 3 emulation through Supermodel; this is the native
  recompilation path.
