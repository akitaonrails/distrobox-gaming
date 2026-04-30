# Repository Guidelines

## Project Structure & Module Organization

This repo manages an Arch-based `gaming` distrobox with Ansible. Core playbooks
live in `ansible/`, reusable roles in `ansible/roles/`, defaults in
`ansible/group_vars/all/`, and machine-specific overrides in
`ansible/host_vars/localhost.yml`. Rendered desktop entries live under
`config/desktop/rendered/`; source templates live under role `templates/`.
Focused setup notes are in `docs/`.

## Build, Test, and Development Commands

Run commands from `ansible/` unless noted:

```sh
ansible-playbook site.yml                  # full setup
ansible-playbook --syntax-check site.yml   # validate playbook syntax
ansible-playbook install-sonic-p06.yml     # run optional P-06 setup
desktop-file-validate ../config/desktop/rendered/*.desktop
```

Use focused playbooks for optional apps (`install-xenia.yml`,
`install-pc-racing.yml`, `install-unleashed-recomp.yml`) instead of folding
large or user-specific installs into the default rebuild path.

## Ansible Path Customization

Never hardcode maintainer-local paths such as `/mnt/data`,
`/mnt/terachad`, `/run/media/akitaonrails`, or `/home/akitaonrails` in new
Ansible roles, templates, or active docs. Add or reuse `dg_*` variables in
`ansible/group_vars/all/*.yml`, derive paths from roots such as `dg_data_root`,
`dg_box_home`, `dg_external_games_root`, `dg_roms_final_root`, and document
overrides in `ansible/host_vars/localhost.yml.example`. Personal paths are
acceptable only as default values in central variables or as clearly historical
examples in archival docs.

## Reuse And Wine Game Patterns

Avoid duplicated Ansible logic. Before adding a new role or playbook, check
whether an existing role can be extended with data, variables, or a small shared
template change. For Windows games, prefer improving the reusable Wine/PC racing
flow instead of creating one-off install logic. Capture lessons from each tested
game, such as required `winetricks` components, DLL overrides, DXVK needs,
controller quirks, and installer flags, as data-driven `dg_*` variables so the
next Wine game benefits from the same path.

## Coding Style & Naming Conventions

Use YAML with two-space indentation. Prefix project variables with `dg_`.
Name roles with lowercase snake_case verbs, for example
`install_sonic_p06`. Keep shell snippets POSIX-compatible where practical and
quote paths because ROM names often contain spaces.

## Testing Guidelines

Before committing Ansible changes, run syntax checks for touched playbooks and
validate rendered `.desktop` files. For idempotent roles, rerun the playbook and
confirm the second run reports no unexpected changes.

## Commit & Pull Request Guidelines

Commits use concise imperative messages, such as `Add Sonic P-06 install role`.
PRs should state what role or emulator changed, which commands were run, and
whether the change touches optional user-specific assets or the default rebuild.
