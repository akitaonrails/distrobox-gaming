#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

require_writable_dir "$DG_HOST_APPLICATIONS_DIR"
ensure_dir "$DG_DESKTOP_RENDER_DIR"

log "Rendering Walker/desktop launchers into $DG_DESKTOP_RENDER_DIR"

for desktop in \
  gaming-shadps4.desktop \
  gaming-shadps4-driveclub-no-patch.desktop \
  gaming-shadps4-gui.desktop \
  gaming-flycast.desktop
do
  render_template \
    "$DG_DESKTOP_TEMPLATE_DIR/$desktop.in" \
    "$DG_DESKTOP_RENDER_DIR/$desktop"
  install_desktop_symlink \
    "$DG_DESKTOP_RENDER_DIR/$desktop" \
    "$DG_HOST_APPLICATIONS_DIR/$desktop"
done

if [ -x "$DG_XENIA_MANAGER_BIN" ]; then
  desktop="gaming-xenia-manager.desktop"
  render_template \
    "$DG_DESKTOP_TEMPLATE_DIR/$desktop.in" \
    "$DG_DESKTOP_RENDER_DIR/$desktop"
  install_desktop_symlink \
    "$DG_DESKTOP_RENDER_DIR/$desktop" \
    "$DG_HOST_APPLICATIONS_DIR/$desktop"
else
  rm -f "$DG_DESKTOP_RENDER_DIR/gaming-xenia-manager.desktop" \
    "$DG_HOST_APPLICATIONS_DIR/gaming-xenia-manager.desktop"
fi

if command -v desktop-file-validate >/dev/null 2>&1; then
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4.desktop"
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4-driveclub-no-patch.desktop"
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4-gui.desktop"
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-flycast.desktop"
  if [ -f "$DG_HOST_APPLICATIONS_DIR/gaming-xenia-manager.desktop" ]; then
    desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-xenia-manager.desktop"
  fi
fi

if command -v pkill >/dev/null 2>&1; then
  pkill -f '/usr/bin/walker --gapplication-service' 2>/dev/null || true
fi

log "Desktop integration completed"
