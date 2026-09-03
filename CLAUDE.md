# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Ansible playbooks for reproducibly creating and configuring an Arch-based distrobox named `gaming`. The box hosts ES-DE, standalone emulators (shadPS4, Dolphin, PCSX2, DuckStation, Flycast, xemu, RPCS3, PPSSPP, Azahar for 3DS, RetroArch, and Supermodel for Sega Model 3), and Walker desktop entries.

Beyond the core emulators, a large set of **opt-in** roles (all `never`-tagged in `site.yml`, or run via a standalone `install-*.yml` playbook) install:

- **Sega arcade** (see `docs/sega-arcade.md`): Model 1 via the Wanszai Virtua Racing / Virtua Fighter Wine frontends (`install_model1`), Model 2 via ElSemi's Model 2 Emulator (`install_m2emulator`) and the Wanszai Sega Rally HD wrapper (`install_sega_rally`).
- **Namco arcade**: Wanszai Ridge Racer Collection (System 22: Ridge Racer, RR2, Rave Racer) via a D3D11/DXVK Wine wrapper (`install_ridge_racer`, see `docs/ridge-racer.md`).
- **Xbox 360**: Wine-managed Xenia Manager (`install-xenia.yml`).
- **Native recomp / decomp / source ports**: Ship of Harkinian (OoT), 2Ship2Harkinian (Majora's Mask), Starship (Star Fox 64), Render96ex (SM64), SpaghettiKart (MK64), Sonic P-06, Unleashed Recomp, PrBoom-Plus Doom II RT, DUDE (Doom 3, `docs/dude.md`), GoldenEye 007 Recompiled (`docs/goldeneye-recomp.md`), Donkey Kong 64 Recompiled (prebuilt N64Recomp+RT64 release; `install_dk64_recomp`, `docs/dk64-recomp.md`), and the Perfect Dark PC port (native decomp port, OpenGL; rolling `ci-dev-build` pinned by sha256 + NAS-staged tarball; `install_perfect_dark`, `docs/perfect-dark.md`).
- **Native fan games**: Mega Man X Regenesis (Godot 4, official Linux export; `install_mmx_regenesis`, see `docs/mmx-regenesis.md`), Project Reignition — Sonic and the Secret Rings remake (Godot 4.7/.NET native Linux build from the NAS-staged Gamejolt zip; `install_project_reignition`, see `docs/project-reignition.md`) and OpenBOR beat-'em-ups run on the native OpenBOR 4.0 engine (`install_openbor`, data-driven `dg_openbor_games`; Streets of Rage: Troubles in Japan; see `docs/openbor.md`). Star Fox Enhanced (SNES Star Fox source port via UltraStarFox — distinct from the N64 Starship port; official native linux-x64 release, first launch builds assets from the user's Rev 2 ROM, optional MSU-1 music; `install_starfox_enhanced`, see `docs/starfox-enhanced.md`). JHDev2006 Godot remakes: Super Mario Bros. Remastered (SMB1, `install_smb_remastered`) and Super Mario World Remastered (SMW, `install_smw_remastered`, see `docs/smw-remastered.md`) — both need the matching original ROM.
- **Windows/Wine games** (see `docs/external-installers.md`): Colin McRae Rally 04/2/3 + DiRT, OutRun 2006, Sega Rally Revo, Richard Burns Rally + RallySimFans (`docs/richard-burns-rally.md`), GT5 Master Mod, Dusk, FFVII 7th Heaven, Metal Gear Master Collection fixes, and the shared `install_pc_racing` pipeline.
- **MS-DOS games**: Screamer, Screamer 2 (GOG) + Screamer Rally (CD) via dosbox-staging (`install_screamer`, see `docs/screamer.md`).
- **Content / tooling**: DLC installers, Switch/PCSX2/DuckStation per-game configs, RetroArch extras, HD texture packs, cheat/trainer tooling, SMM2 offline levels, and reproducible IPS romhack patches (`install_rom_patches`, see `docs/rom-patches.md`), and per-game Steam launch options (`steam_launch_options`, data-driven `dg_steam_launch_options_by_appid`, see `docs/steam-launch-options.md`), and the Wine COM-MTA keepalive proxy DLL for games that crash creating COM objects from worker threads (`install_mta_shim`, see `docs/mta-shim.md`).

See `docs/external-installers.md` for the download inventory and `docs/rebuild-runbook.md` for a from-scratch rebuild.

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

### Helper scripts and config sources

`scripts/` holds helper scripts invoked **by the Ansible roles** — `install-host-launchers.sh` (host `.desktop` export, used by `desktop_apps` and several game roles), the `set-*.py` Steam/INI helpers (`metal_gear`, `steam_lib32_nvidia`, `steam_trainers`), `sync-emulator-cheats.py`, and a couple of download utilities. `config/` holds the live config **source trees** (emulator INIs, ES-DE, Steam vdfs, `config/desktop/` templates) that `seed_configs` and related roles copy into the box. Neither directory is a standalone interface — the roles drive them.

The original POSIX shell implementation (`bin/dg` dispatcher, `lib/paths.sh`/`lib/common.sh`, and the numbered `scripts/NN-*.sh` orchestration layer, plus its `config/{emulator-overrides,wrappers,package-lists}` and `config/distrobox-gaming.env.example`) was **removed** once Ansible fully superseded it. Recover from git history if ever needed.

## Coding Conventions

### Ansible roles

- Variables use `dg_*` lowercase names in `group_vars/all/`.
- New roles, templates, and active docs must not hardcode maintainer-local paths
  such as `/mnt/data`, `/mnt/terachad`, `/run/media/akitaonrails`, or
  `/home/akitaonrails`. Add or reuse `dg_*` variables, derive paths from roots
  like `dg_data_root`, `dg_box_home`, `dg_external_games_root`, and
  `dg_roms_final_root`, and document user overrides in
  `ansible/host_vars/localhost.yml.example`.
- Avoid duplicated Ansible logic. Extend existing roles with data, variables,
  and shared templates before creating a one-off role. For Windows games, fold
  tested Wine lessons back into reusable `dg_*` data such as installer flags,
  `winetricks` components, DLL overrides, DXVK needs, and controller quirks.
- Roles use `ansible.builtin.*` fully qualified module names.
- File operations use `backup: true` so user state is preserved.
- Per-emulator config is split into subtask files under `seed_configs/tasks/`.
- Static config files live in role `files/` directories; templates in `templates/`.

### Helper scripts (`scripts/`)

- These are called at runtime by roles (mostly Python `set-*.py` / `*.py` helpers plus `install-host-launchers.sh`), not a standalone CLI.
- They take their paths from the invoking role (env vars / args) and never hardcode mount paths.

## Path Configuration

For Ansible: create `ansible/host_vars/localhost.yml` and override any `dg_*` variable. Or pass `-e dg_emudeck_root=/other/path` on the command line.

## Safety

Playbooks and scripts only detect, link, and configure existing files. They must not delete ROMs, BIOS, saves, firmware, or game data. Never commit generated state, shader caches, saves, logs, firmware, or ROMs.

## Commit and PR Style

Short imperative subjects like `Manage desktop launchers from project templates`, `Simplify shadPS4 setup around QtLauncher`. One operational change per commit. PRs should state what workflow changed, which paths or env vars are affected, and the exact verification commands run. Include screenshots only when desktop entries or launcher behavior changes.
