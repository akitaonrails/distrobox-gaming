#!/usr/bin/env bash
# Replace a Distrobox-created container with a restricted Docker container.
# Keep the original container, renamed to NAME-legacy, for rollback.
set -euo pipefail

recreate=0
if [[ ${1:-} == --recreate ]]; then
  recreate=1
  shift
fi

if (( $# != 8 )); then
  echo "usage: $0 [--recreate] NAME BOX_HOME DATA_ROOT ROM_ROOT STEAM_LIBRARY UID BACKUP_MOUNT NVIDIA_ENABLED" >&2
  echo "  --recreate  rebuild an already-restricted container with the current device set" >&2
  exit 2
fi

name=$1 box_home=$2 data_root=$3 rom_root=$4 steam_library=$5 uid=$6 backup_mount=$7 nvidia_enabled=$8
[[ $nvidia_enabled == 0 || $nvidia_enabled == 1 ]] || { echo "NVIDIA_ENABLED must be 0 or 1" >&2; exit 2; }
candidate="${name}-restricted-candidate"
legacy="${name}-legacy"
previous="${name}-previous"
seccomp_profile=$(realpath "$(dirname "$0")/../config/docker/gaming-seccomp.json")
[[ -f $seccomp_profile ]] || { echo "Missing seccomp profile: $seccomp_profile" >&2; exit 1; }
username=$(getent passwd "$uid" | cut -d: -f1)
[[ -n $username ]] || { echo "No host user for UID $uid" >&2; exit 1; }
gid=$(id -g "$username")
display_number=${DISPLAY:-:0}
display_number=${display_number#:}
display_number=${display_number%%.*}
[[ $display_number =~ ^[0-9]+$ ]] || { echo "Unsupported DISPLAY: ${DISPLAY:-}" >&2; exit 1; }
xsocket="/tmp/.X11-unix/X$display_number"
[[ -S $xsocket ]] || { echo "X11 socket missing: $xsocket" >&2; exit 1; }
wayland_display=${WAYLAND_DISPLAY:-}
if [[ -z $wayland_display ]]; then
  for socket in "/run/user/$uid"/wayland-[0-9]*; do
    [[ -S $socket ]] || continue
    wayland_display=${socket##*/}
    break
  done
fi
[[ -n $wayland_display && -S /run/user/$uid/$wayland_display ]] || {
  echo "Wayland socket missing for UID $uid" >&2
  exit 1
}

for path in "$box_home" "$data_root" "$rom_root" "$steam_library" /tmp/.X11-unix \
  /run/dbus/system_bus_socket \
  "/run/user/$uid/pulse/native" "/run/user/$uid/pipewire-0" "/run/user/$uid/bus"; do
  [[ -e $path ]] || { echo "Required path missing: $path" >&2; exit 1; }
done
if [[ $nvidia_enabled == 1 ]]; then
  for path in /usr/share/vulkan/icd.d/nvidia_icd.json /usr/share/vulkan/implicit_layer.d/nvidia_layers.json; do
    [[ -s $path ]] || { echo "NVIDIA metadata missing: $path" >&2; exit 1; }
  done
fi

source_id=$(docker inspect --format '{{.Id}}' "$name")
source_image=$(docker inspect --format '{{.Image}}' "$name")
privileged=$(docker inspect --format '{{.HostConfig.Privileged}}' "$name")
if [[ $privileged == false && $recreate == 0 ]]; then
  echo "$name is already restricted"
  exit 0
fi
[[ $privileged == true || $privileged == false ]] || {
  echo "Cannot inspect $name" >&2; exit 1; }
if (( recreate )); then
  if docker container inspect "$previous" >/dev/null 2>&1; then
    docker rm "$previous" >/dev/null 2>&1 || {
      echo "Previous container $previous is running; stop it first" >&2; exit 1; }
  fi
elif docker container inspect "$legacy" >/dev/null 2>&1; then
  echo "Rollback container $legacy already exists; inspect it before migrating" >&2
  exit 1
fi
if docker container inspect "$candidate" >/dev/null 2>&1; then
  echo "Candidate $candidate already exists; inspect it before migrating" >&2
  exit 1
fi

# The home, ROMs and Steam library are bind mounts and are not copied into
# this image. The image holds the already-installed Arch packages only.
snapshot="dg-gaming-snapshot:${source_id:0:12}"
if ! docker image inspect "$snapshot" >/dev/null 2>&1; then
  docker commit "$name" "$snapshot" >/dev/null
fi

args=(
  --name "$candidate"
  --label manager=distrobox
  --label distrobox.unshare_groups=0
  --label "dg.migration.source=$source_id"
  --init
  --security-opt "seccomp=$seccomp_profile"
  --shm-size 1g
  --device /dev/dri
  --mount "type=bind,src=$data_root,dst=$data_root"
  --mount "type=bind,src=$steam_library,dst=$steam_library"
  --mount "type=bind,src=$rom_root,dst=$rom_root,readonly"
  --mount "type=bind,src=$data_root,dst=/run/host$data_root"
  --mount "type=bind,src=$rom_root,dst=/run/host$rom_root,readonly"
  --tmpfs /tmp/.X11-unix:rw,nosuid,nodev,mode=1777
  --mount "type=bind,src=$xsocket,dst=$xsocket,readonly"
  --mount "type=bind,src=/run/user/$uid/pulse/native,dst=/run/user/$uid/pulse/native"
  --mount "type=bind,src=/run/user/$uid/pipewire-0,dst=/run/user/$uid/pipewire-0"
  --mount "type=bind,src=/run/user/$uid/bus,dst=/run/user/$uid/bus"
  --mount "type=bind,src=/run/user/$uid/$wayland_display,dst=/run/user/$uid/$wayland_display"
  --mount type=bind,src=/run/dbus/system_bus_socket,dst=/run/dbus/system_bus_socket
  --tmpfs "/run/user/$uid:rw,nosuid,nodev,mode=0700,uid=$uid,gid=$gid"
  --tmpfs "/run/host/home/$username:rw,nosuid,nodev,uid=$uid,gid=$gid"
  --env "HOME=$box_home"
  --env "SHELL=zsh"
  --env container=docker
  --env "CONTAINER_ID=$name"
  --env "DISPLAY=${DISPLAY:-:0}"
  --env "XDG_RUNTIME_DIR=/run/user/$uid"
  --env "WAYLAND_DISPLAY=$wayland_display"
  --env "PULSE_SERVER=unix:/run/user/$uid/pulse/native"
  --env LANG=C.UTF-8
  --entrypoint /usr/bin/sleep
)
if [[ $nvidia_enabled == 1 ]]; then
  args+=(--gpus all)
  args+=(--mount type=bind,src=/usr/share/vulkan/icd.d/nvidia_icd.json,dst=/usr/share/vulkan/icd.d/nvidia_icd.json,readonly)
  args+=(--mount type=bind,src=/usr/share/vulkan/implicit_layer.d/nvidia_layers.json,dst=/usr/share/vulkan/implicit_layer.d/nvidia_layers.json,readonly)
  args+=(--env NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display,video)
fi
[[ ! -S ${xsocket}_ ]] || args+=(--mount "type=bind,src=${xsocket}_,dst=${xsocket}_,readonly")
[[ ! -e /dev/kvm ]] || args+=(--device /dev/kvm)
# AppImages mount themselves over FUSE, but a FUSE mount needs CAP_SYS_ADMIN in
# the container's bounding set (fusermount3 is setuid, yet the default Docker
# bounding set excludes SYS_ADMIN, so it fails with "Operation not permitted").
# Opt in with DG_BOX_FUSE=1, which trades that privilege for mount-based
# AppImages; the default keeps the restricted box and launchers extract instead.
if [[ ${DG_BOX_FUSE:-0} == 1 ]]; then
  [[ ! -e /dev/fuse ]] || args+=(--device /dev/fuse)
  args+=(--cap-add SYS_ADMIN)
fi
[[ ! -e /run/udev ]] || args+=(--mount type=bind,src=/run/udev,dst=/run/udev,readonly)

# Steam and SDL need input nodes. Docker's default device cgroup blocks new
# nodes after hotplug, so allow input's major while keeping other devices out.
args+=(--mount type=bind,src=/dev/input,dst=/dev/input)
args+=(--device-cgroup-rule 'c 13:* rwm')
for link in /dev/input/by-id/*8BitDo* /dev/input/by-id/*8bitdo*; do
  [[ -e $link ]] || continue
  device=$(readlink -f "$link")
  [[ $device == /dev/hidraw* ]] || continue
  args+=(--device "$device:$device:rwm")
done

migration_stage=precutover
cleanup_failed_migration() {
  rc=$?
  trap - EXIT
  [[ $migration_stage != done ]] || return 0
  docker rm -f "$candidate" >/dev/null 2>&1 || true
  if [[ $migration_stage == cutover ]]; then
    # At this point the old box has the legacy name. Any container still
    # named $name is the failed replacement and can be removed safely.
    docker rm -f "$name" >/dev/null 2>&1 || true
    if (( recreate )); then docker rename "$previous" "$name" || true; else docker rename "$legacy" "$name" || true; fi
  fi
  docker start "$name" >/dev/null 2>&1 || true
  exit "$rc"
}
trap cleanup_failed_migration EXIT

docker create "${args[@]}" "$snapshot" infinity >/dev/null
docker start "$candidate" >/dev/null

# Bind-mounted input nodes keep host numeric group IDs, which may have
# different names in Arch. Add the game user to those exact numeric groups.
device_groups=()
for device in /dev/input/event0 /dev/hidraw* /dev/dri/card* /dev/dri/renderD*; do
  [[ -e $device ]] || continue
  device_groups+=("$(stat -c %g "$device")")
done
for device_gid in $(printf '%s\n' "${device_groups[@]}" | sort -un); do
  if ! docker exec "$candidate" getent group "$device_gid" >/dev/null; then
    docker exec "$candidate" groupadd -g "$device_gid" "dg-device-$device_gid"
  fi
  docker exec "$candidate" usermod -aG "$device_gid" "$username"
done

check='set -eu
test ! -e "/home/$3/.ssh"
test ! -e "$5"
test ! -e /run/host/etc/shadow
test ! -e /var/run/docker.sock
test -S /run/dbus/system_bus_socket
test -S "$4"
test -w /tmp/.X11-unix
test -S "/run/user/$(id -u)/$WAYLAND_DISPLAY"
if [ "$6" = 1 ]; then
  test -s /usr/share/vulkan/icd.d/nvidia_icd.json
  test -s /usr/share/vulkan/implicit_layer.d/nvidia_layers.json
fi
for card in /dev/dri/card*; do
  test -e "$card" || continue
  test -r "$card"
done
test -w "/run/user/$(id -u)"
test -r "$1"
test ! -w "$1"
test -w "$2"
command -v wine >/dev/null
command -v steam >/dev/null
sudo -n true'
docker exec --user "$username" --workdir "$box_home" "$candidate" \
  sh -lc "$check" sh "$rom_root" "$box_home" "$username" "$xsocket" "$backup_mount" "$nvidia_enabled"
for link in /dev/input/by-id/*8BitDo* /dev/input/by-id/*8bitdo*; do
  [[ -e $link ]] || continue
  device=$(readlink -f "$link")
  [[ $device == /dev/hidraw* ]] || continue
  docker exec --user "$username" "$candidate" test -r "$device"
done
if [[ $nvidia_enabled == 1 ]]; then
  docker exec --user "$username" "$candidate" nvidia-smi --query-gpu=name --format=csv,noheader >/dev/null
fi

# Switch names only after the new container passes the filesystem and runtime
# checks. The old one stays stopped and available for a fast rollback.
docker stop "$name" >/dev/null
docker stop "$candidate" >/dev/null
if (( recreate )); then
  docker rename "$name" "$previous"
else
  docker rename "$name" "$legacy"
fi
migration_stage=cutover
docker rename "$candidate" "$name"
docker start "$name" >/dev/null
migration_stage=done
trap - EXIT
if (( recreate )); then
  # The verified replacement is running and all state lives in the bind-mounted
  # home, so the superseded container and its snapshot tag are redundant. Keep
  # only the image the new container was built from.
  docker rm "$previous" >/dev/null 2>&1 || true
  if [[ -n $source_image && $source_image != $(docker inspect --format '{{.Image}}' "$name") ]]; then
    docker rmi "$source_image" >/dev/null 2>&1 || true
  fi
  echo "Recreated $name with the current device set; superseded container and snapshot removed"
else
  echo "Migrated $name; rollback container: $legacy; snapshot: $snapshot"
fi
