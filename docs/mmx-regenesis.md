# Mega Man X Regenesis

**Mega Man X Regenesis** (mmxregenesis.itch.io) is a **Godot 4** fan game — an
alternate-timeline Mega Man X action-platformer with eight new Maverick bosses,
armor upgrades, and hand-crafted pixel-art levels. The author ships an official
**native Linux export**, so it runs natively on the RTX 5090 — no Wine, no
Proton — like DUDE and the recomp ports. Managed by `install_mmx_regenesis` /
`install-mmx-regenesis.yml`.

## Game data (user-provided)

Download the **`… Linux.x86_64`** build from the itch.io page and drop it in
`ROMS_FINAL/PC/` (this box: `/mnt/terachad/Emulators/ROMS_FINAL/PC/`). It's a
single self-contained Godot binary with the `.pck` embedded — no installer, no
extraction. The role globs `*Regenesis*Linux.x86_64`, so a version bump
(1.00.4 → 1.00.5 …) is picked up automatically; just drop the new file in.

> Grab the **Linux** build, not the Windows `PC.zip`. The Windows exe would need
> Wine and would hit the same fullscreen/display and controller issues the Wine
> games fight on this box; the native export sidesteps all of it.

## Install

```sh
cd ansible
ansible-playbook install-mmx-regenesis.yml
```

The role stages the binary to `tools/mmx-regenesis/mmx-regenesis.x86_64`,
verifies it runs (`--version`), and installs `bin/mmx-regenesis-launch` + a
"Mega Man X Regenesis" desktop entry (Walker).

## Run

```sh
/mnt/data/distrobox/gaming/bin/mmx-regenesis-launch        # native Vulkan on the RTX, DP-1
DG_MMX_RENDERER=opengl3 mmx-regenesis-launch               # force the GL3 (compatibility) renderer
```

The launcher focuses DP-1, pins the NVIDIA Vulkan/GLX ICD (so Godot's Vulkan
backend can't land on the AMD iGPU and black-screen), and keeps SDL background
joystick events on. Renderer via `--rendering-driver` (`vulkan` | `opengl3`);
default `vulkan` (Forward+). Config/saves live in the box's Godot user data
(`~/.local/share/godot/app_userdata/…`).

## Controller

**8BitDo works out of the box** — Godot 4 bundles the SDL game-controller DB
(the export ships mappings for the 8BitDo range), and the game advertises full
controller support with in-game remapping. Fullscreen toggles with **Alt+Enter**
or **F11**.

## Status

**Working** 2026-08-21 — native Godot **4.7.stable**, `Vulkan 1.4 Forward+`
confirmed rendering on **Device #0: NVIDIA GeForce RTX 5090** (not the iGPU).
All libraries resolve inside the box; no Wine involved.
