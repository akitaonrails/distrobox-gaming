#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

log "Checking host commands"
need_cmd distrobox
need_cmd id
need_cmd find
need_cmd awk
need_cmd sed
need_cmd git

log "Checking configured paths"
require_writable_dir "$DG_BOX_ROOT"
write_test "$DG_BOX_ROOT"
require_readable_dir "$DG_EMUDECK_ROOT"
require_readable_dir "$DG_BIOS_ROOT"
[ -d "$DG_ROM_ROOT" ] || warn "ROM root missing: $DG_ROM_ROOT"
[ -d "$DG_ROM_HEAVY_ROOT" ] || warn "Heavy ROM root missing: $DG_ROM_HEAVY_ROOT"
[ -d "$DG_ROM_RARE_ROOT" ] || warn "Rare ROM root missing: $DG_ROM_RARE_ROOT"
require_writable_dir "$DG_HOST_APPLICATIONS_DIR"
if [ -d "$DG_PS4_ROM_ROOT" ]; then
  extras="$(find "$DG_PS4_ROM_ROOT" -mindepth 1 -maxdepth 1 ! -name "$(basename "$DG_SHADPS4_GAME_DIR")" | wc -l | tr -d ' ')"
  [ "$extras" = "0" ] || warn "PS4 root should contain only $(basename "$DG_SHADPS4_GAME_DIR"); found $extras extra top-level entries in $DG_PS4_ROM_ROOT"
else
  warn "PS4 ROM root missing: $DG_PS4_ROM_ROOT"
fi
[ -d "$DG_SHADPS4_GAME_DIR" ] || warn "shadPS4 game dir missing: $DG_SHADPS4_GAME_DIR"
[ -f "$DG_SHADPS4_GAME_BOOT" ] || warn "shadPS4 game boot file missing: $DG_SHADPS4_GAME_BOOT"

if [ -d "$DG_PS4_FIRMWARE_MODULES" ]; then
  [ -r "$DG_PS4_FIRMWARE_MODULES/libSceFont.sprx" ] || warn "PS4 firmware dir exists but libSceFont.sprx is missing"
else
  warn "PS4 firmware modules not found: $DG_PS4_FIRMWARE_MODULES"
fi

log "Host UID/GID: $DG_HOST_UID:$DG_HOST_GID ($DG_HOST_USER:$DG_HOST_GROUP)"

if distrobox list 2>/dev/null | awk '{print $3}' | grep -qx "$DG_BOX_NAME"; then
  box_uid="$(in_box id -u)"
  box_gid="$(in_box id -g)"
  log "Box UID/GID: $box_uid:$box_gid"
  [ "$box_uid" = "$DG_HOST_UID" ] || die "Box UID $box_uid does not match host UID $DG_HOST_UID"
  [ "$box_gid" = "$DG_HOST_GID" ] || die "Box GID $box_gid does not match host GID $DG_HOST_GID"
else
  warn "Distrobox '$DG_BOX_NAME' does not exist yet"
fi

log "Host check completed"
