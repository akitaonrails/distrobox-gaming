# VF4 Final Tuned (Ver. B) — native Naomi 2 recompilation

`install_vf4ft_recomp` installs **Virtua Fighter 4 Final Tuned (Ver. B)** (SEGA
AM2, Naomi 2, 2004) as a **native Linux program** built from
[djanice1980/VF4-Final-Tuned-Rev-B-Recomp](https://github.com/djanice1980/VF4-Final-Tuned-Rev-B-Recomp).
The game's SH-4 program is translated to C and compiled into an ELF **on this
box, from your own MAME `vf4tuned` set** — no emulator runs at play time; the
Naomi 2 hardware is modelled by the program and the picture is drawn on the GPU
through Vulkan.

Upstream ships **only a Windows release**, so this role does not download a
binary: it checks out the source at a pinned tag and runs the project's own
`tools/make_game.py --target linux` (system `clang` + `SDL3`). A build takes
about a minute.

## Requirements

- Your own MAME **`vf4tuned`** set in MAME layout, read-only on the NAS at
  `roms_rare/naomi2/`:
  - `vf4tuned.zip` (the 317-0387-COM PIC), sha256
    `39d1bddcaed763538d47083ef5423ba4266caef020da64bd36f16a39384b6e0b`
  - `vf4tuned/gds-0036f.chd` (the GD-ROM), sha256
    `aaef037ded8b4197fb65f35dda7f024cb94b707bb4a952c6baf3f6e3765a11eb`

  The set is never restaged or modified. Everything the build produces (the
  decrypted `data/VF41_S.BIN`, `data/dimm.key`, the ELF) stays local under the
  install and is never shared or committed.

- In-box toolchain (installed by the role): `clang`, `sdl3`, `pkgconf`,
  `python`.

## Install

```sh
cd ansible
ansible-playbook install-vf4ft-recomp.yml
```

or, within a full run, `ansible-playbook site.yml --tags vf4ft_recomp`.

The role is idempotent: `.dg-built-ref` records the built commit, so a rerun at
the same pin is a no-op. Bumping `dg_vf4ft_version`/`dg_vf4ft_commit` rebuilds
with `make_game.py --update` (keeps `user/` saves, does not need the set again).

## What the role does

1. Verifies the owned `vf4tuned` PIC and GD-ROM by sha256.
2. Installs the build toolchain in the box.
3. Checks out the source at the pinned tag and asserts the commit.
4. Builds the native ELF (`--set` first time, `--update` on a bump).
5. Confirms the binary's shared libraries resolve in the box (`ldd`).
6. **Primes the cabinet backup once.** The first cold boot writes its settings
   record with the network ON, so it stalls on the network time-out ("then it
   starts again"); priming `user/backup.bin` once (network off) means your first
   real launch boots straight through. Best-effort — it needs the desktop
   session; if it cannot run, the first manual launch regenerates the record
   itself (that one launch is slow, then every launch after it is fast).
7. Seeds `user/settings.txt` with the maximum-graphics display preset
   (`force: false`, so your in-game F10 changes are kept).
8. Deploys the launcher and the host desktop entry.

## Graphics

Seeded in `user/settings.txt` (the game owns the file after first launch):

| Setting | Value | Meaning |
|---|---|---|
| `renderer` | `gpu` | the Vulkan renderer (on the RTX) |
| `scale` | `4` | top internal resolution, 4 × 640×480 (height 1920) |
| `picture` | `16:9` | fills the 4K DP-1 panel (21:9 would letterbox a 16:9 screen) |
| `fullscreen` | `on` | uses DP-1's 3840×2160 desktop mode |
| `window` | `auto` | — |

The launcher pins the **NVIDIA Vulkan ICD** (`VK_ICD_FILENAMES`) so the GPU
renderer binds the RTX and never falls back to the iGPU, and focuses **DP-1**
before SDL picks its fullscreen display. Verified: GPU renderer on the RTX 5090
at 3416×1920, fullscreen on DP-1.

## Controls

Native SDL gamepad support with on-screen glyphs; the default pad layout is the
PlayStation 2 version's (square guard, triangle/cross punch, circle kick). The
8BitDo pad is seen as a standard gamepad. In-game: **F10** opens the settings
menu (Picture / Window / Internal resolution / Renderer / GPU / Controls),
**F3** the performance overlay, **F11** toggles fullscreen, **Enter/Start**
begins, coin slots on `5`/`6`.

## Saves

`user/` holds the cabinet backup RAM and settings record (`backup.bin`), the two
memory-card units (`user/cards/`) and `settings.txt`. Registered in
`dg_save_sets` as `vf4ft-recomp` (`tools/vf4ft-recomp/game/user`). The game
itself is rebuilt from the owned set on a from-scratch remount.

## Revert

Remove `tools/vf4ft-recomp`, `bin/vf4ft` and the desktop entry. The owned MAME
set on the NAS is untouched.
