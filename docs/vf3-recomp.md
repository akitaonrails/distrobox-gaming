# Virtua Fighter 3 Recomp

[mr-finster/vf3-recomp](https://github.com/mr-finster/vf3-recomp) recompiles the
1996 Model 3 arcade game for native Linux. The opt-in install uses upstream's
`v0.1.10-alpha` x86-64 Steam Deck package, pinned by SHA-256. It does not use
Wine or copy the ROM into the install.

## Install and assets

```sh
cd ansible
ansible-playbook install-vf3-recomp.yml
# equivalent: ansible-playbook site.yml --tags vf3_recomp
```

The role requires the MAME **`vf3` Revision D** set at
`dg_vf3_rom_zip` (`dg_roms_final_root/arcade/model3/vf3.zip` by default). The
known archive SHA-256 is pinned in `group_vars/all/vf3_recomp.yml`; all 39
component CRCs match the port's upstream ROM list. `vf3a`, `vf3c`, and `vf3tb`
are different sets; the port does not support Team Battle. The launcher passes
`--roms` to read the NAS set in place. It checks that the file is present on
each launch.

The release archive is cached at `dg_vf3_archive`, then extracted into
`dg_vf3_gamedir`. A tag marker gates future extractions. Settings, EEPROM,
rankings, screenshots, and logs live separately in `dg_vf3_data_dir`; the
`vf3-recomp` save-backup set includes this directory. Reinstalling or updating
the binary does not replace existing game settings.

The desktop entry is **Virtua Fighter 3 · Recompiled** (`ogm` id
`vf3-recomp`). The box launcher is `dg_vf3_launcher` (`bin/vf3-recomp`).

## Display and controller

The initial `settings.ini` selects fullscreen on the preferred 4K display,
16:9, 6x internal scale, 2x antialiasing, GPU Auto, and smooth motion. GPU Auto
checks its output against the CPU renderer on startup and falls back if it
disagrees. The game runs its arcade simulation at about 57.5 frames per second;
smooth motion can show up to 120 pictures per second, paced by the display.
Those are configured limits, not measured gameplay performance. If the in-game
governor reduces scale or interpolation, use Display in the game's menu to
choose a stable setting. The role seeds `settings.ini` only when absent, so
later menu changes remain yours.

An unattended launch on this machine reached 1,200 game frames using the NAS
ROM. Its log reported the Vulkan renderer on the RTX 5090, GPU 3D startup
checked against the CPU picture, a 240 Hz screen, and VSync on. This was a
hidden smoke test; it did not measure visible gameplay FPS or input latency.

The port uses native SDL3 gamepad input: d-pad or left stick for movement,
X guard, A punch, B kick, Y escape, triggers and shoulders for combinations,
and Start to begin. View/Select or L3+R3 opens its menu; controls can be
remapped there. No gamepad was connected during installation, so physical
button input remains unverified.

## Updating

Check [upstream releases](https://github.com/mr-finster/vf3-recomp/releases),
then bump `dg_vf3_release_tag` and `dg_vf3_asset_sha256` together and rerun the
playbook. The ROM pin should change only when a different supported dump has
been verified against upstream's component list.
