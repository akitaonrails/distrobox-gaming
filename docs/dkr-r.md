# DKR-R — Diddy Kong Racing Recompiled — `install_dkr_recomp`

[ThatGuyMcd/DKR-R](https://github.com/ThatGuyMcd/DKR-R) is an **N64Recomp +
N64ModernRuntime + RT64 static recomp** PC port of Diddy Kong Racing. Opt-in
role; updated 2026-10-23 to stable `1.0.8`.

## Native Linux AppImage

Upstream ships a **native Linux x86-64 AppImage** — RT64 renders through
**Vulkan** directly, so no Wine. The role hash-pins the release AppImage on
the NAS (`ROMS_FINAL/PC/dkr-r/`) and copies it (version-gated via
`.dg-installed-ref`) to `tools/dkr-r` in the box. Runtime dep: `fuse2` for the
AppImage (installed by the role).

Features: Accurate (4:3, 30 FPS cadence) and Modern (widescreen, interpolated
unlocked FPS, FOV, extended draw distance, aniso) presentations, per-player
controller assignments with remapping + gyro steering, virtual EEPROM + 4
Controller Paks with rumble, save import/export, Magic Codes, RT64/Rice
texture-pack hot-swap, CRT masks, and 2-player online multiplayer (Quick Join
codes, no port forwarding). In-game overlay: Esc / F1 / controller Back;
Alt+Enter / F11 toggles fullscreen.

## ROM (required — and a trap)

**US v1.0 or US Rev A/v1.1 only**, normalized big-endian z64 sha1 must be one
of:

- `0cb115d8716dbbc2922fda38e533b9fe63bb9670` (US v1.0)
- `6d96743d46f8c0cd0edb0ec5600b003c89b93755` (US Rev A / v1.1)

DKR-R identifies the ROM by hash before renderer/audio startup and **hard
refuses anything else** ("This Diddy Kong Racing revision or modified ROM is
not supported", exit 3). Byte order (`.z64`/`.v64`/`.n64`) is auto-detected.

Trap we hit (2026-09-28): the active `roms_mid/n64/Diddy Kong Racing (USA)
(En,Fr) (Rev A).n64` is a **modified dump** (normalized sha1 `a534d2f2…`,
CRC32 `4B6724F7` — no database match) and DKR-R rejects it. The pristine Rev A
backup at `roms_mid/n64/originals/Diddy Kong Racing (USA) (En,Fr) (Rev A).n64`
verifies clean and is what the role uses (`dg_dkr_rom`). A second clean copy
lives at `ROMS_FINAL/sdcard-bundle-6666/Diddy Kong Racing (U) (V1.1) [!].zip`.
Do not "fix" this by pointing the role at the modified dump.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-dkr-recomp.yml     # or: site.yml --tags dkr_recomp
ansible-playbook install-dkr-recomp.yml -e dg_dkr_revert=true
```

The launcher `bin/dkr-r` passes the sha1-verified ROM via `--rom`, which skips
the ROM picker and boots straight in; it also pins the Vulkan ICD to nvidia
and focuses DP-1. On first run DKR-R caches a normalized copy of the ROM as
`dkr.us.v77.z64` inside its config dir. Saves, settings, Controller Paks and
mods live in `~/.config/dkr-port` inside the box; texture packs go in
`~/.config/dkr-port/` per upstream's TEXTURE_PACKS.md (the community HD pack
is distributed via the DKR-R Discord).

Verified 2026-09-28 on the box: RTX 5090 Vulkan device detected, clean Rev A
dump accepted, game booted. The harmless `Error opening mod …/mods/legacy:
Mod is missing a mod.json` line on startup is upstream's empty-mods-dir stub,
not a problem.
