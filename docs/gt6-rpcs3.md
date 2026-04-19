# Gran Turismo 6 on RPCS3

Captures the setup that actually works on this repo's distrobox +
April-2026 RPCS3 + NVIDIA proprietary driver on a modern GPU.

## Version ceiling

**Install game updates only up to v1.05.** v1.06 and later regress
under RPCS3:

- Black track and car surfaces (HUD still renders)
- Menu glitches
- Makes the long-running "black reflections" bug
  ([issue #17453](https://github.com/RPCS3/rpcs3/issues/17453), still
  open April 2026) worse

The per-title cap lives in
`ansible/roles/scripts_in_box/files/extract_ps3_dlc.py`
(`PER_GAME_MAX_VERSION`). `install_dlcs` role extracts PKGs 1.02 → 1.05
and skips everything past, logging each skipped PKG with the cap
reason. Adding new capped titles is a one-line entry in that dict.

Confirmed symptom on disc-only v1.03: race-finish freeze with results
music looping forever. Root cause is RPCS3's stubbed `cellMusic`
(`cellMusicInitialize2` / `cellMusicGetPlaybackStatus2` return the
same status indefinitely — the game polls waiting for a state change
the stub never produces). v1.05 changes the results flow enough that
the freeze no longer triggers.

Note: LLE-loading `libsysutil_music.sprx` via `Load libraries` does
NOT work here — RPCS3 logs `sys_prx: Ignored module` and routes to
HLE regardless. The `cellMusic` HLE is hard-wired as the default
implementation; upstream fix is the only path.

## PKG installation pitfalls

Game update PKGs must land in
`/dev_hdd0/game/<TITLE_ID>/` so RPCS3 can overlay them on the base.
The legacy extractor unconditionally used the PKG's `content_id`
(e.g. `EP9001-BCES01893_00-0000000000000000`), which is the DLC
convention — patches landed there got read as unrelated DLC and the
game ran at disc version forever
(`SYS: Version: APP_VER=01.00 VERSION=01.03`).

The current extractor detects patch PKGs via the filename
`-A<XX>-V<XX>-` pattern; for those it derives the title ID from the
content ID (`^[A-Z0-9]+-([A-Z]{4}\d{5})_`) and uses the TID as the
destination. Pure DLC PKGs still use `content_id`.

## Per-game RPCS3 config

Shipped as `config_BCES01893.yml` (plus regional aliases
`BCUS98296`, `BCAS25018`, `BCES01977`, `BCJS37016`) by
`rpcs3_per_game_configs`. Deltas from RPCS3 defaults, with reasons:

| Section | Key | Value | Why |
|---|---|---|---|
| Core | `SPU Block Size` | `Mega` | Standard GT6 tune; `Safe` regressed perf |
| Core | `SPU XFloat Accuracy` | `Accurate` | ~10% perf gain; required for correct physics on GT6 per upstream tests |
| Core | `Preferred SPU Threads` | `2` | Best on modern CPUs for GT6 |
| Core | `Enable TSX` | `Disabled` | Avoids Intel TSX issues on recent firmware |
| Core | `Accurate RSX reservation access` | `true` | Correct physics / sim math |
| Core | `Accurate xfloat`, `Accurate DFMA` | `true` | Same |
| Core | `Load libraries` | *(attempted, ignored by RPCS3)* | Documented in-file. Doesn't help but harmless |
| Video | `Renderer` | `Vulkan` | — |
| Video | `Write Color Buffers` | `false` | Mirror stays black on NVIDIA — **deliberate tradeoff**. Flipping it on forces render-target downscale to native (720p) even at 4K internal. HUD stays sharp, the 3D scene blurs. Pick sharp 4K + black mirror, or 720p + working mirror |
| Video | `Read Color Buffers` | `false` | Same tradeoff as WCB |
| Video | `Resolution Scale` | `300` | 4K scale on a modern GPU |
| Video | `Resolution Scale Threshold` | `16 × 16` | Skip upscale for tiny RTs |
| Video | `Anisotropic Filter` | `16` | Default hot |
| Video | `Multithreaded RSX` | `true` | Perf |
| Video | `Driver Wake-Up Delay` | `1` | Reduces NVIDIA stutter |
| Video | `VBlank Rate` | `60` | Normal |
| Video | `Force CPU Blit` | `true` | **Mandatory** — stops the in-race screen flicker. Confirmed mandatory via a live session where the flicker disappeared the instant this was actually loaded (see filename-convention trap below) |
| Video | `Disable ZCull Occlusion Queries` | `true` | Speeds up GT6's RSX path |
| Video | `Shader Mode` | *(tried `Async with Shader Interpreter`, did not apply)* | Intended to eliminate garage/shop car-preview stalls during first-view shader compiles. RPCS3 logs the value as `Async Recompiler (multi-threaded)` regardless — exact enum spelling still unconfirmed. Shaders still compile on first view per car model, stutter fades as the cache populates |
| Audio | `Enable Time Stretching` | `true` | Smooths menu audio dips |

## Filename-convention trap

RPCS3 loads per-game configs from
`custom_configs/config_<SERIAL>.yml`. The `config_` prefix is
mandatory. Files named `<SERIAL>_config.yml` (suffix) are silently
ignored. `generate_rpcs3_configs.py` used to produce the suffix form
for months, so no custom config ever actually loaded; the game was
running on global GUI settings. Fixed as of commit `c4d8916` — if you
see a similar symptom where runtime behavior doesn't match the
deployed YAML, first confirm the filename is prefix-form.

## Mirror status

As of April 2026 the rear-view mirror is **permanently black on this
setup**. The only configuration that makes it render is Write Color
Buffers `true`, which trades away the 4K internal resolution (see
table above). Issue #17453 has been open since August 2024 with no
upstream fix. Not something we can tune around.

## References

- [RPCS3 wiki: Gran Turismo 6](https://wiki.rpcs3.net/index.php?title=Gran_Turismo_6)
- [Forum thread BCES01893](https://forums.rpcs3.net/thread-187131.html)
- [GT Modding Hub setup guide](https://nenkai.github.io/gt-modding-hub/ps3/other/rpcs3_setup/)
- [Issue #17453 — black reflections (open)](https://github.com/RPCS3/rpcs3/issues/17453)
- [Issue #15841 — NVIDIA perf (open)](https://github.com/RPCS3/rpcs3/issues/15841)
- [PR #17135 — virtual Logitech G27 for Linux](https://github.com/RPCS3/rpcs3/pull/17135)
