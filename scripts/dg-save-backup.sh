#!/usr/bin/env bash
# dg-save-backup — host-side wrapper that runs the host save backup.
#
# Invoked by the dg-save-backup.service systemd *user* unit (weekly timer,
# Tuesday 23:00). Kept deliberately env-robust for the bare systemd/cron
# environment: an explicit absolute PATH and NAS mount,
# and a clean skip (exit 0) when the NAS isn't mounted so a transient outage
# doesn't leave the unit in a failed state.
#
# The set list + backup root are rendered by the backup_saves Ansible role
# into the host's ~/.config/distrobox-gaming/.
set -euo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${HOME}/.local/bin"

CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/distrobox-gaming"
. "$CONF_DIR/backup.env"

if ! mountpoint -q "$DG_BACKUP_MOUNT"; then
  echo "dg-save-backup: $DG_BACKUP_MOUNT is not mounted; skipping this run."
  exit 0
fi

echo "dg-save-backup: starting $(date -Is)"
"$HOME/.local/bin/backup-saves" "$@"
echo "dg-save-backup: finished $(date -Is)"
