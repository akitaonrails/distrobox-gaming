#!/usr/bin/env sh
# Flag launcher scripts that call Wine on the host.
#
# Wine (wine / wineboot / wineserver) exists only inside the gaming distrobox.
# A launcher that execs it bare works when a desktop entry happens to wrap it
# in `distrobox-enter`, and then silently breaks the moment someone runs the
# script by hand, copies it, or the entry is regenerated without the wrap —
# this is exactly how RyGT shipped broken ("wine: not found", rc=127).
#
# A wine-using launcher is CORRECT when any of these holds:
#   1. the script itself wraps the call in `distrobox-enter`, or
#   2. it runs under GE-Proton from the host (valid: Proton carries its own
#      runtime; STEAM_COMPAT_* env is all it needs), or
#   3. a desktop entry Execs it (or its `<name>-host` wrapper) through
#      `distrobox-enter`, or the `-host` wrapper boxes it itself, or
#   4. only ES-DE ever runs it, and ES-DE lives inside the box
#      (whitelisted below because the check cannot see esde.yml).
# Anything else is flagged: wrap the wine call, do not rely on the caller.
#
# Usage: check-launcher-wrappers.sh [bin dir] [rendered desktop dir] [repo root]
# Exit: 0 clean, 1 suspicious launchers, 2 usage error.
set -eu

BIN="${1:-/mnt/data/distrobox/gaming/bin}"
DESK="${2:-${DG_DESKTOP_RENDER_DIR:-$PWD/config/desktop/rendered}}"
REPO="${3:-$PWD}"

if [ ! -d "$BIN" ]; then
  printf 'not a directory: %s\n' "$BIN" >&2
  exit 2
fi

# Pattern 4: launched only by ES-DE, which runs inside the box.
esde_only='m2emulator-launch|xenia-canary-launch'

status=0
for f in "$BIN"/*; do
  [ -f "$f" ] || continue
  case "$f" in *'~') continue ;; esac          # editor backups
  grep -qE '(^|[[:space:]/])wine([[:space:]]|$)|wineboot|wineserver' "$f" || continue
  grep -q 'distrobox-enter' "$f" && continue   # pattern 1
  grep -q 'proton' "$f" && continue            # pattern 2
  name=$(basename "$f")
  printf '%s' "$name" | grep -Eq "^($esde_only)$" && continue  # pattern 4
  # pattern 3: an entry wraps this script, or its -host wrapper does.
  wrapped=""
  host="$BIN/$name-host"
  if [ -d "$DESK" ]; then
    wrapped=$(grep -l -E "distrobox-enter.*(${name}([-[:space:]]|$)|${name}-host)" \
                "$DESK"/*.desktop 2>/dev/null | head -1)
  fi
  if [ -z "$wrapped" ] && [ -f "$host" ] && grep -q 'distrobox-enter' "$host"; then
    wrapped="$host"
  fi
  [ -n "$wrapped" ] && continue
  printf 'unwrapped wine: %s (no distrobox-enter in script or -host wrapper, no wrapping entry, not ES-DE-only)\n' "$f"
  status=1
done

# The opposite bug: a desktop entry that wraps a script which enters the box
# itself. The nested distrobox-enter fails — there is none inside the box —
# so the game starts from a terminal but never from the menu. This is how
# GT4 and RyGT both shipped broken launchers.
if [ -d "$DESK" ]; then
  for f in "$DESK"/*.desktop; do
    [ -f "$f" ] || continue
    e=$(grep -m1 '^Exec=' "$f" || true)
    case "$e" in *distrobox-enter*) ;; *) continue ;; esac
    target=$(printf '%s\n' "$e" | grep -oE '/[^ ]+' | tail -1)
    [ -n "$target" ] && [ -f "$target" ] || continue
    if grep -q 'distrobox-enter' "$target"; then
      printf 'double-wrap: %s enters the box for %s, which enters it again\n' \
        "$(basename "$f")" "$target"
      status=1
    fi
  done
fi

if [ "$status" -eq 0 ]; then
  printf '%s\n' 'launcher wrappers OK: every wine call is boxed, proton-hosted or ES-DE-only'
else
  printf '%s\n' 'Wrap the wine call in distrobox-enter (AGENTS.md: "Wine runs inside the box").' >&2
fi
exit "$status"
