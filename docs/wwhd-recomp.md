# The Wind Waker HD — Recompiled (`install_wwhd_recomp`)

[ZeldaWWHDRecomp/ZeldaWWHDRecomp](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp)
is a **static recompilation of the Wii U (USA)** *The Legend of Zelda: The Wind
Waker HD*: the PowerPC code is translated to C ahead of time, Cafe OS is
reimplemented natively, and GX2 graphics run directly on **Vulkan** — no Cemu,
no GPU command emulation. Runs natively on the RTX; native **SDL3** gamepad, so
the 8BitDo works out of the box. Frame interpolation (60/120/240 fps), gyro
aiming, and a mod manager are in the in-game settings overlay.

It ships an **official native Linux x86_64 build**, but **no game code** (legal):
the first run **builds the game locally from your own Wii U dump**, so this role
drives that headlessly at install time.

## Install

```sh
cd ansible
ansible-playbook install-wwhd-recomp.yml       # or: site.yml --tags wwhd_recomp
scripts/install-host-launchers.sh              # refresh the host menu entry
```

Launcher `bin/wind-waker-hd-recomp`; host/Walker entry **"Wind Waker HD ·
Recompiled"**; `ogm` id `wwhd-recomp`. Revert with `-e dg_wwhd_revert=true`
(removes the launcher + install dir — **back up `data/save` first**; your Wii U
dump is untouched).

## How it works

- Downloads the pinned `WindWakerHD-v0.2.7-linux-x86_64.zip` (sha256 in
  `group_vars/all/wwhd_recomp.yml`) and flattens it into `tools/wwhd-recomp/`
  (so the binary + `tools/` + `portable.txt` sit beside the persistent `data/`;
  a version re-extract never wipes saves).
- Runs the setup's **non-interactive CLI** to build the game once:
  `python3 tools/installer/setup.py --yes --game-dir <USA folder> --data-dir
  data --no-launch --no-shortcuts --jobs 16`. It downloads a pinned **zig**
  toolchain (sha256-checked, ~53 MB, once, into `data/toolchain`), translates the
  game's PowerPC to C and compiles it to `data/bin/wwhd` (~a minute on this box).
  The box `python3` (≥3.8) is used directly, so the setup's private-Python
  download never triggers. Idempotent: re-runs skip the build when
  `data/bin/wwhd` exists and `data/install.json` already records this release.
- The front `wind-waker-hd` binary reads `data/install.json` and launches
  `data/bin/wwhd` with the recorded `--game` / `--save`. The launcher focuses
  **DP-1** and pins the nvidia Vulkan ICD (GX2→Vulkan on the RTX, not the iGPU).

Saves (`data/save`, incl. Picto Box pictures) are registered in `dg_save_sets`
as `wwhd-recomp`; a rebuild re-creates the game from your dump but the saves are
restored from the NAS backup.

## Your dump

Uses an **extracted USA `code/content/meta` folder** (no keys needed) — set to
`dg_wwhd_game_dir` (default
`ROMS_FINAL/wiiu/The Legend of Zelda The Wind Waker HD (USA)`), used **in place**
(not copied). A Cemu `.wua` (decrypted, no keys) or a `.wux`/`.wud` disc image
(+ title key + Wii U common key) also work — point the setup at `--archive` /
`--image` instead by editing the build task if you prefer those. The USA version
is the one the recomp targets.

## Updating

Bump `dg_wwhd_release_tag` / `dg_wwhd_asset_name` / `dg_wwhd_asset_sha256` (+
`dg_wwhd_asset_subdir`) from the
[releases](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp/releases) and
re-run; the flatten is version-gated and the game rebuilds once on the first
launch after the new binary lands (saves under `data/save` are preserved).
