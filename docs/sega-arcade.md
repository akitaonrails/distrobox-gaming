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

## Sega Model 2 — Model 2 Emulator (Wine)

ElSemi's Windows-only Model 2 Emulator v1.1a, run under Wine by the
opt-in **`install_m2emulator`** role
(`ansible-playbook site.yml --tags m2emulator`; knobs in
`group_vars/all/m2emulator.yml`).

Source is the copy already on the NAS at
`{{ dg_external_games_root }}/M2emulator_1.1a` — the segaretro.org
download page is **captcha-gated**, so if that copy is ever lost, fetch
it manually in a browser from <https://segaretro.org/Model_2_Emulator>.

What the role does:

- Copies the emulator **box-local** to
  `{{ dg_box_home }}/emulators/m2emulator` (`rsync --ignore-existing`)
  because NVDATA (high scores), CFG (per-game inputs) and EMULATOR.INI
  are all mutated next to the exe — the NAS original is never run in
  place.
- Creates a dedicated wine prefix (`wineprefixes/m2emulator`) with
  `d3dx9`, `d3dcompiler_47` (the emulator compiles its `scripts/*.ps`
  pixel shaders at runtime) and `dxvk`.
- Symlinks the ROM dir as `ROMS/` next to the exe — the emulator always
  scans that subdir (README), which sidesteps `[RomDirs]` Windows-path
  backslash escaping entirely (a first attempt via ini_file produced a
  mangled `Z:\mnt\\terachad\...` value; don't reintroduce it).
- Manages EMULATOR.INI: 4K fullscreen (`AutoFull=1` — safe because
  gamescope hosts the mode), 4x FSAA, bilinear, XInput on.
- Deploys `m2emulator-launch`: reduces ES-DE's `%ROM%` path to the
  romset name (`EMULATOR.EXE` takes names, not paths, and resolves the
  zip via the ROMS dir), runs `emulator_multicpu.exe` (the multicore
  build) under gamescope 4K.

The ES-DE `model2` system lists `roms_rare/model2/*.zip` and launches
through the wrapper. Verified 2026-07-13: Daytona USA boots, renders
and titles its gamescope window.

Per-game input remapping must be done in the emulator's own GUI menu
(windowed mode: set `AutoFull=0` temporarily or run
`m2emulator-launch <romset>` from a terminal and use the menus) — the
CFG/*.input files it writes are preserved across role reruns.
