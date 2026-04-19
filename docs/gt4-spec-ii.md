# Gran Turismo 4 Spec II on PCSX2

Spec II is a community-patched GT4 built on the USA **Online Public Beta**
disc (not retail), with 480p + GT3 chase cam + trigger sensitivity + real
widescreen baked into the ELF. It reports as **serial `SCUS-97436`** with
**CRC `4CE521F2`** under PCSX2 as of Spec II v1.04. Both values differ
from vanilla USA retail (`SCUS-97328` / `77E61C8A`), which is why
vanilla-targeted pnach files and per-serial texture packs silently do
nothing under Spec II.

## What loads under which serial

| Asset | vanilla USA | Spec II |
|---|---|---|
| HD HUD & UI pack (Silentwarior112) | `textures/SCUS-97328/replacements/` | `textures/SCUS-97436/replacements/` |
| Retexture cars/tracks pack | same path above | same path above (per-texture hashes are version-agnostic) |
| PCSX2 widescreen cheats DB | matches SCUS-97328_77E61C8A | no 4CE521F2 entry — must ship renamed |
| Silent's trigger / GT3 cam pnach | applies (SCUS-97328_77E61C8A_*.pnach) | no-op (wrong CRC); redundant anyway since Spec II has these built in |

The HD HUD pack's per-texture hashes are preserved across vanilla and
Spec II, so the same pack files work for both — it's just the **serial
directory** PCSX2 scans that changes. We symlink the same pack dirs
under both `SCUS-97328/` and `SCUS-97436/` so both ISOs pick up the
pack without duplicating 8+ GB of source.

## Widescreen setup

Spec II's ELF has the same code layout as the Online Public Beta base
(`SCUS-97436_32A1C752`), so the widescreen patch from the PCSX2
bundled DB applies — but PCSX2 filename-matches pnach to the running
CRC, and `32A1C752 ≠ 4CE521F2`. Fix: download the upstream pnach,
rename to Spec II's CRC on deploy.

Config for `SCUS-97436` (in `ansible/group_vars/all/pcsx2.yml`),
deployed to `~/.config/PCSX2/gamesettings/SCUS-97436_4CE521F2.ini`:

- `AspectRatio = 16:9` — **not** `Widescreen (16:9)`. PCSX2 logs
  `Unrecognized value 'Widescreen (16:9)'` and falls back to 4:3, which
  is why the in-game 16:9 toggle previously produced squished output.
  The GUI label differs from the INI value — the actual enum is the
  terse form (`16:9`, `4:3`, `Auto 4:3/3:2`, `Stretch`).
- `EnableWideScreenPatches = true` — PCSX2 loads any matching
  `<SERIAL>_<CRC>.pnach` from `~/.config/PCSX2/patches/` when this is
  on.
- `MaxAnisotropy = 16`, `TextureFiltering = 2`, `AccurateBlendingUnit = Basic`
- Texture replacement flags enabled per-game.

### Deinterlace + color grading (added after live-test tuning)

- `deinterlace_mode = 8` — Adaptive TFF. Spec II's baked-in 480p and
  the Online-Public-Beta widescreen pnach's `[No-Interlacing]` code
  patch (which forces Autoboot in 480p) together confuse PCSX2's
  interlaced/progressive auto-detection. Symptoms before this setting:
  subtle flicker during gameplay and clearly ghosted double-image
  when paused. Adaptive TFF deinterlaces intelligently when needed
  and passes progressive content through untouched. Change also
  benefits you if you toggle the in-game 480p option.
- `ShadeBoost = true` — enables PCSX2's built-in ShadeBoost post-
  process shader.
- `ShadeBoost_Saturation = 60` (+10 from default 50) — Polyphony
  ground GT4 flatter than GT3 because GT4 targeted 480p LCDs.
  Saturation +10 matches GT3's punchier look.
- `ShadeBoost_Brightness = 53` (+3) — lifts shadow detail slightly
  without blowing out highlights.
- `ShadeBoost_Contrast = 52` (+2) — keeps shadow depth from
  washing out with the brightness lift.

### PCSX2 global AA chain (applies to all games)

Already set in `dg_pcsx2_settings`:

- `upscale_multiplier = 4.0` — 4× SSAA is the primary AA contributor.
- `MaxAnisotropy = 16` / `TextureFiltering = 2` / `mipmap = 1` — full
  texture filter chain.
- `TriFilter = -1` (Automatic) — forced values cause PCSX2 to warn
  and break rendering in some games.
- `fxaa = true` — post-process FXAA catches sub-pixel aliasing that
  the integer upscale misses (thin HUD lines, distant sprite edges).
  ~1-2% perf cost.
- `pcrtc_antiblur = true` — turns off PCSX2's PCRTC-emulation blur
  (which exists to match CRT scanlines). Sharper output now that
  we're on progressive display + 4× upscale.

Patch deployment:

- `dg_pcsx2_patch_url_renames` list supports `{url, dest_name}` entries
  so we can download a pnach at one CRC and save under another.
- Widescreen pnach entry:
  ```yaml
  - url: https://raw.githubusercontent.com/PCSX2/pcsx2_patches/main/patches/SCUS-97436_32A1C752.pnach
    dest_name: SCUS-97436_4CE521F2.pnach
  ```

## Don't bother with

- **Silent's vanilla-CRC camera/trigger pnach** — Spec II has GT3
  chase cam + adjusted triggers built in (Spec II FAQ Q9).
- **`EnableWideScreenPatches = false`** — tried this thinking the
  built-in widescreen handled everything. It doesn't. The built-in
  16:9 toggle in the game's Display Settings actually *relies on* the
  shipped widescreen pnach to correct text aspect ratios; without the
  pnach, the game renders 16:9 geometry but text stays 4:3-stretched,
  which visually reads as "squished".

## Known cosmetic caveat

Per [GBAtemp Spec II HD texture thread](https://gbatemp.net/threads/gran-turismo-4-spec-ii-pcsx2-hd-texture.662899/),
Spec II horizontally squishes some legacy UI textures so they render
correct in 16:9 — this makes the HD HUD pack's brand logos look
narrow in certain menus. Cosmetic only, no Spec-II-aware HUD repack
exists yet (April 2026). In-race HUD is unaffected.

## References

- [Spec II install guide](https://www.theadmiester.co.uk/specii/install.html)
- [Spec II FAQ](https://www.theadmiester.co.uk/specii/faq.html)
- [PCSX2 widescreen pnach for SCUS-97436](https://raw.githubusercontent.com/PCSX2/pcsx2_patches/main/patches/SCUS-97436_32A1C752.pnach)
- [Silent's blog GT4](https://silentsblog.com/mods/gran-turismo-4/)
- [GTPlanet HD HUD thread 417873](https://www.gtplanet.net/forum/threads/gt4-hd-hud-and-user-interface-texture-pack-for-pcsx2.417873/)
- [GTPlanet Retexture thread 408852](https://www.gtplanet.net/forum/threads/gran-turismo-4-retexture-mod-v3-0-4.408852/)
