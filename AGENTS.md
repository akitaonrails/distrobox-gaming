# Repository Guidelines

## Project Structure & Module Organization

This repo manages an Arch-based `gaming` distrobox with Ansible. Core playbooks
live in `ansible/`, reusable roles in `ansible/roles/`, defaults in
`ansible/group_vars/all/`, and machine-specific overrides in
`ansible/host_vars/localhost.yml`. Rendered desktop entries live under
`config/desktop/rendered/`; source templates live under role `templates/`.
Desktop entries carry ogm (omarchy-games-menu) discovery metadata as
`X-OGM-*` keys: every `*.desktop.j2` imports the shared
`ansible/templates/ogm-desktop-entry.j2` macro (`with context`) and calls it
with its rendered stem, which emits the keys from `group_vars/all/ogm.yml`
(`dg_ogm_games`) — add a new game there, never restate metadata in templates.
Every new or updated game install MUST keep its `dg_ogm_games` entry current:
`github` for GitHub-backed projects, otherwise `web_url`/`update_regex` for
web-page update badges where a pollable page exists (see the field docs in
`ogm.yml` and `docs/ogm-launcher.md`; verify regexes against the live page).
The opt-in `ogm_catalog` role (tag `ogm`) renders the same data to a
`catalog.d` fallback fragment. See `docs/ogm-launcher.md`.
The PC side of the library (`ROMS_FINAL/PC`) is bucketed as `ports/`,
`games/`, `mods/`, `releases/` and `tools/`; see `docs/pc-library.md`.
**Nothing stays in the `ROMS_FINAL/PC` root.** Downloads land there by
default, so every install — and every asset you notice while working on
one — must be filed before the task is done: ports, recomps and decomps
(and their source archives) in `ports/`, PC game installs and disc
extracts in `games/`, mods/texture packs/romhacks in `mods/`, upstream
release assets a role verifies in `releases/`, utilities in `tools/`.
Ansible paths must always name a bucket (`…/PC/releases/foo.zip`), never
the root. `scripts/check-pc-layout.sh <ROMS_FINAL/PC>` reports anything
left unfiled. Focused setup notes are in `docs/`. The native macOS baseline is a separate
stack under `macos/` and shares no code with the Linux tree — keep macOS
changes there and Linux changes out of it.

## Build, Test, and Development Commands

Run commands from `ansible/` unless noted:

```sh
ansible-playbook site.yml                  # full setup
ansible-playbook --syntax-check site.yml   # validate playbook syntax
ansible-playbook install-sonic-p06.yml     # run optional P-06 setup
desktop-file-validate ../config/desktop/rendered/*.desktop
../scripts/check-box-sonames.sh            # after box updates: sweep for soname-broken AUR binaries
../scripts/check-pc-layout.sh "$DG_PC_ROOT"  # after any PC install: flag unfiled PC-root entries
```

**After every box package update** (`pacman -Syu` in the box), run
`scripts/check-box-sonames.sh` and rebuild any AUR source packages it flags
(`makepkg -srci` — `yay -S` only reinstalls the cached binary). Soname bumps
(e.g. openexr 3.4 → 3.5 broke ES-DE + freeimage on 2026-09-28) leave AUR
binaries linking the old library. The same sweep also audits the xenia-manager
Wine prefix DPI (wine 11.18's DPI-awareness fix made Avalonia honor
`LogPixels`; anything but 96 renders the UI oversized). See
`docs/rebuild-runbook.md`.

The macOS stack has its own checks, run from the repository root on a Mac:

