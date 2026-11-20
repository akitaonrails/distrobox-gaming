# Lichii / Fritchii Switch 2 experiment

Ocarina of Time runs on a Switch 2 emulator in this box. The main runtime is
**Fritchii** — [Frizti's Lichii fork](https://github.com/Frizti/Fritchii),
specialised for this one title (it descends from
[zortos293/Lichii](https://github.com/zortos293/Lichii), itself Eden-derived).
It ships as a **prebuilt Linux AppDir**, so there is no source build and no
third-party shader-sync tool any more:

| | |
|---|---|
| Release | `fritchii-v6.2` (`dg_fritchii_version: "6.2"`), SHA256-pinned |
| Asset | `Fritchii-v6.2-Linux-x86_64.tar.gz`, staged in `ROMS_FINAL/PC/releases/` |
| Unpacked | `tools/lichii/fritchii-v6.2/fritchii/` (a linuxdeploy AppDir: bundled Qt6 + ~200 libs) |
| Entrypoint | `tools/lichii/fritchii-v6.2/fritchii/AppRun` → `usr/bin/lichii` (`dg_lichii_bin`) |
| Launcher | `bin/lichii`; entries **Lichii Switch 2 (Experimental)** and **Ocarina of Time (Lichii Experimental)** |

Run from `ansible/`:

```sh
ansible-playbook install-lichii.yml
```

The regular Eden installation, its keys, settings, saves and caches stay
separate; this runtime keeps its own profile under `tools/lichii/profile/`.

## Why Fritchii (and what it replaced)

Fritchii superseded the old source-built `zortos293/Lichii` `nx2` pin plus the
`oceanpacificpeace/lichii-shader-sync` tool. It is a strict improvement for our
single use case:

- **Prebuilt, OoT-tuned.** It bundles its own Qt6 and all libraries, is built
  with profile-guided optimisation against OoT, and ships a pre-baked recipe for
  our exact dump (`usr/bin/recipes/OoT v131072 (cache v54).nx2recipe`). No clang
  workaround, no 1,816-target CMake build.
- **Its own shaders.** Fritchii prepares and keeps its own Vulkan shaders,
  including on NVIDIA/Linux, so the external shader-sync merge is gone.
- **Real graphics gains for OoT**: Castle Town holding 60 fps, the pot-room
  crash, text-garbage, ocarina-warp freeze and the high-refresh audio/physics
  bugs are all fixed upstream, and DLSS runs on Linux through the NVIDIA driver.

Because Fritchii still shares Eden's `eden/qt-config.ini` format and the `eden/`
config + data directories, the isolated profile, the saves and the 8BitDo
mapping all carried over unchanged across the migration.

The old source build tree, the `lichii-sync` tool and `bin/lichii-shaders` are
removed by the role on the next run (`dg_lichii_retired_paths`); the profile is
never touched.

## The game file

The role checks the owned
`ROMS_FINAL/switch2/The Legend of Zelda Ocarina of Time [0400486024dec000][v131072].nup`
by exact length, NUP v1 header fields and table-of-contents SHA256 without
unpacking its 24 GB payload. The **Ocarina of Time** entry runs that file
directly with the emulator's `-g` option (`bin/lichii --game`). Override
`dg_lichii_game` and `dg_lichii_game_size` in `host_vars/localhost.yml` for
another owned dump. Firmware and keys are not bundled; the unencrypted NUP
format opens without Switch 1 decryption keys.

## Settings (maxed for this box — RTX 5090)

The profile is `tools/lichii/profile/` under its own XDG config, data and cache
roots. A fresh profile is rendered from `templates/qt-config.ini.j2` (docked
mode, Vulkan on the NVIDIA ICD, the 8BitDo mapping, Qt's X11 backend — the
Wayland backend has significant performance problems). The GPU/graphics baseline
below **is** Fritchii's own recommended OoT profile, applied as
`dg_lichii_profile_settings`:

| Key | Value | Why |
|---|---|---|
| `memory_layout_mode` | `2` (8 GB) | the game's own memory size |
| `gpu_accuracy` | `0` (Low / "Fast") | Fritchii's GPU Mode |
| `nvdec_emulation` | `2` (GPU) | GPU video decoding |
| `use_asynchronous_shaders` | `true` | background shader compilation |
| `async_presentation` | `true` | non-blocking present |
| `vsync_mode` | `1` (Mailbox) | lowest-latency pacing |
| `use_docked_mode` | `1` | docked; handheld showed a black 3D scene |
| `resolution_setup` | `3` (1x internal) | see the 4K note below |
| `use_disk_shader_cache` | `true` | persistent pipeline cache |

Each key is written with its `<key>\default=false` companion. That matters: the
frontend treats a missing (or `true`) `\default` flag as "use the built-in
default" and rewrites the value on exit, which silently reverted GPU accuracy and
hardware decoding until this was fixed. The baseline is written once and recorded
in `tools/lichii/profile/.baseline-applied`; later in-app changes win, and a role
rerun does not touch them. To re-apply it, delete that marker and rerun.

### Getting the full 4K output (one-time first-run)

`resolution_setup` stays at **1x internal on purpose**: on an RTX 5090 the 4K
output is produced by Fritchii's upscaler, not by brute internal supersampling,
which keeps the 60 fps hold. Fritchii gates its two biggest graphics levers
behind one-time prompts that check the actual GPU, so finish the first launch
once to lock in max:

1. **"Use recommended settings?" → Use recommended.** Applies Fritchii's
   OoT-tuned profile (and backs up the previous one).
2. **"Max Resolution?" → Yes.** Enables the 1440p internal render target (needs
   ~an RTX 3070 / 8 GB; the 5090 is far past that).
3. **DLSS** defaults to the **Automatic** model on NVIDIA; in
   *Settings → Graphics* set the **Upscale to** output to **4K** (or 1440p→4K)
   and, if you want, DLSS **Quality**. The status bar then reads e.g.
   `1440p → 4K · DLSS`.

The first launch also runs a one-time shader preparation (~several minutes) and
compiles the driver cache; let it finish. These choices are stored in the shared
profile and survive Fritchii updates. The 5090 has ample headroom to raise the
internal `resolution_setup` too — do it in-app and confirm a steady 60 fps, per
*Graphics: Always Max Out* in `AGENTS.md`.

Fritchii's low-level performance switches live in
`fritchii-v6.2/fritchii/usr/bin/nx2_switches.txt` (editable in-app under
*Tools → Switches*); they are auto-tuned for the detected GPU and should be left
alone unless the in-app overlay says otherwise.

## Saves

Game saves live under `tools/lichii/profile/data/eden/nand/user/save/` (and the
system NAND save) and are registered with `dg_save_sets` — the path is unchanged
from the old build because Fritchii keeps the `eden/` data layout. The NUP and
shader caches are not backed up by that service.

## Upgrading

Bump `dg_fritchii_version` and re-pin `dg_fritchii_asset_sha256` from the
release's `SHA256SUMS`, add the previous version to
`dg_fritchii_superseded_versions`, and rerun `install-lichii.yml`. The role
stages and unpacks the new AppDir and the launcher follows `dg_lichii_bin`. Read
Fritchii's release notes first for new one-time prompts or settings (see *GitHub
Release Updates* in `AGENTS.md`).
