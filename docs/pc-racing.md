# PC Racing Games

Windows PC racing games are optional and are not installed during a normal
`site.yml` rebuild. They are managed by `install_pc_racing`, which uses system
Wine inside the `gaming` distrobox. Lutris and UMU are intentionally removed by
this role so the setup stays simple and reproducible.

Currently managed games:

- Colin McRae Rally 2.0
- Colin McRae Rally 3
- Colin McRae Rally 04
- Colin McRae Rally 2005
- OutRun 2006: Coast 2 Coast
- Sega Rally 2: 25th Anniversary Edition
- Sega Rally Revo

Add more entries to `dg_pc_racing_games` only after testing their install and
launch path. Reuse the existing data fields for silent installer flags,
downloadable ZIP patches, `winetricks` components, DLL overrides, INI edits,
and controller quirks instead of creating one-off role logic.
For GOG/Inno Setup packages, prefer `install_mode: innoextract` when the Wine
installer is fragile or does not need to write registry state.

Every new Wine game must explicitly choose a display and controller baseline
before the first launcher test. If the game can fullscreen or query monitor
modes directly, set `gamescope_enabled: true` and use the shared
`dg_pc_racing_gamescope_width`/`dg_pc_racing_gamescope_height` values so Wine
does not select the portrait monitor.

## Controller Policy

USB gamepads are exposed through the distrobox's `/dev/input` and `/dev/hidraw`
devices. The launcher pins SDL to the 8BitDo controller in XInput mode
(`0x2dc8/0x310b`) and disables SDL HIDAPI to avoid duplicate keyboard, mouse,
and HID interfaces being treated as stuck buttons. It still preserves
`SDL_GAMECONTROLLERCONFIG` if you set a custom mapping before launching. The
Wine prefix also sets `winebus` to `DisableHidraw=1`, `DisableInput=1`,
`Enable SDL=1`, and `Map Controllers=0` by default. This keeps Wine from
exposing duplicate raw event devices or an SDL-backed XInput virtual device
unless a game explicitly needs one.

`dg_pc_racing_dinput_disabled_joysticks` disables known pseudo-joystick HID
interfaces, such as the Moonlander keyboard's ABS-axis interfaces, through
Wine's `Software\Wine\DirectInput\Joysticks` registry key. This prevents menus
from scrolling as if a direction were held.

For controllers, first identify whether the game is a legacy DirectInput title
or a newer XInput-aware title. Old DirectInput racing games often misread
modern Xbox-style trigger axes: Linux and Wine expose released triggers at the
minimum axis value, while Windows DirectInput compatibility often presents a
different legacy view. The symptom is a phantom held direction, brake, or
accelerator. Do not stack random `Map Controllers` toggles for these games.
Use the role's `xidi` support when a legacy game needs a per-game DirectInput
virtual controller or trigger remapping.

Current per-game controller handling:

- Colin McRae Rally 2.0 uses the global `Map Controllers=0` baseline and the
  global duplicate-device filters. Do not enable Wine's controller mapping
  unless retesting shows the game cannot see the pad.
- Colin McRae Rally 3 uses `Map Controllers=1` plus a local Xidi virtual
  controller. RT/LT are mapped to the virtual axis CMR3 binds as throttle and
  brake, while physical left-stick Y is ignored.
- Colin McRae Rally 04 starts with the same CMR3-style Xidi baseline because it
  is a nearby legacy DirectInput title and should not retest the raw-trigger
  axis path first.
- Colin McRae Rally 2005 is marked not playable. Keep it on the conservative
  `Map Controllers=0` baseline until the launch crash is solved and controller
  behavior can be tested.
- OutRun 2006 uses the global `Map Controllers=0` baseline and native
  `OutRun2006Tweaks` `dinput8.dll`; Xidi is not enabled because it would
  conflict with the Tweaks loader.
- Sega Rally Revo uses `Map Controllers=1`, because this game needs Wine's
  SDL-backed XInput device to see the 8BitDo controller.
