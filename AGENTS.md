# Repository Guidelines

## Project Structure & Module Organization
`bin/dg` is the entrypoint for all setup phases. Numbered scripts in `scripts/` implement each phase in order, such as `00-check-host.sh`, `02-bootstrap-packages.sh`, and `08-verify.sh`. Shared shell helpers and environment-derived paths live in `lib/`. Machine-editable defaults live in `config/`, including `package-lists/`, `desktop/templates/`, emulator overrides, wrappers, and `distrobox-gaming.env.example`. Reference material and rebuild notes live in `docs/`.

## Build, Test, and Development Commands
Use the wrapper instead of calling scripts directly when possible:

```sh
cp config/distrobox-gaming.env.example config/distrobox-gaming.env
./bin/dg check
./bin/dg create
./bin/dg bootstrap
./bin/dg configure
./bin/dg verify
./bin/dg all
```

`check` validates host paths, permissions, and UID/GID alignment. `create` creates the distrobox. `bootstrap` installs packages. `configure` renders launchers, links storage, and seeds configs. `verify` is the main regression check for commands, generated files, and shadPS4 links. `all` runs the full rebuild flow.

## Coding Style & Naming Conventions
Write POSIX `sh`, not Bash-specific code. Follow the existing pattern: `#!/usr/bin/env sh`, `set -eu`, small functions, and shared logic moved into `lib/common.sh` or `lib/paths.sh`. Use uppercase `DG_*` names for exported configuration and descriptive lowercase names for local variables. Keep script filenames numbered as `NN-action.sh` so execution order stays obvious. Preserve shellcheck-friendly code; existing `# shellcheck disable=...` comments are intentional and should stay narrowly scoped.

## Testing Guidelines
There is no separate unit test suite in this repository. Treat `./bin/dg verify` as the required validation step for functional changes, and run the affected phase before it when needed, for example `./bin/dg configure && ./bin/dg verify`. For path or template changes, also check generated launcher output under `config/desktop/rendered/`. Do not commit machine-specific generated state, ROMs, BIOS files, firmware, or local caches.

## Commit & Pull Request Guidelines
Recent commits use short, imperative subjects such as `Manage desktop launchers from project templates` and `Simplify shadPS4 setup around QtLauncher`. Keep commits focused on one operational change. PRs should state what workflow changed, which paths or env vars are affected, and the exact verification commands run. Include screenshots only when desktop entries or launcher behavior changes.
