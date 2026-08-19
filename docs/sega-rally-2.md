# Sega Rally 2 — Wine dead-end (removed)

**Status: not viable under Wine on this box. The `install_pc_racing` entries and
launchers were removed 2026-08-17.** This doc records why, so it isn't
re-attempted from scratch.

The game is the *Sega Rally 2 ~ 25th Anniversary Edition* (OldNewPixel 1.9.0
repack of the 1999 PC version, MUSASHI engine). It shipped two launchers here —
`SEGA RALLY 2 WIDESCREEN.exe` (16:9) and `SEGA RALLY 2.EXE` (4:3 classic).

## The failure

Both launchers fail:

- **4:3** crashes on launch.
- **Widescreen** shows the dgVoodoo splash, then hangs.

Both are the same fault: a **null-pointer dereference at `MGameD3D.dll+0x7375`**
(`read null at ...7375`, `EXCEPTION_ACCESS_VIOLATION`), inside the game's **own
compiled Direct3D renderer**, called from `SEGA RALLY 2.EXE`. It fires **right
after dgVoodoo successfully creates the D3D11 swapchain** — the device works; the
game then reads a null in its post-init code.

## Everything that was ruled out

Investigated exhaustively 2026-08-03, re-verified 2026-08-17:

- **Renderer wrapper:** dgVoodoo 2.79.3 *and* wine builtin ddraw → same crash.
- **Wine version:** 11.14, 11.15, **11.8**, and **wine-staging 9.19** (with
  dgVoodoo) all hit the identical `+0x7375` crash. (9.19 + *builtin* ddraw avoids
  the crash but the game just exits before rendering — not a fix.)
- **GE-Proton8-26** bare: can't init a GL context outside the Steam runtime
  (inconclusive, not the game crash).
- **Software rendering:** the game has a "Ramp Emulation" software path, but
  Wine/dgVoodoo expose no software D3D device for it, and forcing software GL
  (`LIBGL_ALWAYS_SOFTWARE`) hits the same crash — the fault precedes rendering.
- **The game's OpenGL renderer** (`MGameGL.dll`, `MUSASHI.GameGL`) loads but is
  never used; the game is hardwired to `MGameD3D`. `LAUNCH.EXE`'s device dropdown
  and `SR2.CFG` device index (0–7) all route to D3D. Forcing GL needs
  binary-patching the exe's `CoCreateInstance`.
- Also independent of: gamescope on/off, GPU, controller/input, WinXP compat, the
  widescreen-vs-vanilla exe, and the wine-11 EGL→GLX fix.

## Why no upstream fix helps

There is **no GitHub repo / issue tracker** — OldNewPixel develops the repack on
X/Twitter and ships via archive.org. Its updates (v1.5–v1.8+) are all
**Windows-side** (Win10/11 compat, ReShade, widescreen, 60fps). The crash is in
**Sega's original 1999 `MGameD3D` binary**, which the repack wraps but never
rewrites — so no repack version fixes the Wine-specific null-deref. Every online
"fix" (SR2 Modern-Sys, Retro Renew, PCGamingWiki, Repair Pack) is Windows-only.
The "Proton fixed a Sega Rally launcher crash" changelog line is **Sega Rally
Revo** (Steam appid 10400), not SR2.

## Play Sega Rally instead

- **Sega Rally Championship HD** (Wanszai Model 2) — `install_sega_rally`, works.
- **Sega Rally Revo** — `install_pc_racing` `sega-rally-revo`, native on the RTX.
- SR2 specifically needs a **Windows VM** (where its D3D runs), or a real binary
  patch to force the unused GL renderer.