- Sega Rally 2 uses the 1.9.0 widescreen executable with `Map Controllers=0`.
  Disable the repack's top-level `dinput.dll`/`dinput8.dll` shims on Linux;
  they crash the widescreen launcher in `mginput` or early swapchain setup.

If `evdev-joystick --listdevs` only shows the Moonlander keyboard and SDL sees
zero joysticks, the 8BitDo is in a hidraw-only mode such as `2dc8:6013`. Switch
the controller/dongle to XInput mode so Linux creates a real `/dev/input/js*`
or event device before launching Wine games. The distrobox cannot create that
kernel input node by itself.

Game payloads default to the distrobox home:

```text
{{ dg_pc_racing_install_root }}/<game-slug>
```

Per-game Wine prefixes are separate:

```text
{{ dg_pc_racing_prefix_root }}/<game-slug>
```

Prepare packages, prefixes, wrappers, rendered desktop entries, and copy
already unpacked games:

```sh
cd ansible
ansible-playbook install-pc-racing.yml
```

Focused install for OutRun 2006:

```sh
cd ansible
ansible-playbook install-outrun-2006.yml
```

Focused install for Colin McRae Rally 3:

```sh
cd ansible
ansible-playbook install-colin-mcrae-rally-3.yml
```

Focused install for Colin McRae Rally 04:

```sh
cd ansible
ansible-playbook install-colin-mcrae-rally-04.yml
```

Focused install for Colin McRae Rally 2005:

```sh
cd ansible
ansible-playbook install-colin-mcrae-rally-2005.yml
```

Focused install for Sega Rally Revo:

```sh
cd ansible
ansible-playbook install-sega-rally-revo.yml
```

Focused install for Sega Rally 2:

```sh
cd ansible
ansible-playbook install-sega-rally-2.yml
```

Install or refresh host menu entries separately from the host:

```sh
scripts/install-host-launchers.sh
```

The host installer only exports rendered entries whose target wrapper exists
inside the `gaming` distrobox, so optional or untested games stay hidden.

Run installer helpers manually from inside the box when a game still needs a
GUI installer:

```sh
distrobox-enter -n gaming -- "{{ dg_box_home }}/bin/install-colin-mcrae-rally-2005"
```

To let Ansible launch installer helpers for games whose launcher executable is
still missing:

```sh
ansible-playbook install-pc-racing.yml -e dg_pc_racing_run_installers=true
```

That mode may open Windows installer GUIs. Use `G:\<game-slug>` as the target
directory when an installer asks where to install. Games that need a fixed
installed path, such as Colin McRae Rally 2.0, define `installed_path` and run
from that prefix directory instead.

Colin McRae Rally 2.0 uses SilentPatch from:

```text
{{ dg_pc_racing_cache_root }}/silentpatch_cmr2.zip
```

The role configures `SPCMR2.ini` with `Region=AMERICA` for the US media found
in `CountrySpecific/USA`, and uses fullscreen mode (`Window=0`,
`Borderless=0`) because Wine's built-in DirectDraw path leaves the menu stuck
behind the intro frame in windowed modes. dgVoodoo is not installed because it
crashes in this Wine setup.

The launcher wraps CMR2 in `gamescope` at `3840x2160` so Wine does not choose
the portrait monitor's `2160x3840` mode on the multi-monitor desktop.

## Colin McRae Rally 3

Colin McRae Rally 3 uses the Magipack Inno Setup repack under
`{{ dg_pc_racing_source_root }}/Colin-McRae-Rally-3_Win_EN-FR-DE-IT-ES-PL-CS_Repack`.
The focused playbook runs the installer silently to
`{{ dg_pc_racing_install_root }}/colin-mcrae-rally-3` through the prefix `G:`
drive and launches `Rally_3PC.exe`.

The repack notes state that patch 1.1, SilentPatch v2.1, the language pack, HD
UI assets, and dgVoodoo D3D9 support are already included. The installed game
ships `dinput8.dll` as Ultimate ASI Loader for `SilentPatchCMR3.asi`. The role
preserves that loader as `dsound.dll`, installs Xidi's 32-bit `dinput8.dll`,
and writes a CMR3-specific `Xidi.ini`. The wrapper sets
`WINEDLLOVERRIDES=dinput8,dsound,d3d9=n,b` so Xidi handles DirectInput while
SilentPatch still loads through the DSOUND proxy.

