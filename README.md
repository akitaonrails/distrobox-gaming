# Distrobox Gaming

Reproducible setup scripts for the `gaming` distrobox used for ES-DE, standalone
emulators, Walker desktop entries, Flycast high-resolution rendering, controller
quit hotkeys, and the Driveclub-focused shadPS4 setup.

This repository is now the canonical home for the gaming-box notes and scripts.

## Quick Start

For a future rebuild:

```sh
cp config/distrobox-gaming.env.example config/distrobox-gaming.env
$EDITOR config/distrobox-gaming.env
./bin/dg check
./bin/dg create
./bin/dg bootstrap
./bin/dg shadps4
./bin/dg configure
./bin/dg verify
```

Optional Xbox 360/Xenia Manager setup:

```sh
./bin/dg xenia
```

For a full run:

```sh
./bin/dg all
```

The current machine already has a working box. These scripts are intended for
future rebuilds and for documenting the known-good setup.

## Path Configuration

All NAS and storage paths are configurable. Your current paths are the defaults:

```sh
DG_BOX_NAME=gaming
DG_DATA_ROOT=/mnt/data
DG_BOX_HOME=$DG_DATA_ROOT/distrobox/gaming
DG_EMUDECK_ROOT=/mnt/terachad/Emulators/EmuDeck
DG_BIOS_ROOT=/mnt/terachad/Emulators/EmuDeck/Emulation/bios
DG_ROM_ROOT=/mnt/terachad/Emulators/EmuDeck/roms
DG_ROM_HEAVY_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_heavy
DG_ROM_RARE_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_rare
DG_PS4_ROM_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4
DG_SHADPS4_GAME_DIR=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003
DG_PS4_FIRMWARE_MODULES=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4-firmware/11.00_sys_modules
DG_SHADPS4_QTLAUNCHER_ROOT=$DG_BOX_HOME/tools/shadps4-qtlauncher
DG_SHADPS4_QTLAUNCHER_BIN=$DG_BOX_HOME/bin/shadps4-qtlauncher-current
DG_SHADPS4_VERSIONS_ROOT=$DG_BOX_HOME/.local/share/shadPS4QtLauncher/versions
DG_SHADPS4_CHANNEL=Pre-release
DG_SHADPS4_MANAGED_BIN=$DG_SHADPS4_VERSIONS_ROOT/$DG_SHADPS4_CHANNEL/Shadps4-sdl.AppImage
DG_SHADPS4_BIN=$DG_BOX_HOME/bin/shadps4-current
```

For another machine, copy and edit:

```sh
cp config/distrobox-gaming.env.example config/distrobox-gaming.env
```

Runtime overrides also work:

```sh
DG_EMUDECK_ROOT=/media/games/EmuDeck ./bin/dg verify
```

To move the whole gaming box off `/mnt/data`, set `DG_DATA_ROOT` in
`config/distrobox-gaming.env` and let `DG_BOX_ROOT`/`DG_BOX_HOME` follow it.

Scripts should never hardcode `/mnt/terachad` directly. Use the `DG_*`
variables in `lib/paths.sh`.

Desktop launchers owned by this project live under `config/desktop/templates/`.
The scripts render machine-specific copies into `config/desktop/rendered/` and
symlink those into `$DG_HOST_APPLICATIONS_DIR`.

For PS4, the expected layout is a clean root with extracted title directories,
not raw `.pkg` files or Windows extraction tools mixed into the same folder. In
this setup that means:

```text
$DG_PS4_ROM_ROOT/
  CUSA00003/
    eboot.bin
    ...
```

## UID/GID And Permissions

The scripts are designed for rootless distrobox. The container user must match
the host UID/GID so files written to NAS mounts remain editable by the host
user.

By default these are auto-detected:

```sh
DG_HOST_UID=$(id -u)
DG_HOST_GID=$(id -g)
DG_HOST_USER=$(id -un)
DG_HOST_GROUP=$(id -gn)
```

`./bin/dg check` verifies:

- host and distrobox UID/GID match when the box exists
- the box home is writable
- NAS ROM/BIOS paths are readable
- host desktop entry path is writable
- PS4 firmware modules are present when configured

