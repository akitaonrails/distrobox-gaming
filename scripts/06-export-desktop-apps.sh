#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"

cd "$DG_PROJECT_ROOT/ansible"
ansible-playbook site.yml --tags desktop

exec "$DG_PROJECT_ROOT/scripts/install-host-launchers.sh"
