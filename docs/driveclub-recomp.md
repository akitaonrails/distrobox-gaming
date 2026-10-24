# DriveClub Recomp

[OverkillLabs3/driveclub-recomp](https://github.com/OverkillLabs3/driveclub-recomp)
v0.3.1 is staged as an optional Windows runtime alongside the working shadPS4
Driveclub installation. The pinned release ZIP is stored under
`dg_roms_final_root/PC/`; `install-driveclub-recomp.yml` extracts it to
`dg_box_home/tools/driveclub-recomp` without copying or changing game data.

The US PS4 title `CUSA00093` is now present as a base 1.00 PKG and a 1.28
update PKG under `dg_dcr_source_root/packages/`. Both were extracted to
separate `dg_dcr_source_root/dump/` subdirectories. Each PKG's original
`param.sfo` was copied from its metadata table into the matching dump's
`sce_sys/` directory because the PKG extractor omitted it. The base dump has
`game000.dat`; the update dump has `eboot.bin` and reports `APP_VER=01.28`.
The role recognizes them and renders a **DriveClub Recomp** desktop entry.
The original EU `CUSA00003` shadPS4 installation remains untouched.

**2026-10-23 update:** v0.3.1 replaces the program and runtime files over the
existing install. Its release notes describe fixes for race-exit hangs,
rendering errors, and Wine/Proton two-thread defaults, plus DLSS/FSR upscaling
options. The role retains `launcher.ini`, `data/user`, `mods/`, logs, and the
Proton prefix. The installed ZIP is SHA256-pinned and kept under
`dg_roms_final_root/PC/` for rebuilds. These new graphics options are available
in the launcher; existing user settings are left in place.

This 1.28 update is explicitly labeled **Patched 60FPS**, a repack. Upstream
tested CUSA00093 v1.28 but says repacked dumps are untested. The release
requires Windows 10/11. A controlled `driveclub-recomp --play` smoke test
through GE-Proton11-1 prepared the executable, started `DriveClubGame.exe`,
opened a `DRIVECLUB™` window, and logged the RTX 5090 Vulkan device. Gameplay,
frame rate, rendering quality, saves, and controller input still need a
hands-on check.

**2026-10-24: the endless "Downloading" tours were an upstream bug, fixed in 0.3.0.**
The Tour events stuck on "Downloading" after the tutorial are upstream issue #95,
fixed in 0.3.0 ("endless Downloading on every track and car after the tutorial").
0.2.4 also fixed the exact crash this box hit ("read access to
0000000000000000 at guest offset 0x64db13"), the career event-start freeze
(#23/#24/#49) and quiet stereo audio. The role now pins **0.3.1**, which adds
DLSS/FSR **upscaling**, HDR10, graphics detail/effects options, a Detail tab,
wheel support and VRR pacing. The operator's profile (archived during
diagnosis) was restored — the bug was runtime-side, not save corruption.

**2026-10-18: crash after the intro, diagnosed and fixed.** The first
hands-on run of v0.2.1 crashed right after the intro (guest NULL read at
32 s, log in `logs/`). Upstream's 0.2.2/0.2.3 target exactly this class:
0.2.2 turned **Unlock DLC content** off for everyone (its missing Nissan R34
livery template caused race-start crashes; our verified setup sets
`dg_dcr_unlock_dlc: true` after the template guard fix) and fixed repacked-dump version handling; 0.2.3 replaced
the event-start lock (#23/#24) and added device-lost self-healing. After the
0.2.3 upgrade the intro passes cleanly (user-confirmed; 120 s smoke run with
zero faults). Known still-open: event-start freezes in career time trials
(#24) — if a race start freezes, it is that issue, not our setup.

Since v0.2.3 the recomp also accepts the **European CUSA00003 v1.28** dump;
the EU shadPS4 dump in this library could feed a second install if ever
needed.

The source path defaults to `dg_dcr_source_root`, derived from
`dg_roms_final_root`. Override it in `host_vars/localhost.yml` if moving the
dump. The role points the launcher at separate `dg_dcr_base_dir` and
`dg_dcr_update_dir` and seeds its settings only when absent. To reapply:

```sh
cd ansible
ansible-playbook install-driveclub-recomp.yml
```

The default launcher settings request 4K output and 60 FPS with deltatime,
show the FPS counter, and set `unlock=1` for DLC content. This machine's
`patches_enabled.txt` also enables the 4K internal resolution patch, which
upstream marks `[DEPTH BUG]`; the role preserves that user choice. These are
configured targets, not measured gameplay results. The recomp builds its DLC overrides from the game's
vehicle, tour and livery lists when Play is pressed; its own source says the
toggle is on by default and does not modify the game dump. The controlled
launch produced all three override files (`newdata/vehicles.csv`,
`data/databases/dc.tour`, and `liveryeditor/assets/assets.txt`) under
`data/unlock/`, confirming that DLC unlock preparation completed. Actual
in-game availability remains unverified. The archive also
contained 117 small `CUSA00093` DLC entitlement PKGs under
`dg_dcr_source_root/packages/dlc/`, retained for PS4 use but not needed by the
recomp's built-in unlock.

The recomp has native gamepad input for Xbox, PlayStation, Switch Pro and
8BitDo controllers, but controller input has not been tested on this host.
The PCMRace article's “mods” refers to the recomp's loose-file `mods/`
override mechanism; it does not provide a separate mod pack. The role creates
that folder and preserves it, as well as settings, logs and saves on future
updates. The five redundant multipart RAR files were removed after verified
extraction and decryption, recovering about 36 GB; the two source PKGs and
decrypted dumps remain on the NAS.
