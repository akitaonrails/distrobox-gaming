# Forza Motorsport (Xbox, 2005) — Redline Recompiled (not installed)

[DivxPlays/redline-recompiled](https://github.com/DivxPlays/redline-recompiled)
is a static recompilation of the original Xbox **Forza Motorsport** (2005):
x86-32 code lifted to C and rebuilt as a 64-bit Windows program with a new
D3D11/12 + DLSS/FSR graphics layer, 144 fps and ultrawide support. v0.1.0
(2026-11-06) is the first playable release.

**Status on this box: parked (2026-11-06), nothing installed.** Resuming it
needs a Windows (MSVC) build, or a cross-compile effort — see *Staged for a
future attempt* at the end. Two independent reasons it cannot be built here:

## 1. The build is Windows/MSVC only

The release is source-only (358 files, `runtime/`, `recomp/`, `launcher/`,
`tools/`). `tools/build.py` builds `redline.exe` by running
`cmd /c "…vcvars64.bat"` and then **MSVC** (`cl`, `rc`) with MSVC-style flags
(`/O2 /W3 /MP /D…`); `third_party/dlss` and `third_party/fsr` are fetched by
`tools/fetch_sdks.py` during the build. There is no CMake, MinGW or clang-cl
path, and nothing prebuilt in the zip or in CI, so it cannot be produced here
without installing MSVC in a Windows environment (or cross-compiling with
clang-cl against an MSVC SDK, which is a project in its own right).

## 2. The disc does not match the one the launcher accepts

`launcher/launcher.cpp` hard-codes one executable:
`XBE_SHA1 e60a968e7ea73a1065b87dc1120f0b02e2eb1b58` for **Forza Motorsport
(USA) (Rev 1), `Forza.xbe`**. Both Forza ISOs in this library
(`EmuDeck/roms_heavy/xbox/` and `ROMS_FINAL/xbox-iso/`, same 3,195,770,880-byte
image) are a repack whose game executable is named `default.xbe`, title id
`0x4D53006E` ("Forza Motorsport"), SHA-1 `42f796aa4aad85d941fce3eae0ab8b3f8fc9bc82`
— a different pressing (the retail disc's `Forza.xbe` is the game; its
`default.xbe` is the CDX launcher). `tools/build.py` itself does not check the
hash, so a manual/CI build might still lift this image, but the supplied
launcher refuses it.

## Staged for a future attempt

`ROMS_FINAL/PC/ports/redline-recompiled/v0.1.0/RedlineRecompiled-0.1.0.zip`
(SHA-256 `9c87c1da38dc0a6a0cc6d2a89f7d93aa458f65d00c89bf44102ae5c3c424f624`).

Paths forward, in order of effort:

1. **Build on Windows** (a VM qualifies): run `RedlineLauncher.exe`, point it
   at the disc, press Build, then copy the resulting folder to the box. A role
   can then install that artifact the way the PGR1/PGR2 roles install their
   launchers, and a Wine prefix with DXVK runs it.
2. **Cross-compile here**: `clang-cl` + an MSVC CRT/Windows SDK fetched by
   `xwin`, plus `llvm-rc` for the launcher's resources, and a shim for
   `build.py`'s `vcvars64` step. This is untested upstream.
3. **Get the Rev 1 `Forza.xbe`** (SHA-1 `e60a968e…`) before either of the above
   if the launcher is to be used as shipped.
