# Restricted game runtime

The `gaming` name now points to a Docker container created by `migrate_box`.
It was migrated from the package-filled Distrobox without moving game files,
Steam data, ROMs, prefixes, or saves. The original privileged container is
stopped as `gaming-legacy` for rollback while the migration was being
validated. That container was removed on 2026-11-06, once normal play in the
restricted runtime was confirmed: everything it held beyond the bind-mounted
home was package state that `site.yml` rebuilds.

The new runtime uses private PID/IPC namespaces, Docker's default capabilities,
a narrow extension of the Moby seccomp profile, and bridge networking. Steam's
`bwrap` needs `clone`, `unshare`, `mount`, `umount2`, `pivot_root`, and
`mount_setattr` for its nested user and mount namespaces; the profile in
`config/docker/gaming-seccomp.json` adds those calls to the default allowlist.
It is derived from `moby/profiles` commit
`4b8214fc4971e06172938a1f1554ccff6647ee80` (upstream default profile
SHA256 `6416b47770785a41ac59073cdc77d9fe98517df2799dc83ef207e622de3053f6`);
the upstream license is in `config/docker/LICENSE-moby-profiles`. This weakens
one syscall boundary compared with Docker's built-in default, but keeps the
rest of the default profile. The runtime has no real host home, Docker
socket, `dg_save_backup_nas_mount`, or writable host root. `dg_data_root` remains writable
for installed games and saves; the Emulators tree is read-only. The canonical
Steam library at `dg_steam_iscsi_root` remains writable. X11, Wayland,
PulseAudio, PipeWire, session D-Bus, and system D-Bus sockets are mounted individually so
desktop games and Steam still work. Those sockets and the writable data root
are meaningful remaining access to the host; this is a practical reduction in
filesystem and container privilege, not a complete sandbox.

The container image is a local snapshot of the old box's installed packages,
identified by the old container ID. `site.yml` creates and bootstraps a box
on a clean rebuild, then `migrate_box` snapshots and restricts it before
installing the optional games. Existing launchers still use
`distrobox-enter -n gaming`; the Docker container carries the discovery label
that makes this work. `ansible-playbook migrate-gaming-box.yml` runs just the
migration. A second run must report `changed=0`.

The old Distrobox's NVIDIA mounts leave zero-byte placeholders in a committed
image. Migration binds the host's current Vulkan ICD and implicit-layer JSON
files read-only, sets the NVIDIA graphics/display driver capabilities, and
runs the existing 32-bit NVIDIA library repair after the new container starts.
The repair links the matching extracted 32-bit libraries from the persistent
game home. The migration also restores NVIDIA EGL platform links from the
nonempty versioned package files and grants the box user the numeric DRM
device groups. This lets gamescope's Xwayland server use EGL. Verify with
`glxinfo -B`, `vulkaninfo --summary`, a short gamescope launch, and the 32-bit GLX
check in `ansible-playbook reset-configs.yml --tags gpu` after a driver update.

Direct input nodes are mounted for gamepads. The migration adds the box user
to the host input and hidraw numeric groups, and passes connected 8BitDo
hidraw devices. If the controller receives a different hidraw node after a
reconnect, the container has to be rebuilt while idle so Docker passes the new
node — `migrate_gaming_box.sh` refuses to touch an already-restricted box, so
use its recreate mode:

```sh
cd ansible
ansible-playbook migrate-gaming-box.yml -e dg_box_recreate=true
```

It snapshots the running container, creates the replacement with the current
device/capability set, runs the same filesystem and runtime checks, and only
then swaps the names. On success the superseded container is deleted and its
snapshot tag untagged, so the only image left is the one the new container was
built from (`dg-gaming-snapshot:<id>`) — see the rollback note below. This is
also the switch for `dg_box_fuse` and for any later device change — stop games
first, the box restarts. Test the pad in-game after such a change.

The Wayland socket is also bound as one file rather than granting the entire
host runtime directory (which contains credential sockets). After a compositor
restart, restart `gaming` to rebind the current socket inode before using
gamescope. Its Xwayland server needs to create its own X11 socket, so the
container has a private writable `/tmp/.X11-unix` with only the host display
socket bound into it. `migrate_box` also removes gamescope's `cap_sys_nice`
file capability, which otherwise makes `execve` fail under the restricted
Docker capability set; gamescope can run without that scheduling privilege.

