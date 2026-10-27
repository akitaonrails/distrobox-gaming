# Doom 64 RT — `install_doom64_rt`

Path-traced **Doom 64: Retribution** — [jlrouzies-fr/doom64-rt](https://github.com/jlrouzies-fr/doom64-rt)
(gzdoom-rt engine + RTGL1 path tracing, DLSS 2 / FSR 2, A-SVGF denoiser).
Opt-in role; installed 2026-10-03 at `v0.1.21-linux-beta.2`.

## Native Linux AppImage (the #8 unblock)

Issue #8 parked this: RTGL1 ray tracing wouldn't initialize under distrobox
Wine ("needs real Proton RT/Vulkan plumbing"). Moot since 2026-09 — the
upstream-endorsed community port
[acolomba/doom64-rt](https://github.com/acolomba/doom64-rt) ships a **native
Linux x86-64 AppImage** (linked from upstream's README). No Wine, no Proton.
DLSS auto-selected on NVIDIA (RTX 5090 ✓); `D64RT_UPSCALER=dlss|fsr|none`
overrides. Caveat per the author: beta, tested on one machine (NVIDIA,
X11/XWayland).

## Game data (required)

The AppImage needs a `game/` dir beside it with:

| File | Source | Status |
|---|---|---|
| Doom 64: **Retribution v1.5** (whole archive — WAD, brightmaps, soundfont) | [ModDB](https://www.moddb.com/mods/doom-64-retribution) | ✅ `ROMS_FINAL/PC/releases/D64RTRv1.5.zip` |
| `D64MUS.PK3` (OGG music pack v1.3) | [ModDB addon](https://www.moddb.com/mods/doom-64-retribution/addons/doom-64-retribution-ogg-music-pack-v13) | ✅ `ROMS_FINAL/PC/releases/D64MUS.zip` |
| `doom2.wad` (DOOM II, required IWAD) | copied by the role from `Emulators/Doom/GZDOOM/DOOM2.WAD` | ✅ local |

The exact ModDB downloads are `D64RTRv1.5.ZIP` (28,465,541 bytes, MD5
`ddc3b438bb3a68306bc2900389b59b61`) and `D64MUS.ZIP` (73,344,335 bytes,
MD5 `91c5b71683f36260ab9b0e29643cea34`). The role uses the original
downloads directly from `ROMS_FINAL/PC`. The old `Doom64-RT` engine ZIP
in the PC collection has only a placeholder in its `game/` directory; it is
not either of these downloads.

The role extracts the Retribution archive, drops D64MUS.PK3 + doom2.wad in,
and verifies with the AppImage's own `./doom64-rt-*.AppImage check`.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-doom64-rt.yml
ansible-playbook install-doom64-rt.yml -e dg_d64rt_revert=true
```

Launcher `bin/doom64-rt` (Walker: **Doom 64 RT**), native fullscreen Vulkan
(no gamescope). Config/saves in `~/.config/doom64-rt` in the box. The ogm
update-check tracks the **acolomba fork** (not upstream).

Upstream extras left out: the **Unseen Evil** monster pack (needs a local
build, art not redistributable) and **DLSS Ray Reconstruction** (alpha, ships
off upstream — A-SVGF is the intended denoiser).
