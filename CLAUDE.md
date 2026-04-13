# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Ansible playbooks for reproducibly creating and configuring an Arch-based distrobox named `gaming`. The box hosts ES-DE, standalone emulators (shadPS4, Dolphin, PCSX2, DuckStation, Flycast, xemu, RPCS3, PPSSPP), Walker desktop entries, and an optional Wine-managed Xenia Manager for Xbox 360.

## Commands

All operations run from the `ansible/` directory:

```sh
cd ansible
ansible-playbook site.yml              # full setup from scratch
ansible-playbook reset-configs.yml      # reset emulator configs without rebuilding
ansible-playbook backup.yml             # backup before destructive testing
ansible-playbook restore.yml            # restore from backup
ansible-playbook refresh-shadps4.yml    # update shadPS4 builds
ansible-playbook install-xenia.yml      # install/update Xenia Manager (optional)
```

Tags allow running subsets:

```sh
ansible-playbook site.yml --tags check       # host validation only
ansible-playbook site.yml --tags bootstrap   # packages only
ansible-playbook site.yml --tags configure   # configs, desktop entries, ES-DE
ansible-playbook site.yml --tags verify      # post-setup assertions
ansible-playbook reset-configs.yml --tags esde     # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs   # reset only emulator INIs
ansible-playbook reset-configs.yml --tags desktop   # reset only desktop entries
```

There is no unit test suite. The `verify` role is the validation step — run it after any change.

## Architecture

### Ansible (primary)

- **`ansible/site.yml`** — Full setup playbook. Roles execute in order: `check_host` → `create_box` → `bootstrap_packages` → `refresh_shadps4` → `link_storage` → `seed_configs` → `desktop_apps` → `configure_esde` → `verify`.
- **`ansible/reset-configs.yml`** — Re-applies config roles without rebuilding the box or reinstalling packages. For when you screw up emulator settings and want to restore defaults.
- **`ansible/group_vars/all/`** — All `dg_*` variables split by concern: `main.yml` (paths, box identity, UID/GID), `packages.yml` (pacman + AUR lists), `emulators.yml` (INI settings as structured data), `shadps4.yml`, `xenia.yml`, `esde.yml` (system definitions as YAML list).
- **`ansible/roles/`** — One role per phase. Each is idempotent. Key roles:
  - `seed_configs` — Subtask files per emulator (`dolphin.yml`, `pcsx2.yml`, etc.). Uses `community.general.ini_file` for INI manipulation, `ansible.builtin.template` for xemu TOML.
  - `desktop_apps` — Jinja2 `.desktop.j2` templates rendered to `config/desktop/rendered/`, symlinked to `~/.local/share/applications/`.
  - `configure_esde` — `es_systems.xml.j2` loops over `dg_esde_systems` list. Adding systems is a YAML data change.
  - `refresh_shadps4` — Fetches releases via `ansible.builtin.uri` against GitHub API, downloads/extracts AppImages, deploys wrapper scripts.
- Tasks run on `localhost` targeting the bind-mounted box home at `dg_box_home`. Commands that must execute inside the container use `shell: "{{ dg_in_box }} ..."`.
- Override defaults by creating `ansible/host_vars/localhost.yml` (see `.example`).
- UID 1026 is the default for NAS access — set `dg_host_uid`/`dg_host_gid` to override.

### Legacy shell scripts (retained for reference)

The `bin/dg`, `scripts/`, `lib/`, and `config/` directories contain the original POSIX shell implementation. The Ansible playbooks are the primary interface; the shell scripts are kept as reference.

## Coding Conventions

### Ansible roles

- Variables use `dg_*` lowercase names in `group_vars/all/`.
- Roles use `ansible.builtin.*` fully qualified module names.
- File operations use `backup: true` so user state is preserved.
- Per-emulator config is split into subtask files under `seed_configs/tasks/`.
- Static config files live in role `files/` directories; templates in `templates/`.

### Legacy shell scripts

- POSIX `sh`, not Bash. Every script starts `#!/usr/bin/env sh` + `set -eu`.
- All exported config uses `DG_*` uppercase names (defined in `lib/paths.sh`).
- Scripts never hardcode mount paths — use `DG_*` variables.

## Path Configuration

For Ansible: create `ansible/host_vars/localhost.yml` and override any `dg_*` variable. Or pass `-e dg_emudeck_root=/other/path` on the command line.

For legacy shell scripts: `cp config/distrobox-gaming.env.example config/distrobox-gaming.env` and edit.

## Safety

Playbooks and scripts only detect, link, and configure existing files. They must not delete ROMs, BIOS, saves, firmware, or game data. Never commit generated state, shader caches, saves, logs, firmware, or ROMs.

## Commit and PR Style

Short imperative subjects like `Manage desktop launchers from project templates`, `Simplify shadPS4 setup around QtLauncher`. One operational change per commit. PRs should state what workflow changed, which paths or env vars are affected, and the exact verification commands run. Include screenshots only when desktop entries or launcher behavior changes.
