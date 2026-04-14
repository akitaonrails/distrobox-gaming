# Distrobox Gaming

Ansible playbooks for an Arch-based distrobox named `gaming`. Sets up ES-DE,
standalone emulators (shadPS4, Dolphin, PCSX2, DuckStation, Flycast, xemu,
RPCS3, PPSSPP, Eden, Cemu, Vita3K), RetroArch cores, host-side Walker desktop
launchers, DLC/patch batch installers for PS3 and Switch, per-game RPCS3
optimization configs, optional Wine-managed Xenia Manager for Xbox 360, and
a minimal zsh + starship shell inside the box.

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
ansible-playbook site.yml --tags check           # host path and UID/GID validation
ansible-playbook site.yml --tags create          # create the distrobox
ansible-playbook site.yml --tags bootstrap       # install pacman + AUR packages
ansible-playbook site.yml --tags shadps4         # install/update shadPS4
ansible-playbook site.yml --tags configure       # configs, desktop entries, ES-DE
ansible-playbook site.yml --tags dlcs            # install PS3 DLCs + Switch NSPs
ansible-playbook site.yml --tags cheats          # link Switch cheats to Eden
ansible-playbook site.yml --tags rpcs3_configs   # per-game RPCS3 tuning
ansible-playbook site.yml --tags retroarch       # download RA cores + assets
ansible-playbook site.yml --tags scripts         # deploy box helper scripts
ansible-playbook site.yml --tags shell           # deploy zsh + starship
ansible-playbook site.yml --tags verify          # post-setup assertions
ansible-playbook reset-configs.yml --tags esde     # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs   # reset only emulator INIs
ansible-playbook reset-configs.yml --tags desktop   # reset only desktop entries
ansible-playbook reset-configs.yml --tags shell     # reset only zsh/starship
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
dg_rom_heavy_root: /mnt/terachad/Emulators/EmuDeck/roms_heavy
dg_ps3_dlc_source: "{{ dg_rom_heavy_root }}/ps3-DLC"
dg_switch_updates_source: "{{ dg_rom_heavy_root }}/switch_updates"
dg_switch_cheats_source: "{{ dg_rom_heavy_root }}/switch_cheats"
```

For another machine, create `ansible/host_vars/localhost.yml` and override any
variable. Or pass overrides on the command line:

```sh
ansible-playbook site.yml -e dg_emudeck_root=/media/games/EmuDeck
```

## GPU Preference (NVIDIA vs AMD iGPU)

On systems with both an NVIDIA dGPU and an AMD iGPU, emulators are forced to
use NVIDIA by injecting `VK_ICD_FILENAMES` into every desktop launcher and
ES-DE command. The distrobox is also created with `--nvidia` so NVIDIA drivers
are bind-mounted into the container. Controlled by `dg_nvidia_enabled: true`
in `group_vars/all/gpu.yml`. Set to `false` to disable.

## Resetting Configs

If you screw up your emulator configs (ES-DE, DuckStation, PCSX2, etc.) and
want to restore to Ansible-managed defaults without reinstalling the box:

```sh
ansible-playbook reset-configs.yml           # reset everything
ansible-playbook reset-configs.yml --tags esde    # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs  # reset only emulator INIs
ansible-playbook reset-configs.yml --tags shell    # reset only zsh/starship
```

This re-applies `seed_configs`, `desktop_apps`, `configure_esde`, and
`shell_config` roles. Existing files are backed up automatically before
overwriting.

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

### Base setup

- Arch-based distrobox named `gaming` with `--nvidia` drivers bind-mounted
- Pacman and AUR emulator packages (see `group_vars/all/packages.yml`)
- ES-DE (emulationstation-de) as the frontend
- RetroArch plus 21 buildbot cores (fbneo, mednafen variants, etc.) and
  all 8 asset packs (info, assets, autoconfig, cheats, databases, shaders,
  overlays) — ~760 MB total
- Minimal zsh + starship prompt inside the box

### Per-emulator

- Flycast high-resolution wrapper at `$DG_BOX_HOME/bin/flycast-hires`
- PCSX2 `Select+Start` shutdown hotkey
- Dolphin 8BitDo Ultimate 2 defaults for GameCube and Wii profiles
- DuckStation Vulkan/PGXP/widescreen defaults
- xemu config plus BIOS/HDD links from `$DG_BIOS_ROOT`
- shadPS4 wrapper launching QtLauncher-managed builds, Driveclub-specific
  `CUSA00003.toml` config with v1.28 patch XML, PS4 11.00 sys_module symlinks

### DLCs, patches, and per-game tuning

- **PS3 DLCs and patches**: `install_dlcs` role batch-extracts every .pkg
  from `$DG_PS3_DLC_SOURCE` into RPCS3's `dev_hdd0/game/` — bypasses the
  GUI-only installer limitation
- **Switch updates and DLC**: same role extracts NSPs from
  `$DG_SWITCH_UPDATES_SOURCE` into Eden's NAND at
  `~/.local/share/eden/nand/user/Contents/registered/`
- **Switch cheats**: `switch_cheats` role symlinks Atmosphere-format cheats
  from `$DG_SWITCH_CHEATS_SOURCE` into Eden's load path
- **Per-game RPCS3 configs**: `rpcs3_per_game_configs` role scans installed
  PS3 games, queries the RPCS3 compatibility API, and writes tuned
  `custom_configs/<TITLE_ID>_config.yml` for games with "Ingame" or "Loadable"
  status. Hand-curated overrides for known-problematic titles (Gran Turismo 6,
  Gran Turismo 5, Metal Gear Solid 4).

### Host-side launchers

- Repo-managed Walker desktop entries for every emulator, defined as data in
  `group_vars/all/launchers.yml` and rendered via a single Jinja2 template.
  Each Exec line is wrapped with the NVIDIA-preference env vars.
- Entries cover: ES-DE, Dolphin, DuckStation, PCSX2, PPSSPP, RPCS3, xemu,
  Eden, Cemu, Vita3K, shadPS4 (Driveclub + No Patch + GUI), Flycast,
  Xenia Manager (when installed).

### Optional

- Wine-managed Xenia Manager with .NET/VC++ runtimes for Xbox 360

## Helper Scripts (manual use)

The `install_dlcs` role also deploys standalone scripts into the box that you
can run manually for advanced tasks:

```sh
# List / download missing PS3 patches from PSN's public update server
python3 $DG_BOX_HOME/scripts/check_ps3_updates.py \
    /mnt/terachad/Emulators/EmuDeck/roms_heavy/ps3 \
    --dlc-dir /mnt/terachad/Emulators/EmuDeck/roms_heavy/ps3-DLC --list

