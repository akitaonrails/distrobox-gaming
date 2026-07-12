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

There is also a per-game pattern for windows that must land on a
specific monitor: OutRun 2006 runs borderless without gamescope, and
XWayland's coordinate mapping pushes the mod's absolute window position
off the layout (an "invisible" window with audio still playing). Two
rules pin its class to the racing monitor and fullscreen it:

```ini
windowrule = monitor DP-1, match:class ^(or2006c2c\.exe)$
windowrule = fullscreen on, match:class ^(or2006c2c\.exe)$
```

Prefer this windowrule approach over in-game absolute positioning for
any non-gamescope wine game — compositor coordinates win under
XWayland scaling.

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

## Gotcha: Vulkan emulators + forced fullscreen at creation

The `fullscreen on` rule fullscreens a window *at creation*, which
resizes it while the app is still initializing. Some Vulkan emulators
can't survive that — their swapchain is created against the pre-resize
surface and fails, e.g. **standalone Dolphin** dies on ws7 with a
"failed to create Vulkan swap chain" dialog (click OK → it quits). It
works fine launched *manually* because then it fullscreens *itself*
(`Dolphin.ini` `Fullscreen=True`) only after its swapchain is ready —
a client-requested fullscreen, not a WM-forced one.

Not all Vulkan emulators are affected — eden (also Vulkan) survives the
forced fullscreen on ws7. It's app-specific to how gracefully the
emulator recreates its swapchain on an early resize.

Workarounds if you hit this on another Vulkan emulator:
- Switch that emulator's video backend to **OpenGL** (verified to
  survive forced fullscreen — no swapchain to race), or
- Let it self-fullscreen and keep it off the forced-fullscreen path.

**Decision for Dolphin:** GC/Wii runs through **RetroArch's Dolphin
core** (window class `retroarch`, which fullscreens fine), not
standalone Dolphin — so this is moot in practice. `dolphin` is left out
of the fallback fullscreen class list in `gaming.conf` for that reason.
Attempts to keep standalone Dolphin on Vulkan by floating it instead of
fullscreening (so its own `Fullscreen=True` takes over) did **not** stop
the crash on ws7 in testing; OpenGL was the only reliable fix.

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