```sh
bash -n macos/bootstrap.sh
python3 macos/tests/verify.py       # real Ansible, temp dirs, installs nothing
brew bundle check --file=macos/Brewfile
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

For each new Wine game, preconfigure the known display and controller baseline
before launch testing. Use gamescope with the shared 1440p `dg_pc_racing_*`
settings when a game can pick monitor modes directly, and explicitly choose the
per-game `Map Controllers` value instead of relying on trial-and-error after the
user tests. For legacy DirectInput games, prefer the role's Xidi support and a
per-game virtual controller mapping over ad hoc registry toggles when modern
controller triggers show up as permanently pressed axes. Document each game's
controller policy in `docs/pc-racing.md`.

## PC Port, Decompilation, and Recompilation Defaults

For every PC port, decompilation, or recompilation, inspect settings that can be
edited outside the running game and configure them as part of installation when
practical. This machine has an RTX 5090 and 4K displays: target 3840×2160 output,
high or ultra graphics, and the highest stable frame rate the game supports.
Check the actual FPS cap, interpolation, VSync, and frame-pacing settings, and
select at least 60 FPS or a higher stable target when supported. Distinguish
the configured cap from measured gameplay FPS. Respect engine timing caps;
do not use an unpaced/debug mode just to report a higher frame rate or enable
competing VSync and pacer controls that cause uneven cadence or game-speed
changes. Keep these choices reproducible in `dg_*` variables or role
tasks, preserve saves and existing user customization, and document any setting
that can only be changed inside the game.

Always provide gamepad support. Prefer the game's native controller input;
select a working controller profile and configure buttons, sticks, triggers,
and rumble outside the game when possible. If native support is absent, provide
an appropriate controller-to-keyboard mapping. Check that the installed launcher
can see the connected pad, test actual input when feasible, and state clearly
when input could not be verified. Document the controller policy with the game.

## Documentation & Inventory Updates

Every new game install (and every patch, move, or removal of a game) must land
with its documentation and inventory in the same change — an install without
its inventory edit is incomplete. Concretely: a `docs/<game>.md` page (or an
update to the existing one), a row in `docs/sources.md` and the matching
section of `docs/external-installers.md` whenever an external artifact is
fetched or staged, a current `dg_ogm_games` entry in
`ansible/group_vars/all/ogm.yml`, and, when a required dump moves, an update to
the `dg_*` path variable or `docs/setup-assets.md` that references it. When
asked to install something that is already present and documented, verify the
inventory still matches reality instead of skipping the check.

A PC install additionally starts with the asset's placement: if the archive was
downloaded to the `ROMS_FINAL/PC` root (the usual case), move it into the right
bucket first, then point the role and docs at `…/PC/<bucket>/…`. An install that
leaves a file in the PC root is not finished, and
`scripts/check-pc-layout.sh` must report a clean root.

## Coding Style & Naming Conventions

Use YAML with two-space indentation. Prefix project variables with `dg_`.
Name roles with lowercase snake_case verbs, for example
`install_sonic_p06`. Keep shell snippets POSIX-compatible where practical and
quote paths because ROM names often contain spaces.

## Testing Guidelines

Before committing Ansible changes, run syntax checks for touched playbooks and
validate rendered `.desktop` files. For idempotent roles, rerun the playbook and
confirm the second run reports no unexpected changes.

## Temporary Resources & Cleanup

Track temporary files, extraction directories, test profiles, source checkouts,
and Docker resources created while working. After verification, remove scratch
resources that the playbook, a future rebuild, or the user will not use. Check
the exact path and its contents before removal; never clean by a broad glob.
When adding an installer, keep large downloads or extracted copies only if the
role uses them on later runs or they are needed to reproduce the install.

This host runs containers and build jobs for other projects. Inspect Docker
containers, images, volumes, and build cache before cleanup, and remove only
resources known to have been created for this task and no longer in use. Never
run blanket `docker system prune`, `docker volume prune`, or remove the
`gaming` distrobox as routine cleanup. Preserve game sources, installed files,
saves, active containers, and shared caches. Report what was removed and what
was retained when storage use is material.

## Commit & Pull Request Guidelines

Commits use concise imperative messages, such as `Add Sonic P-06 install role`.
PRs should state what role or emulator changed, which commands were run, and
whether the change touches optional user-specific assets or the default rebuild.