python3 $DG_BOX_HOME/scripts/check_ps3_updates.py \
    /mnt/terachad/Emulators/EmuDeck/roms_heavy/ps3 \
    --dlc-dir /mnt/terachad/Emulators/EmuDeck/roms_heavy/ps3-DLC \
    --download-dir /mnt/data/distrobox/gaming/dlc-temp --download

# List outdated Switch games (Nintendo's CDN needs console auth, so no download)
python3 $DG_BOX_HOME/scripts/check_switch_updates.py \
    /mnt/terachad/Emulators/EmuDeck/roms_heavy/switch \
    --updates-dir /mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_updates

# Reorganize a messy switch_updates dump into per-title-ID folders
python3 $DG_BOX_HOME/scripts/reorganize_switch_nsps.py \
    /mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_updates --dry-run
```

Note on Switch updates: Nintendo's update CDN requires device-specific
certificates from a hacked Switch. `check_switch_updates.py` only reports
what's outdated (using the public blawar/titledb version database) — you
source the NSPs yourself.

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
ansible/                            # Ansible playbooks and roles (primary)
  site.yml                          # full setup playbook
  reset-configs.yml                 # config-only reset playbook
  backup.yml / restore.yml          # backup and restore
  refresh-shadps4.yml               # standalone shadPS4 update
  install-xenia.yml                 # standalone Xenia Manager install
  group_vars/all/                   # all dg_* variable defaults
    main.yml                        # paths, UID/GID, box identity
    packages.yml                    # pacman + AUR package lists
    emulators.yml                   # per-emulator INI settings
    esde.yml                        # ES-DE system definitions
    launchers.yml                   # host desktop launchers
    gpu.yml                         # NVIDIA preference config
    shadps4.yml                     # shadPS4 release / path config
    xenia.yml                       # Xenia Manager config
  host_vars/localhost.yml.example   # machine-specific overrides template
  roles/                            # one role per setup phase
    check_host/                     # host validation
    create_box/                     # distrobox creation (--nvidia)
    bootstrap_packages/             # pacman + AUR packages
    link_storage/                   # BIOS/firmware symlinks
    seed_configs/                   # emulator INI settings, wrappers
    scripts_in_box/                 # deploy Python helpers into box
    install_dlcs/                   # PS3 PKG + Switch NSP batch install
    switch_cheats/                  # symlink cheats into Eden load path
    rpcs3_per_game_configs/         # per-title RPCS3 tuning from API
    retroarch_extras/               # 21 buildbot cores + 8 asset packs
    desktop_apps/                   # .desktop entry rendering and symlinks
    configure_esde/                 # ES-DE custom systems XML
    shell_config/                   # minimal zsh + starship
    verify/                         # post-setup assertions
    refresh_shadps4/                # shadPS4 GitHub release management
    install_xenia/                  # Wine prefix and Xenia Manager
bin/                                # legacy shell CLI (reference)
scripts/                            # legacy numbered scripts (reference)
lib/                                # legacy shell helpers (reference)
config/                             # static config files and package lists
docs/                               # historical notes and focused docs
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
