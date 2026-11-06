# Star Wars Trilogy Arcade — native port (not installed)

[snicolast/StarWarsTrilogyNative](https://github.com/snicolast/StarWarsTrilogyNative)
recompiles Sega's 1998 **Star Wars Trilogy Arcade** (Model 3 Step 2.1) to C++
with a Vulkan renderer: true 16:9/21:9, ray-traced sun shadows and AO, MSAA or
DLAA, 120/144 Hz interpolation, arcade sound with the DSB music/voices, and
mouse/gamepad/light-gun input.

**Status on this box: parked (2026-11-06), nothing installed.** The ROM is
correct and the disc-side pipeline runs here; the missing piece is the
Windows-only build.

## The ROM: present and correct

The port asks for **`swtrilgy.zip`, the Rev. A set**. It is in the Model 3
collection, not in a `mame/` folder (this library has no `ROMS_FINAL/mame`; the
Model 3 sets live in `ROMS_FINAL/arcade/model3/`):

```
/mnt/terachad/Emulators/ROMS_FINAL/arcade/model3/swtrilgy.zip   71,476,302 B, 42 files
```

`tools/romtool.py` identifies the set by CRC32. Verified against the upstream
table:

| File | Expected | In our zip |
|---|---|---|
| `epr-21379a.17` | `24dc1555` | ✓ match |
| `mpr-21339.01` | `c0ce5037` | ✓ match |

The neighbours `swtrilgya.zip` (plain, non-Rev-A) and `swtrilgyp.zip`
(prototype) are **not** what the port accepts.

## What already works here

Both ROM-side stages are plain Python and ran on this machine:

```sh
python3 tools/romtool.py …/model3/swtrilgy.zip data   # crom, banked crom, vrom, sound, dsb, drive
python3 tools/recomp.py data/crom.bin build/gen       # 3736 functions in 94 files, 86 untranslated instructions
```

So the ROM is complete (every bank extracts; a wrong set fails the CRC check)
and the recompiler is portable. What is left is compiling the generated C++.

## Why it cannot be installed here

Upstream is **Windows 10/11 + MSVC only**:

- `build.bat` requires Visual Studio 2022's C++ tools, locates `vcvars64.bat`
  through `vswhere`, then runs its bundled CMake/Ninja; `get_dlss.bat` fetches
  NVIDIA's DLSS SDK on first build.
- `CMakeLists.txt` links Windows libraries and declares a Win32 Vulkan surface:
  `VK_USE_PLATFORM_WIN32_KHR`, `winmm ole32 oleaut32 windowscodecs mfplat
  mfuuid gdi32 dwmapi shell32`.
- 17 of the 39 runtime sources include `windows.h`; `src/video/image_io.cpp`
  and `src/ui/splash_video.cpp` use the Windows Imaging Component and Media
  Foundation for textures and the FMV sequences, and audio/window/input are
  Win32 backends. There is no CMake/MinGW/clang-cl path, no prebuilt binary and
  no release.

## Paths forward

1. **Build on Windows** (a VM qualifies): put `swtrilgy.zip` beside
   `build.bat`, run it, then copy the folder (exe + `data/` + `res/` + DLSS
   DLL) to the box. A role can install that artifact and launch it under Wine —
   Vulkan is native there; the risk is Media Foundation support for the video
   sequences.
2. **Cross-compile** with `clang-cl` + an MSVC CRT/Windows SDK fetched by
   `xwin` (clang 23, lld-link and llvm-rc are already on this host) — the
   same effort as Redline's, and it still needs Wine to run.
3. Park until a Linux build appears upstream; the ROM and a verified recomp
   pipeline stay ready either way.

The author's sibling port of *The Lost World* (`snicolast/LostWorldNative`)
shares this build system and the same limitation.
