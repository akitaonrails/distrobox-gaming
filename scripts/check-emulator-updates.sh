#!/usr/bin/env sh
# Check the repo-managed, upstream-pinned EMULATOR AppImages for updates.
#
# `update-gaming` (inside the box) updates pacman + AUR + RetroArch, but it does
# NOT touch the emulators we moved off AUR onto sha256-pinned upstream AppImages
# — rpcs3 and xemu. Those only move when their pin in ansible/group_vars/all/ is
# bumped and the role re-run, so a routine box update silently leaves them
# behind. This flags that.
#
# Report-only: it compares the pinned asset name in group_vars against the
# current upstream release and prints OK / OUTDATED. It never edits a pin or
# downloads anything — applying an update is a deliberate bump (new sha256) +
# `ansible-playbook install-<emu>.yml`, so the change is reproducible and tested.
#
# Exit 1 if anything is outdated (so it stands out in the update procedure).
#
# NOT covered here (by design): shadps4 and xenia-manager self-update to the
# latest upstream release when their roles run — just re-run them as part of the
# procedure (refresh-shadps4.yml, install-xenia.yml). Game ports/recomps/mods
# are the separate, per-game "ports update sweep", not routine box maintenance.
#
# See docs/rebuild-runbook.md ("Updating the box").
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
gv="$here/../ansible/group_vars/all"

pin_of() { grep -m1 "^$2:" "$gv/$1" | sed -E 's/^[^:]+:[[:space:]]*"?([^"#]+)"?.*/\1/' | sed 's/[[:space:]]*$//'; }

# Latest non-dbg x86_64 AppImage asset name for a GitHub release endpoint.
latest_appimage() { # <api-url> <grep-filter>
  curl -s "$1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
flt = '''$2'''
names = [a['name'] for a in d.get('assets', []) if a['name'].endswith('.AppImage') and flt in a['name'] and '-dbg-' not in a['name']]
print(names[0] if names else '')
"
}

rc=0
report() { # <name> <pinned> <latest>
  if [ -z "$3" ]; then printf '  ?  %-8s pin %s (could not read upstream)\n' "$1" "$2"; return; fi
  if [ "$2" = "$3" ]; then printf '  \342\234\223  %-8s %s\n' "$1" "$2"
  else printf '  \342\206\221  %-8s OUTDATED: %s -> %s\n' "$1" "$2" "$3"; rc=1; fi
}

echo "emulator-appimage-updates:"

# rpcs3 — latest release of the binaries repo
rp_pin="$(pin_of rpcs3.yml dg_rpcs3_asset_name)"
rp_new="$(latest_appimage 'https://api.github.com/repos/RPCS3/rpcs3-binaries-linux/releases/latest' 'linux64')"
report rpcs3 "$rp_pin" "$rp_new"

# xemu — the rolling "pre-release" tag's current x86_64 AppImage
xe_pin="$(pin_of xemu.yml dg_xemu_asset_name)"
xe_new="$(latest_appimage 'https://api.github.com/repos/xemu-project/xemu/releases/tags/pre-release' 'x86_64')"
report xemu "$xe_pin" "$xe_new"

if [ "$rc" -ne 0 ]; then
  echo "Bump the pin (asset name + version + sha256 from the GitHub asset digest) in" >&2
  echo "ansible/group_vars/all/<emu>.yml, then: ansible-playbook install-<emu>.yml" >&2
fi
exit "$rc"