The silent installer may still leave a final `Setup` window open after files
are copied. Press Enter to close it if Ansible appears to wait after install.
Once `Rally_3PC.exe` exists, rerunning the focused playbook skips the installer
and only refreshes managed wrapper/desktop files.

The launcher wraps the game in `gamescope` at the configured 3840x2160 output
to avoid the same portrait-monitor mode selection seen in other Wine games.
Colin 3 also overrides Wine's `Map Controllers` to `1` so Wine exposes the
SDL-backed XInput device that Xidi consumes. Raw Wine DirectInput trigger axes
caused the accelerator to behave as permanently pressed; Xidi is the intended
compatibility layer for this class of games.
In CMR3's controller setup, the game binds accelerator/brake to the virtual
left-stick Y axis. The managed Xidi mapper therefore sends physical RT to
virtual left-stick up, physical LT to virtual left-stick down, and ignores
physical left-stick Y so steering cannot accidentally apply throttle or brake.

## Colin McRae Rally 04

Colin McRae Rally 04 uses the Magipack Inno Setup repack under
`{{ dg_pc_racing_source_root }}/Colin-McRae-Rally-04_Win_EN-FR-DE-ES-IT_Repack`.
The focused playbook runs the installer silently to
`{{ dg_pc_racing_install_root }}/colin-mcrae-rally-04` through the prefix `G:`
drive and launches `cmr4.exe`.

Public Wine notes are mixed by edition: old PlayOnLinux scripts warn that
original copy-protected retail media does not run, while CrossOver reports a
DRM-free/budget edition running well with DXVK. This repo uses the local repack
source and does not attempt to support protected retail media.

Current status: playable. The game registry is forced to `2880x2160` (4:3
within 4K), and gamescope uses the same 4:3 nested resolution inside the
configured `3840x2160` monitor with `fit` scaling and NIS filtering. This
avoids the horizontal stretch from a 16:9 internal output and the black
screen seen when the nested display was reduced to `640x480`. If the
2004-era engine refuses to render at `2880x2160`, fall back to `1920x1440`
in `pc_racing.yml` (both `gamescope_game_*` and the registry values);
gamescope still scales the 4:3 nested display onto the 4K monitor. The
image is not perfectly centered on the monitor, but it is usable.

Controller status: analog driving works. Xidi is configured as a
keyboard-emulation layer for CMR04 because selecting the Xidi joystick in-game
allowed menu navigation but did not reliably bind in-race actions. The mapper
sends d-pad and left stick to arrow keys, RT to accelerate, LT to brake,
A/Start to confirm, B/Back to cancel, X to Space, and Y to C.

## Colin McRae Rally 2005

Colin McRae Rally 2005 uses the GOG/Inno Setup DRM-free package under
`{{ dg_pc_racing_source_root }}/Colin-McRae-Rally-2005_Win_EN-FR-DE-IT-ES_DRM-Free`.
The focused playbook extracts it with `innoextract` to
`{{ dg_pc_racing_install_root }}/colin-mcrae-rally-2005` and launches
`cmr5.exe`. This avoids the Wine-hosted installer path, which crashed before
copying files during testing.

The entry preconfigures gamescope at the shared 3840x2160 output before the
first launch test so Wine does not select the portrait monitor. It uses system
Wine, DXVK D3D9, an isolated Wine desktop, `NOVIDEOMEMORYCHECK`, and `NOVIDEO`.
Wine-GE 8.26 was rejected for this game: pure win32 prefixes fail to create
GUI windows in the distrobox, while its WoW64 prefix cannot run 32-bit
executables because the 32-bit subsystem is incomplete.

