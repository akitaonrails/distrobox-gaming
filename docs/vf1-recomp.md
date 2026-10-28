# Virtua Fighter Recompiled (`install_vf1_recomp`)

[mr-finster/vf1-recomp](https://github.com/mr-finster/vf1-recomp) is an
unofficial native PC port of the 1993 SEGA arcade **Virtua Fighter** (Model 1
hardware). The NEC V60 program is statically recompiled to native code at
startup; the rest of the Model 1 board (TGP, rasterizer, tile layers, sound,
I/O) is reimplemented from MAME's work. The 3D renders on **Vulkan** on the RTX
— no emulator, no Wine. This is the way to actually play VF on the box; the
Wanszai Wine frontend in `install_model1` stays only as a fallback.

Upstream ships an **official native Linux build** (the Steam Runtime "sniper"
`deck` tarball), so this is a prebuilt-release role (no source build). You
supply your own MAME **`vf`** romset — the same one already on the NAS for the
Wine Model 1 frontend.

## Install

```sh
cd ansible
ansible-playbook install-vf1-recomp.yml       # or: site.yml --tags vf1_recomp
scripts/install-host-launchers.sh             # refresh the host menu entry
```

Launcher `bin/vf1`; host/Walker entry **"Virtua Fighter · Recompiled"**; `ogm`
id `vf1`. Revert with `-e dg_vf1_revert=true` (removes the launcher + install
dir; your `vf.zip` on the NAS is untouched — note that removes the `data/`
EEPROM/NVRAM + ranking names beside the executable, which the `backup_saves` role captures as the
`vf1-recomp` set).

## How it works

- Downloads the pinned `VirtuaFighterRecomp-deck.tar.gz` (sha256 in
  `group_vars/all/vf1_recomp.yml`) to `cache/vf1-recomp/` and unpacks the
  `VirtuaFighter/` folder into `tools/vf1-recomp/`. The binary is an x86-64 PIE
  with RUNPATH `$ORIGIN/lib` (bundled SDL3); the only system deps are zlib + the
  Vulkan loader, both already in the box (the role asserts `ldd` is clean).
- Extraction is version-gated on `.dg-installed-ref` and extracts **over the
  top**, so a version bump never wipes your `data/` saves or the `roms/` symlink.
- The role verifies `vf.zip` is the expected MAME set (sha256
  `ff288457…` — the NAS `roms_rare/model1/vf.zip`), then **symlinks** it into the
  gamedir's `roms/vf.zip`. Nothing is copied to the NVMe and the recomp never
  writes to the shared romset dir. The optional `model1io.zip` BIOS is not
  present and not needed (the recomp reimplements the I/O board).
- A `portable.txt` is dropped in the gamedir so settings, rankings and saves
  stay in `data/` next to the binary (self-contained + backed up), instead of
  leaking into `~/.local/share/Virtua Fighter Recomp`.
- The launcher `cd`s into the gamedir and runs `./vf`. DP-1 focus + the nvidia
  Vulkan ICD pin (`VK_ICD_FILENAMES` + PRIME offload) are set in the wrapper so
  the 3D runs on the RTX, not the AMD iGPU. 8BitDo works via the bundled SDL3.

In-game: tap **View/Select** for the menu (display, sound, controls, quit);
**View + LB/RB** cycles render scale / picture shape. **Display > 3D renderer**
is Auto (Vulkan) by default; force GPU or CPU there if needed.

## ROM

MAME `vf` set, `vf.zip`, at `roms_rare/model1/vf.zip` (shared with
`install_model1`). Override `dg_vf1_rom_src` / `dg_vf1_rom_sha256` if yours lives
elsewhere or is a different valid `vf` set.

## Updating

Bump `dg_vf1_release_tag` / `dg_vf1_asset_name` / `dg_vf1_asset_sha256` (from the
[releases](https://github.com/mr-finster/vf1-recomp/releases)) and re-run. The
version gate re-extracts over the top; your `data/` saves survive.
