# Hyprland tweaks for gaming

Host-side `~/.config/hypr/` adjustments that the distrobox-gaming
playbooks don't manage but matter for a usable gaming session. Keep
this doc in sync after any change to the host config that's there
because of gaming.

## Inhibit hypridle while a window is fullscreen

### Symptom

Hypridle's screensaver kicks in mid-game and the lock screen takes the
display while you're playing. Most affected: Xenia (Wine/Xwayland),
Steam Proton games, and other Wine-launched titles. Native Wayland
games that grab `idle-inhibit-v1` themselves don't hit this; the rest
do because the protocol isn't transparently bridged through Xwayland.

### Fix

Add a window rule to `~/.config/hypr/looknfeel.conf`:

```
windowrule = idle_inhibit fullscreen, match:class .*
```

After saving, `hyprctl reload` and confirm `hyprctl configerrors` is
empty.

### Syntax notes

This took longer than it should have because the docs lag the source.
Hyprland 0.54.3:

- The keyword is **`idle_inhibit`** (with underscore). Older docs and
  most blog posts say `idleinhibit` (one word) — that produces
  `Config error: invalid field type idleinhibit`. The 0.54+ rename is
  visible in `src/desktop/rule/windowRule/WindowRuleEffectContainer.cpp`
  in the Hyprland source.
- Use the unified `windowrule` keyword. `windowrulev2` is rejected
  with `windowrulev2 is deprecated. Correct syntax can be found on
  the wiki.`
- The matcher uses the `match:` prefix. The bare `class:^(.*)$`
  shorthand still works for older rules but throws `invalid field
  class:^(.*)$: missing a value` in the `idle_inhibit` parser
  specifically. `match:class .*` is what reloaded clean.
- Valid `idle_inhibit` modes: `none`, `focus`, `fullscreen`, `always`.
  `fullscreen` is the right pick — it inhibits idle only while the
  window is fullscreen, so the desktop's normal 20-min screensaver +
  40-min lock timers still work outside of gaming.

### Caveat

Triggers on Hyprland's notion of fullscreen — i.e. the actual
fullscreen state (F11 / true fullscreen). Borderless-windowed games
that cover the whole screen but never take the fullscreen flag won't
inhibit. If you hit one of those, narrow to a class allowlist:

```
windowrule = idle_inhibit always, match:class ^(xenia_canary\.exe|.*\.exe|steam_app_.*)$
```

`always` here means "always inhibit while this window exists" — fine
for game windows that close when the user is done.
