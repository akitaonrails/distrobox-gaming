# Driveclub shadPS4

Driveclub is configured as the only first-class shadPS4 target in this setup.

Current defaults:

```sh
DG_SHADPS4_TITLE_ID=CUSA00003
DG_PS4_ROM_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4
DG_SHADPS4_GAME_DIR=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003
DG_PS4_FIRMWARE_MODULES=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4-firmware/11.00_sys_modules
```

The canonical layout is a clean PS4 root containing the extracted game
directory only:

```text
$DG_PS4_ROM_ROOT/
  CUSA00003/
    eboot.bin
    ...
```

Do not treat raw `.pkg` files or Windows extraction tools in `$DG_PS4_ROM_ROOT`
as part of the normal runtime layout. The expected patch target is Driveclub
v1.28.

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

The desktop launcher uses the extracted game directory directly:

```sh
shadps4 -g "$DG_SHADPS4_GAME_DIR" -p "$DG_BOX_HOME/.local/share/shadPS4/patches/Driveclub.xml" -f true
```

ES-DE should point to `$DG_PS4_ROM_ROOT/$DG_SHADPS4_TITLE_ID/eboot.bin` and run
`shadps4 -g %ROM% -p ...`, which keeps the library view aligned with the clean
directory layout.

If Driveclub fails because of sysmodule behavior, the official patch XML also
has a `Run without sysmodules` option upstream. It is not enabled here because
it can remove text and slow boot. Treat it as a fallback after inspecting logs.

## Local PKG Tools

For future PS4 PKG debugging, keep the locally built `pkg_pfs_tool` here:

```text
/mnt/data/distrobox/gaming/tools/pkg_pfs_tool
```

The built binary is:

```text
/mnt/data/distrobox/gaming/tools/pkg_pfs_tool/build/pkg_pfs_tool
```

Notes from the current attempt:

- the upstream `pkg_pfs_tool` repo needed a small local CMake fix so it uses
  its bundled `mbedtls 2.24.0` headers instead of Arch's incompatible
  `mbedtls 3` headers
- `blz-dc.pkg` and the v1.28 patch identify as `CUSA00003`
- the tool can be used for `--help` and should stay available for future tests
- on the current Driveclub retail PKG, `-i` and `-l` failed because the
  required retail entry decryption keys/passcode are not available locally
- this means the tool is preserved for future work, but it is not currently a
  complete extraction path for the retail Driveclub PKGs on this machine
