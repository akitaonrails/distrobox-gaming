# Colin McRae Rally (1998) through REA

The [REA Colin McRae launcher](https://github.com/akitaonrails/rea-colin-mcrae)
replaces our older Wine setup. The role uses the original PC game in
`{{ dg_cmr1_source_dir }}` without modifying it. This machine has the supported
European v1.5 fan-pack `Rally.exe` (SHA256
`46500c8e22ce3e943b6855eca63ae9288261162347ca76fa36cad77cbb19c0bb`).
The REA launcher v0.9.2 ZIP is pinned by SHA256 and staged in
`ROMS_FINAL/PC/releases/`. Future updates come from this GitHub repository.
v0.5.1 fixes a post-stage crash with this exact community-patched executable
and applies fixes F20–F27 to it, including the depth-buffer and HD-art fixes.
v0.6.0 brings HD art pack 3 with redrawn skies and distant scenery, corrects
the pace-note sign colors and transparency, and smooths the rev bar. The
launcher installs the new pack on first start. There are no new launch or
configuration options, so the existing 4K, pacing, graphics, and controller
profile remains appropriate.
The pack 3 release changed art bytes without changing the list used as the
upstream cache key. Our role removes that one generated BMP cache once, so
the v0.6.0 launcher rebuilds it from pack 3 on first start. It does not touch
the game source, saves, or settings. The v0.6.0 launch log confirmed the pack
was rebuilt (1,450 ms) and loaded. Its generated BMP cache is retained for
future launches.

v0.7.0 replaces pack 3 with HD art pack 4: redrawn car textures, trackside
signs, car icons, badges, and flags. It selects the 4× art at our 4K target
and the lighter 2× art at up to 1080p. The launcher window now supports a
gamepad: Start plays, the d-pad navigates, A changes a setting, and LB/RB
switch tabs. New installations default to the Steam Deck look and smooth
Linux scaling; our existing managed 4K/120 FPS, Smooth scaler, 3× distance,
and modern controls remain appropriate. The new pack installs on first start;
the one-time pack 3 cache refresh above remains a historical migration and
does not need to run again.

The bounded v0.7.0 launch logged pack 4 loaded from its 4× set, 3× draw
distance, the new `cmrhooks.dll`, and `game started`. The test ended and its
Wine processes were reaped. The launcher-window gamepad shortcuts and a full
stage finish were not exercised in that check.

v0.9.2 patches the launcher's private `Rally.exe` on disk and makes it import
`cmrhooks.dll` when the game starts. It no longer changes the running game's
memory. The owned game folder stays untouched, and upstream verified a 4K
race, HD art and window closing. The release adds Windows version metadata to
the launcher and hook DLL. Our 4K/120 FPS, 3× distance and modern controller
settings need no changes. Downgrading later requires deleting the private
`Rally.exe` first; a normal role rerun never removes player saves or settings.

Run `ansible-playbook install-rea-colin-mcrae.yml` from `ansible/`. The role
checks the game hash, installs the launcher in its own directory and Wine
prefix, preserves the old save slot and `cmRally.cfg`, and removes only the
superseded CMR1 installed copy, prefix, scripts and desktop entry. It does not
remove the owned PC game source or other Colin McRae titles. A later run leaves
the player's settings and saves intact.

The first-run settings request 3840×2160 widescreen, 120 FPS redraw cap,
VSync, the maximum 3× draw distance, smooth distance changes and textures, bundled HD art,
and the modern pad layout with triggers and 60% rumble. The gamescope scaler is
Smooth (`linear`). The driving simulation
keeps its fixed rate; the FPS cap only affects redraws. Adjust settings in the
launcher's window; the role seeds the config only if absent and applies the
requested 3×/Smooth/Modern profile once to an earlier install. Upstream's Linux
helper uses gamescope to fit the race frame to the monitor and keeps the
launcher session synchronous so Wine processes can be reaped.
Upstream notes that long draw distances can reveal distant flicker; lower the
value in the launcher if that appears in a stage.

The original game's **Options → Settings → Graphics → Resolution** must use
640×480: REA replaces that slot with 3840×2160 during a race. The migrated
config selected 800×600, which left the race in a small top-left viewport
despite the launcher reporting 4K. The role changes only the resolution byte
(`0x13`, value `3` to `2`) once, preserves the original config as
`previous-cmRally.cfg`, and leaves the save slot untouched. Later changes made
in game are preserved on playbook reruns.

In the game, set **Options → Settings → Controller 1 → Joystick 1 → Analogue
joystick**, then set steering, acceleration and braking to **Analogue**. The
launcher provides the modern A/B/Y and bumper layout, d-pad menu navigation,
triggers and Start. The migrated `cmRally.cfg` may still have the old keyboard
mode, so this in-game change is required once. The save backup watches
`{{ dg_cmr1_saves }}`, the previous config, and the user-edited `launcher.cfg`; the launcher cache
and game files are reproducible. The bounded launch check logged 4K, 120 FPS
cap, 3× draw distance, HD art and `game started`. On v0.5.1, the log also
confirmed F20–F27 applied to the community-patched executable. A full stage
finish was not exercised. No pad was connected during that check, so in-game
pad controls still need verification.
