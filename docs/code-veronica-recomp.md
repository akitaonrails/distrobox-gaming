# Resident Evil Code: Veronica X HD Recomp

The optional `install_code_veronica` role installs
[kastieloficial's v1.1.11 Windows release](https://github.com/kastieloficial/RE-Code-Veronica-PS3-HD-Recomp-PC/releases/tag/v1.1.11)
through GE-Proton. Run `ansible-playbook install-code-veronica.yml` from
`ansible/`. The pinned ZIP is downloaded into `ROMS_FINAL/PC/releases/` and
installed under `dg_cv_root`; `current` points at the selected version.

## Game assets

The PS3 collection contains the US PSN **NPUB30467** install PKG, not an ISO.
Its extracted `PARAM.SFO` reports `TITLE_ID=NPUB30467` and `APP_VER=01.00`,
the exact version this port accepts. The role uses an already installed RPCS3
game folder at `dg_cv_game_dir` or extracts the base PKG with the repository's
PS3 PKG extractor on a clean box. It does not use the separate crack PKG.

The US release requires the matching `.rap` license. The local PS3 collection
and RPCS3 `exdata` did not contain one on 2026-10-29. A launcher screenshot
confirmed that the NPUB30467 game folder is recognized but shows **License
missing**. Place your license at
`dg_cv_rap_file` (or override that variable in `host_vars/localhost.yml`),
then rerun the playbook. The role deliberately fails with this exact request
after staging the port when the license is missing. The desktop launcher
still opens; when Play is pressed, the port itself checks the `.rap` and
shows a license-required message before starting the game.

## Display and controller

The initial `cv_launcher.ini` is seeded only if missing: borderless 4K,
SMAA, 60 FPS with CPU interpolation, VSync on, FSR frame generation off,
automatic controller glyphs and full rumble. The port's original simulation
remains at 30 Hz; its 60 FPS option interpolates poses. Frame generation and
VSync are mutually exclusive. Forced anisotropic filtering was retired by
upstream in v1.1.8, despite older README text advertising 16x, so it is not
forced. Settings are under `dg_cv_user_dir` and later changes in the launcher
survive Ansible reruns. The port has native controller bindings for sticks,
triggers, shoulders, face buttons, D-pad and Start. The launcher screenshot
shows **Xbox controller connected**; controls during gameplay still need a
check once the license is present.

The release is Windows-only and uses Direct3D 12. GE-Proton provides the
D3D12-to-Vulkan path on Linux. A 20-second launcher smoke test stayed alive
and wrote the v1.1.11 startup log, but actual gameplay, rendering, controller
input and frame rate cannot be verified without the license. If graphics fail under Proton, check
`bin/run-log.txt` under the selected release before changing the baseline.

## Saves

The role links `bin/gamedata` to the stable `dg_cv_user_dir/gamedata` so saves
survive release changes. `dg_save_sets` backs up only that save directory;
the extracted game, shaders and EBOOT cache are reproducible. Re-render the
backup manifest with `ansible-playbook site.yml --tags backup_saves`, then
check `distrobox enter gaming -- sh -lc '$HOME/bin/backup-saves --dry-run'`.
