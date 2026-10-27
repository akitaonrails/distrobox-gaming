# Conker's Bad Fur Day: Recompiled — `install_cbfd_recomp`

[sciaschi/CBFD-Recompiled](https://github.com/sciaschi/CBFD-Recompiled) is an
**N64Recomp + N64ModernRuntime + RT64 static recomp** PC port of Conker's Bad
Fur Day (US), built from the [mkst/conker](https://github.com/mkst/conker)
decompilation. Opt-in role; updated 2026-10-23 to `V0.1.6` (save states,
achievements, graphics and crash fixes). The role now checks an installed
version marker before extracting a newer build; config and saves stay in
`dg_cbfd_config_dir`.

## Native Linux (like Pilotwings, unlike Wave Race)

Upstream ships a **native Linux x86-64 build** — RT64 renders through
**Vulkan** directly, so no Wine. The role hash-pins the release tarball on the
NAS (`ROMS_FINAL/PC/ports/cbfd-recomp/`) and extracts it to `tools/cbfd-recomp` in
the box. Runtime deps per `ldd` on the binary: `sdl2 vulkan-icd-loader
freetype2 dbus` (installed by the role).

Features: widescreen, higher resolutions, anti-aliasing, high frame-rate
presentation, remappable gamepad/keyboard controls with rumble, EEPROM saves,
and a RecompFrontend launcher (as in Zelda 64 / Banjo Recompiled) with a mod
menu. Three `.nrm` mods ship in the release's Mods zip: **Skip Intro**, **Skip
Any Cutscene**, **Cheats** — drop them into `~/.config/ConkerRecompiled/mods`
in the box and enable them in the Mods menu.

## ROM (required)

**Conker's Bad Fur Day (USA) only** — z64 sha1
`4cbadd3c4e0729dec46af64ad018050eada4f47a`. The NAS dump
`ROMS_FINAL/n64/Conker's Bad Fur Day (USA).zip` contains a `.v64` that is in
fact already big-endian; the role unzips it, normalizes the byte order
anyway, verifies the sha1, and keeps the `.z64` next to the tarball. Asset-only
ROM hacks (e.g. an uncensored patch) also work — load them via the launcher's
**Add ROM**; code-changing hacks and other regions are refused upstream.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-cbfd-recomp.yml     # or: site.yml --tags cbfd_recomp
ansible-playbook install-cbfd-recomp.yml -e dg_cbfd_revert=true
```

The launcher `bin/cbfd-recomp` passes the verified `.z64` as argv — the
frontend imports it into `~/.config/ConkerRecompiled/rom_versions/` on first
launch ("ROM version in play: US Original"), so the ROM picker never blocks;
afterwards choose **Start Game**. The launcher also pins the Vulkan ICD to
nvidia and focuses DP-1. Settings, saves and loaded ROM versions live in
`~/.config/ConkerRecompiled` inside the box.

Verified 2026-09-28 on the box: RTX 5090 Vulkan device detected, 8BitDo
controller picked up via SDL, ROM imported and the game booted at V0.1.4.
The V0.1.6 update still needs a hands-on game check.
Default keyboard: WASD = stick, Space = A, Left Shift = B, Q = Z, E/R = L/R,
Enter = Start, arrows = C buttons, IJKL = D-pad — remappable in Controls.
