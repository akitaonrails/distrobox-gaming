# Tom Clancy's Splinter Cell (2002, Steam 13560)

UE2-family / D3D8 stealth classic on the removable STEAM drive. Three separate
problems on this box, three fixes — the reproducible parts live in
`install_splinter_cell_fixes` (`install-splinter-cell-fixes.yml`,
`site.yml --tags splinter_cell`) + a `steam_launch_options` entry.

## 1. Game renders in the bottom-left corner

Cause: the game defaults to **1024×768 exclusive fullscreen**; on the 4K panel
the viewport paints in the corner of a black screen. Fix: the role sets
`Resolution=3840x2160` in `system/SplinterCellUser.ini`. **The inis are CRLF** —
a plain `sed 's/...$/'` silently misses; the role's edits are CRLF-safe.
(The Bink intro videos still draw at their native size in a corner — the game
renders video 1:1; `-nointro` in the launch options skips them.)

## 2. Menu mouse cursor pinned / snapping to corners

Under XWayland the game's software cursor and the real pointer disagree by the
1.5× fractional-scale factor — the menu cursor sticks at the corners. Fix
(community-verified on ProtonDB): run the game with the **Wine Wayland driver**.
Launch options (in `dg_steam_launch_options_by_appid`):

```
PROTON_ENABLE_WAYLAND=1 PROTON_USE_NTSYNC=1 %command% -nointro
```

plus per-game compat tool **GE-Proton11-5** (one-time Steam UI:
Properties → Compatibility). Verified: native Wayland window (`xwayland: False`),
menu fullscreen at 4K, mouse moves freely.

## 3. Gamepad

The game's native joystick support is partial (left stick + face buttons only;
the right-stick camera is effectively unbindable — community threads agree), so
the pad is handed entirely to **Steam Input**:

- The role sets `UseJoystick=False` in `system/SplinterCell.ini` so the game's
  raw dinput reading can't double-input against the emulation.
- One-time Steam UI: game Properties → Controller → enable Steam Input, then
  pick a **Keyboard (WASD) and Mouse** style layout (community layouts exist
  for this game; camera on right stick → mouse). Cloud-synced afterwards.
- SC1 gotcha: analog movement speed is governed by the **mouse wheel** — bind
  wheel-up/down in the layout (or scroll once at mission start) to walk/run.

## Files touched

- `system/SplinterCellUser.ini` — `Resolution=` (backup `*.bak-dg`)
- `system/SplinterCell.ini` — `UseJoystick=False` (backup `*.bak-dg`)
