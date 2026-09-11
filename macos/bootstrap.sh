#!/bin/bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
case "${1:-}" in
  install|configure|check) mode="$1"; shift ;;
  *) echo "Usage: $0 {install|configure|check} [ansible-playbook arguments]" >&2; exit 2 ;;
esac
[[ "$(uname -s)" == Darwin ]] || { echo "This entry point requires macOS." >&2; exit 1; }
if [[ "$mode" == install ]]; then
  [[ "$#" -eq 0 ]] || { echo "install accepts no additional arguments" >&2; exit 2; }
  exec "$root/install-apps.sh"
fi
command -v ansible-playbook >/dev/null || { echo "Run $0 install first (Ansible is missing)." >&2; exit 1; }
cd "$root/ansible"
if [[ "$mode" == check ]]; then
  exec ansible-playbook -i localhost, site.yml --check --diff "$@"
fi
exec ansible-playbook -i localhost, site.yml "$@"
