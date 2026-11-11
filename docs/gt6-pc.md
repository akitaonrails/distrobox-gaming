# Gran Turismo 6 PC

[Mabec-games/Gran-Turismo-6-PC](https://github.com/Mabec-games/Gran-Turismo-6-PC)
packages a **GT6-tuned RPCS3** with a launcher: the patched emulator that fixes
GT6's race-time freezes, stale-band rendering and save-state bugs, plus
graphics patches (100–300% internal resolution, ultrawide, Sharper MLAA, FSR1 +
CAS, 16× AF, sharp shadows, 60 FPS menus), firmware/update installers, gamepad
and wheel setup (a G27 with force feedback), mods and LAN.

```sh
cd ansible && ansible-playbook install-gt6-pc.yml     # or site.yml --tags gt6_pc
```

| | |
|---|---|
| Release | `v1.1.3` — `GT6-Launcher-x86_64.AppImage` (245 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Game | owned GT6 dump at `ROMS_FINAL/ps3/Gran.Turismo.6.PS3-DUPLEX` (Europe BCES01893) |
| Install | `tools/gt6-launcher/v1.1.3/squashfs-root` (unpacked once) |
| Data | `~/.local/share/gt6-launcher/` — `launcher.json`, RPCS3 config/saves, firmware, caches |
| Launcher | `bin/gt6` (GUI) / `bin/gt6 play`; entry **Gran Turismo 6 · PC** |

## How it runs here

The launcher and its bundled RPCS3 run **on the host**, not in the box: RPCS3 is
an AppImage that needs FUSE, which the restricted box does not have, and the
box's RPCS3 cannot verify the installed firmware. The data directory stays in
the box home (`XDG_DATA_HOME` is pointed at it), so saves, the launcher profile
and the emulator config are shared and covered by `dg_save_sets`.

The role stages and unpacks the AppImage, seeds `launcher.json` with the max
profile (4K output, **300%** internal resolution, Sharper MLAA, 16× anisotropic,
sharp shadows, 60 FPS menus), registers the disc with `add-game`, and installs
the official PS3 firmware (Sony's PUP, ~200 MB) when it is missing.

## Updates

The official 1.02 → 1.22 chain is ~10.5 GB and is **not** downloaded by
default. Once, from the launcher or command line:

```sh
bin/gt6 updates            # resumable, checksum-verified
```

or set `dg_gt6_install_updates: true` before running the playbook. First boot
after 1.22 also runs the game's one-time ~20 minute data install.

## Settings worth knowing

`launcher.json` holds the profile. The role's baseline is the highest supported
here; the launcher's settings menu rewrites it and later changes survive. In
game, set *Display Size (HD) = 100* (removes the 90% border), the units, and
R2/L2 accelerate/brake for a pad; wheels go through the launcher's wizard.

## Verified here

The role registers BCES01893, installs firmware 04.9300 and reruns `changed=0`.
`bin/gt6 play` starts the patched RPCS3 at **59.94 FPS on Vulkan** with the GT6
window; the updates, wheel force feedback, mods and LAN were not exercised.

## Notes

- Europe BCES01893 is the supported disc in this library (NA BCUS98296 also
  works). Other regions are partly supported by upstream.
- Saves are RPCS3's `dev_hdd0/home/.../savedata` under the data dir and are
  mirrored as the `gt6` backup set together with `launcher.json`.
- The box's own RPCS3 installation (`install_rpcs3`) is untouched; GT6 uses its
  own patched build and config directory.