# Daytona USA 2 PC

[wanszai/DaytonaUSA2](https://github.com/wanszai/DaytonaUSA2) is installed as an
optional Windows PC game in the `gaming` distrobox, replacing the earlier
`daytona-usa-2-web` browser install. The pinned release is `0.0.16`; the release
archive is checksum-verified and staged in `ROMS_FINAL/PC/releases/`. Run from
the menu's **Daytona USA 2** entry or with `daytona2` from the host.

## Required and optional arcade data

The port requires the Daytona USA 2 Power Edition ROM set (`dayto2pe.zip`,
MD5 `d05ef348c9be8408ef50ea74dae29f71`) and accepts two optional bonus sets that
unlock extra tracks:

| Archive | Expected name | MD5 | Source in collection |
|---|---|---|---|
| Daytona USA 2: Power Edition | `dayto2pe.zip` | `d05ef348c9be8408ef50ea74dae29f71` | `ROMS_FINAL/arcade/model3/dayto2pe.zip` |
| Daytona USA 2: Battle on the Edge (optional) | `daytona2.zip` | `6d26677eb531870542347e7503762a27` | `ROMS_FINAL/arcade/model3/daytona2.zip` |
| Scud Race (optional) | `scud.zip` | `d2d619b0ee5cbf74596431b28080c420` | `ROMS_FINAL/arcade/model3/scuda.zip` |

The role verifies all three MD5 checksums and symlinks the archives under the
names expected by the port. Adjust `dg_daytona2_roms` in host vars if the same
data lives elsewhere. No ROM data is copied to the box.

## Rebuild

```sh
cd ansible
ansible-playbook install-daytona2.yml
```

The role stages the release, installs Wine, SDL2, and rsync in the box, creates
a dedicated Wine prefix, and deploys a re-entrant launcher and desktop entry.
The running game and its player files live in `dg_daytona2_game_dir`. Release
updates copy program files there without replacing settings, saves, or custom
music. The first install seeds `daytona2.ini`; later runs preserve player edits.

## Display and input

The seeded settings match our [Scud Race](scud-race.md) baseline: fullscreen
widescreen (`aspect43=0`), `scale=4`, smooth motion (`smooth=1`, unlocked
display-rate mode), 4× MSAA, 2D and 3D filtering, and enhanced textures. These
are configured caps/modes, not measured gameplay FPS results; if frame pacing
needs adjustment on 4K, lower `scale` in `daytona2.ini` before reducing other
image settings.

The port has native SDL/XInput controller support. The role selects pad input
(`pad=2`, `input_backend=auto`) and maps RT/LT to gas/brake, A/X to shift
up/down, and Y to view. Its dedicated Wine prefix enables SDL controller
mapping (`Enable SDL=1`, `Map Controllers=1`) and suppresses duplicate raw
devices (`DisableHidraw=1`, `DisableInput=1`), with NVIDIA GLX forced
(`UseEGL=N`). The launcher restricts SDL game controllers to
`dg_pc_racing_gamepad_only` (8BitDo Ultimate 2 `2dc8:310b`). Actual in-race pad
input and rumble still need a hands-on check; adjust bindings in the game's
input menu or `pad_map_*` in `daytona2.ini`. See
[PC racing controller policy](pc-racing.md#controller-policy).

## Save data

The generated `daytona2.nv` is the cabinet NVRAM save file. It along with
`daytona2.ini` and `online.ini` are registered in `dg_save_sets` under
`daytona2`. The release payload, symlinked ROMs, and shader caches are not
backed up as save data.
