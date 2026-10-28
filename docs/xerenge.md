# Burnout Revenge — Xerenge (Xbox 360 PC port)

[shipa-2/Xerenge](https://github.com/shipa-2/Xerenge) recompiles the Xbox 360
release of **Burnout Revenge** to C++ ahead of time (ReXGlue) and draws through
its own **plume** renderer, with Xenia's Xenos backend as the alternative. The
release is a **native Linux** installer — no Wine, no distrobox.

## Install

```sh
cd ansible && ansible-playbook install-xerenge.yml
```

| | |
|---|---|
| Release | `v0.4.8`, `Burnout_Revenge_Installer-x86_64.AppImage` (pinned + sha256) |
| Disc | `ROMS_FINAL/xbox360/Burnout Revenge [NTSCU].iso` (USA) |
| Installed tree | `tools/xerenge/releases/v0.4.8/Burnout Revenge/` in the box home (`bin/`, `game/` ≈ 3.6 GB, `xerenge.conf`) |
| Launcher | `bin/xerenge` → `burnout_revenge` |
| Entry | Walker/menu **Burnout Revenge · Xerenge** |

The AppImage is unpacked with `--appimage-extract` (no FUSE) and its installer
runs headless: `xerenge-installer --iso <disc> --path <dir> --bloom
--no-shortcuts` with `QT_QPA_PLATFORM=offscreen` and `XERENGE_PAYLOAD` pointing
at the unpacked payload. `--no-shortcuts` keeps desktop entries in this repo's
hands; `--bloom` is upstream's sky bloom.

### The disc hash caveat

Upstream supports exactly two images, by full-image SHA-256: Europe
`34c1bd4d…` and USA `7abf689f…`. This library's copy is **the USA release but a
different mastering** — it carries `language/strings/MainUS.bin`, `CredUS.bin`
and only the NTSC `ovid/*_N.xmv` movies, and it is 7,834,892,288 bytes like
upstream's — yet it hashes to `2dee23fb…`, so the installer's built-in check
refused it.

The role therefore rewrites the installer's **USA** constant to the local hash
(`scripts/patch-binary-string.py`, same-length in-place patch of the unpacked
copy in the cache). The installer then identifies the image as the American
release and installs `bin/burnout_us` → `bin/burnout`, which is what this disc
is. Verified: the game boots to the menus, runs fullscreen and registers pad
presses; the renderer logs no missing-data errors.

If a matching upstream dump is ever added, point `dg_xerenge_disc` (and
`dg_xerenge_disc_sha256`) at it and drop `dg_xerenge_upstream_usa_sha256` from
the role — the patch then simply finds nothing to replace.

## Settings (`xerenge.conf`)

`xerenge.conf` sits next to the game, is read on every start, and is also what
the in-game **Driver Details > Settings** menu (GRAPHICS / HACKS / DEBUG)
writes. The role only enforces the keys it owns, so anything changed in game
survives a rerun.

| Key | Value | Why |
|---|---|---|
| `windowed` | `false` | fullscreen on the 4K display |
| `render_resolution` | *(empty)* | the frame is drawn at the window size, so empty = 3840×2160 native; set it only to *lower* the internal resolution |
| `aspect_16_9` | `true` | the console's 16:9 with bars on wider screens |
| `aa` | `smaa` | upstream offers `off` / `fxaa` / `smaa`; SMAA is the sharper of the two AA modes |
| `anisotropy` | `16` | from the default 8 |
| `bloom` | `true` | sky bloom and the low-res gaussian blur |
| `motion_blur` | `false` | clarity at 60 fps; flip it in game if you prefer it |
| `renderer` | `plume` | the project's own renderer (default); `xenos` exists as a fallback |
| `crash_interpolation` | `true` | 60 fps crash cameras |
| `keyboard` | `false` | keyboard-as-pad off, so it cannot shadow the controller |

Frames: the game is a 60 fps title; `fps_30` stays `false`. `power_mode =
stock` is upstream's default pacing — `performance` only helps weak handhelds.

## Controller

Native **SDL gamepad** input through the runtime's XInput (`XamInput*`)
implementation — no mapping layer needed. Verified in the log with the 8BitDo
Ultimate 2 (`2dc8:310b`): the device is picked up as `GameControllerType(1)`
(Xbox layout) and button presses translate to XInput bits
(`input: first press from device 1 '8BitDo Ultimate 2 Wireless Controller'`).

## Notes

- The disc is read straight from the NAS for the one-time extraction; the
  extraction itself is written locally (unlike the FM4 disc tool, which mangled
  its output when writing across NFS).
- `install.log` in the install directory is the installer's own transcript.
- Online play needs the `ealobby` service (`lobby_server` in `xerenge.conf`);
  it is not installed here — local multiplayer works without it.
