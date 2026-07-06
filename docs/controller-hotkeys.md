# Controller Notes

## melonDS (standalone) savestates

melonDS's configurable hotkey list (22 entries: pause, fast-forward,
swap screens, reset, lid, mic, volume, solar sensor, guitar grip...)
has **no save/load state entries** — savestates cannot be bound to the
gamepad. This is a standalone limitation; the RetroArch core allowed it.

- System menu → Save state / Load state (slots 1-8 + file), plus
  "Undo state load".
- Fixed keyboard shortcuts: `Shift+F1`..`F8` save, `F1`..`F8` load.
- Savestates (`.ml1`..`.ml8`) live next to the ROM.
- Pad workaround: map the 8BitDo Ultimate 2's back paddles to
  `F1` / `Shift+F1` in 8BitDo Ultimate Software (the mapping is stored
  on the pad; it types keys via the pad's extra Keyboard HID
  interface, no Linux-side config needed).

## Multiple controllers

Two pads are used interchangeably; both pass through to the distrobox
natively (shared /dev + udev):

- 8BitDo Ultimate 2 Wireless — `2dc8:310b` (XInput mode via dongle)
- Xbox Series X|S — `045e:0b12` (host `xone`/GIP driver via the Xbox
  Wireless Adapter `045e:02e6`)

The pc-racing games only see pads on the SDL allow-list
(`dg_pc_racing_gamepad_only` in `group_vars/all/pc_racing.yml`) — add
new pads there. SDL-based emulators (Dolphin, PCSX2, RetroArch, Cemu)
see every pad without configuration, but their button *profiles* in
this repo are captured for the 8BitDo; map the Xbox pad in each
emulator's GUI if you want per-emulator bindings for it.

PCSX2 is configured to exit emulation with `Select+Start`:

```ini
[UI]
ConfirmShutdown = false

[Hotkeys]
ShutdownVM = SDL-0/Start & SDL-0/Back
```

This matches the 8BitDo controller auto-bind observed in PCSX2:

```ini
[Pad1]
Select = SDL-0/Back
Start = SDL-0/Start
```

If PCSX2 rewrites or ignores the chord, configure it through the UI:

```text
Settings -> Controllers -> Hotkeys -> Shutdown VM / Close Game
```

Then press `Select+Start`.

Dolphin is pre-configured for the 8BitDo Ultimate 2 through repo-managed
templates copied into `$DG_DOLPHIN_CONFIG_DIR` by `./bin/dg configure`:

- GameCube default:
  - left stick = main stick
  - right stick = C-stick
  - `Trigger L` / `Trigger R` = L / R
  - `Shoulder R` = Z
  - d-pad + rumble enabled
- Wii default:
  - `Button A` = Wii `A`
  - `Trigger R` = Wii `B`
  - `Button X` / `Button Y` = Wii `1` / `2`
  - right stick = IR pointer
  - left stick = Nunchuk stick
  - `Shoulder L` / `Trigger L` = Nunchuk `C` / `Z`
  - `Thumb R` = Wii shake
  - `Thumb L` = Nunchuk shake

Repo-owned Dolphin templates live under:

- [`config/emulator-overrides/dolphin/Profiles/GCPad/8BitDo Ultimate 2 SDL.ini`](../config/emulator-overrides/dolphin/Profiles/GCPad/8BitDo%20Ultimate%202%20SDL.ini)
- [`config/emulator-overrides/dolphin/Profiles/Wiimote/8BitDo Ultimate 2 Nunchuk.ini`](../config/emulator-overrides/dolphin/Profiles/Wiimote/8BitDo%20Ultimate%202%20Nunchuk.ini)
- [`config/emulator-overrides/dolphin/Profiles/Wiimote/8BitDo Ultimate 2 Classic.ini`](../config/emulator-overrides/dolphin/Profiles/Wiimote/8BitDo%20Ultimate%202%20Classic.ini)

The live copies inside the box are:

- [`Profiles/GCPad/8BitDo Ultimate 2 SDL.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/GCPad/8BitDo%20Ultimate%202%20SDL.ini)
- [`Profiles/Wiimote/8BitDo Ultimate 2 Nunchuk.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/Wiimote/8BitDo%20Ultimate%202%20Nunchuk.ini)
- [`Profiles/Wiimote/8BitDo Ultimate 2 Classic.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/Wiimote/8BitDo%20Ultimate%202%20Classic.ini)

The active live configs are:

- [`GCPadNew.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/GCPadNew.ini)
- [`WiimoteNew.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/WiimoteNew.ini)

Wii still needs per-game judgment. Use the default Nunchuk layout first, then
switch to the Classic profile for games that support it and play better on a
standard pad.
