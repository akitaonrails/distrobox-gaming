# Hyprland gaming window rules

Emulators launched from ES-DE and games launched from Steam would
otherwise **tile** next to the frontend (Hyprland's default is a tiling
layout) or open **behind** it — instead of taking over the screen. The
rules in `~/.config/hypr/gaming.conf` make games open **fullscreen and
on top**: launch → game fills the screen → quit → back to the frontend
(console-like).

## Where it lives

**Host omarchy config, not this Ansible repo.** The rules are in
`~/.config/hypr/gaming.conf`, sourced from `~/.config/hypr/hyprland.conf`:

```ini
source = ~/.config/hypr/gaming.conf
```

Not Ansible-managed because `~/.config/hypr/` is the host's
omarchy/Hyprland domain. This doc is the repo-side record.

## Design: dedicated gaming workspace (primary)

Rather than enumerate every emulator/game window class, **workspace 7
is the gaming workspace**: anything that opens there goes fullscreen,
and the frontends are pinned there so their launches inherit it.

```ini
# Everything on workspace 7 opens fullscreen (console-like).
windowrule = fullscreen on, match:workspace 7

# Send ES-DE and Steam (and everything they spawn) to workspace 7.
windowrule = workspace 7, match:class (?i).*(es-de|steam).*
```

Flow: launch ES-DE or Steam (from Walker) → it opens on workspace 7,
fullscreen, and the view follows → launch a game from it → the game
opens on workspace 7, fullscreen, on top → quit → the frontend is back.
This covers **native Steam games too** (arbitrary window classes) with
no per-class maintenance — they just open on workspace 7.

Verified live: launching ES-DE from workspace 1 → it moves to
workspace 7 and opens `fullscreen=2`.

## Fallback: per-class fullscreen for direct launches

Launching an emulator **directly** (from Walker / a desktop entry,
bypassing ES-DE) opens it on your current workspace, not 7 — so the
workspace rule doesn't catch it. A per-class fullscreen rule covers
that case:

```ini
windowrule = fullscreen on, match:class (?i).*(melonds|dolphin|duckstation|pcsx2|ppsspp|rpcs3|xemu|eden|cemu|azahar|retroarch|flycast|shadps4|supermodel|vita3k).*
windowrule = fullscreen on, match:class (?i).*gamescope.*
```

This is redundant for the ES-DE/Steam flow and can be deleted if you
only ever launch via the frontends.

## Class-matching gotchas (both cost debugging)

Relevant to the fallback rules and to adding any class-based rule:

1. **The matched class is the Wayland app_id, NOT the `.desktop`
   StartupWMClass.** The launcher catalog says melonDS is `melonDS`,
   but Hyprland sees `net.kuribo64.melonDS`; azahar is
   `org.azahar_emu.Azahar` (capital A). Read the real class from a live
   window:
   ```sh
   hyprctl clients -j | jq -r '.[] | "\(.class)\t\(.title)"'
   ```
2. **Hyprland full-matches the class regex.** A bare substring like
   `melonds` never matches `net.kuribo64.melonDS`; wrap it:
   `(?i).*(melonds).*` (case-insensitive, any position).

## Notes

- `fullscreen` is a *static* effect — evaluated once at window open,
  against the initial class/workspace.
- `focus_on_activate` is already `true` by omarchy default, which helps
  emulators that request activation come to the front.
- To drop a game out of fullscreen temporarily, use your Hyprland
  fullscreen-toggle keybind.
- Workspaces 1–7 are on DP-1, 8–9 on DP-2 (see
  `~/.config/hypr/workspaces.conf`); 7 was the free DP-1 workspace.
- A backup of the pre-change `hyprland.conf` is at
  `~/.config/hypr/hyprland.conf.bak.<timestamp>`.
