# Sega Arcade Systems (Model 2, Model 3, NAOMI 1/2)

The four Sega arcade ROM sets live under `{{ dg_emudeck_root }}/roms_rare/`
(`model2/`, `model3/`, `naomi/`, `naomi2/`) and each shows up as its own
system in ES-DE. Three different emulators cover them:

| System  | Emulator                | Install path                    |
|---------|-------------------------|---------------------------------|
| Model 3 | Supermodel (native)     | AUR `supermodel` package        |
| Model 2 | Model 2 Emulator (wine) | see its section below           |
| NAOMI 1/2 | Flycast (native)      | AUR `flycast-git` (already in)  |

## Sega Model 3 — Supermodel

Installed from the AUR as `supermodel` (a maintained release snapshot;
`supermodel-git` is orphaned, and `supermodel-bin` is an **unrelated AI
tool** — don't "upgrade" to it). The package ships two binaries:

- `/usr/bin/supermodel-binary` — the real emulator.
- `/usr/bin/supermodel` — a packaging wrapper that is **unusable from a
  frontend**: it drops its arguments (no ROM ever reaches the binary),
  requires a ROMs dir behind a zenity error, and seeds
  `~/.config/supermodel`, a path this build never reads.

The 0.3a binary resolves everything under **`~/.supermodel/`**
(`Config/Games.xml`, `Config/Supermodel.ini`, `NVRAM/`, `Saves/`).
Our `supermodel-launch` wrapper (deployed by `seed_configs` to
`{{ dg_box_home }}/bin/`) seeds that layout from `/usr/share/supermodel`
on first run, forces SDL onto XWayland (`WAYLAND_DISPLAY=''` — the
native Wayland GL context fails with "OpenGL initialization failed"),
and passes the ROM through. The ES-DE `model3` entry launches it.

Managed render settings (`dg_supermodel_settings` →
`~/.supermodel/Config/Supermodel.ini`, merged into the pre-staged file):
4K, **borderless window instead of exclusive fullscreen** — SDL
fullscreen needs an XRandR mode matching 3840x2160 and scaled XWayland
only exposes logical modes ("Couldn't find any matching video modes",
then the emulator exits). The Hyprland `gaming.conf` supermodel class
rule fullscreens the borderless window. Widescreen FOV + wide
backgrounds are on; the New3D engine, quad rendering and force feedback
come from the pre-staged ini.

Verified 2026-07-13: Daytona USA 2 (`daytona2.zip`) boots and renders
on the RTX 5090 (GL 4.5 core profile) via the wrapper.

Controls: the binary's built-in defaults already include SDL gamepad
bindings alongside the keyboard; tune per-game overrides in
`~/.supermodel/Config/Supermodel.ini` (sections named after the ROM
set, e.g. `[ daytona2 ]`).
