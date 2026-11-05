# Screamer Trilogy — REA launcher

[akitaonrails/rea-screamer-trilogy](https://github.com/akitaonrails/rea-screamer-trilogy)
replaced the old dosbox-staging role on 2026-11-01. One native binary
(**ScreamerLauncher**) plus its own statically hooked **dosbox-staging v0.82.2**
covers all three games — **Screamer** (1995), **Screamer 2** (1996) and
**Screamer Rally** (1997) — and obsoletes every workaround the old install
needed.

```sh
cd ansible && ansible-playbook install-rea-screamer.yml
```

| | |
|---|---|
| Release | `v0.8.2`, `ScreamerLauncher-v0.8.2-linux-x86_64.zip` (pinned + sha256 from the release `SHA256SUMS`; archived in `ROMS_FINAL/PC/releases/`) |
| Installed at | `tools/rea-screamer/ScreamerLauncher-v0.8.2-linux-x86_64/` (launcher + hooked dosbox + resources) |
| Trilogy games | `tools/rea-screamer/games/{screamer,screamer2,screamer-rally}` — read-only, moved from the retired role |
| Settings | `~/.config/screamer-launcher/launcher.cfg` |
| Runtime + saves | `~/.local/share/screamer-launcher/{runtime,saves}/<game>` |
| Launcher | `bin/rea-screamer`; entry **Screamer Trilogy (REA)** |

v0.8.2 updates the shared launcher SDK to v0.4.3 and adds Windows executable
metadata and a manifest to reduce antivirus false positives. The Linux ZIP
remains the managed install; the existing graphics and controller settings do
not require changes. The role removes only the explicitly listed older
launcher extracts and release ZIPs, preserving `games/`, saves and settings.

## What it does that the old role could not

- **3dfx Voodoo Glide** rendering (`S2_3DFX.EXE`, `STRT3FX.EXE`), with the
  genuine DOS `GLIDE2X.OVL` linked from Screamer Rally when present, and 2×
  internal Voodoo superscale (1280×960) under `renderer = auto`.
- **FSR 1.0 upscaling** to the display (`texture_filter = fsr`; the role seeds
  `resolution = fullscreen`, i.e. the 4K panel). `sharp`/`smooth`/`original`
  remain available in the Picture tab.
- **Hor+ 16:9 widescreen** via the camera-projection patch, and **extended
  draw distance** (Screamer +20% managed animations, S2/Rally 2× admission
  radius).
- **100 FPS optical-flow frame generation** — presentation only: the engines'
  SOS timer and 50-entry physics table stay on the native 50 Hz step, so game
  speed is untouched. `fps_limit = 50` is the fallback if it ever misbehaves.
- **Modern gamepad support** with proportional analog steering, L2/R2 analog
  triggers, rumble and a **Buttons** tab — including the 8BitDo Ultimate 2
  (`2dc8:310b`), which SDL2's GUID database does not know. The old role needed
  a committed dosbox mapperfile binding the pad to keyboard keys; that file is
  gone with it.
- **Automatic GOG CUE/redbook mounting** (Screamer's `SCREAM.DAT`, Rally's ISO)
  and synthesized `SCREAMER.CFG` / `SETUP.CFG` / `CONTROLS.CFG` — no SETUP.EXE
  runs, no Ctrl+F1 mapper, no hand-edited dosbox.conf.

## Settings seeded by the role

`launcher.cfg` is seeded once (`force: false`), then it belongs to the
launcher window: `renderer auto`, `resolution fullscreen`, `widescreen true`,
`extended_draw_distance true`, `fps_limit 100`, `vsync true`,
`texture_filter fsr`, `gamepad_axes true`, `deadzone 0`. The `game` key always
points at the trilogy folder.

## CLI

```sh
rea-screamer                  # settings window (pad-navigable), then play
rea-screamer 1|2|rally        # pick the game for this run
rea-screamer --play rally     # saved settings, no window
rea-screamer stop|status
```

`ScreamerLauncher --check --game <folder>` validates every discovered game,
CD image and binary patch, and `--controllers` lists pads and their events —
both headless, both useful after touching the games folder.

## If the games folder ever moves

The launcher's private runtime keeps **symlinks** into the game folder (only
the patched executables are copied). Moving `tools/rea-screamer/games` — which
is exactly what replacing the old role did — leaves those links dangling, and
a game then fails with dosbox's `Stub exec failed: dos4gw.exe` (the stub rides
in through a broken link). Fix: delete the affected game's folder under
`~/.local/share/screamer-launcher/runtime/` — it rebuilds on the next Play;
saves live in `saves/` and are unaffected. The role's move already cleaned the
Screamer Rally runtime that had been built against the old path.

## Sources

GOG installers stay in `ROMS_FINAL/PC/ports/Screamer/`
(`setup_screamer_1.01_gog_v2_*.exe`, `setup_screamer2_2.0.0.1.exe`, Rally's
installer) — a from-scratch rebuild re-extracts them into
`tools/rea-screamer/games/`. The separate `patch_screamer_1.0_to_1.01_*.exe`
is **not needed** (the GOG installer is already 1.01 v2). Old saves found in
the game folders (`*.SAV`, `CHOICE.DAT`, `REPLAYS/*.RPL`) are moved into the
launcher's `saves/<game>` dir, which `dg_save_sets` mirrors.
