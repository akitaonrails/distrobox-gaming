# OutRunners PC port

[cheviman/outrunners-port](https://github.com/cheviman/outrunners-port/releases/tag/v1.1.0)
v1.1.0 is installed as a native Linux game. Run `ansible-playbook
install-outrunners.yml` from `ansible/`; the role stages the SHA256-pinned Linux
tarball in `ROMS_FINAL/PC/releases/`, extracts it to the box home and adds
**OutRunners · PC Port** and **OutRunners Arcade · PC Port** launchers.

The owned `ROMS_FINAL/arcade/mame/orunners_dup1.zip` is the World MAME set.
Upstream `tools/verify_rom.py` verified all 17 required files; the role also
checks its whole-file SHA256 before linking it beside both binaries as
`orunners.zip`. Neither the ROM nor the generated assets are copied into Git.

The console build uses SDL2 GameController input: d-pad or left stick steers,
A/RT accelerates, B/LT brakes, shoulders shift, Y selects music and Start
pauses. The arcade build also accepts a controller. The role seeds
`~/.local/share/OutRunners/outrunners.ini` once with fullscreen, 16:9, smooth
pixel scaling and an FPS display. The original game is a pixel game paced at
60 FPS; fullscreen scales it to the 4K desktop rather than rendering new 4K
detail. `fps=1` shows the actual rate; it is not an uncapped mode. Arcade
video options are controlled in its running UI.

The connected 8BitDo Ultimate 2 (`2dc8:310b`) was detected by host SDL2 as a
mapped GameController. Button behavior and measured game FPS still need an
in-game check.

EEPROM, bookkeeping, controls and settings files in the user-data folder are
registered for save backup. The first run extracts ROM assets there; those
generated assets are omitted from backup.
