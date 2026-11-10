# Ratchet & Clank (PS4) — ReCasted

[AndyALRLabs/ReCasted](https://gitlab.com/AndyALRLabs/ReCasted) is not an
emulator: it is a small **HLE compatibility layer and native x86-64 loader** for
*Ratchet & Clank (PS4)*. It maps the Orbis system calls and the Liverpool GNM
graphics pipeline onto POSIX and Vulkan 1.3 and runs the game binary as a host
process — no full-system emulation, no Wine.

```sh
cd ansible && ansible-playbook install-recasted.yml    # or: site.yml --tags recasted
```

| | |
|---|---|
| Release | `v0.4.0` Linux x86_64 tarball (30 MB, SHA256-pinned, staged in `ROMS_FINAL/PC/ports/recasted/v0.4.0/`) |
| Install | `tools/recasted/v0.4.0/recasted-linux-x86_64/`, with `tools/recasted/current` pointing at it |
| Launcher | `bin/recasted`; entry **Ratchet & Clank · ReCasted (PS4)** |
| Save data | `user/` in the install dir (emulated PS4 user/save data), mirrored as `recasted` |

## The game dump is required and not in this library

ReCasted contains no game data. It needs an extracted dump of:

- **CUSA01073 v1.09 (EU)** — upstream's "fully playable" target, or
- **CUSA01047 v1.09 (USA)** — "supported".

Put the folder that holds `eboot.bin` at
`ROMS_FINAL/ps4/Ratchet & Clank (CUSA01073)` (the `dg_recasted_game_dir`
default) or override that variable, then rerun the playbook: it links the dump
as `<app>/game/CUSA01073`, which is where the launcher auto-detects it. As of
2026-11-09 this library has PS2/PS3/PSP/Vita Ratchet titles but **no PS4
dump**, so the role installs the loader and reports the missing dump instead of
pretending the game is playable.

## Using it

The launcher has a **Game Setup** tab (pick/auto-detect the game folder), a
display tab (fullscreen, borderless, resolution, VSync, monitor), a settings tab
(mouse sensitivity, volume, motion blur, bloom, experimental light occlusion)
and presets: 1080p 30, 1080p 60, Steam Deck 720p 30 and **PS4 Pro 1440p Neo**
(1440p with IGTI reconstruction toward 4K). On this box the 1440p Neo preset is
the one to pick; the launcher is an ImGui desktop app, so it runs directly and
remembers its display settings.

`run.sh <game dir>` exists for headless/interactive terminal starts and sets the
library paths and present mode; `--playnow` on the launcher skips the UI with
the saved preset (useful for a Steam shortcut).

## Status here

Installed and the launcher opens on the landscape monitor; the game cannot boot
until the CUSA dump is present. Controller support, the 60 FPS patch, level
streaming and the Neo/IGTI path are therefore **unverified**.

## Notes

- The loader is game-specific: it will not run other PS4 titles (use shadPS4 for
  those).
- It uses Vulkan 1.3 on the RTX 5090; the release notes stress Intel/iGPU
  compatibility but nothing is AMD-only.
- Upstream is a GitLab project (no GitHub Releases API), so ogm tracks the
  project page for update badges; bumps are pinned by SHA256 in
  `dg_recasted_*`.
