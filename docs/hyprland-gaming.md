# Hyprland gaming window rules

Emulators launched from ES-DE and games launched from Steam would
otherwise **tile** next to the frontend — Hyprland's default is a
tiling layout, so a new game window splits the screen with ES-DE/Steam
instead of taking over. The fix is a set of window rules that force
game/emulator windows to open **fullscreen**: launch → game fills the
screen → quit → back to ES-DE/Steam (console-like).

## Where it lives

**Host omarchy config, not this Ansible repo.** The rules are in
`~/.config/hypr/gaming.conf`, sourced from `~/.config/hypr/hyprland.conf`:

```ini
source = ~/.config/hypr/gaming.conf
```

They aren't Ansible-managed because `~/.config/hypr/` is the host's
omarchy/Hyprland domain (see the omarchy skill), separate from the
distrobox. This doc is the repo-side record of what was done and why.

## The rules (Hyprland 0.55.2)

```ini
windowrule = fullscreen on, match:class (?i).*(melonds|dolphin|duckstation|pcsx2|ppsspp|rpcs3|xemu|eden|cemu|azahar|retroarch|flycast|shadps4|supermodel|vita3k).*
windowrule = fullscreen on, match:class (?i).*gamescope.*
windowrule = fullscreen on, match:class (?i).*steam_app.*
```

## Two gotchas (both cost real debugging)

1. **The matched class is the Wayland app_id, NOT the `.desktop`
   StartupWMClass.** The launcher catalog
   (`group_vars/all/launchers.yml` `wm_class`) says melonDS is
   `melonDS`, but Hyprland sees `net.kuribo64.melonDS`. Always read the
   real class from a live window:
   ```sh
   hyprctl clients -j | jq -r '.[] | "\(.class)\t\(.title)"'
   ```
2. **Hyprland full-matches the class regex.** A bare substring like
   `melonds` never matches `net.kuribo64.melonDS`; it must be wrapped:
   `(?i).*(melonds).*` (case-insensitive, any position). This is why
   the rules use `.*(…).*` around the alternation — it catches both
   short forms and reverse-DNS app_ids in one pattern.

Verified live: `melonDS` → `net.kuribo64.melonDS` opens `fullscreen=2`.

## Coverage and gaps

- **Standalone emulators** — the alternation covers the ones in the
  ES-DE catalog. Names are distinctive enough that substring matching
  won't misfire on non-gaming windows.
- **gamescope-wrapped titles** (pc-racing games, xenia, anything under
  gamescope) already fullscreen themselves; the `gamescope` rule is a
  safety net.
- **Steam Proton games** present as `steam_app_<appid>` — covered.
- **Native Linux Steam games** each have an arbitrary class and are the
  one gap. Add them by name as you play them.
- **ES-DE itself** (class `es-de`) is deliberately not matched — it
  stays as the frontend.

## Adding an emulator/game that still tiles

1. Launch it, read its real class:
   `hyprctl clients -j | jq -r '.[] | "\(.class)\t\(.title)"'`
2. Add a distinctive lowercase substring to the alternation in
   `~/.config/hypr/gaming.conf`.
3. `hyprctl reload` (then `hyprctl configerrors` to confirm clean).

## Notes

- `fullscreen` is a *static* effect — evaluated once at window open,
  against the initial class. It can't react to later class/title
  changes (use a dispatch + event listener for that; not needed here).
- To temporarily drop a game out of fullscreen, use your normal
  Hyprland fullscreen-toggle keybind.
- A backup of the pre-change `hyprland.conf` is at
  `~/.config/hypr/hyprland.conf.bak.<timestamp>`.
