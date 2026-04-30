# PC Racing Games

Windows PC racing games are optional and are not installed during a normal
`site.yml` rebuild. They are managed by `install_pc_racing`, which uses system
Wine inside the `gaming` distrobox. Lutris and UMU are intentionally removed by
this role so the setup stays simple and reproducible.

Only Colin McRae Rally 2.0 is currently managed. Add more entries to
`dg_pc_racing_games` only after testing their install and launch path.

Game payloads default to the distrobox home:

```text
/mnt/data/distrobox/gaming/Games/pc-racing/<game-slug>
```

Per-game Wine prefixes are separate:

```text
/mnt/data/distrobox/gaming/wineprefixes/pc-racing/<game-slug>
```

Prepare packages, prefixes, wrappers, rendered desktop entries, and copy
already unpacked games:

```sh
cd ansible
ansible-playbook install-pc-racing.yml
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
distrobox-enter -n gaming -- /mnt/data/distrobox/gaming/bin/install-colin-mcrae-rally-2005
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
/mnt/data/distrobox/gaming/cache/pc-racing/silentpatch_cmr2.zip
```

The role configures `SPCMR2.ini` with `Region=AMERICA` for the US media found
in `CountrySpecific/USA`, and uses fullscreen mode (`Window=0`,
`Borderless=0`) because Wine's built-in DirectDraw path leaves the menu stuck
behind the intro frame in windowed modes. dgVoodoo is not installed because it
crashes in this Wine setup.

The launcher wraps CMR2 in `gamescope` at `2560x1440` so Wine does not choose
the portrait monitor's `1440x2560` mode on the multi-monitor desktop.

USB gamepads are exposed through the distrobox's `/dev/input` and `/dev/hidraw`
devices. For CMR2 the launcher pins SDL to the 8BitDo controller
(`0x2dc8/0x310b`) on `/dev/input/js0` and disables SDL HIDAPI to avoid duplicate
keyboard/mouse/HID interfaces being treated as stuck buttons. It still preserves
`SDL_GAMECONTROLLERCONFIG` if you set a custom mapping before launching.
The Wine prefix also sets `winebus` to `DisableHidraw=1` and `Enable SDL=1` so
Wine uses the SDL controller backend instead of raw HID for this game.

The game list lives in `ansible/group_vars/all/pc_racing.yml`.
