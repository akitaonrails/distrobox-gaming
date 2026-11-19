# Gran Turismo 3: A-Spec — PC Enhanced

`install_gt3_pc_enhanced` installs [Silentwarior112/GT3-PC-ENHANCED](https://github.com/Silentwarior112/GT3-PC-ENHANCED),
a **decompilation** of the PS2 Gran Turismo 3 engine ported to Windows (C++,
Direct3D 11), run in the gaming distrobox under **Wine + DXVK** on the RTX.

Opt-in, like every game role:

```sh
cd ansible
ansible-playbook install-gt3-pc-enhanced.yml
# or: ansible-playbook site.yml --tags gt3_pc_enhanced
```

## Why this over GT3 Revisited

Both play GT3 from the user's own NTSC-U disc and neither redistributes game
data. They are different kinds of port:

- **GT3 Revisited** (`install_gt3_revisited`) is a *from-scratch
  reimplementation* of the engine — native Linux/Vulkan, online multiplayer,
  but no HD texture support.
- **GT3 PC Enhanced** is the *real decompiled game code*, so it is
  behaviour-accurate, and it ships a working **hash-keyed HD texture
  replacement** system (dump with F10, drop upscaled replacements back in).

PC Enhanced is the better single-player experience and is the one we keep;
GT3 Revisited was retired once this was confirmed working.

## How it runs

The two shipped binaries (`gt3launcher.exe`, `gt3pc.exe`) are **32-bit**
(PE32 i386), plus the bundled `SDL3.dll` for gamepad input. The role:

- deploys only the runtime files (the release also carries 135 MB of
  `.pdb`/`.ilk` debug artifacts, which are left out);
- builds a dedicated Wine prefix with **DXVK 3.1.1** and a native
  `d3dcompiler_47` installed into **both** architectures (the 32-bit game
  loads `d3d11` from `syswow64`);
- **pins GLX** (`UseEGL=N`) — Wine 10.17+ EGL otherwise picks the iGPU /
  llvmpipe and renders in software;
- maps the `winebus` service to SDL so the 8BitDo maps as an Xbox controller;
- seeds **4K fullscreen + max graphics** (16× AF, full reflection
  detail/resolution, all car reflections) once, so later in-game changes win;
- runs **without gamescope** — the game's own Direct3D 11 fullscreen presents
  borderless 4K on the RTX.

## One-time disc install

There is **no headless install CLI** — the upstream GUI launcher unpacks the
game files from the disc. The role maps Wine **drive D:** to the PS2 ROM folder
so the picker finds the image. On a fresh box the role stops with an assertion
until the game files exist; to create them:

```sh
~/bin/gt3-pc-enhanced build     # opens the GUI launcher
```

In the launcher: **Start** → **Install game files…** → pick the GT3 disc from
**D:** (its Play tab) → let it unpack into `bin/data_US`. Re-run the role
afterwards; it then seeds the graphics defaults and passes.

`~/bin/gt3-pc-enhanced` with no argument plays the installed game.

## HD textures

The replacement system is keyed by **PC Enhanced's own dump hashes** (F10 in
game → `tex_replacements/dumps`), then add a replacement folder in the
launcher's Textures manager. **PCSX2 HD texture packs are not compatible** —
their filenames are PCSX2 GS-upload hashes, a different scheme, so none of them
match. The images could in principle be re-keyed by a dump-and-match pipeline,
but that is a separate effort, not a drop-in.

## Disc, saves, paths

- Disc: `dg_gt3pc_disc` — the owned NTSC-U image (SCUS-97102 / PBPX-95503),
  the same one GT3 Revisited reads. Override per host in
  `host_vars/localhost.yml`.
- Saves live in `tools/gt3-pc-enhanced/bin/saves` and are registered in
  `dg_save_sets` (`gt3-pc-enhanced`).
- Everything else is derived from `dg_box_home` / `dg_roms_final_root`; see
  `ansible/group_vars/all/gt3_pc_enhanced.yml`.
