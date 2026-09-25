# Road Rash 64 Recompiled (`install_roadrash64_recomp`)

[linkssy2/RoadRash64Recompiled](https://github.com/linkssy2/RoadRash64Recompiled)
is a native **N64 recompilation** of Road Rash 64 (N64Recomp + N64ModernRuntime
/ RT64), with 60 FPS presentation, MAX LOD, widescreen, a draw-distance slider,
custom-music rotation and experimental multiplayer. Runs on the RTX via Vulkan —
no emulator.

The **v1.3.1 Linux build** (CalenCyr's native contribution) ships as an
AppImage; you supply your own **Road Rash 64 USA v1.0** ROM.

## Install

```sh
cd ansible
ansible-playbook install-roadrash64-recomp.yml   # or: site.yml --tags roadrash64
scripts/install-host-launchers.sh                # refresh the host menu entry
```

Launcher `bin/roadrash64`; host/Walker entry **"Road Rash 64 · Recompiled"**;
`ogm` id `roadrash64`. Revert with `-e dg_rr64_revert=true` (removes the launcher
+ install dir; your ROM and `~/.config/RoadRash64Recompiled` are untouched).

## How it works

- Downloads the pinned `RoadRash64Recompiled-v1.3.1-Rev2-Linux-Experimental.zip`
  (sha256 in `group_vars/all/roadrash64_recomp.yml`) and extracts the AppImage +
  `music/` to `tools/roadrash64-recomp/`.
- The role verifies your ROM is USA v1.0 (normalized z64 SHA-1
  `87727a298f583ec8325f5655088ff21e37b335b2`) — the `.n64` in `roms_mid/n64`
  matches — and fails early with a clear message otherwise.
- The launcher runs the AppImage with **`--auto-rom <rom> --force-vulkan`**: the
  recomp validates the dump, stores the normalized ROM at
  `~/.config/RoadRash64Recompiled/rr64.n64.us.1.0.z64`, and **auto-starts** — so
  the "Select Game ROM" launcher screen never appears. DP-1 focus + nvidia
  Vulkan ICD are set in the wrapper. 8BitDo works via SDL.

Saves + settings live in `~/.config/RoadRash64Recompiled/`. **Custom music:**
drop `.ogg/.flac/.mp3/.wav/…` into `tools/roadrash64-recomp/music/` (FFmpeg is
bundled). Extra keybinds (Eject from Bike, Spoke Jam) are in Settings.

## ROM

Road Rash 64 (USA) v1.0, 32 MiB, normalized SHA-1 `87727a29…`. The recomp accepts
`.z64/.n64/.v64` and normalizes; override `dg_rr64_rom` if yours lives elsewhere.

## Updating

Bump `dg_rr64_release_tag` / `dg_rr64_asset_name` / `dg_rr64_asset_sha256` (from
the [releases](https://github.com/linkssy2/RoadRash64Recompiled/releases), take
the sha256 from the release's `SHA256SUMS.txt`) and re-run; the extract is
version-gated.
