# Driveclub shadPS4

Driveclub is configured as the only first-class shadPS4 target in this setup.

Current defaults:

```sh
DG_SHADPS4_TITLE_ID=CUSA00003
DG_PS4_ROM_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4
DG_PS4_FIRMWARE_MODULES=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4-firmware/11.00_sys_modules
```

Local game packages identify as `CUSA00003`. The expected patch target is
Driveclub v1.28.

Runtime files:

- `$DG_BOX_HOME/.local/share/shadPS4/custom_configs/CUSA00003.toml`
- `$DG_BOX_HOME/.local/share/shadPS4/patches/Driveclub.xml`
- `$DG_BOX_HOME/.local/share/shadPS4/sys_modules/`

Known-good shadPS4 guidance collected from the current setup:

- use game version 1.28
- use the official `60 FPS with deltatime` patch
- enable readbacks
- disable readback linear images
- keep window/internal size at 1920x1080
- use vblank frequency equivalent to the old vblank divider 2 setup
- symlink PS4 11.00 sys_modules instead of copying them

The desktop and ES-DE launch command is:

```sh
shadps4 -g CUSA00003 -p "$DG_BOX_HOME/.local/share/shadPS4/patches/Driveclub.xml" -f true
```

If Driveclub fails because of sysmodule behavior, the official patch XML also
has a `Run without sysmodules` option upstream. It is not enabled here because
it can remove text and slow boot. Treat it as a fallback after inspecting logs.

