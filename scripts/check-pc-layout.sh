#!/usr/bin/env sh
# Fail when something is sitting loose in the ROMS_FINAL/PC root.
#
# The PC library is bucketed (ports/, games/, mods/, releases/, tools/ —
# see docs/pc-library.md). Files downloaded to the root must be filed into
# the right bucket before the install is considered done, so this check is
# the cheap way to notice a stray archive before it becomes a path in a
# playbook.
#
# Usage:
#   scripts/check-pc-layout.sh /path/to/ROMS_FINAL/PC
#   DG_PC_ROOT=/path/to/ROMS_FINAL/PC scripts/check-pc-layout.sh
#
# Exit status: 0 clean, 1 unfiled entries, 2 usage/not a directory.
set -eu

PC="${1:-${DG_PC_ROOT:-}}"
if [ -z "$PC" ]; then
  printf '%s\n' 'usage: check-pc-layout.sh <ROMS_FINAL/PC>   (or set DG_PC_ROOT)' >&2
  exit 2
fi
if [ ! -d "$PC" ]; then
  printf 'not a directory: %s\n' "$PC" >&2
  exit 2
fi

status=0
for entry in "$PC"/* "$PC"/.[!.]*; do
  [ -e "$entry" ] || continue
  name=$(basename "$entry")
  case "$name" in
    ports | games | mods | releases | tools) continue ;;
  esac
  printf 'unfiled: %s\n' "$name"
  status=1
done

if [ "$status" -eq 0 ]; then
  printf '%s\n' 'PC layout OK: only ports/ games/ mods/ releases/ tools/ at the root'
else
  printf '%s\n' 'File each entry above into ports/ games/ mods/ releases/ or tools/ (docs/pc-library.md).' >&2
fi
exit "$status"