Current status: CMR2005 is not playable. It remains in Ansible only as a
documented failed experiment so future work does not repeat the same tests.
System Wine reaches the game executable in Windows XP mode and then crashes
consistently at `cmr5+0x1da27` (`0x0041DA27`, null read from
`ECX+0x10`). Disassembly places the crash in a text/font measurement path, and
the expected `.pcf` font metadata and `.dds` font textures are present. Tested
non-fixes include DXVK versus WineD3D, Windows XP/SP3 registry settings, 64 MB
video memory, `NOVIDEOMEMORYCHECK`, `NOVIDEO`, `SAFEMODE`, restored
`MathPIII.dll`, and `.dds` to `.xxx` aliases. Keep this entry experimental
until a proven official patch or installer-registry fix changes the crash.

The game list lives in `ansible/group_vars/all/pc_racing.yml`.

## OutRun 2006

OutRun 2006 uses the Inno Setup repack source under
`{{ dg_pc_racing_source_root }}/OutRun-2006-Coast-2-Coast_Win_EN-FR-DE-IT-ES_Repack`.
The focused playbook runs the installer silently to `G:\outrun-2006`, installs
`vcrun2022`, downloads `OutRun2006Tweaks`, backs up the original
`OR2006C2C.exe`, and extracts the Tweaks DLL/EXE/INI into the game directory.

The launcher sets `WINEDLLOVERRIDES=dinput8=n,b;d3d9=n,b` so the native Tweaks
DLL loads under Wine and D3D9 is served by DXVK from the prefix. The repack also
installs a local SpecialK `d3d9.dll` and `d3d9.ini`; the role backs them up with
`.disabled-by-distrobox-gaming` suffixes and removes the active copies because
local DLL search order would otherwise load SpecialK before DXVK. If OutRun is
slow, verify `winetricks list-installed` includes `dxvk` and that no active
`d3d9.dll` remains in the game directory.

The role disables `gamescope` for this game and writes a fixed `3840x2160`
borderless-window config to avoid Wine picking the portrait monitor mode or
using an XRandR exclusive-fullscreen mode switch.
`dg_pc_racing_target_monitor_x` and `dg_pc_racing_target_monitor_y` pin the
borderless window to the target monitor; on the tested layout this is the
Samsung Odyssey G8 (`DP-1`) monitor at logical `4000,619` in the Hyprland
layout from `~/.config/hypr/monitors.conf`. Antialiasing stays disabled in
`outrun2006.ini` until DXVK is confirmed stable with the game's multisample
mode.

## Sega Rally Revo

Sega Rally Revo uses the full-rip payload under
`{{ dg_pc_racing_source_root }}/SEGA-Rally-Revo_Win_EN-FR-DE-ES-IT-PL_Full-Rip/Sega Rally`.
It is copied directly to `{{ dg_pc_racing_install_root }}/sega-rally-revo`
instead of running an installer. The role replaces the shipped `SEGA Rally.reg`
by writing the required `HKLM\SOFTWARE\WOW6432Node\Sega\SEGA Rally` registry
values for `installdir`, `sku`, and `language`.

The .NET launcher can create `config.ini`, but its UI is unreliable under Wine.
The role therefore seeds
`Documents\SEGA Rally\Saved Games\config.ini` directly with a 3840x2160,
high-quality, 60 Hz configuration. The game ignores `RunWindowed=1` in this
Wine setup and still requests an exclusive fullscreen mode, which crashes
outside containment with an XRandR `RRSetCrtcConfig` error. The launcher runs
the game through `gamescope` at a fixed 3840x2160 to keep it on the Samsung
Odyssey G8 monitor and avoid the portrait display mode.

The startup videos are disabled by backing up and removing the two WMV files
under `Bootup/video/Rally`. Wine's Quartz/GStreamer path spends a long time on
those files and makes startup look stuck even though DXVK has initialized.
The role also creates the expected `Saved Games` and Public Documents
`Shared Data` layout, including initial `SEGA Rally.dat` and
`SR_RANKTABLES.DAT` files without overwriting later real saves. Without that
layout, the game can reach the main menu and then crash with an access
violation.

The game uses Direct3D 9, so the focused playbook installs `directplay`,
`d3dx9`, `dxvk`, and the offline June 2010 DirectX runtime into the per-game
prefix. The full-rip only ships `dxwebsetup.exe`; the role uses
`dg_pc_racing_directx_jun2010_redist` instead. In the tested setup, installing
that offline DirectX runtime stopped the repeatable main-menu access violation.

