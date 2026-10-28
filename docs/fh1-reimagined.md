# Forza Horizon 1: ReImagined

[FH1-ReImagined/ForzaHorizon1-ReImagined](https://github.com/FH1-ReImagined/ForzaHorizon1-ReImagined)
v0.2.0 is a **native Linux static recompilation** (ReXGlue SDK, same approach
as hl360-forza4 FM4) of the 2012 Xbox 360 *Forza Horizon*. It is the only Forza
game not covered by Azimuth (FH2/3, FM5/6) or hl360 (FM4), and the only one of
those that runs **natively on Linux with Vulkan** — no Wine, no Proton.

## What it adds over the original

- **Online through Forza Live**: free roam (up to 8 players), leaderboards,
  Rivals, co-op campaign, car clubs. Public server, self-hosted, or offline.
- **Frame rate 30 → 240 fps**; the original's 30 fps is the default.
- **AMD FSR 1/3, CAS, SMAA, NVIDIA DLSS/DLAA**, HDR, ultrawide.
- **HD texture packs** + a built-in AI upscaler ("Make HD pack").
- **Mods** through the launcher's Mods page.
- **Controller**: gamepad, keyboard, or wheel with FFB (G29/G920/G923 tested).
- Title Update 4 and all 23 DLC packages supported (each needs its own dump).

## Install

```sh
ansible-playbook install-fh1-reimagined.yml    # or: site.yml --tags fh1r
```

The role installs the launcher (a PySide6 app) and its build prerequisites.
**The game itself is built interactively** by the launcher from your own disc:

1. Launch **Forza Horizon 1 · ReImagined** from Walker.
2. **Setup → Game files** → pick the Forza Horizon ISO
   (`ROMS_FINAL/xbox360/Forza Horizon (USA) …iso`).
3. **Build** — the launcher extracts + fingerprints `default.xex` (title
   `4D5309C9`, version `0.0.0.7`, media id `2B7A1346`; any printing with the
   same code is accepted), generates the recompilation and compiles it
   (~5 min on this box).
4. **Prebuild shaders** (optional, recommended on the RTX 5090).
5. **Play**.

Title Update 4 (Horizon Rally + 1000 Club) and DLC are optional; no TU4 or
DLC package is in the library yet.

## Disc compatibility

The USA printing is accepted by code fingerprint, not just media ID. The
library's `Forza Horizon (USA) (En,Ja,Fr,De,Es,It,Pt,Zh,Pl,Ru).iso`
(8,738,846,720 bytes) is the only FH1 image present.

## Known NVIDIA issues

Stutter with warm shader cache ([#49](https://github.com/FH1-ReImagined/ForzaHorizon1-ReImagined/issues/49)),
green texture glitches ([#106](https://github.com/FH1-ReImagined/ForzaHorizon1-ReImagined/issues/106)),
flicker at render scale 3 ([#47](https://github.com/FH1-ReImagined/ForzaHorizon1-ReImagined/issues/47)).
Shader prebuild (step 4) mitigates the first. Vulkan is the default and
recommended graphics API.

## Maintenance

The tarball stays in `PC/releases/` for rebuilds. The launcher self-updates
(**About → Launcher updates**); the Ansible pin tracks the launcher version
only — the game build is produced locally from the disc and never downloaded.
