# Colin McRae Rally 3 (2003) — REA launcher

[akitaonrails/rea-colin-mcrae-3](https://github.com/akitaonrails/rea-colin-mcrae-3)
replaces the old pc-racing Colin McRae Rally 3 install on this box
(2026-11-01). Like [rea-dirt](rea-dirt.md), the release is a **self-contained
Linux AppImage** — its own Wine (WoW64, so the 32-bit game needs no multilib),
DXVK, SilentPatch, Xidi and the HD UI, with a pad-navigable settings window and
gamescope for true fullscreen. It works on a **private runtime copy** and never
touches the owned install.

```sh
cd ansible && ansible-playbook install-rea-colin-mcrae-3.yml
```

| | |
|---|---|
| Release | `v0.3.2`, `CMR3Launcher-v0.3.2-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/Colin-McRae-Rally-3` (`Rally_3PC.exe` sha256 `c56344b4…`, MD5 `2744404b…` — the launcher's recognised "DRM-free v1.1 variant B, the community repack") |
| AppImage | `tools/rea-colin-mcrae-3/` |
| Prefix + private runtime | `~/.local/share/cmr3-launcher/` (launcher's own default; `CMR3_PREFIX` can override) |
| Launcher | `bin/rea-colin-mcrae-3` → AppImage: settings window, then play |
| Entry | Walker **Colin McRae Rally 3 (REA)** |

v0.3.2 adds Windows executable metadata and shared SDK v0.4.3. Upstream lists
no graphics, frame pacing, or controller changes for this release. The role
keeps the existing profile and copies the verified release asset from the NAS
to its local executable path.

## What the launcher handles

Everything the old pc-racing slug needed by hand (DXVK override, a hand-built
Xidi mapper, the preserved ASI loader) is now built into the launcher, which is
why the slug was retired rather than kept alongside:

- **Edition detection by MD5**, then a private writable copy
  (`%LOCALAPPDATA%\CMR3Launcher\Rally3` inside the prefix, ~3 GB, hard-linked
  when the source and prefix share a disk). Our source is the recognised
  DRM-free "community repack", so it plays as-is with no xdelta patching; an
  official 1.1 DRM executable would be converted automatically (SilentPatch's
  DRM-free xdelta). v1.0 is not supported.
- **4K widescreen + the HD UI** (`launcher.cfg`: `resolution 3840x2160`,
  `display_mode fullscreen`, `hd_ui on`, `anisotropic 16`, `fsaa on`,
  `shadows sharp`). SilentPatch adds any aspect ratio (16:9 shows more to the
  sides, unstretched) and fixes the sun/shadow rendering; the settings window
  re-detects the screen when resolution is unset.
- **DXVK on** — the difference between native speed and ~10 FPS at 4K under
  Wine's OpenGL translator (the exact collapse the old pc-racing slug hit
  before its `d3d9=n,b` + winetricks DXVK fix). Bundled, no winetricks.
- **Gamepad via Xidi, `gamepad = rally`** — the hardware-validated preset:
  the triggers are the pedals (both at once, left-foot braking), a resting
  left thumb can't open the throttle, and the d-pad + Start work the menus.
  Hot-swappable; `standard` passes the pad straight through, `off` uses the
  game's own DirectInput.
  - **The new-profile gotcha (fixed in v0.1.1):** a *new* game profile has no
    controller chosen in Options → Controls, so the game ignores Xidi's pad even
    though Xidi loads and binds it — the pad does nothing in-game. (It is not a
    Wine/WineBus problem: upstream confirmed the bundled Wine 11.20 enumerates
    the 8BitDo on a fresh prefix with no `WineBus` settings at all, so the
    earlier box-local `Map Controllers=1` workaround was unnecessary and has
    been removed from the wrapper.) v0.1.1 writes Xidi's controller (Medium
    vibration, byte-for-byte as the game would, CRC included) into any
    never-configured profile when a Xidi preset is on, and stops `cmr3-play`
    double-counting the pad via `SDL_JOYSTICK_DEVICE`. Hand-configured profiles
    (keyboard included) are left alone. Reported + fixed:
    [rea-colin-mcrae-3#1](https://github.com/akitaonrails/rea-colin-mcrae-3/issues/1).
    **Known limit:** a brand-new player's *very first* session runs before the
    game has created its profile, so the pad is chosen from the second start on
    (or once by hand in Options → Controls). Our prefix keeps the migrated `CMR3`
    profile, so this only bites a from-scratch rebuild.
  - **v0.1.2 steering/d-pad:** new profiles now steer with the **left stick** and
    brake/accelerate on the **triggers** with no remapping (the game's own
    defaults pointed both at the right stick); and the Rally preset's d-pad is
    the arrow keys only again, so the Controls menu moves **one** row per press
    (A still presses Enter as well as its button). **Upgrade caveat:** a profile
    whose pad was bound under *v0.1.1* (d-pad as a hat) steers from the wrong
    stick now and must be remapped once in Options → Controls; profiles from
    v0.1.0 — and our hand-configured migrated `CMR3` — are unaffected.
  - `postfx = off` (and `--postfx`, `--shadows`, `--gamepad-log`) were rejected
    by the cfg/CLI parser though documented valid; **fixed in v0.1.1**
    ([#2](https://github.com/akitaonrails/rea-colin-mcrae-3/issues/2), the CLI
    and `launcher.cfg` now share one parser). The role still omits `postfx` to
    keep post-processing off; v0.1.2 added optional **Colour / Cinematic** LUT
    grades (real blacks, fuller contrast before CAS) and fixed Cinematic's MxAO
    depth pass — left off by default.
- **True fullscreen via gamescope** (box-provided, `scaler = linear`); without
  gamescope it falls back to a plain Wine window at the same size.

## Saves

The player's profile is the game's `CMR3` file. The launcher keeps it under
`Saved Games/Colin McRae Rally 3` inside its prefix and copies it into the
runtime copy before each run and back on exit. The role migrates the loose
`CMR3` profile out of the retired pc-racing install once, then removes that
install (the 2.8 GB game is now staged clean on the NAS) and its per-game Wine
prefix. `dg_save_sets` mirrors
`~/.local/share/cmr3-launcher/prefix/.../Saved Games/Colin McRae Rally 3` plus
the launcher's `launcher.cfg`.

## The owned source

The clean source at `ROMS_FINAL/PC/games/Colin-McRae-Rally-3` is the stock game
only — `Rally_3PC.exe`, `Rally_3PC.ico`, the `Math*.dll` libraries and
`Data/fonts/shaders`. It was staged from the previous pc-racing install with
that install's injected Xidi (`dinput8.dll`), SilentPatch (`SilentPatchCMR3.*`),
the proxy `dsound.dll`, the Inno uninstaller and the `CMR3` profile stripped
out: the launcher supplies its own components and keeps the profile in the
prefix, so the source stays a clean, read-only game folder (the rea-dirt /
rea-colin-mcrae convention). The source exe is sha256-verified by the role.

## CLI

```sh
rea-colin-mcrae-3                 # settings window (pad-navigable), then play
rea-colin-mcrae-3 --play          # saved settings, no window
rea-colin-mcrae-3 stop|status     # manage a run
```

The launcher exe itself also takes `--check`, `--game <folder>`,
`--resolution`, `--gamepad`, `--dxvk on|off` etc.; `--game` is remembered in
`launcher.cfg`, which the role seeds with the NAS source as a Windows path
(`Z:\…`, Wine maps `Z:` to `/`).

## History

The retired path is documented in `docs/pc-racing.md` (and the removed
`colin-mcrae-rally-3` slug in `group_vars/all/pc_racing.yml`): a Magipack
`_Repack_v4` Inno installer to `G:\colin-mcrae-rally-3`, winetricks DXVK with
`WINEDLLOVERRIDES d3d9=n,b` for the ~10 FPS-at-4K OpenGL fallback, and a
hand-written Xidi `CMR3Gamepad` mapper. None of that is needed any more; the
NAS keeps the `_Repack` installer archive for a from-scratch rebuild of the
owned source.
