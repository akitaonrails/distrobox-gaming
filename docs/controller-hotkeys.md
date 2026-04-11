# Controller Notes

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

Dolphin is pre-configured for the 8BitDo Ultimate 2:

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

Reusable Dolphin profiles are stored at:

- [`Profiles/GCPad/8BitDo Ultimate 2 SDL.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/GCPad/8BitDo%20Ultimate%202%20SDL.ini)
- [`Profiles/Wiimote/8BitDo Ultimate 2 Nunchuk.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/Wiimote/8BitDo%20Ultimate%202%20Nunchuk.ini)
- [`Profiles/Wiimote/8BitDo Ultimate 2 Classic.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/Profiles/Wiimote/8BitDo%20Ultimate%202%20Classic.ini)

The active live configs are:

- [`GCPadNew.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/GCPadNew.ini)
- [`WiimoteNew.ini`](/mnt/data/distrobox/gaming/.config/dolphin-emu/WiimoteNew.ini)

Wii still needs per-game judgment. Use the default Nunchuk layout first, then
switch to the Classic profile for games that support it and play better on a
standard pad.
