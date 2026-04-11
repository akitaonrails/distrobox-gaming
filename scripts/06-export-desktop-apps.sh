#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

require_writable_dir "$DG_HOST_APPLICATIONS_DIR"

log "Writing Walker/desktop launchers"

cat > "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4.desktop" <<EOF
[Desktop Entry]
Name=shadPS4 Driveclub (on $DG_BOX_NAME)
Exec=/usr/bin/distrobox-enter -n $DG_BOX_NAME -- shadps4 -g $DG_SHADPS4_TITLE_ID -p $DG_SHADPS4_PATCH_XML -f true
Terminal=false
Type=Application
Icon=shadps4
Comment=PlayStation 4 emulator configured for Driveclub
Categories=Game;Emulator;
StartupWMClass=shadps4;
EOF

cat > "$DG_HOST_APPLICATIONS_DIR/gaming-flycast.desktop" <<EOF
[Desktop Entry]
Name=Flycast Hi-Res (on $DG_BOX_NAME)
Exec=/usr/bin/distrobox-enter -n $DG_BOX_NAME -- $DG_BOX_HOME/bin/flycast-hires %f
Terminal=false
Type=Application
Icon=flycast
Comment=Dreamcast and Naomi emulator
Categories=Game;Emulator;
StartupWMClass=flycast;
EOF

if command -v desktop-file-validate >/dev/null 2>&1; then
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-shadps4.desktop"
  desktop-file-validate "$DG_HOST_APPLICATIONS_DIR/gaming-flycast.desktop"
fi

if command -v pkill >/dev/null 2>&1; then
  pkill -f '/usr/bin/walker --gapplication-service' 2>/dev/null || true
fi

log "Desktop integration completed"

