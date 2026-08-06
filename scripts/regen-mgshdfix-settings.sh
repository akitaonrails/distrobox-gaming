#!/usr/bin/env bash
# Regenerate a valid MGSHDFix.settings for an MGS Master Collection game.
#
# MGSHDFix 4.x refuses to run with a missing or old-format settings file (e.g.
# after the .asi is updated to a newer version than the on-disk settings) and it
# does NOT auto-generate one — its Config Tool must be run once. This runs that
# Config Tool *offscreen* (SDL_VIDEODRIVER=offscreen) so it can generate the
# settings headlessly. Must run INSIDE the gaming box (needs Proton/wine).
#
# Idempotent: if a valid settings (containing a [Debugging] section) already
# exists it does nothing. Safe to run every playbook — it self-heals drift.
#
# Usage (typically piped into the box via `bash -s`):
#   regen-mgshdfix-settings.sh <game_dir> <wineprefix> <proton_wine>
set -euo pipefail

game="${1:?game_dir required}"
pfx="${2:?wineprefix required}"
wine="${3:?proton wine path required}"
plugins="$game/plugins"

[ -f "$plugins/MGSHDFix.asi" ] || { echo "skip: MGSHDFix not installed"; exit 0; }
[ -f "$plugins/MGSHDFix Config Tool.exe" ] || { echo "skip: no Config Tool"; exit 0; }
if [ -f "$plugins/MGSHDFix.settings" ] && grep -qE '^\[Debugging\]' "$plugins/MGSHDFix.settings"; then
  echo "already-valid"; exit 0
fi
[ -d "$pfx" ] || { echo "skip: prefix not created yet — launch the game once, then re-run"; exit 0; }
[ -x "$wine" ] || { echo "skip: wine not executable: $wine"; exit 0; }

cd "$plugins"
[ -f MGSHDFix.settings ] && cp -f MGSHDFix.settings MGSHDFix.settings.dg-stale-backup
rm -f MGSHDFix.settings
WINEPREFIX="$pfx" SDL_VIDEODRIVER=offscreen WINEDEBUG=-all \
  "$wine" "MGSHDFix Config Tool.exe" >/tmp/mgshdfix_cfgtool.log 2>&1 &
wp=$!
for _ in $(seq 1 150); do [ -f MGSHDFix.settings ] && break; sleep 1; done
kill "$wp" 2>/dev/null || true; sleep 1; kill -9 "$wp" 2>/dev/null || true

if grep -qE '^\[Debugging\]' MGSHDFix.settings 2>/dev/null; then
  echo "regenerated ($(grep -cE '^\[' MGSHDFix.settings) sections)"
else
  echo "FAILED to regenerate (see /tmp/mgshdfix_cfgtool.log in the box)"; exit 1
fi