Ansible seeds `config.ini` only when it is missing, then leaves it alone so the
game or launcher can preserve controller GUIDs. Sega Rally needs the 8BitDo in
XInput mode (`2dc8:310b`) with a real `/dev/input/js*` device. If the controller
is in `2dc8:6013` mode, Linux exposes only hidraw and Wine cannot present it as
a usable joystick to this game. Sega Rally also overrides `Map Controllers=1`
for its prefix so Wine can expose the SDL-backed XInput controller; the global
PC racing default stays `Map Controllers=0` for games that get duplicate or
stuck inputs.

The launcher runs `SEGA Rally.exe`; keep `SEGA Rally_SSE1.exe` only as a
fallback for older CPUs. In testing, `SEGA Rally_SSE1.exe` crashed on the same
main-menu path before the offline DirectX runtime was installed.

## Sega Rally 2

Sega Rally 2 uses the OldNewPixel 1.9.0 archive under
`{{ dg_pc_racing_source_root }}/Sega Rally 2 ~ 25th Anniversary Edition 1.9.0.7z`.
The role extracts that archive into the PC racing cache so the installer files
are available. The installer must still be run interactively, because the
1.9.0 Inno setup exposes the widescreen mode through a custom UI page rather
than a reliable `/COMPONENTS` flag. Choose the 16:9 widescreen option and keep
the install path at `G:\sega-rally-2`.

After a widescreen install, launch `SEGA RALLY 2 WIDESCREEN.exe` directly. The
launcher exposes the repack's 1067x600 16:9 dgVoodoo mode through gamescope and
scales it to the configured output. The normal `SEGA RALLY 2.EXE` remains the
4:3 fallback and should not be used for the desktop launcher.

The package ships its own compatibility stack: dgVoodoo files, ReShade, DSOAL,
Dinputto8, Xidi, and ogg-winmm support. On Linux, do not use the top-level
`dinput.dll` or `dinput8.dll` shims, including the nested `MUSASHI/dinput.dll`
Dinputto8 wrapper, and do not use the ReShade `dxgi.dll` layer. The launcher
sets `WINEDLLOVERRIDES=ddraw,d3dimm=n,b` and the role disables those
conflicting DLLs. Keep `DisableInput=0` and `Map Controllers=0`; basic
DirectInput needs Wine input enabled for keyboard/controller events, but Wine's
SDL controller mapper caused repeated menu input in earlier tests.
The shared DirectInput disabled-device list also hides the 8BitDo composite
keyboard/mouse interfaces by name, because this controller exposes extra HID
functions that can confuse old DirectInput games.

The role applies the repack's bundled Linux dgVoodoo 2.79.3 fallback from
`Troubleshooting/Linux/dgVoodoo2_79_3.zip`. It replaces `D3DImm.dll`,
`MUSASHI/DDraw.dll`, and `dgVoodooCpl.exe`, preserving `.original` backups
before the first replacement. This matches the repack's Linux note for avoiding
newer dgVoodoo failures under Wine/Proton.

The game profile is still forced to the Logitech wheel device type
(`nDeviceType=0A000000`, `InputSettings=10`) for now, but controller behavior
needs retesting after the widescreen launcher is stable. A stale `dinput.dll`
from the earlier 1.1.0 overlay caused the widescreen launcher to crash at
`mginput+0x3fee`; the 1.9.0 `dinput8.dll`/Dinputto8 path also crashed under
Wine with the 8BitDo attached, matching the repack's Linux troubleshooting
note.

During manual testing, the game kept running and music continued even when the
gamescope window lost focus or disappeared behind the desktop. Test from the
host launcher rather than from an active terminal so tmux or assistant output
does not steal focus while the game is switching modes.
The bundled manual documents `Alt+F4` as the clean application quit shortcut;
use that instead of Hyprland force-close, which can leave the game or
`_inmmserv.exe` alive. The generated wrapper still supervises gamescope and
runs `wineserver -k` for this prefix when gamescope exits.
