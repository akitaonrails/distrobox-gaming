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

## ZSA Moonlander steals RetroArch player 1 (phantom joystick)

**Symptom:** the 8BitDo works in ES-DE menus, RetroArch says it "recognized
the 8BitDo", but in-game every button is dead. Rebooting doesn't help.

**Cause:** the ZSA Moonlander keyboard's *System Control* HID interface
(`3297:1969`) is tagged `ID_INPUT_JOYSTICK=1` by udev's `input_id` builtin.
RetroArch's `udev` joypad driver enumerates it as Pad #0 → **player port 1**
(unconfigured), pushing the real 8BitDo to **port 2**. The game reads player 1,
so nothing responds. ES-DE (SDL2) tolerates the phantom, hence it feels fine
there. The `retroarch.log` shows it plainly:

```
[Autoconf] ZSA ... Moonlander Mark I System Control (12951/6505) not configured.
[Autoconf] 8BitDo Ultimate 2 Wireless configured in port 2.
```

It surfaces after a reboot reshuffles `/dev/input/eventN` so the Moonlander's
phantom pad enumerates *before* the 8BitDo. Nothing in the RetroArch config is
wrong — all `input_player1_*` = `nul` is normal (autoconfig supplies binds).

**Fix (host udev rule — permanent, survives reboots):** clear the joystick tag
on that one interface so the 8BitDo takes port 1. Tracked at
`config/host-udev-rules/85-zsa-ignore-fake-joystick.rules`; install on the host:

```sh
sudo install -m0644 config/host-udev-rules/85-zsa-ignore-fake-joystick.rules \
  /etc/udev/rules.d/85-zsa-ignore-fake-joystick.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=input
```

Verify: `udevadm info --query=property --name=/dev/input/event6 | grep JOYSTICK`
should now show `ID_INPUT_JOYSTICK=0` (event number may differ). This is a HOST
rule (like `85-8bitdo-ignore-fake-input.rules` and `99-8bitdo-xpad.rules`); the
distrobox inherits it through the shared `/dev`. Re-apply after a host rebuild.

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
