# Scud Race PC

[wanszai/Scud-Race](https://github.com/wanszai/Scud-Race) is installed as an
optional Windows PC game in the `gaming` distrobox. The pinned release is
`0.0.15`; the release archive is checksum-verified and staged in
`ROMS_FINAL/PC/releases/`. Run from the menu's **Scud Race** entry or with
`scud-race` from the host.

Version 0.0.15 adds sequential/H-pattern shifting options, F11 fullscreen
toggle and regional/world record boards. The role preserves existing player
settings so transmission selection remains the player's choice.

## Required arcade data

The port requires `scud.zip` with MD5
`d2d619b0ee5cbf74596431b28080c420`. In this collection, that exact data
is named `ROMS_FINAL/arcade/model3/scuda.zip`. The optional Daytona 2 Power
Edition set (`dayto2pe.zip`, MD5 `d05ef348c9be8408ef50ea74dae29f71`)
unlocks the Hornet car. The role checks both hashes and links the archives
under the names expected by the port. Adjust `dg_scud_roms` in host vars if
the same data lives elsewhere. No ROM data is copied to the box.

## Rebuild

```sh
cd ansible
ansible-playbook install-scud-race.yml
```

The role stages the release, installs Wine and SDL2 in the box, creates a
dedicated Wine prefix, and deploys a re-entrant launcher and desktop entry.
The running game and its player files live in `dg_scud_game_dir`. Release
updates copy program files there without replacing settings, saves, or custom
music. The first install seeds `scudrace.ini`; later runs preserve player edits.

## Display and input

The seeded settings select fullscreen widescreen, `scale=4`, smooth motion,
4× MSAA, 2D and 3D filtering, and enhanced textures. The game describes
smooth motion as an unlocked display-rate mode, so this is a frame-rate
setting, not a measured FPS result. The exact internal render resolution at
`scale=4` has not been independently measured. On the 4K display the title
screen rendered correctly through Wine; longer gameplay and stable FPS have
not yet been verified. If performance or frame pacing is poor, reduce
`scale` in `scudrace.ini` before lowering other image settings.

The port has native SDL/XInput controller support. The role selects pad input
(`pad=2`, `input_backend=auto`) and maps RT/LT to gas/brake, A/X to shift
up/down, and Y to view. Its dedicated Wine prefix enables SDL controller
mapping and suppresses duplicate raw devices. The 8BitDo Ultimate 2
`2dc8:310b` is present as a Linux joystick, and the launcher permits it;
actual in-race pad input and rumble still need a hands-on check. If necessary,
change bindings in the game's input menu or the `pad_map_*` entries in
`scudrace.ini`. See [PC racing controller policy](pc-racing.md#controller-policy).

The generated `scudrace.nv` is the actual save file. It and the two INI files
are registered in `dg_save_sets` for backup. The release payload, arcade
archives, and shaders are not backed up as save data.

## 2026-11-01 release update

Version 0.0.15 adds sequential/H-pattern and hold/push shifter choices, a PC F11 fullscreen toggle, a Miami online server, and revised records. The role keeps the existing gamepad and graphics configuration; the new shifter choices are optional and set in-game.
