# Gran Turismo 5 on RPCS3

Short doc — GT5 (BCUS98114 US, BCES00569 EU) is **already playable**
on current RPCS3 under the repo's existing per-game config.
Documented here: the two specific visual tweaks worth trying for the
classic "shadow dither" + "shiny-specular jags" artifacts.

## If you see dither in dark/shadow areas

PS3 GT5 renders internally in HDR then tonemaps to 8-bit; on certain
display / driver combinations the tonemap quantization shows as
temporal dither in dark interior shots, night tracks, or deep
shadows. RPCS3 can't eliminate it fully (it's what the PS3 actually
does), but two settings reduce it noticeably:

| Setting | Change | Why |
|---|---|---|
| **GPU → Shader Precision** | `High` → **`Ultra`** | GT5's tonemap / postprocess shaders use 16-bit float intermediates. Bumping to Ultra uses 32-bit throughout the pipeline — the extra precision eats the quantization banding. |
| **GPU → Force High Precision Z buffer** | `false` → **`true`** | Dark distant geometry also loses precision in the depth pass; forcing 32-bit Z rebuilds that detail. |
| **Advanced → SPU XFloat Accuracy** | `Approximate` → **`Accurate`** | Physics + camera math at higher precision — often resolves flickering in very dark specular surfaces too. Paired cost ~5% fps on current CPUs. |

Apply via RPCS3 GUI → right-click GT5 → Create Custom Configuration
(or edit the existing one) → GPU / Advanced tabs.

## If you see jaggy specular highlights

The "shiny specs jagging" is classic sub-pixel aliasing on
high-contrast highlights — PS3 GT5 renders at 1280×1080 internally,
and even with `Resolution Scale: 200%` you're at 2560×2160, which
still aliases on near-mirror reflections.

| Setting | Change | Why |
|---|---|---|
| **GPU → Resolution Scale** | `200` → **`300`** (or as high as your GPU can sustain 60 fps at) | Supersampling beyond display resolution eats specular aliasing. On an RTX 5090 / 4090-class GPU, 300% holds 60 fps in-race comfortably. |
| **GPU → Anisotropic Filter Override** | already 16 — leave it | Helps texture shimmer at glancing angles; already maxed on your config. |
| **GPU → Output Scaling Mode** | `Bilinear` → **`FidelityFX Super Resolution`** *or* `Nearest` | At 300% internal output downscaling to your monitor, FSR downsample path preserves edges better than bilinear, which blurs the antialiased pixels you paid for. |
| **GPU Vulkan → Asynchronous Texture Streaming** | already `true` — leave it | Keeps stutter down when the texture cache misses at 300% scale. |

## What's already in your config (don't change)

- `Write Color Buffers: false` / `Read Color Buffers: false` — NVIDIA
  tradeoff. Enabling would fix the black rear-view mirror but risks
  `VK_ERROR_DEVICE_LOST` and the "black reflections" regression that
  plagues GT6 v1.06+. Same family, same bug class. Not worth it.
- `Strict Rendering Mode: false` — helps. Don't flip.
- `Multithreaded RSX: true` — perf. Keep.
- `Accurate RSX reservation access: true`, `Accurate DFMA: true` —
  correct physics math. Keep.

## If you do a fresh setup

The Ansible `rpcs3_per_game_configs` role writes a stronger default
for BCUS98114 that bakes the above into the initial per-game YAML —
Resolution Scale 300, Shader Precision Ultra, Force High Precision Z,
SPU XFloat Accurate, plus the GT-family safety rails (WCB/RCB off,
SPU Block Size Mega, Preferred SPU Threads 2).

Running the role against an already-tuned install is a no-op unless
`dg_rpcs3_force_overwrite=true` is passed — so your GUI adjustments
won't be clobbered by re-running the playbook.

## References

- [Project Cerbera — GT5 on RPCS3](https://projectcerbera.com/gt/5/rpcs3/)
- [RPCS3 Wiki — Gran Turismo 5](https://wiki.rpcs3.net/index.php?title=Gran_Turismo_5)
- [Issue #17453 — WCB-induced black reflections (whole GT family)](https://github.com/RPCS3/rpcs3/issues/17453)
