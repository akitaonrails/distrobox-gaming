# Sega Rally Revo (2007) — REA launcher

[akitaonrails/rea-sega-rally-revo](https://github.com/akitaonrails/rea-sega-rally-revo)
replaces the old pc-racing Sega Rally Revo install on this box (2026-11-02).
Like the other REA launchers ([rea-outrun-2006](rea-outrun-2006.md),
[rea-colin-mcrae-3](rea-colin-mcrae-3.md), [rea-dirt](rea-dirt.md)), the release
is a **self-contained Linux AppImage** — its own Wine 11.20 (WoW64, so the
32-bit game needs no multilib) and DXVK 3.1.1 — with a pad-navigable settings
window. It works on a **private runtime copy** and never touches the owned
install.

```sh
cd ansible && ansible-playbook install-rea-sega-rally-revo.yml
```

| | |
|---|---|
| Release | `v0.3.3`, `SRRLauncher-v0.3.3-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/SEGA-Rally-Revo_Win_EN-FR-DE-ES-IT-PL_Full-Rip/Sega Rally` (the pristine NAS Full-Rip, `SEGA Rally_SSE1.exe` sha256 `22655a54…` + `SEGA Rally.exe` sha256 `ad84ecea…`, the recognised v4.0.6.0 release) |
| AppImage | `tools/rea-sega-rally-revo/` |
| Prefix + private runtime | `~/.local/share/srr-launcher/` (launcher's own default; `SRR_PREFIX` can override) |
| Launcher | `bin/rea-sega-rally-revo` → AppImage (`srr-play`): settings window, then play |
| Entry | Walker **Sega Rally Revo (REA)** |

v0.3.3 adds Windows executable metadata and shared SDK v0.4.3 to reduce
antivirus false positives. The release does not change graphics, pacing, or
controller setup; the role preserves the existing profile and stages the
verified AppImage on the NAS before installing its local executable copy.

## What the launcher handles

The entire pile of box-specific fixes the old pc-racing slug carried by hand is
now **built into the launcher**, which is why the slug was retired rather than
kept alongside:

- **Edition detection by SHA-256**, then a private writable copy
  (`%LOCALAPPDATA%\SRRLauncher\SegaRally` inside the prefix, ~4.2 GB, only
  changed files after the first build). An unknown EXE is refused with its
  SHA-256 rather than patched blindly.
- **The community stutter fix** (pacer patch) applied to the private copy — it
  needs the clean `SEGA Rally_SSE1.exe`; with the fix off it runs the no-DVD
  `SEGA Rally.exe` unpatched.
- **The registry + `config.ini` + Documents layout** the game expects, written
  the way its flaky .NET settings tool would (that tool misbehaves under Wine).
  The player's `[Audio]`/`[GameController]` sections in `config.ini` are
  preserved verbatim.
- **Isolated Wine desktop for fullscreen** — this is the old `wine_desktop`
  lesson: exclusive fullscreen crashes on multi-monitor / high-refresh Linux
  desktops (the `RRSetCrtcConfig BadValue` when DP-1 is at 240 Hz, not 60), so
  the game runs in a Wine-internal desktop of the chosen size. **No gamescope**
  — on this dual-GPU box gamescope routes this DXVK title's Vulkan to the AMD
  iGPU (black screen); the Wine desktop avoids it.
- **The NVIDIA Vulkan ICD pin** on hybrid-GPU hosts, so DXVK renders on the RTX
  and never the iGPU — the old `VK_ICD_FILENAMES` hack, now automatic.
- **WineBus controller bridge** (`Map Controllers=1`, raw duplicate devices
  disabled), seeded once per prefix.
- **winetricks `d3dx9 directplay d3dcompiler_47`** on first run (via the box's
  winetricks) — the offline DirectX equivalents that stop a main-menu access
  violation.
- **DXVK frame limit** for even pacing (60 default; this box seeds **120** for
  the 240 Hz panel), the logo-video skip, and the 21:9/32:9 aspect patch.

## Graphics

`launcher.cfg` is seeded maxed out: `resolution 3840x2160`, `aspect 16:9`,
`quality ultra` (every per-feature slider at 3; Ultra renders at 4K),
`vsync on`, `stutter-fix on`, `frame-limit 120`, `language English`. Quality
*High* is the reference 4K configuration; *Ultra* pushes every slider to 3.

## Gamepad

The game uses its **own native XInput support** — nothing is remapped to the
keyboard. The launcher seeds Wine's controller bridge and shows the connected
pad with a rumble test; **bind the 8BitDo in the game's own Controls menu**.
Keep the game's force feedback **off** (a known crash). The settings window
itself is pad-navigable (d-pad moves, A changes a setting, LB/RB switch tabs,
Start plays).

## Saves

The career save (`SEGA Rally.dat`) and `config.ini` live in
`Documents\SEGA Rally\Saved Games` inside the prefix. The role migrates both out
of the retired pc-racing prefix once (`force: false`, so the launcher's/player's
later writes win); the launcher keeps the `[GameController]` binding from the
migrated `config.ini`. `dg_save_sets` mirrors
`~/.local/share/srr-launcher/prefix/.../Documents/SEGA Rally/Saved Games` plus
the launcher's `launcher.cfg`.

## The owned source

Unlike CMR3 and OutRun 2006 (whose box installs carried pc-racing injections and
had to be re-staged clean), the Sega Rally Revo pc-racing slug used
`install_mode: copy` and only ever **read** the NAS Full-Rip folder, so that
folder is already the pristine owned source — `SEGA Rally_SSE1.exe`,
`SEGA Rally.exe`, the game data, the manual. The role points the launcher at it
directly and sha256-verifies both executables; nothing was restaged.

## CLI

```sh
rea-sega-rally-revo                 # settings window (pad-navigable), then play
rea-sega-rally-revo --play          # saved settings, no window
rea-sega-rally-revo stop|status     # manage a run
```

`rea-sega-rally-revo` re-enters the `gaming` box and runs the AppImage's
`srr-play`. The launcher exe inside also takes `--check`, `--setup`,
`--no-window`, `--settings` and the per-setting flags in the README; `--game` is
remembered in `launcher.cfg`, which the role seeds with the NAS source as a
Windows path (`Z:\…`, Wine maps `Z:` to `/`).

## History

The retired path is documented in `docs/pc-racing.md` (and the removed
`sega-rally-revo` slug in `group_vars/all/pc_racing.yml`): the Full-Rip copied
to `G:\sega-rally-revo`, the `wine-11.8` sidecar pin (system wine 11.13
black-screened the game), `VK_ICD_FILENAMES` pinned to the NVIDIA ICD,
`gamescope_enabled: false`, a 4K Wine virtual desktop (to survive DP-1's 240 Hz
refresh), winetricks `directplay`/`d3dx9`/`dxvk`, the DirectX June 2010 redist,
`winebus Map Controllers=1`, the `Sega\SEGA Rally` registry values and a
hand-seeded `config.ini`. All of that is now inside the launcher; the NAS keeps
the Full-Rip as the owned source.
