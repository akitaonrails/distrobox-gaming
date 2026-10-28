# Gran Turismo 2 — native PC port (GT2-PC-Port-Mod-Kit)

[CurtisSlone/GT2-PC-Port-Mod-Kit](https://github.com/CurtisSlone/GT2-PC-Port-Mod-Kit)
`0.3.0` runs **Gran Turismo 2 natively from a byte-matched decompilation** of
the game's code on the PSX Runtime — not an emulator. GT2's own logic and
renderer, on the GPU: widescreen, sub-pixel vertices, perspective-correct
textures, longer draw distance. Windows x64 exes run through GE-Proton.
Managed by `install_gt2_pc` / `install-gt2-pc-port.yml`.

## Game data (user-provided, exact)

The installer accepts **one disc**: *Gran Turismo 2 (USA), Simulation Mode,
v1.0* (SCUS-94488; redump disc/85; 680,497,104 bytes; md5
`7f3e9b9555556da8638d475fd6e46e01`), as `.cue`+`.bin`. It fingerprints the disc
and refuses everything else. This library collected all the wrong ones first:
Rev 1 (disc/2643), Rev 2/Greatest Hits (disc/2818) and the patched v1.2 in the
DuckStation tree are all rejected — keep hunting for the **unsuffixed first
print** ("(v1.0)" / no Rev tag). The one-time install (`--install-only` under
Proton, ~1 min) copies the game into `data/` (~2 GB); the disc is not needed
afterwards. The role re-verifies with `--verify-data` on every run.

## Run

Walker entry: **Gran Turismo 2 · PC Port**; launcher
`/mnt/data/distrobox/gaming/bin/gt2-pc-port` → `psx-play.exe --hle` through
GE-Proton. Saves go to `cards/card1.mcr` (a standard 128 KB PlayStation
memory card — copy your DuckStation card over it to bring progress across;
a timestamped backup lands in `cards-backup/` before each session's first
write). Screenshots (F12) into `shots/`. Both live in
`~/.local/share/gt2-pc/`, symlinked so they survive kit upgrades.

Keys: F3 widescreen, F4 perspective-correct textures, F5 sub-pixel vertices,
F6 dither, F7 render scale, F8 software/GPU renderer, F12 screenshot, P pause,
Tab fast-forward. Gamepad: XInput/DualShock/DualSense or keyboard
(arrows=D-pad, X/Z/S/A=✕/○/□/△, Q/W/E/R=shoulders, Enter=Start).

## Mod kit

Blender 4.2+ track tools (`kit/setup-kit.bat`, .NET 8 for the pez2k car
tools), course export/import, track compiler — untouched here; see the kit's
guides if track modding is wanted.

## Status

Installed and disc-verified 2026-10-27 (manifest `known: true`, title
*(v1.0)*, data-track sha256 `0cc97dbd…` = the port's pinned fingerprint).
**Not yet launched** — first boot is the verification step.

## Controller — broken under Wine, cause isolated (2026-10-28)

psx-play's pad input is **gilrs 0.11.2** (Rust), whose default Windows backend
enumerates through WinRT **Windows.Gaming.Input** and builds its gamepad set
from the `GamepadAdded`/`RawGameControllerAdded` **events**. Verified with a
probe exe under this exact prefix and launch method:

- the pad is visible at every layer below: SDL in the box (8BitDo Ultimate 2,
  vid 2dc8 pid 310b), Wine **XInput** (`XInputGetState(0)` = connected, both
  via `proton run` and plain wine), and the WGI **lists**
  (`Gamepad.Gamepads` = 1, `RawGameControllers` = 1, correct name);
- the WGI **arrival events never fire** under Wine/GE-Proton 11-1 — so gilrs
  reports zero gamepads and psx-play prints "no gamepad found yet".

This is not fixable by configuration: the registry/WineBus/SDL tweaks do not
touch the WGI event path, and gilrs' XInput fallback is a compile-time feature
of the app (`gilrs = { default-features = false, features = ["xinput"] }`).
Keyboard input works (its events were observed through --pad-debug).

**Fix belongs upstream**: ask the kit author to ship the xinput gilrs feature
(the runtime strings show WSLg support, so Wine is on his radar). Until then
the interim option is a controller-to-keyboard bridge (AntimicroX in the box)
mapped to the documented keyboard controls; say the word and it gets wired.
