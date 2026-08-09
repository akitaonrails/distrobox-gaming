# Donkey Kong Land Remake (DKLR) — `install_dklr`

kasquez's free fangame remake of the GameBoy *Donkey Kong Land* in the SNES
*Donkey Kong Country* style. Opt-in role; installed 2026-08-08.

- **Engine:** Windows **Unity (IL2CPP)** → runs under **Wine + DXVK**.
- **Native resolution:** 256×224 pixel art (Alt+Enter toggles fullscreen in the
  raw build). The launcher **integer-scales** it to the panel with gamescope for
  crisp pixels — no blur.
- **Source:** staged on the NAS at `dg_dklr_source_dir`
  (`ROMS_FINAL/PC/DKLR`); the role copies it to a writable local install
  (`{{ dg_box_home }}/Games/dklr`) so autosaves work.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-dklr.yml           # or: site.yml --tags dklr
# refresh the host menu entry:
scripts/install-host-launchers.sh
# remove it (launcher + prefix + local copy; NAS source untouched):
ansible-playbook install-dklr.yml -e dg_dklr_revert=true
```

Launcher: `{{ dg_box_home }}/bin/dklr`. It pins the RTX (`VK_ICD_FILENAMES`
=nvidia — a Unity/DXVK title black-screens on the AMD iGPU otherwise, like Sega
Rally Revo), focuses DP-1, and wraps the game in gamescope.

## Controls (pad → keyboard bridge)

The game is **keyboard-only** (the README bundles Windows JoyToKey). Instead the
launcher runs an **evsieve** bridge that maps the pad to the game's keys — real
controller play, no JoyToKey. Mapping follows the README's SNES layout by
physical button position:

| Pad (8BitDo/Xbox) | Game key | SNES button |
|---|---|---|
| D-pad | Arrows | D-pad |
| A (south) | X | B (jump) |
| B (east) | S | A |
| X (west) | Z | Y (run/roll) |
| Y (north) | A | X |
| LB | Q | L |
| RB | W | R |
| Start | Return | Start |
| Select/Back | Backspace | Select |

Keyboard also works directly (arrows + S/X/A/Z/Q/W/Return/Backspace). To pick a
different pad or remap, edit `roles/install_dklr/templates/dklr.sh.j2`.

## Presentation notes

gamescope runs `-w 256 -h 224 -W 3840 -H 2160 -S integer -f` — integer scaling
centres a crisp pixel image with a border. For a fill-the-screen look instead,
change `-S integer` to `-S fit` in the launcher (slightly softer). Output size
is `dg_dklr_output_width`/`_height`.
