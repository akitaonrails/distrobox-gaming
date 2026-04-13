#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

log "Preparing xemu runtime directories"
ensure_dir "$DG_XEMU_CONFIG_DIR"
ensure_dir "$DG_XEMU_DATA_DIR"

for mapping in \
  "$DG_XEMU_BOOTROM_SOURCE:$DG_XEMU_BOOTROM" \
  "$DG_XEMU_FLASHROM_SOURCE:$DG_XEMU_FLASHROM" \
  "$DG_XEMU_HDD_SOURCE:$DG_XEMU_HDD"
do
  src="${mapping%%:*}"
  dst="${mapping#*:}"
  if [ -e "$src" ]; then
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
      warn "Leaving existing non-symlink xemu asset in place: $dst"
      continue
    fi
    ln -sfn "$src" "$dst"
  else
    warn "xemu asset missing: $src"
  fi
done

log "Preparing shadPS4 runtime directories"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/sys_modules"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/patches"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/custom_configs"
ensure_dir "$DG_BOX_HOME/.config/shadPS4/custom_configs"

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

log "Storage links completed"
