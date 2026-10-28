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
../scripts/check-launcher-wrappers.sh "$DG_BOX_HOME/bin" "$DG_DESKTOP_RENDER_DIR"  # wine launchers must be boxed
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

## Reproducibility (every install)

**Every install is code in this repo, not a sequence of commands run once on
this box.** A new emulator, port, recomp, Wine game, mod set, fix or tool is
only finished when re-running the repo produces it again from a clean box:

- the logic lives in `ansible/roles/install_<name>/` with a thin
  `ansible/install-<name>.yml` playbook; opt-in features carry a `never` tag in
  `site.yml`, anything the default rebuild needs is on the plain path;
- every download is pinned in `ansible/group_vars/all/<name>.yml` by version,
  URL and SHA256, recorded as an **AUTO** row in `docs/external-installers.md`,
  and staged in `ROMS_FINAL/PC/releases/` — not left in a browser download
  folder or a shell history;
- paths come from `dg_*` variables, so another machine only edits
  `host_vars/localhost.yml`;
- when a step genuinely cannot be automated (a GUI-only preparation inside a
  Windows installer, a user-owned dump), the role fails or skips with the exact
  instructions and `docs/<name>.md` records it. A step that exists only on this
  machine, undocumented, is a bug — backfill a role for it or write down why it
  cannot be one;
- the change ships with its docs and inventory rows (see *Documentation &
  Inventory Updates*) and a second `ansible-playbook` run reports `changed=0`
  (or only the known Wine-registry churn).

## Reuse And Wine Game Patterns

### Wine runs inside the box (hard rule — this broke twice)

Wine (`wine`, `wineboot`, `wineserver`) exists **only inside the gaming
distrobox**. A host-side launcher that calls it bare dies with
`wine: not found` (rc=127) — exactly how RyGT shipped — and a desktop entry
that wraps a script which *also* wraps itself fails differently: the nested
`distrobox-enter` does not exist inside the box, so the game starts from a
terminal but never from the menu (how GT4 and RyGT both broke on 2026-10-28).
When writing or touching a launcher:

- **Make every Wine launcher re-entrant** and let the desktop entry point at
  the script directly (`Exec={{ dg_*_bin }}`, no outer `distrobox-enter`):

  ```sh
  if [ ! -e /.dockerenv ]; then
    exec distrobox-enter -n {{ dg_box_name }} -- sh "$0" "$@"
  fi
  # … wine runs here, inside the box
  ```

- GE-Proton launchers run **from the host** on purpose (Proton carries its own
  runtime; set `STEAM_COMPAT_*` and call the `proton` binary) — do not box them.
- Scripts that only ES-DE runs (inside the box already) are exempt.
- After any launcher change, run
  `scripts/check-launcher-wrappers.sh [bin dir] [rendered desktop dir]` — it
  flags bare host-side Wine **and** entry/script double-wraps, and must be clean.

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

## Graphics: Always Max Out (every install)

Every game here runs on the same machine — an RTX 5090 driving 4K displays — so
the default answer to "which preset?" is **the highest one that still holds a
stable frame rate**. Study the game's graphics settings while installing it, not
after a disappointing first launch, and apply the ceiling as part of the role:

- **Find the knobs first.** Look for a settings file, launch flags, or
  environment variables the installer can preconfigure, then read the game's /
  port's own docs and issue tracker for combinations known to break (for FM4:
  async shader compilation with readback off, guest `vsync` off, a 4K *guest*
  video mode; for GT2: widescreen hack fighting the widescreen patch). Prefer
  documented-safe maximal settings over guesswork, and never adopt a
  "better" setting that upstream lists as artifact-prone.
- **Target:** 3840×2160 output; native render resolution where the engine
  supports it, render-scale + downscale where it does not; highest texture,
  model, shadow and draw-distance tier; 16× anisotropic filtering; the engine's
  best-supported anti-aliasing (MSAA/SMAA/TAA, whichever it implements); and the
  highest stable frame rate — at least 60 FPS, higher when the game's physics,
  timing and pacing are built for it.
- **Keep it reproducible.** The chosen values live in `dg_*` variables or role
  tasks. Seed a settings file only when it does not exist, or enforce only the
  keys the role owns, so a rerun reports `changed=0` and the player's later
  in-game changes survive.
- **Settings that only exist in-game** (or behind a GUI toggle the installer
  cannot reach) are recorded in `docs/<game>.md` with the exact menu path and
  value, together with what was deliberately left at default and why.
