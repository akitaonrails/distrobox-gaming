# Lichii Switch 2 experiment

Lichii is an experimental Switch 2 emulator. It is installed from
[upstream source](https://github.com/zortos293/Lichii) at a pinned commit on
branch `nx2`, because the releases trail the branch — the newest one
(`build-117`) is 56 commits behind this pin — and those commits are the Ocarina
of Time performance and stability work this box wants:

| | |
|---|---|
| Commit | `ad477ef1f4b54ed48db6ce73cc990a141637e55b` (`ad477ef`, branch `nx2`, 2026-11-08) |
| Source | `Lichii-<commit>.tar.gz`, SHA256-pinned, staged in `ROMS_FINAL/PC/ports/lichii/` |
| Build tree | `tools/lichii/build-ad477ef/{src,build-clang}` |
| Binary | `tools/lichii/build-ad477ef/build-clang/bin/lichii` (43 MB), plus `eden-cli` |
| Launcher | `bin/lichii`; entries **Lichii Switch 2 (Experimental)** and **Ocarina of Time (Lichii Experimental)** |

Run from `ansible/`:

```sh
ansible-playbook install-lichii.yml
```

The regular Eden installation, its keys, settings, saves and caches stay
separate; Lichii has its own profile under `tools/lichii/profile/`.

## Building it

The role installs the documented Arch dependencies from `docs/Deps.md`
(`clang`, `cmake`, `ninja`, Qt6, sdl3, Vulkan headers, spirv-tools, boost…;
`zlib` is left out because this box already carries `zlib-ng-compat`, which
conflicts), extracts the pinned tarball once, configures with CMake + Ninja and
builds 1,816 targets (`-j 30`, about twelve minutes here). It then checks the
binary exists; a failed build is reported as a failure, not skipped.

**clang, not gcc.** GCC 16 rejects the build at
`src/shader_recompiler/backend/spirv/emit_spirv_tensor.cpp:55`: the lambda
parameter `columns` shadows the enclosing function's parameter and upstream
builds with `-Werror=shadow`. clang does not warn there (verified with a
minimal repro of both compilers), so the configure step pins
`-DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++`. Upstream's own
"Fix Linux builds with GCC shadow warnings" commit predates the code that
still trips it. The running window reports the build:
`Lichii | ad477ef1f4-nx2 | Clang 23.1.4`.

## The game file

The role checks the owned
`ROMS_FINAL/switch2/The Legend of Zelda Ocarina of Time [0400486024dec000][v131072].nup`
by exact length, NUP v1 header fields and table-of-contents SHA256 without
unpacking its 24 GB payload. The **Ocarina of Time** entry runs that file
directly with Lichii's `-g` option. Override `dg_lichii_game` and
`dg_lichii_game_size` in `host_vars/localhost.yml` for another owned dump.
Lichii's firmware and keys are not bundled; the unencrypted NUP format opens
without Switch 1 decryption keys.

## Settings

The profile is `tools/lichii/profile/` under its own XDG config, data and cache
roots. A fresh profile is rendered from `templates/qt-config.ini.j2` (docked
mode, Vulkan on the NVIDIA ICD, the 8BitDo mapping, Qt's X11 backend — Lichii
warns that its Wayland backend has significant performance problems). The
GPU/graphics baseline below mirrors the defaults of the Frizti fork (a
Windows-only build, tested here under Wine and removed), applied to the source
build as `dg_lichii_profile_settings`:

| Key | Value | Why |
|---|---|---|
| `memory_layout_mode` | `2` (8 GB) | the game's own memory size |
| `gpu_accuracy` | `0` (Low / "Fast") | Frizti's GPU Mode |
| `nvdec_emulation` | `2` (GPU) | GPU video decoding |
| `use_asynchronous_shaders` | `true` | background shader compilation |
| `async_presentation` | `true` | non-blocking present |
| `vsync_mode` | `1` (Mailbox) | lowest-latency pacing |
| `use_docked_mode` | `1` | docked; handheld showed a black 3D scene |
| `resolution_setup` | `3` (1x) | see the note below |
| `use_disk_shader_cache` | `true` | persistent pipeline cache |

Each key is written together with its `<key>\default=false` companion. That
matters: the frontend treats a missing (or `true`) `\default` flag as "use the
built-in default" and rewrites the value on exit, which silently reverted GPU
accuracy and hardware decoding until this was fixed. The baseline is written
once and recorded in `tools/lichii/profile/.baseline-applied`; later in-app
changes win, and a role rerun does not touch them. To re-apply it, delete that
marker and rerun the playbook.

`resolution_setup` stays at 1x deliberately. Upstream reports low speed and
rendering problems above it, this box has no verified 4K gameplay claim for the
title, and the fork's own recommendation is native. Raise it only after
measuring stable gameplay, per *Graphics: Always Max Out* in `AGENTS.md`.
Lichii also has `fps_limit` (0 = the game's own vblank); it is left at 0 so the
bundled **Dynamic FPS** mod keeps pacing the game.

## Shared shader caches (unofficial)

[oceanpacificpeace/lichii-shader-sync](https://github.com/oceanpacificpeace/lichii-shader-sync)
merges cache packs published by other players into the profile's Vulkan
pipeline cache, so a first playthrough stutters less than when Lichii compiles
every pipeline on first use. The Ocarina pack covers **88,982 pipelines**; with
the 1,398 this box built by playing, the merged `vulkan.fork-v54.bin` holds
**90,203** entries (4.4 GB).

```sh
lichii-shaders sync -title 0400486024DEC000 -dry-run   # report only
lichii-shaders sync -title 0400486024DEC000            # merge the pack
lichii-shaders info <cache file>                       # version + entry count
```

`bin/lichii-shaders` is the re-entrant wrapper (it needs the box: network plus
the shared profile path). The tool verifies each chunk against the SHA256 in its
manifest, keeps the previous cache as `<file>.bak`, resumes from chunks already
fetched, and deletes its `.chunks` staging directory when the merge validates.
Only the tool is pinned here (`dg_lichii_shaders_*`, staged in
`ROMS_FINAL/PC/tools/`); the packs come from that third-party repository.

Cache versions must match. The pack is `source_version 54`, which is what
Lichii has written since build 115; delete older `vulkan.fork-vNN.bin` files
first, because the tool would otherwise merge v54-format entries into files the
current build never reads (this box had stale v52/v53 files from earlier
builds). The `.bak` (45 MB) can be deleted after a clean session, or renamed
back to restore the pre-sync cache.

On build 117+ leave `EDEN_NX2_PRELOAD_ALL_PIPELINES` **off** in
`nx2_switches.txt` for normal play: preloading a pack this size freezes the game
for ~20 s, and the driver-memory eviction that runs after ~2.5 min discards the
prebuilt pipelines. The pack still pays off through ordinary disk-cache
lookups. To warm the driver's own cache instead, turn preload on once, stay on
the title screen until compiling stops, quit, then turn it off (with NVIDIA's
`__GL_SHADER_DISK_CACHE_SIZE` raised to 10 GB as the pack README suggests).

## What changed since our previous pin (`d549411`, 2026-11-07)

61 `nx2` commits; upstream cut build-116/117 from them. The OoT items that
matter on this box:

- **FPS Unlock is built in**, next to `nx2_frame_rate_limit` (30–240, default
  60, the Switch 2 VSync event rate). Above 60 the game keeps its speed only
  because OoT's real-time step is patched, so the limit stays at 60 here until
  it is measured in play.
- **`oot_anti_aliasing`** chooses between the game's own anti-aliasing network
  with its sharpening output pass and the plain tonemapped image. The DLSS
  replacement path (`game_dlss_network`, `nvidia_dlss`) is Windows/NGX only.
- **Shader precaching before play** (`precache_shaders`,
  `EDEN_NX2_PRELOAD_ALL_PIPELINES`) builds cached pipelines and the game's
  compute programs on the loading screen; see the pack notes above for why it
  stays off with a large shared cache.
- Frizti/Fritchii v4 imports: **OoT water flicker**, staging-buffer reuse and
  per-method switch reads.
- Rendering fixes with OoT symptoms: noperspective varyings interpolated
  perspective-correct (**tomb red line**), query results landed before macro-DMA
  reads, cached task/mesh pipelines built at boot without
  `VK_EXT_mesh_shader`, HMMA kept off AMD's emulated cooperative matrices.
- Movie/audio sync and refused decoder packets; texture-cache uploads no longer
  read stale guest memory or a whole image a join copy overwrites.
- Pipeline cache: a new version starts from the newest compatible cache and
  only damaged, stale or duplicate records are dropped.

## What this build adds over build 88

169 `nx2` commits sit between the build-88 tag and this commit. The ones that
matter for Ocarina of Time:

- **HMMA ported to Vulkan cooperative matrices** — `HMMA.16816.F16` on
  cooperative matrices (upstream: +12% standing, +24% walking) and the pinned
  `VK_KHR_cooperative_matrix` 16x16x16 path (upstream: 41 → 60 FPS on RDNA4).
  The fork's *software* K8 HMMA is also unrolled.
- **GPU thread poll interval** 1 ms → 50 µs (upstream: about 11% faster in
  Kokiri village), plus a 50 µs suspended-channel poll.
- **Shader correctness fixes with OoT symptoms**: near-foliage cbuf pointer
  competition, Hyrule Field grass (null compute pointer slots, up to 64 storage
  buffers), white flashes from macro-DMA queries, split-thread deadlock, and
  gradient/global-atomic register shadowing in `TXD`/`ATOMG`.
- **Dynamic FPS** keeps working down to 10 FPS, and **LayeredFS mods now apply
  to NUP titles** through Lichii's own add-on path.
- Pipeline/present work: opt-in `EDEN_NX2_ASYNC_DISCARD`, bounded waits for
  unbuilt Switch 2 pipelines, `EDEN_NX2_FRAMES_AHEAD`, an optional host FPS
  limit for the game's present rate, and pinning the split GPU threads to their
  own cores on Linux as well as Windows.
- Diagnostics: `EDEN_NX2_PIPELINE_BUILD_TRACE`, `VK_EXT_device_fault` on
  device loss, desktop compatibility reports, frame-generation state in the
  status bar.

## Local verification (2026-11-07)

The built binary reports `ad477ef1f4-nx2` and boots the NUP with the Vulkan
RTX 5090 device to a rendered title screen, including with the 90,203-entry
shared shader cache (see above); bounded runs inside the box were stopped and
reaped afterwards. Earlier build-88 sessions reached
the menu at about 59–60 FPS at 1x docked, then showed a 3D scene with severe
overexposure at 9–23 FPS while shaders were compiling. Those readings were
momentary, not a steady benchmark, and **no verified 60 FPS gameplay claim
exists for this build either** — measure before raising the resolution scale.
(The preliminary per-PR figures quoted above are upstream's, on their hardware.)
The controller map is installed; individual buttons and sustained gameplay
have not been re-verified on the source build.

## Saves

Game saves live under `tools/lichii/profile/data/eden/nand/user/save/` and are
registered with `dg_save_sets`; the live session created `option.sav` and
`account.sav` there. The NUP and shader caches are not backed up by that
service.

## Restricted runtime pilot

`ansible-playbook install-lichii-sandbox.yml` builds a separate, unprivileged
Docker runtime and adds **Ocarina of Time (Lichii Restricted)** to the menu.
The recipe is `config/docker/lichii-sandbox/Dockerfile` with a pinned Arch base
digest.

The restricted runtime **still runs the released build-88 AppImage**
(`dg_lichii_sandbox_*`), not the source build: its image intentionally carries
no Qt6, and the AppImage bundles its own. The two versions are therefore
decoupled — `install-lichii.yml` keeps the pinned AppImage staged in
`tools/lichii/build-88/` and unpacked to `squashfs-root/` for this role, and
only updates it when `dg_lichii_sandbox_release` moves. Because the migrated
`gaming` container has no `/dev/fuse`, both paths avoid mounting an image: the
AppImage is unpacked once with `--appimage-extract` and the launcher runs
`squashfs-root/AppRun` (a symlink to `usr/bin/lichii`).

Vulkan inside the runtime needs two pieces the AppImage does not carry: the
loader and the GPU's ICD manifest. The image installs `vulkan-icd-loader` (and
`vulkan-tools` for the check below); `--gpus all` mounts the driver libraries
but **not** `/usr/share/vulkan/icd.d/nvidia_icd.json`, so the launcher
bind-mounts the host manifest (`dg_lichii_sandbox_icd`) read-only. Without both,
Lichii exits with `Failed to initialize Vulkan: VK_ERROR_INITIALIZATION_FAILED`
— which is exactly what this runtime did until 2026-11-07.

The host launcher is `~/.local/bin/lichii-sandbox`. It starts with no network,
all Linux capabilities dropped, a read-only container root, no host home or
`/run/host`, and no NAS directory mounts. It grants only the Lichii profile
read/write, the emulator tree and the NUP read-only, the NVIDIA GPU, X11 and
PulseAudio sockets, and the 8BitDo Ultimate 2 input nodes when connected.
Connect the controller **before** launching; hotplugging it later requires a
restart. The regular and restricted sessions share a profile, so the launcher
refuses to start while the regular emulator is running (it matches both the
source-build binary and, for an in-flight container, the AppImage tree). Run
`~/.local/bin/lichii-sandbox --check` to verify mounts, the driver and the
Vulkan device without opening the game.

The restricted runtime is a pilot, not a claim that GUI applications are fully
sandboxed: the X11 and audio sockets still link it to the desktop session.
A bounded 2026-11-07 launch reached the game (`Lichii | build-88 | … |
Ocarina of Time`) with the menu fonts in place and the RTX 5090 as the Vulkan
device, then was stopped and reaped; controller input and sustained gameplay in
this runtime still need live verification.

## Upgrading

Bump `dg_lichii_commit`/`dg_lichii_short` and re-pin `dg_lichii_source_sha256`;
the role extracts into a new `build-<short>` tree, builds it, and the launcher
follows `dg_lichii_bin`. Read the release notes / commit range for new launch
options and settings first (see *GitHub Release Updates* in `AGENTS.md`), and
delete the previous `build-<short>` tree once a run reports `changed=0`.
