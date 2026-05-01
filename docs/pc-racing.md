# PC Racing Games

Windows PC racing games are optional and are not installed during a normal
`site.yml` rebuild. They are managed by `install_pc_racing`, which uses system
Wine inside the `gaming` distrobox. Lutris and UMU are intentionally removed by
this role so the setup stays simple and reproducible.

Currently managed games:

- Colin McRae Rally 2.0
- OutRun 2006: Coast 2 Coast
- Sega Rally Revo

Add more entries to `dg_pc_racing_games` only after testing their install and
launch path. Reuse the existing data fields for silent installer flags,
downloadable ZIP patches, `winetricks` components, DLL overrides, INI edits,
and controller quirks instead of creating one-off role logic.

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

Focused install for Sega Rally Revo:

```sh
cd ansible
ansible-playbook install-sega-rally-revo.yml
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

The launcher wraps CMR2 in `gamescope` at `2560x1440` so Wine does not choose
the portrait monitor's `1440x2560` mode on the multi-monitor desktop.

USB gamepads are exposed through the distrobox's `/dev/input` and `/dev/hidraw`
devices. The launcher pins SDL to the 8BitDo controller in XInput mode
(`0x2dc8/0x310b`) and disables SDL HIDAPI to avoid duplicate keyboard/mouse/HID
interfaces being treated as stuck buttons. It still preserves
`SDL_GAMECONTROLLERCONFIG` if you set a custom mapping before launching. The
Wine prefix also sets `winebus` to `DisableHidraw=1`, `DisableInput=1`,
`Enable SDL=1`, and `Map Controllers=0`. This keeps Wine from exposing duplicate
raw event devices or an SDL-backed XInput virtual device, while still allowing
the cleaner SDL controller path. OutRun 2006 otherwise sees a phantom held
direction in menus even when Linux SDL and evdev report the 8BitDo as neutral.
`dg_pc_racing_dinput_disabled_joysticks` disables known pseudo-joystick HID
interfaces, such as the Moonlander keyboard's ABS-axis interfaces, through
Wine's `Software\Wine\DirectInput\Joysticks` registry key. This prevents menus
from scrolling as if a direction were held.

If `evdev-joystick --listdevs` only shows the Moonlander keyboard and SDL sees
zero joysticks, the 8BitDo is in a hidraw-only mode such as `2dc8:6013`. Switch
the controller/dongle to XInput mode so Linux creates a real `/dev/input/js*`
or event device before launching Wine games. The distrobox cannot create that
kernel input node by itself.

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

The role disables `gamescope` for this game and writes a fixed `2560x1440`
borderless-window config to avoid Wine picking the portrait monitor mode or
using an XRandR exclusive-fullscreen mode switch.
`dg_pc_racing_target_monitor_x` and `dg_pc_racing_target_monitor_y` pin the
borderless window to the target monitor; on the tested layout this is the ASUS
`DP-1` monitor at `2160,0` in XRandR coordinates. Antialiasing stays disabled in
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
`Documents\SEGA Rally\Saved Games\config.ini` directly with a 2560x1440,
high-quality, 60 Hz configuration. The game ignores `RunWindowed=1` in this
Wine setup and still requests an exclusive fullscreen mode, which crashes
outside containment with an XRandR `RRSetCrtcConfig` error. The launcher runs
the game through `gamescope` at a fixed 2560x1440 to keep it on the ASUS
monitor and avoid the portrait display mode.

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
