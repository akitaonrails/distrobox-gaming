# Lichii Switch 2 experiment

Lichii is an experimental Switch 2 emulator. The optional install uses
[upstream build 88](https://github.com/zortos293/Lichii/releases/tag/build-88),
the Linux x86_64 AppImage (build 88 has no PGO variant; build 83 was the last
one). Its SHA256-pinned release stays in `ROMS_FINAL/PC/releases/`; the
executable copy lives in `tools/lichii/build-88/`.
The regular Eden installation, keys, settings, saves and caches are separate.

**No FUSE in the migrated container.** The `gaming` runtime codex built from
`migrate_box` exposes no `/dev/fuse`, so an AppImage cannot be mounted there.
The role therefore unpacks the AppImage once with `--appimage-extract` and both
launchers run `squashfs-root/AppRun` (`dg_lichii_appdir` / `dg_lichii_apprun`);
the stored `.AppImage` stays as the provenance/rebuild artifact. Upgrading the
release also deletes the replaced `tools/lichii/<release>/` tree and NAS archive
(`dg_lichii_superseded_releases`).

Run from `ansible/`:

```sh
ansible-playbook install-lichii.yml
```

The role checks the owned
`ROMS_FINAL/switch2/The Legend of Zelda Ocarina of Time [0400486024dec000][v131072].nup`
by exact length, NUP v1 header fields, and table-of-contents SHA256 without
unpacking its 24 GB payload. It publishes **Lichii Switch 2 (Experimental)**
and **Ocarina of Time (Lichii Experimental)** menu entries. The latter runs
the same file directly with Lichii's `-g` option. Override `dg_lichii_game`
and `dg_lichii_game_size` in `host_vars/localhost.yml` for another owned dump.

The isolated profile is `tools/lichii/profile/`, under separate XDG config,
data and cache roots. The first-run config requests docked mode, Vulkan on
the NVIDIA ICD, a 12 GB memory layout, and 1x internal resolution. 1x is an
intentional starting point: upstream reports low speed and rendering issues
even on RTX 50-series GPUs. The USB 8BitDo Ultimate 2 SDL GUID and all core
controls (sticks, triggers, shoulders, face buttons, Start/Back, d-pad and
rumble) are seeded from this machine's working Eden mapping. The file is
seeded only when absent, so later in-app settings survive role reruns.
The wrapper requests Qt's X11 backend because Lichii warns that its Wayland
backend has significant performance problems.

## Restricted runtime pilot

`ansible-playbook install-lichii-sandbox.yml` builds a separate, unprivileged
Docker runtime and adds **Ocarina of Time (Lichii Restricted)** to the menu.
This is separate from the migrated, restricted `gaming` container. The image
recipe is `config/docker/lichii-sandbox/Dockerfile` with a pinned Arch base
digest. Re-running the playbook refreshes the image and launcher when their
inputs change. The AppImage, NUP and existing Lichii profile remain in their
original locations; no game data is copied into the image.

The host launcher is `~/.local/bin/lichii-sandbox`. It starts with no network,
all Linux capabilities dropped, a read-only container root, no host home or
`/run/host`, and no NAS directory mounts. It grants only the Lichii profile read/write,
the AppImage and NUP read-only, the NVIDIA GPU, X11 and PulseAudio sockets, and
the 8BitDo Ultimate 2 input nodes when connected. Connect the controller
**before** launching; hotplugging it later requires a restart. The regular
Lichii session and restricted one share a profile, so the launcher refuses to
start while the regular AppImage is running. Run
`~/.local/bin/lichii-sandbox --check` to verify mounts and GPU without opening
the game.

The restricted runtime is a pilot, not a claim that GUI applications are fully
sandboxed: the X11 and audio sockets still link it to the desktop session.
The NUP and save behavior is the same experimental build described below.
The 2026-11-05 bounded launch reached the game with normal menu fonts after
adding Noto/DejaVu fonts; controller input and sustained gameplay in this
runtime still need live verification.

[The build-75 report for this exact game](https://github.com/zortos293/Lichii/issues/94)
documents a black 3D scene in handheld mode. Switching to docked mode fixed
that symptom for two NVIDIA users, but stutter and exposure problems remained.
There is no supported 60 FPS or 4K gameplay claim for this build. Raise the
resolution scale only after verifying stable gameplay on this machine.

## What build 88 changed (upstream, since build 83)

No settings keys changed (`src/common/settings.h` is identical between the
tags), so the seeded profile stays valid. From the release notes:

- **Zelda: Ocarina of Time Dynamic FPS** — Dark's mod, ported by Frizti, is now
  bundled and **enabled by default for Ocarina**; disable it in the game's
  Add-Ons settings. It patches only the supported build (with instruction,
  padding and timer checks), and the notes recommend **CPU Clock Normal** while
  evaluating it — our profile never raises the clock.
- Frizti's performance ports: cached storage-buffer bindings, direct native
  uniform-bank uploads, batched command-page readbacks, less writer tracking,
  earlier GPU submission, and explicit GPU-to-host visibility before readback.
- Vulkan pipeline cache v53 (keeps compatible v52 caches; interrupted cache
  migrations are retryable) and bounded background preparation of cached
  pipelines and task/mesh shader state.
- FSR3 frame generation fixes (still off by default).

The four commits on `nx2` after the build-88 tag are AMD shader/depth fixes, a
MinGW-only AV1 change and one SSBO-alignment fix upstream has not released yet;
the notes say the AMD work lands in the next build, so build 88 is the newest
usable version for this NVIDIA box.

## Local smoke test (2026-11-05)

The NUP booted with the NVIDIA RTX 5090 Vulkan device and reached a fully
rendered title screen with **New Game** selectable. Its intro and title screen
showed roughly 59–60 FPS at 1x, docked. A second bounded test with Lichii's
keyboard defaults also reached the menu, but synthetic key input did not enter
a new game. Both bounded tests were stopped and reaped.

A later desktop-launched session, with the 8BitDo controller connected,
advanced through the opening story and rendered 3D scene. The scene had severe
overexposure and ran at about 9 FPS while hundreds of shaders were building;
a later frame showed about 23 FPS with four shaders building. These are
momentary readings, not a steady gameplay benchmark. The installed controller
map is present, but individual buttons and sustained gameplay have not been
verified. Leave this experiment at 1x until rendering and frame pacing improve.

Game saves are under `tools/lichii/profile/data/eden/nand/user/save/` and
registered with `dg_save_sets`; the live session created `option.sav` and
`account.sav` there. The NUP game file and shader caches are not
backed up by that service. Lichii's firmware and keys are not bundled; the
unencrypted NUP format can be opened without Switch 1 decryption keys.
