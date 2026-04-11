#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

need_cmd distrobox
require_writable_dir "$DG_BOX_HOME"

if distrobox list 2>/dev/null | awk '{print $3}' | grep -qx "$DG_BOX_NAME"; then
  log "Distrobox '$DG_BOX_NAME' already exists"
else
  log "Creating distrobox '$DG_BOX_NAME' from $DG_IMAGE"
  distrobox create \
    --name "$DG_BOX_NAME" \
    --image "$DG_IMAGE" \
    --home "$DG_BOX_HOME" \
    --volume "$DG_EMUDECK_ROOT:$DG_EMUDECK_ROOT:rw" \
    --volume "$DG_BOX_ROOT:$DG_BOX_ROOT:rw" \
    --volume "$DG_HOST_APPLICATIONS_DIR:$DG_HOST_APPLICATIONS_DIR:rw"
fi

box_uid="$(in_box id -u)"
box_gid="$(in_box id -g)"
[ "$box_uid" = "$DG_HOST_UID" ] || die "Box UID $box_uid does not match host UID $DG_HOST_UID"
[ "$box_gid" = "$DG_HOST_GID" ] || die "Box GID $box_gid does not match host GID $DG_HOST_GID"
log "Distrobox UID/GID verified: $box_uid:$box_gid"

