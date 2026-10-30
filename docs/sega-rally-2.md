# Sega Rally 2 (original PC release)

The opt-in `install_sega_rally_2` role installs the original English 1999 PC
release with [sr2-patcher v0.9.2](https://github.com/pairomaniac/sr2-patcher/releases/tag/v0.9.2).
It does not use the 25th Anniversary repack: that repack's executable fails
the patcher's exact build check and previously crashed in Wine's renderer.
The original-disc route was found through [issue #3](https://github.com/akitaonrails/distrobox-gaming/issues/3).

## Assets and install

Place the original English install ISO and play BIN/CUE in
`{{ dg_roms_final_root }}/PC/games/Sega Rally 2 (1999 original PC discs)/`.
The three exact names and SHA-1 hashes are pinned in
`ansible/group_vars/all/sega_rally_2.yml`. The install ISO's European
Pentium III executable is 1,469,952 bytes, MD5
`51b3da97c3c73611d3516b65bb684cb5`, which the patcher recognizes.
Override `dg_sr2_discs_dir` in `host_vars/localhost.yml` if your owned discs
live elsewhere. The host needs `bwrap` so the downloaded patcher runs with
the network disabled and only its staging directory writable. The role
downloads the SHA256-pinned patcher to
`ROMS_FINAL/PC/releases/`, checks the disc hashes, installs and patches the
ISO, rips all 13 CD audio tracks, and publishes the complete install only
after those steps succeed. Its temporary staging directory is removed even
if a step fails.

```sh
cd ansible
ansible-playbook install-sega-rally-2.yml
```

Launch **Sega Rally 2 (Original PC)** from the menu or run
`{{ dg_box_home }}/bin/sega-rally-2` on the host. The script enters the
`gaming` distrobox itself. `sega-rally-2 status` checks the executable,
soundtrack, and dedicated Wine prefix. A second playbook run should report
`changed=0`. The role refuses to overwrite an unmarked game directory, and
subsequent runs leave saves and controller bindings intact.

## Display, frame rate, audio, and controller

The patcher supplies native widescreen and a 3840×2160 resolution option.
The role sets `Resolution = 3840X2160` in `SR2.CFG`, forces Wine's GLX path,
and offloads OpenGL to NVIDIA. The game runs directly on the 4K display;
Wine's EGL path had selected software rendering in the earlier headless
test. The 2026-10-30 installed-launcher test showed an RTX 5090 graphics
process and a 2560×1440 logical window on a 1.5-scaled 3840×2160 monitor.
The exact in-game resolution selection and sustained gameplay FPS were not
measured. Upstream does not document an external FPS cap; leave the game's
frame pacing at its patched default. Avoid adding a competing VSync or
uncapped debug override without a gameplay timing test.

The patcher reads `music/track02.wav` through `track14.wav` in place of CD
audio. All 13 files were produced; the installed game opened PipeWire audio
streams. Audible output and music during a full race were not verified.

The patcher adds XInput support: left stick steers, RT accelerates, LT brakes,
A/X shift, B handbrake, Y view, Start pauses, and the d-pad or stick moves
menus. The role maps Wine's SDL controller to XInput and disables duplicate
hidraw/input paths. In **Options → Device Settings**, bindings, deadzone,
and vibration can be adjusted. On 2026-10-30 the attached 8BitDo Ultimate 2
was visible only as USB ID `2dc8:6013`, without a physical gamepad input
device at first. Once the controller entered gaming mode, Linux exposed it as
`2dc8:310b`, Wine created `WINEXINPUT\\VID_2DC8&PID_310B`, and the game
repeatedly called `XInputGetState` for player 1. Wine opened that device at
index 0. No button press or rumble was exercised during the test. The
patcher's generated `SR2.CFG` has complete 1P and 2P controller bindings,
with 10% deadzone and 70% vibration.

## Saves and updates

The game writes `SR2_SAVE.DAT` beside its executable. The patcher keeps
controller bindings and display settings in `SR2.CFG` and `SR2.DSP`.
`dg_save_sets` backs up all three through the `sega-rally-2` set; the rip,
extracted game, and patcher are reproducible and are not backed up. To update
the patcher, review its release notes and binary compatibility first; do not
rerun the ISO installer over a played save.
