# CannonBall DX (OutRun engine) — `install_cannonball`

An enhanced C++ reimplementation of Sega's **OutRun** arcade engine (higher
frame-rate, widescreen, CRT shaders, Mesen2 pixel scalers). Upstream:
[Endprodukt/cannonball-dx](https://github.com/Endprodukt/cannonball-dx) — a fork
of CannonBall-SE, itself based on the original
[djyt/cannonball](https://github.com/djyt/cannonball). Opt-in role; migrated from
plain CannonBall to the DX fork 2026-09-05.

- **Distribution:** **built from source** (native Linux, CMake + SDL2 +
  TinyXML2, **OpenGL ES2 / EGL**) — no Linux release binary. Pinned to
  `dg_cannonball_ref`; the build pulls Mesen2 (scalers) and miniz via CMake
  FetchContent, so it needs network. Binary is `cannonball-dx`.
- **You must provide** the original **OutRun Revision B** arcade ROMs (same set
  as classic CannonBall). This box has the MAME `outrun` parent set as
  `arcade/mame/outrun_dup2.zip` (31 epr/mpr/opr files incl. the rev-B CPU roms
  `epr-10380b/10382b/10383b`); the role extracts them into `roms/`.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-cannonball.yml          # or: site.yml --tags cannonball
scripts/install-host-launchers.sh                # refresh the host menu entry
ansible-playbook install-cannonball.yml -e dg_cannonball_revert=true
```

Launcher: `{{ dg_box_home }}/bin/cannonball` (menu: **"CannonBall - OutRun"**).

## The native-Linux fullscreen patch (the whole reason this took work)

The fork targets Ubuntu/Raspbian/Windows and had two issues on this
multi-head, dual-GPU, fractional-scale box. Both are fixed by
`files/cannonball-dx-linux-landscape-fullscreen.patch`, applied on top of the
pinned commit before building:

1. **It sized itself from SDL display 0 — which here is the *portrait* DP-2
   panel** (`2160x3840`). `RenderBase::sdl_screen_size()` called
   `SDL_GetCurrentDisplayMode(0,…)`, so the game laid itself out for a portrait
   screen and its (correct-aspect) image landed in a **corner** of the landscape
   DP-1 display it was actually shown on. The patch makes it iterate the
   displays and pick a **landscape** one (width ≥ height, largest area), storing
   the index in `display_index`, and creates the window on that display
   (`SDL_WINDOWPOS_CENTERED_DISPLAY`). This was the *actual* corner-render cause
   — not scaling.
2. **The window lacked `SDL_WINDOW_ALLOW_HIGHDPI`**, so `SDL_GL_GetDrawableSize`
   returned logical points (2560×1440) instead of physical pixels (3840×2160)
   and the GL viewport under-filled the framebuffer. The patch adds the flag.

To move the pin forward: bump `dg_cannonball_ref`, re-apply the patch to the new
tree (`git apply`; refresh the patch if it no longer applies cleanly), rebuild.

## Rendering, audio, controller

- **Rendering:** native **OpenGL ES2 (EGL)** — unlike classic CannonBall's
  desktop GL. Pinned to the RTX on XWayland (`SDL_VIDEODRIVER=x11`). Because it
  uses EGL, the launcher pins **both** vendor libraries to nvidia:
  `__GLX_VENDOR_LIBRARY_NAME=nvidia` **and** `__EGL_VENDOR_LIBRARY_NAMES=nvidia`.
  Without the EGL pin, EGL binds the AMD iGPU/llvmpipe (`MESA-EGL: … failed to
  create dri2 screen`) and the game renders wrong. A single residual
  `MESA-EGL … driver (null)` line for the nvidia PCI id is harmless — Mesa
  declines the nvidia card and the nvidia EGL vendor then drives it. **No
  gamescope** (it grabs the iGPU here → flicker/black). `config.xml` is seeded
  `<mode>1` (full-screen) + `<widescreen>1`.
- **Audio:** CannonBall outputs straight to ALSA and has **no in-config
  volume**. The role installs **`pipewire-alsa`** so the ALSA default routes
  through PipeWire (fixes `dmix` contention and exposes a per-app stream); the
  launcher sets that stream to `dg_cannonball_volume` (**60%**) on launch and
  PipeWire's stream-restore remembers it. Do NOT set
  `SDL_AUDIODRIVER=pulseaudio` — the box's SDL pulse backend produces no stream.
- **Controller (always supported):** modern SDL2 `SDL_GameControllerOpen` with
  the bundled `gamecontrollerdb.txt` (155 8BitDo entries); the 8BitDo is
  auto-detected and `config.xml` ships `<pad_id>0` + `<analog enabled="1">`.
  Fine-tune axes in the in-game **Settings → Controls** menu, which writes
  `config.xml` — so the role seeds `config.xml` only when absent (in-game
  changes, including pad config, are preserved).

## Notes

- `config.xml`, `roms/` and `res/` are read relative to the working dir; the
  launcher `cd`s into the install dir. **`res/` must stay a subdirectory** (the
  fork opens `res/` relative to CWD; flattening it triggers a directory-iterator
  error).
- Bump `dg_cannonball_ref` to move to a newer commit (triggers a rebuild).
- **Build hazard:** a partial box upgrade can leave `cmake` linked against a
  newer `jsoncpp` soname than is installed (`cmake: … libjsoncpp.so.27: cannot
  open shared object file`). Fix: `sudo pacman -Sy jsoncpp` in the box (the
  soname-bump class from the box-update notes).
- The OutRun romset on the NAS is only read, never modified.
