# Controller Hotkeys

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

Other standalone emulators do not all share a portable controller-hotkey config
format. Prefer native UI hotkey binding when the config syntax is not stable.

