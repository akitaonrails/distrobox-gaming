# Colin McRae Rally (1998) through REA

The [REA Colin McRae launcher](https://github.com/akitaonrails/rea-colin-mcrae)
replaces our older Wine setup. The role uses the original PC game in
`{{ dg_cmr1_source_dir }}` without modifying it. This machine has the supported
European v1.5 fan-pack `Rally.exe` (SHA256
`46500c8e22ce3e943b6855eca63ae9288261162347ca76fa36cad77cbb19c0bb`).
The REA launcher v0.5.0 ZIP is pinned by SHA256 and staged in
`ROMS_FINAL/PC/releases/`. Future updates come from this GitHub repository.

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
cap, 3× draw distance, HD art and `game started`. No pad was connected during
that check (`XInput pads: [0]`), so in-game pad controls still need verification.
