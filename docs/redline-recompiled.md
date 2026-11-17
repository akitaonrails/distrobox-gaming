# Forza Motorsport (Xbox, 2005) — Redline Recompiled (not installed)

[DivxPlays/redline-recompiled](https://github.com/DivxPlays/redline-recompiled)
is a static recompilation of the original Xbox **Forza Motorsport** (2005):
x86-32 code lifted to C and rebuilt as a 64-bit Windows program with a new
D3D11/12 + DLSS/FSR graphics layer, 144 fps and ultrawide support. The checked
release is v0.3.0 (2026-11-13), which adds a `--zig` build path next to the
original MSVC one.

**Status on this box: parked, nothing installed (re-checked 2026-11-17).**
The disc blocker below is gone: the correct Rev 1 image is now in the library,
so only the Windows build remains before an install can be attempted.

## 1. The build is Windows-only

The release is source-only (launcher, `runtime/`, `recomp/`, `tools/`), with no
prebuilt game in the zip or CI. v0.3.0 has two Windows build paths in
`tools/build.py`:

- the default **MSVC** path (`vcvars64.bat` + `cl.exe`/`rc.exe`);
- **`--zig`** (clang/lld with the mingw-w64 target and Windows' C runtime),
  using `build/tools/zig-0.14.1/.../zig.exe`, which the launcher downloads.

Both produce a Windows `redline.exe`; there is no Linux target. Running the
launcher/build under Wine or Proton has not been tested upstream, so the
remaining step is to try it, or build on a real Windows PC/VM.

## 2. The disc is now correct

`ROMS_FINAL/xbox/Forza Motorsport (USA) (En,Ja,Fr,De,Es,It,Pt,Zh,Ko) (Rev 1)/`
holds a 7.3 GiB ISO. Extracting it shows `Forza.xbe` with SHA-1
`e60a968e7ea73a1065b87dc1120f0b02e2eb1b58`, exactly the image the port's
launcher accepts; the ISO's SHA-256 is
`d32d510d906f221a7d189e52de364cd38ad4d95434e8a1e4a110b3bb767b5d1a`.

The launcher sees the extracted folder, so the previous repack/`default.xbe`
mismatch no longer applies. The remaining question is the build: v0.3.0's
`--zig` path still runs Windows tools and the launcher downloads Python,
Capstone and Windows Zig; it has not been built under Wine/Proton yet.

## Next attempt

1. Run **RedlineLauncher.exe** under Wine/Proton with the correct disc, press
   Build (first build downloads Python/Capstone/Zig, ~95 MB, then compiles for
   5–10 minutes) and check the resulting `build/redline.exe` under the same
   prefix.
2. If the launcher's Windows build is the only failure, build on a real
   Windows PC/VM and copy the resulting folder into the box.

