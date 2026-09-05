# Parallel Launcher (standalone N64) — `install_parallel_launcher`

[Parallel Launcher](https://parallel-launcher.ca/) (AUR `parallel-launcher`) is a
standalone N64 launcher that bundles **its own, newer RetroArch AppImage** plus
the **newest ParaLLEl core** (`parallel_n64_next`, ParaLLEl-RDP Vulkan). Opt-in
role; installed 2026-09-05 to run the newest heavy Kaze Emanuar hacks.

## Why it exists

The box's system RetroArch **ParaLLEl-N64** core (seeded with ParaLLEl-RDP +
LLE ParaLLEl-RSP for Last Impact / Star Road) has an **older parallel-rdp**. It
boots the newest hacks but renders their custom 3-D **black** — e.g. *Return to
Yoshi's Island Demo 2* showed only the HUD. Parallel Launcher ships the
**newest** parallel-rdp (2.28.0 at time of writing), which renders them
correctly on the RTX. It is the "NEWEST version only" setup the RTYI author
calls for, native (no Wine, unlike the PJ64+GlideN64 alternative).

Under the hood it runs:
`…/parallel-launcher/appimage/RetroArch-Linux-x86_64.AppImage -L …/retro-data/cores/parallel_n64_next_libretro.so --config …/retroarch.cfg <ROM>`
— entirely separate from the box's system RetroArch and its config.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-parallel-launcher.yml     # or: site.yml --tags parallel_launcher
ansible-playbook install-parallel-launcher.yml -e dg_parallel_launcher_revert=true
```

**First launch downloads the core.** The very first time Parallel Launcher runs
it fetches its RetroArch AppImage + the newest ParaLLEl core from
`parallel-launcher.ca` and shows a one-time **"This emulator core is not
installed or is out of date. Install now?" → Yes**. After that it runs headless
from ES-DE with no prompts. (There's no documented CLI to pre-download the core;
it's a one-time GUI step.)

## ES-DE integration

The role adds a third **n64** alternative emulator,
**"Parallel Launcher (standalone)"** (`parallel-launcher %ROM%`), alongside
Mupen64Plus-Next (default) and the RetroArch ParaLLEl-N64 core. Pick it **per
game** in ES-DE for hacks that need the newest renderer — currently
[Return to Yoshi's Island Demo 2](rom-patches.md). ES-DE prepends the box's GPU
env (`VK_ICD_FILENAMES=…nvidia…`), so the ParaLLEl-RDP Vulkan renderer binds the
RTX, not the iGPU.

## Settings (enforced by the role)

`~/.config/parallel-launcher/settings.cfg` is written by the launcher itself.
`files/seed_pl_settings.py` merges the box's required keys on top and preserves
the rest (idempotent):

- `fullscreen: true` — on the RTX / DP-1.
- `default_gfx_plugin: 1` — **ParaLLEl-RDP** (the whole point; `0` is GLideN64).
- `input_driver: "sdl"` — 8BitDo via SDL2 GameController; Parallel Launcher
  auto-maps Xbox/XInput-style pads (the 8BitDo in XInput mode).
- `pause_on_focus_loss: false` — a focus change (or headless screenshot)
  doesn't freeze the game.

Everything else — controller profiles, RHDC login, per-game overrides — the user
manages in the launcher GUI. Parallel Launcher can also patch/play RHDC hacks
directly (it handles `rhdc://` and `.bps`), but on this box we hard-patch ROMs
reproducibly via `install_rom_patches` and just point the launcher at the
finished `.z64`.
