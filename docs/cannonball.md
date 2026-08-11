# CannonBall (OutRun engine) — `install_cannonball`

An enhanced C++ reimplementation of Sega's **OutRun** arcade engine (higher
frame-rate, widescreen). Upstream: [djyt/cannonball](https://github.com/djyt/cannonball).
Opt-in role; installed 2026-08-11.

- **Distribution:** **built from source** (native Linux, CMake + SDL2 + Boost
  headers, OpenGL) — no Linux release binary. Pinned to `dg_cannonball_ref`.
- **You must provide** the original **OutRun Revision B** arcade ROMs. This box
  has the MAME `outrun` parent set as `arcade/mame/outrun_dup2.zip` (31
  epr/mpr/opr files incl. the rev-B CPU roms `epr-10380b/10382b/10383b`); the
  role extracts them into `roms/`.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-cannonball.yml          # or: site.yml --tags cannonball
scripts/install-host-launchers.sh                # refresh the host menu entry
ansible-playbook install-cannonball.yml -e dg_cannonball_revert=true
```

Launcher: `{{ dg_box_home }}/bin/cannonball` (menu: **"CannonBall - OutRun"**).

## Building (two gotchas)

- **CMake 4** removed compatibility with Cannonball's old
  `cmake_minimum_required` → pass `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
- `-DTARGET` wants the **filename with extension** (`linux.cmake`). A bare
  `linux` silently falls back to the Windows default (`win64-opengl.cmake`) and
  the link fails on `-lopengl32 / -ldinput8`.

## Rendering, audio, controller

- **Rendering:** native OpenGL, pinned to the RTX via GLX + PRIME on XWayland
  (`SDL_VIDEODRIVER=x11`) — the same path Supermodel uses. **No gamescope** (it
  grabs the AMD iGPU here → flicker/black). `config.xml` `<mode>` is seeded to
  `1` (full-screen).
- **Audio:** CannonBall outputs straight to ALSA and has **no in-config
  volume**. Without a bridge that hits ALSA `dmix` directly (loud + "device
  busy" contention). The role installs **`pipewire-alsa`** so the ALSA default
  routes through PipeWire, which fixes the contention and exposes a per-app
  stream (`PipeWire ALSA [cannonball]`). The launcher then sets that stream to
  `dg_cannonball_volume` (**60%**) on launch; PipeWire's stream-restore
  remembers it thereafter. Do NOT set `SDL_AUDIODRIVER=pulseaudio` — the box's
  SDL pulse backend produces no stream; the default (bridged) ALSA path works.
- **Controller (always supported):** native SDL2 with the bundled
  `gamecontrollerdb.txt`; the 8BitDo is auto-detected. Fine-tune axes in the
  in-game **Settings → Controls** menu (auto-detects), which writes `config.xml`
  — so the role seeds `config.xml` only when absent (in-game changes, including
  pad config, are preserved).

## Notes

- `config.xml`, `roms/` and `res/` are read relative to the working dir; the
  launcher `cd`s into the install dir.
- Bump `dg_cannonball_ref` to move to a newer commit (triggers a rebuild).
- The OutRun romset on the NAS is only read, never modified.
