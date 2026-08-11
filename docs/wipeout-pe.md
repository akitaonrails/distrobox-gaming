# WipEout Phantom Edition — `install_wipeout_pe`

An enhanced PC source port of **WipEout (PSX, USA region)** — uncapped frame
rate, high-res + widescreen rendering, particle effects, new audio. Upstream:
[wipeout-phantom-edition](https://github.com/wipeout-phantom-edition/wipeout-phantom-edition).
Opt-in role; installed 2026-08-11.

- **Distribution:** a prebuilt **Windows x64** binary (`wipeout.exe` + bundled
  SDL2 / OpenAL / lua / sndfile DLLs) — no Linux build, so it runs under
  **Wine**. Pinned to `dg_wipeout_pe_version` (`v1.2.256`), fetched from the
  GitHub release by sha256.
- **You must provide** game data from the **PlayStation USA-region** WipEout
  (official PC versions won't work). This box has `WipEout (USA).chd` in
  `psx/`; the role converts it to the disc image the game requires.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-wipeout-pe.yml          # or: site.yml --tags wipeout_pe
scripts/install-host-launchers.sh                # refresh the host menu entry
ansible-playbook install-wipeout-pe.yml -e dg_wipeout_pe_revert=true
```

Launcher: `{{ dg_box_home }}/bin/wipeout-pe` (menu: **"WipEout Phantom
Edition"**). It focuses DP-1, pins the NVIDIA GL path, and runs the game under
gamescope at 4K.

**First launch extracts the game data** (517 files + music) from the disc image
— about 1-2 minutes on this 16-core box. After it reaches the main menu once,
the `diskimages/` files are no longer needed (kept for reproducible rebuilds).

## The disc image (the fiddly part)

The game requires a **multi-bin** `.bin`/`.cue` — 9 `.bin` files + 1 `.cue`,
with `TRACK 01 MODE2/2352` (data) + `AUDIO` tracks — placed in
`<game>/diskimages`. A single combined bin is rejected (the game hash-searches
the data track expecting the multi-FILE layout). The role builds it from the
CHD:

1. `chdman extractcd` → a single combined bin/cue. (This chdman build's
   `--splitbin` errors out — same as the SotN case — so it can't split
   directly.)
2. **binmerge** (`-s`, bundled in the role's `files/`) splits that into the
   9-bin layout named `WipEout USA (Track N).bin` + `WipEout USA.cue`.

## Rendering + controller

- **GLX pin:** wine 11's default EGL backend resolves to the AMD iGPU/llvmpipe
  on this dual-GPU box and spams `egl: failed to create dri2 screen` (black).
  `UseEGL=N` (HKCU\Software\Wine\X11 Driver) reverts to GLX so OpenGL binds the
  RTX. Same fix as the pc_racing / Sonic P-06 prefixes.
- **Fullscreen:** the game's own `DesktopFullscreen` lands as a quarter-screen
  window under Wine, so the launcher wraps it in gamescope `-f` at 4K.
- **Gamepad (always supported):** WipEout PE has native SDL2 pad support and
  ships a full 8BitDo layout in `defaultinput.cfg` (left stick steer/pitch,
  LT/RT airbrakes, A accelerate, B fire, Y change view, Start). First run
  creates an *empty* `input.cfg`, so the role seeds it from `defaultinput.cfg`
  (only when missing/empty, so in-game rebinds are preserved).

## Notes

- Bump `dg_wipeout_pe_version` + `_asset_sha256` for a new release; re-extract
  preserves the extracted game data and configs.
- The WipEout `(USA).chd` stays on the NAS untouched; the role only reads it.
