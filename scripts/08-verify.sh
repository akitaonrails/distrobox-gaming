#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

need_cmd distrobox

log "Verifying host and box identity"
box_uid="$(in_box id -u)"
box_gid="$(in_box id -g)"
[ "$box_uid" = "$DG_HOST_UID" ] || die "Box UID $box_uid does not match host UID $DG_HOST_UID"
[ "$box_gid" = "$DG_HOST_GID" ] || die "Box GID $box_gid does not match host GID $DG_HOST_GID"
printf 'Host UID/GID: %s:%s\n' "$DG_HOST_UID" "$DG_HOST_GID"
printf 'Box UID/GID:  %s:%s\n' "$box_uid" "$box_gid"

log "Verifying paths"
require_readable_dir "$DG_BIOS_ROOT"
require_writable_dir "$DG_BOX_HOME"
write_test "$DG_BOX_HOME"

log "Verifying emulator commands"
for cmd in duckstation-qt pcsx2-qt flycast dolphin-emu PPSSPPQt rpcs3 shadps4; do
  if in_box sh -lc "command -v '$cmd'" >/dev/null 2>&1; then
    printf 'OK command: %s\n' "$cmd"
  else
    warn "Missing command in box: $cmd"
  fi
done

log "Verifying shadPS4 modules"
module_dir="$DG_BOX_HOME/.local/share/shadPS4/sys_modules"
links="$(find "$module_dir" -maxdepth 1 -type l 2>/dev/null | wc -l | awk '{print $1}')"
broken="$(find "$module_dir" -maxdepth 1 -xtype l 2>/dev/null | wc -l | awk '{print $1}')"
printf 'shadPS4 module links: %s\n' "$links"
printf 'shadPS4 broken links: %s\n' "$broken"
[ "$broken" = "0" ] || die "Broken shadPS4 sys_module symlinks found"
for m in libSceFont.sprx libSceNgs2.sprx libSceUlt.sprx libSceJson.sprx libSceJson2.sprx libSceLibcInternal.sprx; do
  [ -e "$module_dir/$m" ] || die "Missing shadPS4 module: $m"
done

log "Verifying generated files"
[ -x "$DG_BOX_HOME/bin/flycast-hires" ] || die "Flycast wrapper missing or not executable"
[ -f "$DG_BOX_HOME/.local/share/shadPS4/custom_configs/$DG_SHADPS4_TITLE_ID.toml" ] || die "shadPS4 game config missing"
[ -f "$DG_SHADPS4_PATCH_XML" ] || die "shadPS4 Driveclub patch XML missing"
[ -f "$DG_BOX_HOME/ES-DE/custom_systems/es_systems.xml" ] || die "ES-DE custom systems XML missing"
[ -f "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4.desktop" ] || warn "Host shadPS4 desktop entry missing"

log "Checking for root-owned config files"
root_owned="$(find "$DG_BOX_HOME/.config" "$DG_BOX_HOME/.local/share" -maxdepth 4 -user 0 -print 2>/dev/null | sed -n '1,20p')"
if [ -n "$root_owned" ]; then
  printf '%s\n' "$root_owned"
  die "Root-owned files found under box user config"
fi

log "Verification completed"
