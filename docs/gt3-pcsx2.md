# Gran Turismo 3 A-spec on PCSX2

Three distinct gotchas compound on this game. Miss any of them and
you get a crash, a stretched 4:3 display, or settings that appear to
save but never load. All three are covered below.

## 1. PCSX2 version: stable 2.6.3 crashes, 2.7.x works

On PCSX2 `2.6.3` (current Arch stable) GT3 reproducibly
`SIGABRT`s when entering the car-selection/showcase screen —
deterministic, same stack offset every crash, under every renderer
(Vulkan / OpenGL / Software), every upscale multiplier, with every
game-fix toggled off. The assertion is in PCSX2's GS code. Hundreds
of fixes landed in 2.7.x between Feb 2025 and Apr 2026; the same ISO
runs cleanly on `2.7.274`.

Fix: `dg_aur_packages` in `group_vars/all/packages.yml` is pinned to
`pcsx2-latest-bin` (rolling 2.7.x AppImage). If you had `pcsx2`
installed before, `pacman -Rdd pcsx2` removes it and installing
`pcsx2-latest-bin` takes over.

## 2. PCSX2 ≥ 2.7 per-game ini filename: `SERIAL_CRC.ini`, not `SERIAL.ini`

PCSX2 2.7.x loads per-game overrides ONLY from
`~/.config/PCSX2/gamesettings/<SERIAL>_<CRC>.ini`. Files named just
`<SERIAL>.ini` are silently ignored — Game Properties shows
"using globals" even though the file is right there on disk.

Every entry in `dg_pcsx2_per_game_settings` now carries a `crc:`
field, and `seed_configs/pcsx2.yml` writes
`{{ serial }}_{{ crc }}.ini`. Find the 8-hex-char CRC in PCSX2's
`logs/emulog.txt` on first boot:
```
Serial: PBPX-95503
CRC: 8AA991B0
```

## 3. GT3 ISO variants: SCUS-97102 vs PBPX-95503

A widely-mirrored GT3 dump labeled "Gran Turismo 3 - A-spec (USA)
(v1.10)" actually reports at runtime as **serial `PBPX-95503`, CRC
`8AA991B0`** — the **PS2 Bundle** reissue, which Sony sold in USA
markets with the OPB-style serial baked in. Same CRC as the EU
`SCES-50294` v1.10 disc; PCSX2's bundled `GameIndex.yaml` gets the
disc type right ("Gran Turismo 3 - A-Spec [PS2 Bundle]").

The repo ships per-game entries for BOTH serials with identical
settings (YAML anchor `&gt3_settings`) so whichever rip you have,
PCSX2 picks up the right file:

| Serial | CRC | Variant |
|---|---|---|
| `SCUS-97102` | `85AE91B3` | USA retail v1.10 |
| `PBPX-95503` | `8AA991B0` | PS2 Bundle (USA distribution + EU/JP, same CRC as `SCES-50294`) |

## 4. Widescreen is an in-game toggle, not a pnach force

AeroWidescreen's `PBPX-95503_8AA991B0_widescreen.pnach` is shipped
and loading correctly (log: `Enabled patch: Widescreen 16:9`), but
its description is literally:
> Corrects the text aspect ratio when 16:9 is selected in the options menu.

It's a text-aspect helper for the in-game 16:9 mode, not a viewport
force. Without the in-game toggle, GT3 renders 4:3 geometry which
PCSX2 then stretches to the window.

**To actually get 16:9:**

1. Load GT3. Exit any race (press Start → Retire).
2. Back out to the **Main Menu** (Circle repeatedly).
3. Pick **Option** → **TV Type** (or **Display Settings**).
4. Change from **4:3** → **16:9**. Save back out.
5. Widescreen takes effect from the next race. The setting persists
   to the memcard so it's a one-time thing.

If you try the toggle mid-race — you won't find it; the option is
only in the Main Menu.

## 5. PCSX2 host hotkeys to avoid mid-game

Our global `dg_pcsx2_settings` binds:
- `Select + Start` (controller) → `ShutdownVM` — **kills the
  emulator instantly.** Convenient emergency exit, lethal to muscle
  memory if your PS1/PS2 mental model uses the same combo for
  pause-to-main-menu. GT3 *also* tries to use Start for its in-game
  pause — that still works; it's the `Select + Start` *combination*
  that PCSX2 intercepts.
- `F1` → load state
- `F3` → save state
- `F11` → toggle fullscreen
- `Tab` → turbo

Rebind `ShutdownVM` in `ansible/group_vars/all/emulators.yml` if the
combo collides with what you expect.

## 6. Retexture pack: wired but off by default

The `GT3 Retexture 1.0` pack (4.7 GB, 566 PNGs) is on the NAS and
symlinked to `textures/SCUS-97102/replacements/` and
`textures/PBPX-95503/replacements/`. Per-game settings have
`LoadTextureReplacements = false` by default because streaming those
PNGs from the NFS-mounted NAS during car-showcase caused visible
flicker in live testing. Your options:

- **Leave off (shipped default).** Vanilla car textures, no flicker,
  4K upscale still looks great.
- **Copy the pack to local disk + enable.** If you rsync
  `GT3 Retexture 1.0/` onto the box's local `$dg_box_home/...` the
  flicker may not reappear since NFS latency is eliminated. Flip
  `LoadTextureReplacements = true` in
  `dg_pcsx2_per_game_settings` for both serials.
- **Try `PrecacheTextureReplacements = true`.** Loads all 566 PNGs
  up front at boot (slow first launch, no mid-race streaming).
  Requires `LoadTextureReplacements = true` too.

Enable via `dg_pcsx2_per_game_settings` + re-run the
`pcsx2_textures` role tag, or by direct edit of the deployed
`~/.config/PCSX2/gamesettings/PBPX-95503_8AA991B0.ini`.

## References

- [PCSX2 Wiki — Gran Turismo 3](https://wiki.pcsx2.net/Gran_Turismo_3)
- [AeroWidescreen PCSX2-Cheats — GT3 PBPX-95503 widescreen text](https://github.com/AeroWidescreen/PCSX2-Cheats/tree/main/Gran%20Turismo%203/PBPX-95503)
- [PCSX2-patches upstream DB](https://github.com/PCSX2/pcsx2_patches/tree/main/patches)
- [GT3 Retexture Mod v1.0](https://gbatemp.net/threads/gran-turismo-3-scus-97102-texture-pack-finished.633662/)
- PCSX2 GameIndex entry for PBPX-95503: `recommendedBlendingLevel: 3`, `getSkipCount: GSC_PolyphonyDigitalGames` (both auto-applied when `ApplyCompatibilitySettings = true`)
