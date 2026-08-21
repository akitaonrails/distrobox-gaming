# DOOM 3 via DUDE

**DUDE** (Doom3 Unified Development Engine) is a modernized fork of **dhewm3** — the
classic Doom 3 source port — with new **OpenGL 3.3** and **Vulkan 1.4** renderers and
an opt-in enhancement suite (shadow maps, HDR, SSAO, PBR, SMAA/FXAA/FSR2; ray-traced
sun shadows + tessellation on Vulkan). Built natively and run on the RTX 5090.
Managed by `install_dude` / `install-dude.yml`.

## Game data (required, user-provided)

DUDE needs the **classic PC Doom 3** game data — `base/*.pk4` (and `d3xp/*.pk4` for
*Resurrection of Evil*). **NOT the BFG Edition** (different, incompatible data) and
not the Xbox version. You own Doom 3 on **Steam (appid 9050)** — install it; the
launcher auto-detects it in the Steam libraries (or pass a path:
`dude-launch /path/to/doom3`). BFG Edition would need a different engine
(RBDOOM-3-BFG), which this isn't.

## Build

Native build in the box (deps already present: cmake, gcc, sdl2, openal,
vulkan-headers, vulkan-icd-loader, glslang, shaderc):

```sh
cd ansible
ansible-playbook install-dude.yml     # clone + build (Vulkan) + launcher + desktop entry
```

The role clones `github.com/Inkub0/dude`, runs `./build.sh --vulkan` →
`tools/dude-src/build/dude`, and installs `bin/dude-launch` + a "DOOM 3 · DUDE"
desktop entry.

## Run

```sh
/mnt/data/distrobox/gaming/bin/dude-launch          # auto-detect Doom 3, Vulkan renderer, DP-1
DUDE_API=opengl3 dude-launch                         # force the GL3 renderer
DOOM3_BASEPATH="/path/to/doom3" dude-launch          # explicit game path
```

The launcher pins the nvidia Vulkan/GLX ICD and focuses DP-1. Config/saves live in
`~/.local/share/dude`. Renderer is chosen via `r_graphicsAPI` (`opengl | opengl3 |
vulkan`); enhancement quality via in-game presets (Potato → Nightmare).

## Status

**Working** 2026-08-20 — DUDE launches and loads classic Doom 3 (all base pak000–004
+ d3xp for Resurrection of Evil). Classic Doom 3 (appid 9050) is installed on the
removable **STEAM drive** at `/run/media/akitaonrails/STEAM/steamapps/common/Doom 3`;
the launcher auto-detects Steam libraries including removable-drive mounts. BFG
Edition (also installed) is intentionally not used — DUDE needs the classic data.
8BitDo works via SDL2 (native gamepad support).
