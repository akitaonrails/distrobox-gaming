# Super Mario 64 DS — PC port (`install_sm64ds_port`)

A decompilation-based PC build of **Super Mario 64 DS** from
[tangos.dev](https://tangos.dev/downloads) (repo
[tangosdev/sm64ds-decomp](https://github.com/tangosdev/sm64ds-decomp), the same
group as Tango). It runs the real game code — physics, camera, every level via
the level-select, the minigames, and 4-player versus netplay. It ships **no game
data**: the game's filesystem is unpacked from your own SM64 DS `.nds` dump.

**There is no native Linux build** (the project's README and download manifest
both say so; its PC-port CI only link-checks ROM-free smoke targets on Windows).
The **official Linux path** is Proton: tangos.dev ships a helper kit
`sm64ds-port-linux.tar.gz` (`launch.sh` + `extract_assets.py`, by diemitchell)
that runs the Windows build through the Proton your Steam already uses. Proton —
not bare Wine — is required: the launcher is self-contained **.NET** and the game
is **D3D11**, and Proton's bundled .NET + DXVK are what make both work. Verified
booting under **GE-Proton11-1** on the RTX/DP-1.

## Install

```sh
cd ansible
ansible-playbook install-sm64ds-port.yml      # or: site.yml --tags sm64ds_port
scripts/install-host-launchers.sh             # refresh the host menu entry
```

Launcher `bin/sm64ds-port`; host/Walker entry **"Super Mario 64 DS · PC Port"**;
`ogm` id `sm64ds-port`. Revert with `-e dg_sm64ds_revert=true` (removes the
launcher + install dir incl. its Proton `.compatdata`; the NAS zip and your
`.nds` are untouched).

## How it works

- Extracts the Windows port zip to `Games/sm64ds-port/`, drops the vendored,
  pinned `launch.sh` + `extract_assets.py` (roles/install_sm64ds_port/files/)
  next to `SM64DSLauncher.exe`, and symlinks the user's dump
  (`dg_sm64ds_rom_src`, the EU release — EU and NA both work) into
  `PLACE YOUR ROM HERE/`.
- Runs **`extract_assets.py --ensure-current`** at install time: stdlib-only
  python3 (no ndspy, no pip) that validates the ROM revision and unpacks
  `extracted/dsd/files/` + `build/assets/{files,handles,nitrofs}.*` and assembles
  a hash-checked `build/assets/romdata.bin`. (This is the Linux port of the
  Windows launcher's PowerShell extractor, which can't run under Proton/Wine.) So
  the first launch is instant rather than spending ~a minute unpacking.
- Turns off the launcher's `SendCrashReports` + `AutoUpdate` in `settings.json`
  (we pin the build via Ansible).
- The launcher `bin/sm64ds-port` focuses **DP-1**, pins the nvidia Vulkan ICD +
  `DXVK_FILTER_DEVICE_NAME=NVIDIA` (DXVK on the RTX, never the AMD iGPU = black
  screen), and runs the official `./launch.sh`, which auto-detects the Steam
  Proton (GE-Proton / proton-cachyos live in the box's `compatibilitytools.d`),
  builds its prefix under `Games/sm64ds-port/.compatdata/`, and starts the game.

In-game: **F12** fullscreen, **F5/Esc** debug menu (level select, warp, character
swap), **F4** swap Mario/Luigi/Wario/Yoshi, **F8/F9** save/load state. Settings
(60 fps + smooth motion, key rebinds, multiplayer) are in the launcher UI.

## ROM

Super Mario 64 DS, EU or NA `.nds`, your own dump. Override `dg_sm64ds_rom_src`
for a different dump. The game extracts assets from it; the dump is never
modified. Keep it in `PLACE YOUR ROM HERE/` — after a port update the data is
rebuilt once on first launch.

## Updating

tangos.dev ships new builds periodically. Download the newer port zip, update
`dg_sm64ds_version` + `dg_sm64ds_zip`, and re-run (remove the install dir or bump
to force a re-extract). Refresh the vendored `launch.sh` / `extract_assets.py`
from a newer `sm64ds-port-linux.tar.gz` if the kit changes.
