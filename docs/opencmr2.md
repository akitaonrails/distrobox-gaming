# OpenCMR2

The native Linux build is pinned to [v1.7.0](https://github.com/pablocpas/OpenCMR2/releases/tag/v1.7.0), which smooths scenery draw distance and fixes object blending. The archive is SHA256-verified and updates the executable without replacing user settings.

Run `ansible-playbook install-opencmr2.yml` from `ansible/` to install the
native Linux port alongside the existing Colin McRae Rally 2.0 Wine setup.
The optional `site.yml --tags opencmr2` path does the same. The original Wine
launcher and prefix remain untouched.

The role downloads the pinned Linux release with a SHA-256 check. It reads the
untouched extracted US CD game data directly, while the Wine launcher keeps its
Official WRC Liveries overlay. The overlay replaces car geometry as well as
textures; on the native port, a Subaru body appeared partly transparent with
that overlay. No upstream car-rendering fix was available as of 2026-10-13.
The Wine overlay was verified against the archive: all 953 files match, so the
native glitch was not caused by a partial extraction. Default liveries are the
safer choice for the native port.
Override `dg_opencmr2_game_data` in `host_vars/localhost.yml` if the original
game lives elsewhere. The role sets `sku = AMERICA` for the US media and
preserves other user settings. OpenCMR2 saves, settings, and logs live under
`dg_opencmr2_user_dir`, separate from the Wine game's `gamesave` directory.

The host application launcher is **Colin McRae Rally 2.0 (OpenCMR2)**. Test
controller steering and triggers, menu/video playback, a full stage, and car
models before considering it a replacement for the Wine launcher.
OpenCMR2 is a new work-in-progress port; the project's physics parity checks
do not establish controller or mod compatibility on this machine.

The port maps gamepad D-pad directions to the original game's joystick POV for
menu navigation, with no separate INI setting for menu up/down. On this host,
the 8BitDo D-pad up/down were not recognized in menus as of 2026-10-13; keyboard
arrows remain a usable fallback. Do not change the global controller mapping
for this menu-only issue without testing the live controller first.
