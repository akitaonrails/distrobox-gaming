#!/usr/bin/env bash
# dg-save-backup — host-side wrapper that runs the in-box save backup.
#
# Invoked by the dg-save-backup.service systemd *user* unit (weekly timer,
# Tuesday 23:00). Kept deliberately env-robust for the bare systemd/cron
# environment: an explicit absolute PATH, an explicit box name and NAS mount,
# and a clean skip (exit 0) when the NAS isn't mounted so a transient outage
# doesn't leave the unit in a failed state.
#
# The actual set list + backup root live in the box (rendered by the
# backup_saves Ansible role into ~/.config/distrobox-gaming/); this wrapper only
# drives it.
set -euo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${HOME}/.local/bin"

BOX="${DG_BOX:-gaming}"
NAS_MOUNT="${DG_NAS_MOUNT:-/mnt/terachad}"

if ! mountpoint -q "$NAS_MOUNT"; then
  echo "dg-save-backup: $NAS_MOUNT is not mounted; skipping this run."
  exit 0
fi

echo "dg-save-backup: starting $(date -Is) (box=$BOX)"
/usr/bin/distrobox enter "$BOX" -- bash -lc '$HOME/bin/backup-saves'
echo "dg-save-backup: finished $(date -Is)"
