# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Reproducible setup scripts for an Arch-based distrobox named `gaming`. The box hosts ES-DE, standalone emulators (shadPS4, Dolphin, PCSX2, DuckStation, Flycast, xemu, RPCS3, PPSSPP), Walker desktop entries, and an optional Wine-managed Xenia Manager for Xbox 360. The current machine already has a working box — these scripts exist for future rebuilds and to document the known-good configuration.

## Commands

All operations go through the `./bin/dg` wrapper:

```sh
./bin/dg check       # validate host paths, permissions, UID/GID
./bin/dg create      # create the distrobox
./bin/dg bootstrap   # install pacman + AUR packages
./bin/dg shadps4     # install/update shadPS4 QtLauncher + managed build, refresh PS4 config
./bin/dg xenia       # install/update Wine-managed Xenia Manager (optional)
./bin/dg configure   # apply configs, wrappers, desktop entries, ES-DE
./bin/dg verify      # regression check: commands, generated files, symlinks
./bin/dg all         # run all phases in order
```

There is no unit test suite. `./bin/dg verify` is the validation step. After any functional change, run the affected phase then verify:

```sh
./bin/dg configure && ./bin/dg verify
```

For desktop entry changes, also inspect `config/desktop/rendered/`.

## Architecture

- **`bin/dg`** — CLI entrypoint; dispatches to numbered scripts in `scripts/`.
- **`scripts/NN-action.sh`** — Each phase is a standalone script. Numbering defines execution order. `bin/dg all` runs them sequentially.
- **`lib/paths.sh`** — All `DG_*` environment variables with defaults. Sources `config/distrobox-gaming.env` if it exists. Every path the scripts touch is defined here.
- **`lib/common.sh`** — Shared helpers: logging (`log`/`warn`/`die`), `in_box` (distrobox exec), `render_template`, `replace_or_add_ini_key`, `sudo_begin`/`box_sudo_begin` (keepalive wrappers), `ensure_multilib`.
- **`config/`** — Static inputs: `package-lists/` (pacman.txt, aur.txt, xenia-pacman.txt), `desktop/templates/` (`.desktop.in` files with `@DG_*@` placeholders), `emulator-overrides/` (per-emulator configs and profiles), `wrappers/` (e.g. flycast-hires), `ES-DE/`, and `distrobox-gaming.env.example`.
- **`config/desktop/templates/` → `config/desktop/rendered/`** — `render_template` in `lib/common.sh` does sed substitution of `@DG_*@` placeholders. Rendered files are gitignored; templates are committed.

## Ansible Setup

The `ansible/` directory contains an Ansible conversion of the shell scripts. It is the preferred way to manage the gaming distrobox going forward.

```sh
cd ansible
ansible-playbook site.yml              # full setup from scratch
ansible-playbook reset-configs.yml      # reset emulator configs only
ansible-playbook backup.yml             # backup before destructive testing
ansible-playbook restore.yml            # restore from backup
ansible-playbook refresh-shadps4.yml    # update shadPS4 builds
ansible-playbook install-xenia.yml      # install/update Xenia Manager
```

Tags allow running subsets: `--tags esde`, `--tags configs`, `--tags desktop`, `--tags bootstrap`.

### Ansible Architecture

- **`group_vars/all/`** — All `dg_*` variables split by concern: `main.yml` (paths, identity), `packages.yml`, `emulators.yml`, `shadps4.yml`, `xenia.yml`, `esde.yml`.
- **Roles** map 1:1 to the original shell script phases: `check_host`, `create_box`, `bootstrap_packages`, `link_storage`, `seed_configs`, `desktop_apps`, `configure_esde`, `verify`, `refresh_shadps4`, `install_xenia`.
- Tasks run on `localhost` targeting the bind-mounted box home. In-container commands use `shell: "{{ dg_in_box }} ..."`.
- Override defaults by creating `host_vars/localhost.yml` (see `.example`).
- `reset-configs.yml` re-applies `seed_configs`, `desktop_apps`, `configure_esde` without rebuilding the box.
- UID 1026 is the default for NAS access — set `dg_host_uid`/`dg_host_gid` to override.

## Coding Conventions

- POSIX `sh`, not Bash. Every script starts `#!/usr/bin/env sh` + `set -eu`.
- All exported config uses `DG_*` uppercase names (defined in `lib/paths.sh`). Local variables use descriptive lowercase names.
- Scripts never hardcode mount paths like `/mnt/terachad` directly — use the `DG_*` variables from `lib/paths.sh`.
- Script filenames are numbered `NN-action.sh` to preserve execution order.
- Existing `# shellcheck disable=...` comments are intentional; keep them narrowly scoped.
- Shared logic goes in `lib/common.sh` or `lib/paths.sh`. Use the existing helpers (`log`, `die`, `in_box`, `ensure_dir`, `render_template`, etc.) rather than reinventing.

## Path Configuration

For a new machine: `cp config/distrobox-gaming.env.example config/distrobox-gaming.env` and edit. Runtime overrides also work: `DG_EMUDECK_ROOT=/other/path ./bin/dg verify`.

## Safety

Scripts only detect, link, and configure existing files. They must not delete ROMs, BIOS, saves, firmware, or game data. Never commit generated state, shader caches, saves, logs, firmware, or ROMs — the `.gitignore` already excludes these.

## Commit and PR Style

Short imperative subjects like `Manage desktop launchers from project templates`, `Simplify shadPS4 setup around QtLauncher`. One operational change per commit. PRs should state what workflow changed, which paths or env vars are affected, and the exact verification commands run. Include screenshots only when desktop entries or launcher behavior changes.
