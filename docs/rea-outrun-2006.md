# OutRun 2006: Coast 2 Coast (2006) — REA launcher

[akitaonrails/rea-outrun-2006](https://github.com/akitaonrails/rea-outrun-2006)
replaces the old pc-racing OutRun 2006 install on this box (2026-11-02). Like
[rea-colin-mcrae-3](rea-colin-mcrae-3.md) and [rea-dirt](rea-dirt.md), the
release is a **self-contained Linux AppImage** — its own Wine 11 (WoW64, so the
32-bit game needs no multilib), DXVK, emoose's **OutRun2006Tweaks** (the
DRM-free EXE and the fixes the PC port needs), the x86 VC++ runtime DLLs and the
soundtrack patch, with a pad-navigable settings window and gamescope for true
fullscreen. It works on a **private runtime copy** and never touches the owned
install.

```sh
cd ansible && ansible-playbook install-rea-outrun-2006.yml
```

| | |
|---|---|
| Release | `v0.3.2`, `OutRunLauncher-v0.3.2-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/OutRun-2006-Coast-2-Coast` (`OR2006C2C.exe` sha256 `68ceb386…` — the launcher's recognised OutRun2006Tweaks DRM-free EXE, an already-patched install) |
| AppImage | `tools/rea-outrun-2006/` |
| Prefix + private runtime | `~/.local/share/or-launcher/` (launcher's own default; `OR_PREFIX` can override) |
| Launcher | `bin/rea-outrun-2006` → AppImage (`or-play`): settings window, then play |
| Entry | Walker **OutRun 2006: Coast 2 Coast (REA)** |

v0.3.2 adds Windows executable metadata and shared SDK v0.4.3 to reduce
antivirus false positives. The release does not change graphics, frame pacing,
or controller options; the role preserves the existing profile and stages the
verified AppImage on the NAS before installing its local executable copy.

## What the launcher handles

Everything the old pc-racing slug needed by hand — the OutRun2006Tweaks CI build
staged on the NAS, the native `dinput8.dll` override, winetricks `vcrun2022`,
DXVK, and disabling the repack's SpecialK `d3d9.dll` — is now built into the
launcher, which is why the slug was retired rather than kept alongside:

- **Edition detection by SHA-256**, then a private writable copy
  (`%LOCALAPPDATA%\OutRunLauncher\OutRun2006` inside the prefix, ~1 GB,
  only changed files after the first build). Our source EXE is the
  OutRun2006Tweaks DRM-free replacement, which the launcher recognises as an
  already-patched install and refreshes the files it manages; an original 2006
  `OR2006C2C.exe` would be swapped for the DRM-free EXE in the copy. An unknown
  EXE is reported with its SHA-256.
- **4K widescreen maxed out** (`launcher.cfg`: `resolution 3840x2160`,
  `draw_distance 8`, `reflections 2048`, `anisotropy 16`, `antialiasing 2` =
  the game's 4× MSAA, `sky_glow on`, `hd_characters on`). OutRun2006Tweaks adds
  any aspect ratio and the console-era effects.
- **DXVK on** — bundled; the launcher wires the native `dinput8`/`d3d9`
  overrides and keeps stray SpecialK `d3d9` files out of its copy. A fresh
  prefix is enough, no winetricks.
- **60 FPS cap** (`fps_limit 60`): OutRun's logic is a fixed 60 Hz, and above 60
  the picture is interpolated (OutRun2006Tweaks marks that experimental), so 60
  is the stable maximum.
- **Gamepad via OutRun2006Tweaks' SDL input, `input_backend xinput`** — under
  Wine the launcher reads the pad through XInput by default (Wine's
  Windows.Gaming.Input loses the d-pad) and turns on Tweaks' SDL input system
  (full trigger range, rumble). `vibration on`. The 8BitDo (XInput mode) works
  without any registry plumbing — no WineBus edits, no Xidi. If the pad or the
  menu d-pad misbehaves, the Controls tab offers RawInput and DirectInput.
- **The gameplay extras the box has always run**: `cd_switcher on` (change the
  music mid-race), `skip_logos on`, `free_drive on` (no countdown), the varied
  roadside animations (`random_anims on`) and the "Rush a Difficulty" soundtrack
  fix (`soundtrack_fix on`).
- **True fullscreen via gamescope** (box-provided, `fullscreen off` = a
  borderless 4K window that gamescope scales to the panel, `scaler linear`);
  without gamescope it falls back to a plain Wine window.

### HD texture pack (optional)

The community HD texture pack (Envido32's compilation of the Sonic-TV
OR2006Sprites project) redraws the menus, HUD, sprites and button prompts. It is
a **3.2 GB** unpacked download the launcher fetches, SHA-256-checks and switches
on from the **HD Pack** tab, so the role leaves it **off** by default rather
than pull it during an Ansible run. Turn it on once from the settings window, or:

```sh
rea-outrun-2006 --download-hd-pack
```

## Saves

OutRun 2006 writes its progress to `SaveGame/{common,rankings,License1}.dat` in
the game folder. The launcher keeps a separate save folder
(`Saved Games\OutRun 2006` inside the prefix) and mirrors it into the runtime
copy's `SaveGame/` before each run and back on exit; the game owns those files
once they exist. The owned source's own `SaveGame/` seeds that folder on the
first run, so the career progress carried over from the retired pc-racing
install (its `SaveGame/*.dat`, staged with the source) is preserved without a
separate migration step. `dg_save_sets` mirrors
`~/.local/share/or-launcher/prefix/.../Saved Games/OutRun 2006` plus the
launcher's `launcher.cfg`.

## The owned source

The clean source at `ROMS_FINAL/PC/games/OutRun-2006-Coast-2-Coast` is the game
only — `OR2006C2C.exe`, its data folders (`Stage/`, `Media/`, `Sound/`, `Cars/`,
`SaveGame/` …), the FXT config tools, the manual and the readme. It was staged
from the previous pc-racing install with that install's injected
OutRun2006Tweaks files (`dinput8.dll`, the whole `OutRun2006Tweaks.*` set), the
disabled SpecialK `d3d9` files, the generated `outrun2006.ini`, the Inno
uninstaller and the runtime `logs/` and `CrashDumps/` stripped out: the launcher
supplies its own components, so the source stays a clean game folder (the
rea-dirt / rea-colin-mcrae-3 convention). The source EXE is sha256-verified by
the role.

## CLI

```sh
rea-outrun-2006                   # settings window (pad-navigable), then play
rea-outrun-2006 --play            # saved settings, no window
rea-outrun-2006 stop|status       # manage a run
rea-outrun-2006 --download-hd-pack  # fetch + enable the HD texture pack
```

`rea-outrun-2006` re-enters the `gaming` box and runs the AppImage's `or-play`.
The launcher exe inside also takes `--no-window`, `--check`, `--settings` and
the per-setting flags in the README; `--game` is remembered in `launcher.cfg`,
which the role seeds with the NAS source as a Windows path (`Z:\…`, Wine maps
`Z:` to `/`).

## History

The retired path is documented in `docs/pc-racing.md` (and the removed
`outrun-2006` slug in `group_vars/all/pc_racing.yml`): the
`OutRun 2006 - Coast 2 Coast_Repack_Setup.exe` Inno repack installed silently to
`G:\outrun-2006`, winetricks `vcrun2022` + DXVK, the OutRun2006Tweaks CI build
(commit `08e5efb4`) fetched via nightly.link and staged on the NAS, the native
`dinput8=n,b;d3d9=n,b` overrides, and the repack's SpecialK `d3d9.dll` backed up
and disabled. None of that is needed any more; the NAS keeps the repack installer
archive for a from-scratch rebuild of the owned source.
