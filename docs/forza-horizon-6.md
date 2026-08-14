# Forza Horizon 6 (Steam) — waiting on NVIDIA 610.57.04

**Status (2026-08-13): configured, but BLOCKED on an NVIDIA driver bug.**
FH6 is set up and *almost* runs; it's held back entirely by a host GPU-driver
bug that is already fixed upstream but not yet in Arch stable. **Plan: wait for
the driver update** — no further game-side config will help.

Steam appid **2483190**. No anti-cheat, ProtonDB Gold. It's a **D3D12/VKD3D**
title → native Vulkan on the RTX 5090 (no DXVK). Manually installed via Steam
(not Ansible-managed); this doc is the record of the working config + blocker.

## The blocker — NVIDIA driver bug (host)

On host driver **610.43.03**, FH6 hangs the GPU under the VKD3D-Proton
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

**To unblock:** update the host to **≥ 610.57.04**, reboot, launch FH6.
- 610.57.04 was not yet in the Arch repos (host on `nvidia-open-dkms 610.43.03-3`,
  `checkupdates` empty). Wait for it to land, then `omarchy update` (pacman `-Syu`)
  + **reboot**. An AUR beta is the impatient path but a host driver swap
  (DKMS + reboot) risks the display — not worth it when the stable pkg is days out.

## The working config (ready for when the driver lands)

- **Compat tool:** **GE-Proton11-5** (its newer VKD3D got furthest; on the fixed
  driver, Proton Hotfix should also work). Set in `config/config.vdf`
  CompatToolMapping for 2483190.
- **Launch options:** `PULSE_LATENCY_MSEC=60 gamescope -W 3840 -H 2160 -f -- env VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command%`
  (gamescope 4K + RTX 5090 nvidia ICD pin; no DXVK, no VKD3D_CONFIG override,
  NVAPI/Reflex removed — none of those were the issue).
- **⚠️ Leave ray tracing OFF** regardless — the VKD3D DXR path is separately
  broken and black-screens (see the memory note); it corrupts state into a
  splash-hang loop.

## Custom Proton management (relevant here)

GE-Proton and proton-cachyos are **manual drops** in
`~/.local/share/Steam/compatibilitytools.d/` — they do **not** auto-update (only
Steam's built-in Proton Hotfix does). Update by downloading the latest tarball
from the [GE-Proton](https://github.com/GloriousEggroll/proton-ge-custom/releases)
/ [CachyOS](https://github.com/CachyOS/proton-cachyos/releases) releases and
extracting into `compatibilitytools.d/`, then restart Steam.
