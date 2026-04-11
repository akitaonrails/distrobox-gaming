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

For future PS4 PKG debugging, keep the working `ShadPKG` build here:

```text
/mnt/data/distrobox/gaming/tools/ShadPKG
```

The working CLI binary is:

```text
/mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg
```

What worked:

- `shadpkg sfo-info blz-dc.pkg` correctly reads `CUSA00003`
- `shadpkg pfs-info blz-dc.pkg` and the v1.28 patch both work
- `shadpkg extract blz-dc.pkg ...` succeeds
- `shadpkg extract Driveclub.v1.28.PATCH.REPACK.PS4-GCMR.pkg ...` succeeds

What this proved:

- the base and patch PKGs are readable and extractable on Linux with `ShadPKG`
- the union of extracted base+patch files has nothing missing compared to the
  live `CUSA00003` tree
- the repeated `/app0/audio/fmodstudio/*.bank` open failures in shadPS4 are not
  explained by missing extracted filesystem files from the PKGs
- this points more toward shadPS4 runtime handling of Driveclub's packed data
  layout than a simple bad extraction

Discarded tool:

- `pkg_pfs_tool` was tested first, but it could not decrypt this retail PKG on
  this machine because the needed retail entry-key/passcode material was not
  available locally, so it was removed
