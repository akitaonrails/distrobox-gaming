# RalliSport Challenge 2 Recompiled

The optional `install_rsc2` role installs
[RalliSportChallenge2-decomp](https://github.com/Mortify7612/RallisportChallenge2-decomp)
v0.7.0 as a native Linux game in the `gaming` distrobox. It downloads the
SHA-256-pinned Linux release, extracts the owned Xbox disc with `extract-xiso`,
and links the extracted files as `game/` beside the binary. The source ISO is
never modified. The extracted game data is kept on the NAS because the port
needs loose files for every launch; it occupies about 6 GB. The pinned
release archive is kept in `dg_rsc2_cache_dir` for rebuilds.

The tested input is `dg_rsc2_iso` in `dg_rom_heavy_root/xbox/`, titled
`RalliSport Challenge 2 (World) (En,Ja,Fr,De,Es,It).iso`. Its `default.xbe`
has Xbox title ID `4D530039` and SHA-256
`cb8b27aed4423fbfcd72876f05e40823cb7a333983996623e38bfa1407d9601e`.
The role validates this exact executable and essential content files. Override
`dg_rsc2_iso` or `dg_rsc2_game_dir` in `host_vars/localhost.yml` for a different
layout. Run `ansible-playbook install-rsc2.yml` from `ansible/` or use
`ansible-playbook site.yml --tags rsc2`.

The initial settings target 4K fullscreen with the game's 16:9 mode, 6×
internal resolution, 4× MSAA, 16× anisotropic filtering, ambient occlusion,
and a 120 FPS clock-based cap. The FPS overlay is on. The launcher writes
settings to `dg_rsc2_settings`; Ansible seeds them only when the file is
absent, preserving later user changes. The game handles timing above 60 FPS,
and this setup leaves Vulkan's mailbox presentation in place instead of
combining its optional FIFO VSync with the frame pacer. These are configured
targets, not measured gameplay results. If 120 FPS is unstable, select 90 or
60 in the pre-game launcher.

SDL gamepad support is native, including sticks, triggers, D-pad and rumble;
keyboard input remains enabled as a fallback. The launcher is **RalliSport
Challenge 2 · Recompiled** in the desktop menu. A 20-second headless boot read
the XBE and game content and selected the NVIDIA GeForce RTX 5090 Vulkan
device; it was stopped by the test timeout. The box's input enumeration saw
only a Moonlander keyboard at install time, so gamepad input, racing, and
measured performance still need a hands-on test.
