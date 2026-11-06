# Tekken Tag Tournament 2 PC recompilation

The optional `ansible/install-ttt2-pc.yml` playbook installs the [v0.1.7
recompilation](https://github.com/shihabal3amri/tekken-tag-tournament-2-pc/releases/tag/v0.1.7)
from the owned retail Xbox 360 disc. The Windows build runs through GE-Proton
11-1. The playbook pins the official installer and the matching Title Update 3
archive by SHA256, stages both in `ROMS_FINAL/PC/releases/`, and runs the
installer's `/silent` path. The installer checks the retail `Default.xex`, TU3
and patched image; a different disc fails with its exact error in the install
log. The release occupies about 13 GB after extraction and shader preparation.

Set `dg_ttt2_iso` if your retail USA/Europe disc is elsewhere. The default is
`ROMS_FINAL/xbox360/Tekken Tag Tournament 2 [RF].iso`. TU3 is extracted into
`ROMS_FINAL/xbox360-updates/tekken-tag-tournament-2/` with the required name
`TU_174Q22P_0000008000000.00000000000O2` (letter O before 2). The archive is
from [Digiex's TU3 listing](https://digiex.net/threads/tekken-tag-tournament-2-xbox-360-title-update-3-download-media-id-5d762d06.18732/)
for Title ID `4E4D0859` and Media ID `5D762D06`.

Run from `ansible/`:

```sh
ansible-playbook install-ttt2-pc.yml
```

The game lives in `dg_ttt2_install_dir` and the desktop entry calls
`dg_ttt2_launcher`. A dedicated Proton prefix at `dg_ttt2_compatdata` holds
the player data. The installer process is supervised for at most one hour and
its PID, parent, exit and output are recorded in
`dg_ttt2_tools/install-v0.1.7.log`; the installer's own progress log is moved
to `dg_ttt2_tools/setup-v0.1.7.log`. Rerunning the playbook skips a completed
release. The backup set mirrors only `saves`, `settings.ini`, server choices
and known servers; it excludes re-derivable shader caches, logs and net
sessions.

The role seeds missing settings at 3840×2160 borderless, FXAA, 16× texture
filtering, shadows on, VSync on and modest sharpening. It preserves all later
in-game changes. The port runs at the original 60 FPS game timing; that is a
configured cap, not a measured gameplay result. Display settings are under
**OPTIONS → DISPLAY SETTINGS**. The 8BitDo Ultimate 2 is expected to work via
the port's native XInput support under Proton. The full button map and rumble
still need an in-game controller check. Online play uses Steam and a community
server; the port can run offline without them.

On 2026-11-01 the owned ISO and TU3 passed the installer's checks, all 6,371
shader preparations completed, and a 45-second supervised launch reached the
Bandai Namco splash screen. The runtime log selected the RTX 5090 and reported
3840×2160, FXAA, 16× filtering, shadows and VSync. Gameplay frame rate and
controller buttons were not measured in that short launch. The test-created
Proton processes were stopped and reaped afterward.

Validate after installing:

```sh
ansible-playbook install-ttt2-pc.yml  # expect changed=0
../scripts/check-pc-layout.sh "$DG_PC_ROOT"
../scripts/check-launcher-wrappers.sh "$DG_BOX_HOME/bin" ../config/desktop/rendered
ansible-playbook site.yml --tags backup_saves
~/.local/bin/backup-saves --dry-run
```