The container is disposable: game data, saves, prefixes and the Steam library
all live in bind mounts, so a broken container is repaired by rebuilding it
rather than by restoring an old privileged one:

```sh
cd ansible
ansible-playbook migrate-gaming-box.yml -e dg_box_recreate=true
```

That snapshots the running container, builds a replacement with the current
device/capability set, runs the mount and runtime checks, and swaps the names.
On success the superseded container and its snapshot tag are removed, so
repeated rebuilds do not pile up 18 GB images; the image the new container
was built from stays as `dg-gaming-snapshot:<id>`. The privileged Distrobox
that preceded the migration is gone — do not recreate it.

## FUSE and AppImages (2026-11-05)

The restricted container keeps Docker's default capability bounding set, which
excludes `CAP_SYS_ADMIN`. `fusermount3` is setuid inside the image and the
seccomp profile allows `mount`, but a FUSE mount still fails with
`Operation not permitted` — so AppImages **cannot** mount here and every in-box
AppImage launcher exports `APPIMAGE_EXTRACT_AND_RUN=1` (the runtime unpacks to
`/tmp/appimage_extracted_<hash>` and reuses that copy). Lichii predates the
flag, so its role pre-extracts the AppImage and runs `AppRun`.

`dg_box_fuse: true` (plus `ansible-playbook migrate-gaming-box.yml -e
dg_box_recreate=true`) rebuilds the container with `--device /dev/fuse --cap-add
SYS_ADMIN` and makes mounting work again. That capability is close to root in
the container and reopens the class of risk the migration closed, so it stays
off; the extraction workaround costs about a second on a launcher's first run
and no permanent space outside `/tmp`.

The extracted copies live in the container's writable layer, one per AppImage
(roughly 0.5–0.8 GB: `eden`/`rpcs3` are the big ones), and are reused on later
launches. They also disappear when the container is recreated. To reclaim them
by hand:

```sh
docker exec gaming rm -rf /tmp/appimage_extracted_*
```

Only caches go; the next launch of that title extracts again.

## Narrower Lichii runtime

Run `ansible-playbook install-lichii-sandbox.yml` from `ansible/`. It builds
`dg-lichii-sandbox:build-88` from the pinned Arch base in
`config/docker/lichii-sandbox/Dockerfile`, installs a host launcher, and
publishes a separate desktop entry. It does not remove the regular Lichii
entry or move game data. The image holds only system runtime libraries and
fonts; the 24 GB owned NUP is bound read-only at launch.

The launcher grants:

| Path or interface | Access | Reason |
| --- | --- | --- |
| Lichii profile under `dg_box_home` | Read/write | Settings, shader cache and saves |
| Lichii AppImage | Read-only | Executable |
| The selected NUP | Read-only | Owned game data |
| NVIDIA GPU | Device access | Vulkan rendering |
| X11 and PulseAudio sockets | Socket access | Display and sound |
| 8BitDo Ultimate 2 device nodes, if present | Read-only device access | Controller |

The runtime has no real host home, `/run/host`, Docker socket, whole NAS
directories, or network. It runs as the configured user with all container
capabilities dropped, a read-only root filesystem, and a private process
namespace. The X11 and sound sockets remain a connection to the desktop
session; this is a practical filesystem and container-privilege boundary,
not full desktop isolation. The controller must be connected before launch
because only its then-present nodes are passed through.

Check the boundary without starting the game:

```sh
~/.local/bin/lichii-sandbox --check
```

The Lichii launcher is deliberately separate and grants fewer mounts than the
general `gaming` runtime. Validate the menu, gamepad, audio, save creation,
and the absence of unwanted host access. When a newer
Lichii release is pinned, rerun the focused playbook to rebuild the runtime
and launcher. Existing game files and saves stay at their original paths.

## Save backups

The `backup_saves` role now renders its manifest and helpers into the
**host** home. The weekly user timer calls the host helper and needs the
`dg_save_backup_nas_mount`. Neither the restricted runtime nor any game launcher
needs write access to that backup share. See [save backups](save-backups.md).
