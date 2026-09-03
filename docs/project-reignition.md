# Project Reignition (Sonic and the Secret Rings remake)

**Project Reignition** ([Gamejolt](https://gamejolt.com/games/project_reignition/1082591),
by KumaPauZ) "brings Sonic and the Secret Rings to modern platforms" — a fan
remake of the 2007 Wii game with updated presentation, native controller
support, and reworked progression. **Godot 4.7 + .NET (mono export)**, with an
official **native Linux build** — no Wine; renders **Vulkan Forward+ on the
RTX**. Fully self-contained (no original game data needed). Managed by
`install_project_reignition` / `install-project-reignition.yml`
(`site.yml --tags project_reignition`).

## Source

The Linux zip from Gamejolt, staged on the NAS:
`ROMS_FINAL/PC/project-reignition-linux-v<version>.zip`, pinned by sha256.
Updating: download the new Linux zip from Gamejolt to that path, bump
`dg_project_reignition_version` + `dg_project_reignition_zip_sha256`, re-run
(extract is version-gated; saves live in the Godot `user://` dir and survive).

## Run

`/mnt/data/distrobox/gaming/bin/project-reignition` or **"Project Reignition"**
in Walker. Launches fullscreen on DP-1 (game-managed; launcher focuses DP-1 via
the Hyprland Lua `eval` API and pins the NVIDIA Vulkan ICD). **8BitDo works
natively** (Godot). The bundled GDExtension ffmpeg libs (`libav*`) sit next to
the exe — the launcher exports `LD_LIBRARY_PATH` to the install dir.

Note: a `ModManager` NullReferenceException appears in the log on a fresh run
(missing mods folder scan) — benign, the game continues past it.

## Status

**Working** 2026-09-03 — v1.0.1, window "Sonic and the Secret Rings Remake"
fullscreen on DP-1, Vulkan Forward+ on `NVIDIA GeForce RTX 5090`.
