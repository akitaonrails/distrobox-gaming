#!/usr/bin/env bash
# Install (or update) the weekly save-backup systemd *user* timer on the host.
# Idempotent. Run from the host (not inside the box):
#
#   scripts/install-save-backup-timer.sh
#
# Removes it with:  scripts/install-save-backup-timer.sh --uninstall
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin/dg-save-backup"
UNIT_DIR="$HOME/.config/systemd/user"

if [ "${1:-}" = "--uninstall" ]; then
  systemctl --user disable --now dg-save-backup.timer 2>/dev/null || true
  rm -f "$UNIT_DIR/dg-save-backup.timer" "$UNIT_DIR/dg-save-backup.service" "$BIN"
  systemctl --user daemon-reload
  echo "dg-save-backup timer removed."
  exit 0
fi

install -Dm755 "$SRC/dg-save-backup.sh" "$BIN"
install -Dm644 "$SRC/systemd/dg-save-backup.service" "$UNIT_DIR/dg-save-backup.service"
install -Dm644 "$SRC/systemd/dg-save-backup.timer"   "$UNIT_DIR/dg-save-backup.timer"

systemctl --user daemon-reload
systemctl --user enable --now dg-save-backup.timer

echo "Installed dg-save-backup weekly timer (Tue 23:00). Schedule:"
systemctl --user list-timers dg-save-backup.timer --no-pager || true
echo
echo "Note: user timers fire while you're logged in; Persistent=true runs a"
echo "missed backup at next login. To run even when logged out:"
echo "  sudo loginctl enable-linger $USER"
