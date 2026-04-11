#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

log "Refreshing shadPS4 runtime directories"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/sys_modules"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/patches"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/custom_configs"
ensure_dir "$DG_BOX_HOME/.config/shadPS4"
ensure_dir "$DG_BOX_HOME/bin"

if [ -d "$DG_PS4_FIRMWARE_MODULES" ]; then
  log "Linking PS4 firmware modules from $DG_PS4_FIRMWARE_MODULES"
  find "$DG_PS4_FIRMWARE_MODULES" -maxdepth 1 -type f | while IFS= read -r src; do
    dst="$DG_BOX_HOME/.local/share/shadPS4/sys_modules/$(basename "$src")"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
      warn "Leaving existing non-symlink module in place: $dst"
      continue
    fi
    ln -sfn "$src" "$dst"
  done
else
  warn "PS4 firmware modules missing: $DG_PS4_FIRMWARE_MODULES"
fi

log "Seeding Driveclub shadPS4 config"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/CUSA00003.toml" \
  "$DG_BOX_HOME/.local/share/shadPS4/custom_configs/$DG_SHADPS4_TITLE_ID.toml"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/Driveclub.xml" \
  "$DG_SHADPS4_PATCH_XML"

log "Linking shadPS4 command alias for QtLauncher"
ln -sfn "$DG_SHADPS4_BIN" "$DG_SHADPS4_CMD_ALIAS"

log "Refreshing desktop launchers from project templates"
"$DG_PROJECT_ROOT/scripts/06-export-desktop-apps.sh"

log "Regenerating ES-DE custom systems so the PS4 entry matches the extracted game layout"
"$DG_PROJECT_ROOT/scripts/07-configure-es-de.sh"

log "shadPS4 refresh completed"
