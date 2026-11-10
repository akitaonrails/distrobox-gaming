# Rad Mobile (Sega System 32) — REA launcher

[akitaonrails/rea-rad-mobile](https://github.com/akitaonrails/rea-rad-mobile) is
a launcher for Sega's 1990 System 32 arcade racer **Rad Mobile**, in the spirit
of Wanszai's arcade ports: one package with a bundled, patched MAME, a gamepad-
and wheel-driven menu, 4K rendering, true widescreen, CRT filters and force
feedback built from the car's state. No ROMs are included.

```sh
cd ansible && ansible-playbook install-rea-rad-mobile.yml   # or site.yml --tags rea_rad_mobile
```

| | |
|---|---|
| Release | `v0.1.0` — `RadMobile-0.1.0-linux-x86_64.tar.gz` (15.7 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| ROM | `ROMS_FINAL/arcade/fbneo/radm.zip` (Rad Mobile World, 21 files, SHA256-pinned) linked as `roms/radm.zip` |
| Install | `tools/rea-rad-mobile/v0.1.0/RadMobile-0.1.0-linux-x86_64/` (launcher + bundled MAME + bgfx) |
| State | `~/.local/share/rea-rad-mobile/` — `settings.ini`, `wheel.ini`, MAME `nvram` (arcade EEPROM), `cfg`, rebuilt `roms/` |
| Launcher | `bin/rad-mobile`; entry **Rad Mobile · REA** |

The launcher detects the set by content (any file name works) and rebuilds it
under MAME's names into the data dir before every run. It also writes the
operator settings into the EEPROM and uses **always the Upright cabinet** — the
Deluxe cabinet's motor board is not emulated.

## Settings

`settings.ini` is seeded once with the maximum this box can use; the in-launcher
menu rewrites the file and later changes survive.

| Key | Value | Meaning |
|---|---|---|
| `display` | `fullscreen` | |
| `resolution` | `2160p` | MAME renders at 3840×2160 |
| `aspect` / `wide_target` | `widescreen` / `16:9` | the patched MAME draws more road at the sides (`REA_S32_WIDE_MARGIN`) |
| `filter` | `sharp` | unfiltered pixels; CRT/CRT Deluxe are selectable |
| `vsync` | `true` | |
| `free_play` | `true` | the menu starts a race with Start, no coin needed |
| `steer_lock` | `270` | the arcade cabinet's lock |

Wheels (Logitech, Thrustmaster, Fanatec CSL/DD, MOZA, generic) are detected
automatically, with a setup wizard for separate pedal devices and buttons;
gamepads steer with the left stick and accelerate/brake with the triggers;
keyboard works too (arrows, Ctrl/Alt, Space/Shift, 1). Force feedback is
synthetic (speed centring/damping, barrier scrape, crash jolts) because the
original cabinet had no steering motor.

## Verified here

`--check-roms` reports `ROM OK: Rad Mobile (World)`; the seeded settings produce
`-resolution 3840x2160 -view Widescreen -bgfx_screen_chains unfiltered -nofilter
-nowindow -waitvsync` with `REA_S32_WIDE_MARGIN=52`; a bounded run reached the
in-game Round 1 view ("GO", Los Angeles, speed readout) on the host, and the box
launch starts the same MAME command under the 4K settings. Wheel force feedback,
the setup wizard and a full race were not exercised.

## Notes

- The World set is used; add `radmu.zip` as well if you prefer the US region.
- Saves/state live in the data dir and are mirrored by `dg_save_sets` as
  `rea-rad-mobile` (settings, wheel profile and the EEPROM that holds the
  arcade's operator settings and high scores).