- **Report the cap, not just a number.** A cap (60 / 120 / uncapped) is a
  setting; measured gameplay FPS is a result. Respect engine timing caps, never
  run an uncapped/unpaced debug mode just to quote a higher figure, and never
  stack competing VSync/pacer controls that cause uneven cadence or change game
  speed.
- **Verify when feasible** — swapchain/window resolution in the log, the preset
  shown in the settings UI, AA/AF and fullscreen in a screenshot — and say
  plainly when a setting could not be verified.

Never leave a game on the installer's "Medium"/"Auto" default when a
higher setting is known-good here, and never trade a stable frame rate for a
higher preset: pick the highest settings that still hold the target, not the
highest numbers on the menu.

## PC Port, Decompilation, and Recompilation Defaults

For every PC port, decompilation, or recompilation, inspect settings that can be
edited outside the running game and configure them as part of installation when
practical, at the ceiling described in *Graphics: Always Max Out* above. Check
the actual FPS cap, interpolation, VSync, and frame-pacing settings, and select
at least 60 FPS or a higher stable target when supported. Distinguish the
configured cap from measured gameplay FPS. Keep these choices reproducible in
`dg_*` variables or role tasks, preserve saves and existing user customization,
and document any setting that can only be changed inside the game.

## Gamepad: Always Supported (every install)

Every game here is played from the couch with a controller (the reference device
on this box is an **8BitDo Ultimate 2**, USB `2dc8:310b`), so a game with no
working pad input is not a finished install. Study how the game reads input
before wiring anything up, and make the pad work as part of the role:

- **Find out how the game reads input.** Native SDL/XInput/RawInput, an
  emulator/libretro core mapping, a port's own controller profile, or
  keyboard-only. Read the game's docs, launcher options and issue tracker for the
  supported backends and their known breakage: Wine's **Windows.Gaming.Input**
  enumerates a pad but never fires `GamepadAdded` (breaks hl360 FM4 and GT2's
  gilrs — the fix there is `WINEDLLOVERRIDES="windows.gaming.input=d"`), legacy
  DirectInput games report modern triggers as permanently pressed axes (Xidi in
  the PC racing pipeline), and some ports only poll one pad or want a specific
  mapping mode.
- **Prefer the game's own pad support**, then a launcher/emulator mapping, and
  only then a keyboard bridge (AntiMicroX for GT2) — and record which of the
  three the install relies on.
- **Configure it in the role, not by hand.** Bind every control the game uses
  (sticks, triggers, shoulders, face buttons, Start/Back, d-pad, rumble where
  supported), select the per-game profile from `dg_*` data, and keep the
  mapping idempotent (`changed=0` on a rerun). Never leave keyboard/mouse mode
  or a "keyboard as pad" default on: it silently steals the d-pad and left stick.
- **Prove the pad is seen**: the device should appear in the port/emulator log
  (SDL device add, `/dev/input`, input settings) and the mapping should be
  exercised in-game when feasible. Say explicitly when a control could not be
  verified rather than implying it works.
- **When native support is missing or broken**, ship the documented workaround
  (mapping file, bridge, DLL override), link the upstream issue, and note which
  controls it cannot cover.
- **Document the controller policy** in `docs/<game>.md` — and in
  `docs/pc-racing.md` for the Wine racing titles — including anything that can
  only be changed in-game.

## Save Data: Every Install Registers Its Paths

`dg_save_sets` in `ansible/group_vars/all/backups.yml` is the only place the
backup service learns what to mirror (see `docs/save-backups.md`). An install is
not finished until its save data is listed there — a game whose saves are
missing from that list is silently unprotected.

- **Find where the game actually writes**, not where the README says: run it
  once and look for the config dir, user-data dir, memory card, or loose
  `.sav`/`.srm`/`.eep`/`.bin`/`.xml` save files beside the executable.
- **Add a `dg_save_sets` entry**: a unique `name` (no spaces) and `src`, which
  is a box-home-relative path, an absolute path for the native ports that run
  on the *host* rather than in the box, or `file:` for one loose save file. A
  set may list several sources and they all mirror into the same `<name>`
  directory.
- **Point at save data only.** Leave out what a rebuild re-derives — extracted
  discs, texture packs, shader caches, ROM caches. Dusk keeps 6 GB of textures
  beside its 36 KB memory card; Fukami a 461 MB extracted disc beside `mc/`.
- **Verify both ends**: re-run `ansible-playbook site.yml --tags backup_saves`
  to re-render the manifest, then
  `distrobox enter gaming -- backup-saves --dry-run` and confirm the new set
  appears (or reports "no local data" until the game is first played).

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
