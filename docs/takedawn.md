# Burnout 3: Takedown — Takedawn (Xbox static recompilation)

[xenophobentx/takedawn](https://github.com/xenophobentx/takedawn) is a static
recompilation of the **original Xbox** Burnout 3: Takedown into a native
program (SDL2 + bundled libs, Linux/Windows/macOS/Android). Upstream is MIT
and ships no game data: it takes the data from your own NTSC-U disc.

## Status: installed, no game data

```sh
cd ansible && ansible-playbook install-takedawn.yml
```

The role installs the pinned AppImage (`bin/takedawn`) and the desktop entry,
then runs the disc gate. **Both Burnout 3 copies in this library fail it:**

| Local source | Result |
|---|---|
| `EmuDeck/roms_heavy/xbox/Burnout 3 Takedown.iso` (2.22 GB) | `wrong-version` — a multi-region pressing: its `default.xbe` hashes to `cda53374…`, where NTSC-U retail is `9f497acd…` |
| `ROMS_FINAL/xbox-hdd-ready/Burnout 3 Takedown/` | `no-xbe` — a trimmed rip with no `default.xbe` at all and 11 manifest files missing (`Tracks/*.xmv`, `_EATrax{0,1}.xwb`, `_femain.rws`) |

So the playbook stops with that reason instead of half-installing. What it
needs is the **North America (NTSC-U) retail** disc:

| | |
|---|---|
| Title ID | `0x4541005B` |
| `default.xbe` | 4,308,992 bytes, SHA-256 `9f497acd82adb8edfb72cc31aeeb35010b45d32b13a3f1fc6540717ff24d13f9` |
| Manifest | `ntsc-u-retail`, id `81dc20fd647fb0b1`, 716 files / 2,476,107,072 bytes |
| Accepted forms | `.iso` / `.xiso` (with or without the video partition) or an extracted disc folder |

Point `dg_takedawn_disc` at it and rerun; the role resumes a partially copied
install from `install.journal`.

## How the install works

One binary is both game and installer, with a stdout line protocol
(`PROTOCOL 1`, `STEP disc BEGIN|OK|SKIP|FAIL`, `RESULT OK <dest>` /
`RESULT FAIL disc <code>`) and **no display needed** — Qt opens only for the
setup window:

```sh
takedawn --install <image|folder> [--dest <dir>] [--check]   # 0 ok, 1 failure, 2 bad args
takedawn --data-status                                        # 0 installed, 3 not
takedawn --build-shaders [--cache-dir <dir>]                  # optional, GPU
```

The role runs `--check` first (identifies the disc, writes nothing), then the
install (2.31 GiB copy into `~/.local/share/takedawn/Game`, resumable), then
renders the launcher `bin/takedawn`, which refuses to open an empty setup
window when `--data-status` says the data is missing.

## Settings (once there is game data)

`~/.local/share/takedawn/settings.toml` holds only the keys that differ from
the defaults, and `RECOMP_*` environment variables win over it. Release
defaults are already fullscreen borderless 16:9 with render scale 3, SMAA and
2× UI. The ceiling for this box — to be applied and verified once a valid disc
exists, then moved into the role:

| Key | Target |
|---|---|
| `graphics.render_scale` | `4` (1–4; 4 = 2560×1920 → 4K) |
| `graphics.aniso` | `16` |
| `graphics.aa` | `smaa` |
| `graphics.lod_bias`, `graphics.texture_upscale(_scale)` | highest useful tier |
| `graphics.high_refresh` | `120`/`144` Hz presentation with 60 Hz game steps |
| `display.present_timing` / `frame_pacing` | pick **one** pacer, never both |
| `input.rumble`, `input.deadzone`, `input.trigger_deadzone`, `input.face_layout` | pad defaults for the 8BitDo |

Pad input is native SDL2 (bundled) with the same `input.*` keys; nothing could
be exercised on device yet because no installable disc exists.

## Removing it

There is no `--uninstall`: delete the AppImage, `~/.local/share/takedawn`
(saves included), `~/.cache/takedawn`, and `bin/takedawn` + the desktop entry.