Package install phases validate sudo inside the distrobox before installing, so
the run fails early instead of prompting halfway through a long setup.

## Commands

```sh
./bin/dg check       # host path, permission, command, and UID/GID checks
./bin/dg create      # create the distrobox if it does not exist
./bin/dg bootstrap   # install pacman and AUR packages
./bin/dg shadps4     # install/update shadPS4 QtLauncher + managed build, then refresh PS4 config
./bin/dg xenia       # install/update Wine, Xenia Manager, and its dedicated prefix
./bin/dg configure   # apply links, configs, wrappers, desktop files, ES-DE
./bin/dg verify      # verify commands and generated files
./bin/dg all         # run every phase
```

## What Gets Configured

- Arch-based distrobox named `gaming`
- Pacman and AUR emulator packages from `config/package-lists/`
- ES-DE custom systems with standalone emulators first
- Flycast high-resolution wrapper at `$DG_BOX_HOME/bin/flycast-hires`
- Flycast Vulkan/upscale/frame-pacing settings
- PCSX2 `Select+Start` shutdown hotkey
- Dolphin 8BitDo Ultimate 2 defaults for GameCube and Wii profiles
- DuckStation Vulkan/PGXP/widescreen defaults
- xemu config plus BIOS/HDD links from `$DG_BIOS_ROOT`
- shadPS4 wrapper at `$DG_SHADPS4_BIN` that launches the QtLauncher-managed build
- official shadPS4 QtLauncher wrapper at `$DG_SHADPS4_QTLAUNCHER_BIN`
- shadPS4 QtLauncher AppImage extracted under `$DG_SHADPS4_QTLAUNCHER_ROOT/releases/`
- shadPS4 Driveclub config for `CUSA00003`
- shadPS4 Driveclub v1.28 patch XML
- extracted Driveclub directory at `$DG_SHADPS4_GAME_DIR`
- PS4 11.00 sys_module symlinks for shadPS4
- repo-managed Walker desktop entries symlinked from `config/desktop/rendered/`
- no-patch Driveclub launcher for A/B testing
- optional Wine-managed Xenia Manager launcher at `$DG_XENIA_MANAGER_BIN`
- optional dedicated Xenia Manager prefix at `$DG_XENIA_PREFIX`

## Xenia Manager

Xbox 360 support in this repo is handled through Xenia Manager inside a
dedicated Wine prefix, not through a separate native Linux Xenia package.
That keeps the manager and the Canary builds it downloads in one place.

`./bin/dg xenia` will:

- enable `multilib` inside the box if needed
- install `wine` and `winetricks`
- create `$DG_XENIA_PREFIX`
- install the required Windows runtimes for Xenia Manager
- download the latest Xenia Manager release into `$DG_XENIA_MANAGER_RELEASES_DIR`
- write the stable launcher wrapper at `$DG_XENIA_MANAGER_BIN`
- export a host desktop entry named `gaming-xenia-manager.desktop`

After that, launch Xenia Manager and use its `Manage` page to install Canary.
The manager owns the Canary download/update flow.

## Historical Docs

`docs/distrobox-gaming-prompts.md` and parts of
`docs/distrobox-gaming-packages.md` are retained as working notes from the
original setup. The current source of truth is the scripts plus this README.

## Documentation

Historical notes:

- [Setup Notes](docs/distrobox-gaming-prompts.md)
- [Package Strategy](docs/distrobox-gaming-packages.md)

Focused docs:

- [Driveclub shadPS4](docs/driveclub-shadps4.md)
- [Flycast Resolution](docs/flycast-resolution.md)
- [Controller Hotkeys](docs/controller-hotkeys.md)
- [Rebuild Runbook](docs/rebuild-runbook.md)
- [Xenia Manager](docs/xenia-manager.md)

## Safety Rules

This repo does not provide ROMs, BIOS files, firmware, keys, or game packages.

Scripts only detect, link, and configure files that already exist on your
machine. They should not delete ROMs, BIOS, saves, firmware, or game data.

Generated emulator state, shader caches, saves, logs, firmware modules, and ROMs
must not be committed.
