#!/usr/bin/env sh
# Fail when a game would be invisible to ogm because its X-OGM-* metadata is
# missing, or when dg_ogm_games no longer matches the desktop templates.
#
# Background: ogm (omarchy-games-menu) lists a desktop entry ONLY when it
# carries `X-OGM-Managed=true`. That block is emitted by the shared macro
# `ansible/templates/ogm-desktop-entry.j2`, which looks the rendered stem up in
# `dg_ogm_games` (ansible/group_vars/all/ogm.yml) and renders NOTHING for a stem
# that is not registered. A new game role whose template calls the macro but has
# no `dg_ogm_games` entry is therefore silently absent from the launcher — it
# installs, it shows up in the applications menu, and ogm never sees it
# (rea-dirt-rally and rea-colin-mcrae-2005 shipped that way).
#
# Usage (from the repository root or ansible/):
#   scripts/check-ogm-coverage.sh
#
# Exit status: 0 consistent, 1 findings, 2 usage/layout problem.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OGM_YML="$ROOT/ansible/group_vars/all/ogm.yml"
TEMPLATES_DIR="$ROOT/ansible/roles"
SHARED_TEMPLATES="$ROOT/ansible/templates"
RENDERED_DIR="$ROOT/config/desktop/rendered"

[ -f "$OGM_YML" ] || { printf 'missing %s\n' "$OGM_YML" >&2; exit 2; }
[ -d "$TEMPLATES_DIR" ] || { printf 'missing %s\n' "$TEMPLATES_DIR" >&2; exit 2; }

status=0
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM

# Registered stems, in file order. Both block (`- desktop_id: x`) and flow
# (`- { desktop_id: x, ... }`) mappings appear in ogm.yml.
grep -oE 'desktop_id:[[:space:]]*("[^"]+"|'"'"'[^'"'"']+'"'"'|[A-Za-z0-9_.-]+)' "$OGM_YML" |
  sed -E 's/^desktop_id:[[:space:]]*//; s/^"//; s/"$//; s/^'"'"'//; s/'"'"'$//' |
  grep -E '^[A-Za-z0-9_.-]+$' >"$tmp/registered" || true
sort -u "$tmp/registered" >"$tmp/registered.sorted" || true

if [ ! -s "$tmp/registered" ]; then
  printf 'no desktop_id entries parsed from %s\n' "$OGM_YML" >&2
  exit 2
fi

# Stems passed to the macro from tracked templates.
{
  grep -rhoE "ogm_metadata\([[:space:]]*'[^']+'[[:space:]]*\)" \
    "$TEMPLATES_DIR" "$SHARED_TEMPLATES" 2>/dev/null || true
  grep -rhoE "ogm_metadata\([[:space:]]*\"[^\"]+\"[[:space:]]*\)" \
    "$TEMPLATES_DIR" "$SHARED_TEMPLATES" 2>/dev/null || true
} | sed -E "s/.*ogm_metadata\([[:space:]]*['\"]([^'\"]+)['\"][[:space:]]*\)/\1/" |
  sort -u >"$tmp/used" || true

# Stems the macro is called with dynamically (loops, concatenation) cannot be
# resolved statically; report the count so "0 checked" is never mistaken for
# full coverage.
dynamic=$(
  grep -rhoE 'ogm_metadata\([[:space:]]*[^'"'"'"][^)]*\)' \
    "$TEMPLATES_DIR" "$SHARED_TEMPLATES" 2>/dev/null | wc -l | tr -d ' '
)

missing=$(comm -23 "$tmp/used" "$tmp/registered.sorted")
if [ -n "$missing" ]; then
  printf '%s\n' 'ogm: template stem missing from dg_ogm_games (invisible in the launcher):'
  printf '  %s\n' $missing
  status=1
fi

dupes=$(sort "$tmp/registered" | uniq -d)
if [ -n "$dupes" ]; then
  printf '%s\n' 'ogm: duplicate desktop_id in dg_ogm_games (the macro uses only the first):'
  printf '  %s\n' $dupes
  status=1
fi


# Rendered entries are a local, gitignored artifact; check them when present
# because this is the exact symptom a user sees (install with no menu entry).
if [ -d "$RENDERED_DIR" ]; then
  for entry in "$RENDERED_DIR"/*.desktop; do
    [ -e "$entry" ] || continue
    if ! grep -q '^X-OGM-Managed=' "$entry"; then
      printf 'ogm: rendered without X-OGM-Managed: %s\n' \
        "config/desktop/rendered/$(basename "$entry")"
      status=1
    elif grep -q '^X-OGM-Managed=true' "$entry" &&
      ! grep -q '^X-OGM-Category=' "$entry"; then
      printf 'ogm: managed entry without X-OGM-Category: %s\n' \
        "config/desktop/rendered/$(basename "$entry")"
      status=1
    fi
  done
fi

printf 'ogm coverage: %s template stem(s) checked, %s registered, %s dynamic call(s)\n' \
  "$(wc -l <"$tmp/used" | tr -d ' ')" \
  "$(wc -l <"$tmp/registered" | tr -d ' ')" \
  "$dynamic"

if [ "$status" -eq 0 ]; then
  printf '%s\n' 'ogm coverage OK: every registered game renders its discovery marker'
else
  printf '%s\n' 'Fix: add/update the dg_ogm_games entry in ansible/group_vars/all/ogm.yml'
  printf '%s\n' '     (see docs/ogm-launcher.md), then re-run the affected install role.'
fi

exit "$status"
