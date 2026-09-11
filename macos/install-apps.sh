#!/bin/bash
# Application inventory lives exclusively in Brewfile.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
usage() {
  cat <<'HELP'
Usage: install-apps.sh [--list | --check | --help]

Without arguments: install/update the packages declared in macos/Brewfile.
--list   List the required packages without installing them.
--check  Report missing/outdated packages without installing them.

Requires macOS and Homebrew (https://brew.sh).
Add new applications to macos/Brewfile, then run this script again.
HELP
}
[[ "$#" -le 1 ]] || { usage >&2; exit 2; }
case "${1:-}" in
  --help|-h) usage; exit 0 ;;
  --list) action=list ;;
  --check) action=check ;;
  '') action=install ;;
  *) usage >&2; exit 2 ;;
esac
[[ "$(uname -s)" == Darwin ]] || { echo "This installer requires macOS." >&2; exit 1; }
command -v brew >/dev/null || { echo "Homebrew is missing. Install it from https://brew.sh, then rerun this script." >&2; exit 1; }
case "$action" in
  list) exec brew bundle list --all --file="$root/Brewfile" ;;
  check)
    brew bundle check --verbose --file="$root/Brewfile"
    python3 "$root/scripts/install-cores.py" --check
    ;;
  install)
    echo "Installing/updating packages from $root/Brewfile"
    brew bundle install --file="$root/Brewfile"
    python3 "$root/scripts/install-cores.py"
    brew bundle check --verbose --file="$root/Brewfile"
    echo "Installation verified. Next: configure library paths and run macos/bootstrap.sh check."
    ;;
esac
