# Gran Turismo 1 & 2 on DuckStation

User complaint: DuckStation's default **Bilinear** texture filter
washes out GT2's hand-painted car and track art. Fix + best settings
for both GT1 (SCUS-94949) and GT2 (SCUS-94455 Simulation, SCUS-94488
Arcade).

## Global DuckStation defaults (benefit every PS1 game)

Written by `seed_configs` → `duckstation.yml` → `dg_duckstation_settings`:

| Section | Key | Value | Why |
|---|---|---|---|
| GPU | `Renderer` | `Vulkan` | NVIDIA ICD injected by launcher |
| GPU | `ResolutionScale` | `8` | 4K+ on modern GPUs |
| GPU | `TextureFilter` / `SpriteTextureFilter` | `JINC2` | 2025-2026 community consensus — sharp but smooth, preserves PS1 car/sprite detail without Bilinear's wash |
| GPU | `Multisamples` | `2` | 2x MSAA, safe across library |
| GPU | `TrueColor` | `true` | 24-bit output, kills banding |
| GPU | `ScaledDithering` | `true` | Keep dither ON with TrueColor — Project Cerbera 2025 recalibration |
| GPU | `DisableInterlacing` | `true` | Progressive output |
| GPU | `PGXPEnable` / `Culling` / `TextureCorrection` | `true` | Stop texture swimming + geometry wobble |
| GPU | `PGXPDepthBuffer` / `PreserveProjFP` | `true` (global) | Helps most games; GT-family overrides to false (breaks GT skies) |
| CDROM | `LoadImageToRAM` | `true` | Load whole disc image (up to ~700 MB) into RAM on boot. Menu / track transitions become instant, especially on NFS-mounted ROMs |
| CDROM | `ReadSpeedup` / `SeekSpeedup` | `4` | Skip the emulated PS1 CD read/seek delays |
| MemoryCards | `Card1Type` | `PerGameTitle` | Separate virtual memcard per title — GT1 and GT2 saves don't collide |
| TextureReplacements | `EnableTextureReplacements` / `PreloadTextures` | `true` | Ready for drop-in retexture packs when they ship |
| Hacks | `MaxVRAMWriteSplits` | `1024` | Required by the Gran Turismo family per DuckStation wiki |

## Per-game overrides

Deployed via `dg_duckstation_per_game_settings` to
`~/.config/duckstation/gamesettings/<SERIAL>.ini`. Override the global
template when a title-specific tradeoff is needed.

### GT2 (SCUS-94455 Simulation, SCUS-94488 Arcade)

| Key | Override | Why |
|---|---|---|
| `TextureFilter` / `SpriteTextureFilter` | `JINC2` | Core user complaint — sharp without raw-pixel aliasing |
| `PGXPDepthBuffer` / `PreserveProjFP` | **`false`** | Global true breaks GT2's skybox + distant road |
| `WidescreenHack` | **`false`** | DuckStation's built-in hack stretches HUD. Use Silent's 16:9 Widescreen 2.0 cheat from [CookiePLMonster/Console-Cheat-Codes](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo%202) via the DuckStation cheat manager instead — patches the viewport without breaking HUD |
| `Multisamples` | `4` | 4x MSAA, GT2 handles it fine |
| `Console.EnableRAM8MB` | `true` | Pair with Silent's "Use 8 MB RAM for polygon buffers" cheat for full-LOD AI cars with no pop-in |
| `Display.AspectRatio` | `16:9` | Output aspect (not the broken hack). Use in tandem with Silent's widescreen cheat |

### GT1 (SCUS-94949)

Same template minus the GT2-specific 8 MB RAM hack. PGXP tradeoffs
identical.

## Known mods / cheats worth knowing about (2026)

From **CookiePLMonster / Console-Cheat-Codes** (still active repo):

- **16:9 Widescreen 2.0** — viewport patch, 21:9 variant included.
- **60 FPS hack** — restores tire smoke + rear-view.
- **Use 8 MB RAM for polygon buffers** + **Full detail AI cars** —
  pair with `EnableRAM8MB = true`.
- **Fixed Event Generator** — fixes arcade missing tracks.
- **True Endurance**, **Metric Units**, **HUD toggle**, **Replay
  cameras in race**, **BGM switch**.

All ship as **DuckStation cheat codes** — no ISO patching, no
serial/CRC change. Install by dropping the `.cht` file into
`~/.config/duckstation/cheats/<SERIAL>.cht` and enabling via Game
Properties → Cheats in the DuckStation GUI.

**GT2 Combined Disc** (https://github.com/CookiePLMonster/GT2-Combined-Disc)
— merges Arcade + Simulation into one disc. Repacks the ISO (new
CRC), but DuckStation still matches by disc serial so per-game
settings above still apply. Not deployed by this repo — it's
optional.

## Retextures — state of the art April 2026

**No consolidated retexture pack** has shipped for GT2. DuckStation
supports the drop-in system (`textures/SCUS-94455/` with hash-named
PNGs; `EnableTextureReplacements` already on globally so you're
ready), but no community pack is published as of April 2026 — only
WIP on [RetroGameTalk Personal Remasters thread](https://retrogametalk.com/threads/my-texture-pack-projects-personal-remasters-for-duckstation-pcsx2.15996/)
and YouTube demos.

For GT3 (different game): the ["Finished" pack on GBAtemp](https://gbatemp.net/threads/gran-turismo-3-scus-97102-texture-pack-finished.633662/).

If you want to dump-and-replace yourself, flip DuckStation's
**Advanced → Dump Replaceable Textures** and play through — PNG
dumps go to `textures/SCUS-94455/dumps/`. Rename/edit/move to
`replacements/` to apply.

## ISO notes

Current setup points at the `GT2 (Simulation Mode) v1.2 patched` +
`GT2 Arcade` m3u under `EmuDeck/roms/psx/Gran Turismo 2/`. GT1 USA
Rev 1 was copied from `ROMS_FINAL/psx/` into the same roms/psx dir
for DuckStation to discover.

## References

- [Project Cerbera — DuckStation for GT2 (updated 2025-11-07)](https://projectcerbera.com/gt/2/duckstation/)
- [Silent's Blog — GT2 mods index](https://silentsblog.com/mods/gran-turismo-2/)
- [CookiePLMonster Console-Cheat-Codes](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo%202)
- [WornOutWill — Best DuckStation Settings for PS1 Emulation (2026-03-13)](https://www.wornoutwill.com/2026/03/the-best-duckstation-settings-for-ps1.html)
- [PulseGeek — DuckStation Texture Filtering and Upscaling (2026-03-05)](https://pulsegeek.com/articles/best-duckstation-texture-filtering-and-upscaling/)
- [Nenkai GT Modding Hub — PS1/GT2 tooling](https://nenkai.github.io/gt-modding-hub/ps1/gt2/tools/)
- [DuckStation Wiki — Texture Replacement](https://github.com/stenzek/duckstation/wiki/Texture-Replacement)
