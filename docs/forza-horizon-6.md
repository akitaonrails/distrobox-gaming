# Forza Horizon 6 (Steam)

**Status (2026-08-17): UNBLOCKED — the driver landed.** The host + box are now on
**NVIDIA 610.57.04** (`nvidia-smi` confirms it live), the release that fixes the
FH6 GPU hang. FH6 should run normally now; ray tracing is a separate question
(retest cautiously — see below).

Steam appid **2483190**. No anti-cheat, ProtonDB Gold. It's a **D3D12/VKD3D**
title → native Vulkan on the RTX 5090 (no DXVK). Manually installed via Steam
(not Ansible-managed); this doc is the record of the working config + the
now-resolved driver blocker.

> **Before launching:** you likely just updated box packages — run
> `distrobox stop gaming`, then relaunch Steam. Proton games hang at the splash
> when run against half-updated libs after a `yay -Syu`. The 610.57.04 bump also
> required refreshing the box's 32-bit nvidia set (`dg_nvidia_lib32`
> 610.43.03→610.57.04, handled by the bootstrap role).

## The blocker (RESOLVED) — NVIDIA driver bug (host)

On host driver **610.43.03**, FH6 hung the GPU under the VKD3D-Proton
**`descriptor_heap`** path. Symptom progression as we chased it:

| Proton | Result |
|---|---|
| Proton Hotfix / GE-Proton11-1 | **black 3D world, HUD renders fine** |
| GE-Proton11-5 (newer VKD3D) | world renders a few seconds → **"Video Card Crash" FHC20** (GPU hang → TDR → device removed) |
| proton-cachyos 20260703 | same GPU hang, stuck sooner |

**Root cause:** [NVIDIA **610.57.04**](https://www.phoronix.com/news/NVIDIA-610.57.04-Linux-Driver)
(released 2026-08-03) explicitly fixes *"a GPU hang in Forza Horizon 6 under the
VKD3D-Proton descriptor heap configuration"* — precisely this. See also the
[CachyOS thread on FH6 black-screen-with-HUD on NVIDIA 610 drivers](https://discuss.cachyos.org/t/forza-horizon-6-black-screen-with-hud-nvidia-610-drivers/31167).
So the black world, the FHC20 crash, and everything in between are one driver
bug — **not** launch flags, graphics settings, Proton choice, Reflex/NVAPI, or
ray tracing (all ruled out by testing).

**Unblocked (2026-08-17):** 610.57.04 landed in Arch stable; host is on
`nvidia-open-dkms 610.57.04-1` / `nvidia-utils 610.57.04-1`, driver `610.57.04`
live per `nvidia-smi`. The box's 32-bit nvidia set was refreshed to match
(`lib32-nvidia-utils 610.57.04`, `/usr/lib32` repaired + stale 610.43.03 pruned)
via the bootstrap role. Just `distrobox stop gaming` before launching so Proton
isn't running against pre-update libs.

## The working config (ready for when the driver lands)

- **Compat tool:** **GE-Proton11-5** (its newer VKD3D got furthest; on the fixed
  driver, Proton Hotfix should also work). Set in `config/config.vdf`
  CompatToolMapping for 2483190.
- **Launch options:** `PULSE_LATENCY_MSEC=60 gamescope -W 3840 -H 2160 -f -- env VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command%`
  (gamescope 4K + RTX 5090 nvidia ICD pin; no DXVK, no VKD3D_CONFIG override,
  NVAPI/Reflex removed — none of those were the issue).
- **Ray tracing — retest cautiously.** RT was a *separate* failure from the
  descriptor-heap hang (the VKD3D DXR path black-screened on 610.43.x). 610.57.04
  may or may not have fixed it too, so try it deliberately: enable it, and if the
  world black-screens, turn it back off. **Gotcha:** a bad RT setting
  (`RTReflectionQuality` / `RTGIQuality`) *persists* and then hangs the game at
  the splash every relaunch. If that happens, clear the RT keys in the config
  (`compatdata/2483190/pfx/.../ForzaHorizon6/LocalStorage_Shared/ForzaUserConfigSelections/UserConfigSelections`)
  before relaunching. Same caution applies to DLSS Frame-Gen.

## Custom Proton management (relevant here)

GE-Proton and proton-cachyos are **manual drops** in
`~/.local/share/Steam/compatibilitytools.d/` — they do **not** auto-update (only
Steam's built-in Proton Hotfix does). Update by downloading the latest tarball
from the [GE-Proton](https://github.com/GloriousEggroll/proton-ge-custom/releases)
/ [CachyOS](https://github.com/CachyOS/proton-cachyos/releases) releases and
extracting into `compatibilitytools.d/`, then restart Steam.
