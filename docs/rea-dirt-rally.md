# DiRT Rally (2015) — REA launcher

[akitaonrails/rea-dirt-rally](https://github.com/akitaonrails/rea-dirt-rally)
**unparks** DiRT Rally on this box (2026-11-02, issue #6). Unlike the other REA
racing launchers this one is **native**: it plays Feral Interactive's **native
Linux port** (`bin/DirtRally`), not a Windows build under Wine. The game was
delisted in 2022 and the Windows-under-Proton fix needed a legit Steam copy —
the native Linux port sidesteps that. The release is a small (6.6 MB)
self-contained AppImage that works on a **private runtime copy** and leaves the
owned game folder untouched.

```sh
cd ansible && ansible-playbook install-rea-dirt-rally.yml
```

| | |
|---|---|
| Release | `v0.2.0`, `DiRTRallyLauncher-v0.2.0-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/DiRT.Rally.Linux-ACTiVATED/DiRT.Rally` — Feral's **Linux 1.0 (build 31946)**, `bin/DirtRally` sha256 `de81c75c…`, the launcher's known-good edition. A pre-activated copy that runs without Steam (the game is delisted; the launcher never patches/cracks Steam or DRM files). |
| AppImage | `tools/rea-dirt-rally/` |
| Private runtime copy | `~/.local/share/dirtrally-launcher/runtime` (the launcher's default) |
| Launcher settings/log | `~/.config/dirtrally-launcher/` (`launcher.cfg`, `launcher.log`, `play.log`, `known-pads.json`) |
| Launcher | `bin/rea-dirt-rally` → AppImage: settings window, then play |
| Entry | Walker **DiRT Rally (REA)** |

v0.2.0 remains the latest release in the 2026-11-05 sweep. The role now also
archives its SHA256-verified AppImage in `ROMS_FINAL/PC/releases/` before
installing the executable locally, and removes the unused v0.1.0 local copy.

## What the launcher handles

**No Wine** — this is the native port; the AppImage carries what the 2017 build
needs on a modern system, given only to the game process:

- **The Ryzen-5000 / recent-CPU crash.** The port SIGSEGVs on the main thread at
  startup on new CPUs; the launcher's exec-implies-read `mmap`/`mprotect` shim
  (plus the game's own `libsteam_api.so`) fixes it.
- **"Error while loading shared libraries".** The old Steam-scout runtime
  libraries the 2017 port needs are bundled and **scoped to the game** (leaking
  them into gamescope crashes gamescope).
- **Feral's "Unsupported Linux distribution" window.** Suppressed
  (`SeenSpecificationAlertUUIDLnxDistributionUnsupported=1`); the **Recommended**
  look goes straight into the race at your screen's size. (**Original** shows
  Feral's pre-game window; **Steam Deck** is 1280×800.)
- **4K.** `resolution 3840x2160` is seeded (the "Graphics: Always Max Out" 4K
  target); graphics **quality** is the game's own — set it in **Options →
  Graphics** (Ultra; 4K works). gamescope (box-provided) puts it fullscreen on
  the right monitor (DP-1).
- **Modern pads.** An 8BitDo / recent Xbox-style pad is hot-plugged as a
  gamepad with the game's ready-made controls (`known-pads.json` remembers it).

## Gamepad

The launcher presents the pad to the game; set it up once in the game's own
**Options → Controls → Controls preset → Controller preset 1**. Upstream played
a full stage on this box config (Arch, NVIDIA, 4K) with an 8BitDo pad.

## Saves

DiRT Rally is native, so there is no Wine prefix. The Feral port keeps its
settings in `~/.local/share/feral-interactive/DiRT Rally/`, and this
pre-activated copy keeps the profile/career saves in the Steam-emu's
`~/.local/share/Steam/ACTiVATED/310560/remote/`. `dg_save_sets` mirrors both
plus `launcher.cfg` (not the ~43 GB private copy, which rebuilds from the
source). Online features are gone for everyone (RaceNet shut down in 2025);
offline career and single stages work.

## CLI

```sh
rea-dirt-rally            # settings window, then play
rea-dirt-rally --play     # saved settings, no window
rea-dirt-rally stop       # end the game
rea-dirt-rally status     # running or idle
```

## History

The retired path is issue [#6](https://github.com/akitaonrails/distrobox-gaming/issues/6):
the Windows game under Proton needed a legitimately-owned Steam copy, and the
title was delisted/unpurchasable, so it stayed parked. The native Feral Linux
port removes the Proton/Steam-copy barrier. The launcher's EDITIONS table also
knows the Windows DX11 build (`drt.exe`) but **blocks** it with a clear message —
it stops while loading under Wine.
