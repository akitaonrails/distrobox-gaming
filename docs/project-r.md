# ProjectR — `install_project_r`

[ProjectR](https://t3hd0gg.com/project-r/) (T3hD0gg) is a **native Vulkan port
of the arcade games San Francisco Rush: The Rock and San Francisco Rush 2049**
for Windows/macOS/Linux. No emulator, no ROM set — the port reimplements the
game engines and reads the original arcade hard-drive dumps. Opt-in role;
installed 2026-09-25 at `v0.7.1`.

## Assets (required)

Neither game is playable without original assets. Both come from the
[Project R Assets pack on archive.org](https://archive.org/details/project-r-assets-v-0.6.0.7z)
(sha1-pinned, kept on the NAS at `ROMS_FINAL/PC/project-r/` and extracted to
`assets/` beside it):

- **Rush: The Rock** — `sfrushrk.chd` hard-drive dump + the four audio ROMs
  (`audio.u62/u61/u53/u49`; the role unpacks the pack's `audio.zip` in place,
  and the zip itself is also accepted). Optionally `sfrush.chd` adds the white
  car color.
- **Rush 2049** — `sf2049se.chd` (Special Edition) or `sf2049te`/`sf2049tea`
  (Tournament Edition) hard-drive dump.

**One-time setup is in-game**: start ProjectR, and from the main menu choose to
set up each game, pointing the file dialogs at the extracted assets on the NAS.
Input is **gamepad/wheel only** — keyboard and mouse are not supported yet, so
do the setup with the 8BitDo. Setup state + config live in
`~/.config/ProjectR/project-r.toml` in the box (`[assets.setup_complete]`).

## Install / run / revert

```sh
cd ansible
ansible-playbook install-project-r.yml     # or: site.yml --tags project_r
ansible-playbook install-project-r.yml -e dg_projectr_revert=true
```

The role hash-pins the AppImage (`project-r-0.7.1-linux-x86_64.AppImage`) and
the asset pack on the NAS, installs the AppImage to `tools/project-r/`
(version-gated), and deploys `bin/project-r` (nvidia Vulkan ICD pinned, focuses
DP-1) + a Walker entry "ProjectR · SF Rush".

**Direct boot flags**: `project-r --rtr` skips the menu into Rush: The Rock,
`project-r --2049` into Rush 2049 (once each game is set up).

Notes: Vulkan 1.2 required (RTX fine); interface scaling is in Settings >
Display if the menu text is too small at 4K; pausing is not implemented yet —
quit via the Options menu (Start/Esc). ogm gets this entry via web-page update
polling (no GitHub repo): the regex keys on the Download section's first
AppImage link, which is always the current version.
