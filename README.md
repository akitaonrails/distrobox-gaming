# Distrobox Gaming

Ansible playbooks for the `gaming` distrobox: ES-DE, standalone emulators,
Walker desktop entries, Flycast high-resolution rendering, controller quit
hotkeys, and the Driveclub-focused shadPS4 setup.

## Quick Start

```sh
cd ansible
ansible-galaxy collection install -r collections/requirements.yml
cp host_vars/localhost.yml.example host_vars/localhost.yml
$EDITOR host_vars/localhost.yml
ansible-playbook site.yml
```

For a full run with optional Xbox 360/Xenia Manager:

```sh
ansible-playbook site.yml
ansible-playbook install-xenia.yml
```

## Commands

All commands run from the `ansible/` directory:

```sh
ansible-playbook site.yml              # full setup from scratch
ansible-playbook reset-configs.yml      # reset emulator configs without rebuilding
ansible-playbook backup.yml             # backup before destructive testing
ansible-playbook restore.yml            # restore from backup
ansible-playbook refresh-shadps4.yml    # update shadPS4 builds
ansible-playbook install-xenia.yml      # install/update Xenia Manager (optional)
```

Tags allow running subsets:

```sh
ansible-playbook site.yml --tags check       # host path and UID/GID validation
ansible-playbook site.yml --tags create      # create the distrobox
ansible-playbook site.yml --tags bootstrap   # install pacman + AUR packages
ansible-playbook site.yml --tags shadps4     # install/update shadPS4
ansible-playbook site.yml --tags configure   # apply configs, desktop entries, ES-DE
ansible-playbook site.yml --tags verify      # post-setup assertions
ansible-playbook reset-configs.yml --tags esde     # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs   # reset only emulator INIs
ansible-playbook reset-configs.yml --tags desktop   # reset only desktop entries
```

## Path Configuration

All paths are configurable via Ansible variables. Defaults match the current
machine's NAS layout:

```yaml
dg_box_name: gaming
dg_host_uid: 1026                    # NAS requires this UID
dg_host_gid: 1026
dg_data_root: /mnt/data
dg_box_home: /mnt/data/distrobox/gaming
dg_emudeck_root: /mnt/terachad/Emulators/EmuDeck
dg_bios_root: /mnt/terachad/Emulators/EmuDeck/Emulation/bios
dg_rom_root: /mnt/terachad/Emulators/EmuDeck/roms
```

For another machine, create `ansible/host_vars/localhost.yml` and override any
variable. Or pass overrides on the command line:

```sh
ansible-playbook site.yml -e dg_emudeck_root=/media/games/EmuDeck
```

## Resetting Configs

If you screw up your emulator configs (ES-DE, DuckStation, PCSX2, etc.) and
want to restore to Ansible-managed defaults without reinstalling the box:

```sh
ansible-playbook reset-configs.yml           # reset everything
ansible-playbook reset-configs.yml --tags esde    # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs  # reset only emulator INIs
```

This re-applies `seed_configs`, `desktop_apps`, and `configure_esde` roles.
Existing files are backed up automatically before overwriting.

## Backup and Restore

Before destructive testing (e.g. rebuilding from scratch):

```sh
ansible-playbook backup.yml     # commits container image + archives configs
ansible-playbook restore.yml    # prompts for timestamp, restores both
```

Backups are stored under `$DG_BOX_HOME/backups/`.

## UID/GID and Permissions

The NAS requires UID/GID 1026 for file access. The `check_host` role asserts
the host user matches `dg_host_uid` before proceeding. The container user
inherits the host UID/GID through distrobox.

Override for another machine:

```yaml
# ansible/host_vars/localhost.yml
dg_host_uid: 1000
dg_host_gid: 1000
```

## What Gets Configured

- Arch-based distrobox named `gaming`
- Pacman and AUR emulator packages (see `group_vars/all/packages.yml`)
- ES-DE custom systems with standalone emulators first
- Flycast high-resolution wrapper at `$DG_BOX_HOME/bin/flycast-hires`
- Flycast Vulkan/upscale/frame-pacing settings
- PCSX2 `Select+Start` shutdown hotkey
- Dolphin 8BitDo Ultimate 2 defaults for GameCube and Wii profiles
- DuckStation Vulkan/PGXP/widescreen defaults
- xemu config plus BIOS/HDD links from `$DG_BIOS_ROOT`
- shadPS4 wrapper launching QtLauncher-managed builds
- shadPS4 Driveclub config for `CUSA00003` with v1.28 patch XML
- PS4 11.00 sys_module symlinks for shadPS4
- Repo-managed Walker desktop entries
- Optional Wine-managed Xenia Manager with .NET/VC++ runtimes

## PS4 Game Layout

The expected layout is clean extracted title directories, not raw `.pkg` files:

```text
$DG_PS4_ROM_ROOT/
  CUSA00003/
    eboot.bin
    ...
```

## Xenia Manager

Xbox 360 support uses Xenia Manager inside a dedicated Wine prefix.
`ansible-playbook install-xenia.yml` will:

- Enable `multilib` inside the box
- Install `wine` and `winetricks`
- Create the Wine prefix with .NET and VC++ runtimes
- Download the latest Xenia Manager release
- Write the launcher wrapper and desktop entry

After that, launch Xenia Manager and use its `Manage` page to install Canary.

## Project Structure

```
ansible/                          # Ansible playbooks and roles (primary)
  site.yml                        # full setup playbook
  reset-configs.yml               # config-only reset playbook
  backup.yml / restore.yml        # backup and restore
  refresh-shadps4.yml             # standalone shadPS4 update
  install-xenia.yml               # standalone Xenia Manager install
  group_vars/all/                 # all dg_* variable defaults
  host_vars/localhost.yml.example # machine-specific overrides template
  roles/                          # one role per setup phase
    check_host/                   # host validation
    create_box/                   # distrobox creation
    bootstrap_packages/           # pacman + AUR packages
    link_storage/                 # BIOS/firmware symlinks
    seed_configs/                 # emulator INI settings, wrappers, configs
    desktop_apps/                 # .desktop entry rendering and symlinks
    configure_esde/               # ES-DE custom systems XML
    verify/                       # post-setup assertions
    refresh_shadps4/              # shadPS4 GitHub release management
    install_xenia/                # Wine prefix and Xenia Manager
bin/                              # legacy shell CLI (reference)
scripts/                          # legacy numbered scripts (reference)
lib/                              # legacy shell helpers (reference)
config/                           # static config files and package lists
docs/                             # historical notes and focused docs
```

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

Playbooks only detect, link, and configure files that already exist on your
machine. They should not delete ROMs, BIOS, saves, firmware, or game data.

Generated emulator state, shader caches, saves, logs, firmware modules, and ROMs
must not be committed.
