# Pilotwings 64: Recompiled — `install_pilotwings_recomp`

[danielgomesvieira2000/pilotwings-64-recomp](https://github.com/danielgomesvieira2000/pilotwings-64-recomp)
is an **N64Recomp + N64ModernRuntime + RT64 static recomp** PC port of
Pilotwings 64 (the launcher/runtime harness comes from Wave Race 64:
Recompiled). Opt-in role; installed 2026-09-24 at `v0.1.1`.

## Why native (unlike Wave Race)

Upstream ships a **native Linux x86-64 build** of the whole game — RT64 renders
through **Vulkan** directly, so there is no reason for the Wine +
vkd3d-proton path we use for Wave Race 64. The role hash-pins the release
tarball on the NAS (`ROMS_FINAL/PC/pilotwings-recomp/`) and extracts it to
`tools/pilotwings-recomp` in the box. Runtime deps per `README-LINUX.txt`:
`sdl2 vulkan-icd-loader gtk3 freetype2` (installed by the role).

Features: widescreen at the display's aspect ratio (HUD at the screen edges),
high frame rate via matrix interpolation, no overscan border, instant screen
changes, and a launcher with graphics/sound/controls settings + remapping.

## ROM (required)

**Pilotwings 64 (USA) only** — cart `PW`, region `E`, revision `0`, z64 sha1
`ec771aedf54ee1b214c25404fb4ec51cfd43191a`. The box's dump
`roms_mid/n64/Pilotwings 64 (USA).n64` is byte-swapped; the role converts it to
a big-endian `.z64` (kept next to the tarball on the NAS) and the binary's
`--identify` confirms "This dump matches the pinned target." The recompiled
binary is distributed prebuilt; the ROM supplies the original assets at
runtime.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-pilotwings-recomp.yml     # or: site.yml --tags pilotwings_recomp
ansible-playbook install-pilotwings-recomp.yml -e dg_pw64_revert=true
```

The launcher `bin/pilotwings-recomp` passes the verified `.z64` as argv
(`Pilotwings64Recomp <rom.z64>`), which skips the launcher's ROM picker, pins
the Vulkan ICD to nvidia, and focuses DP-1. Settings and saves live in
`~/.local/share/Pilotwings64Recomp` inside the box.

Gamepad is used if attached (8BitDo via SDL); on the keyboard, arrows = stick,
`X`=A, `C`=B, `Z`=Z, `Enter`=Start, `A`/`S`=L/R, `I/J/K/L`=C buttons. Known
upstream bugs at v0.1.1: cannonball's aiming HUD stays centred, and changing
the aspect ratio with the photo album open blanks it until reopened.
