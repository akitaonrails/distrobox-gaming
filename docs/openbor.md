# OpenBOR fan games

**OpenBOR** (Open Beats of Rage) is the engine behind a large family of fan
beat-'em-ups. Games ship as a `.pak` (engine-agnostic) — usually bundled with
an old **Windows** `OpenBOR.exe`/`GAME.exe`. We ignore that exe and run the
`.pak` with the **official native Linux OpenBOR 4.0** build on the RTX — no
Wine. Managed by `install_openbor` / `install-openbor.yml`
(`site.yml --tags openbor`).

## Engine

Pinned GitHub release `DCurrent/openbor` **v7533** (OpenBOR 4.0 Build 7533,
linux-x64 AppImage, sha256-verified). The AppImage is **extracted** to
`tools/openbor/engine/` because its bundled libs are required — `libSDL2_gfx`
and an old `libvpx.so.5` that Arch no longer ships. The wrapper
`bin/openbor <game.pak>` puts `engine/usr/lib` first on the library path, pins
NVIDIA GLX (SDL2/OpenGL renderer → the RTX, not the iGPU), focuses DP-1, and
`cd`s into `~/openbor/` because OpenBOR writes `Saves/`, `Logs/`,
`ScreenShots/` **relative to its CWD** (so state never lands in the ROM dir).

## Games (data-driven)

Drop the game's archive in `ROMS_FINAL/PC/` and add a `dg_openbor_games`
entry in `ansible/group_vars/all/openbor.yml` (`archive` + the `.pak` member
path inside it). The role extracts **only the pak** (bsdtar handles rar/zip/7z)
into the ES-DE ROM dir `roms_mid/openbor/` and renders a Walker desktop entry.

| Game | Source | Notes |
|---|---|---|
| Streets of Rage: Troubles in Japan v1.1 (Berlioz) | chronocrash.com resource #443 → `SoR_Troubles_In_Japan.rar` | Needs OpenBOR 4; bundle's `GAME.exe` is OpenBOR v3.0 (ignored). Verified running natively 2026-08-26. |

## ES-DE

The `openbor` system in `dg_esde_systems` scans `roms_mid/openbor` for `.pak`
and launches `bin/openbor %ROM%`. (ES-DE's *stock* definition expects one
AppImage per game — ours is generated from `dg_esde_systems`, so the pak form
wins.) Regenerate after adding games: `ansible-playbook reset-configs.yml
--tags esde`. The `minui-menu-es-de` theme has no `openbor` artwork, so the
system shows with fallback styling.

## Fullscreen (host Hyprland rule)

OpenBOR opens a native **320×240 window** (a postage stamp on the 4K panel) and
only persists fullscreen per game in a binary `Saves/<game>.cfg` — no CLI
flag. Launched **from ES-DE** it inherits workspace 7, which the host
`~/.config/hypr/gaming.lua` fullscreens. Launched **from the Walker entry** it
relies on that file's "emulators launched directly" fallback rule, which must
list `openbor`:

```lua
o.window("(?i).*(melonds|duckstation|...|supermodel|vita3k|openbor).*", { fullscreen = true })
```

This is host config (Omarchy Hyprland Lua), not repo-managed — re-add it after
an `omarchy refresh hyprland`. Dynamic `hyprctl keyword windowrule` no longer
works on Hyprland ≥ 0.56 with the Lua parser ("keyword can't work with
non-legacy parsers. Use eval."); dispatchers must be sent as Lua, e.g.
`eval hl.dispatch(hl.dsp.focus({ monitor = "DP-1" }))` — the wrapper does this
to focus DP-1.

## Controller

OpenBOR uses SDL2 — the **8BitDo is detected natively** (`Joystick: … connected
at port: 0` in `~/openbor/Logs/OpenBorLog.txt`). Buttons are configured in the
game's own Options → Control menu (OpenBOR's per-game `Saves/<game>.cfg`).
