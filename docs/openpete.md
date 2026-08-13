# OpenPete (Spyro the Dragon PC port) — PARKED (blocked on disc image)

**Status: parked 2026-08-13.** Fully scoped and ready to install, but blocked
on a disc-image hash mismatch that only the user can resolve (see Blocker).

## What it is

[OpenPete](https://openpete.com/) is a **native PC port of *Spyro the Dragon*
(PS1, NTSC-U SCUS-94228)** — static recompilation + byte-matching decompilation
(built on `spyro-1`, `PSXRecomp`, `PsyCross`) with a custom **Vulkan** renderer
(widescreen, high FPS, HD textures). Same family as our Ship of Harkinian /
Starship / F-Zero X recomp ports. License: PolyForm Noncommercial 1.0.0. Ships
**no game data** — you supply your own disc image, verified by checksum.

## Linux status (why it's Wine, not native)

- Platforms: **Windows x86-64 (v0.1.2, available)**, Linux "coming soon",
  macOS planned.
- "Linux builds/runs from source already, packaged download follows shortly" —
  **but the source is not public yet.** So there is currently **no Linux binary
  and no buildable source**. The only download is a **Windows binary** (117 MB,
  MEGA): `mega.nz/file/du4UhT4R#uT7JEW_Q2qGS1RRzNT6jlIWFl43RkFhn6Kn2UK4qFgo`.
- Plan was therefore **Windows build under Wine** — it's a *native-Vulkan*
  Windows app, so under Wine its Vulkan calls pass straight to the RTX 5090 (no
  DXVK needed), gamescope + DP-1 + nvidia ICD pin like our other Wine games.
  Revisit for a native build once the Linux package/source drops.

## Blocker — disc image hash mismatch

OpenPete is **byte-matched to one exact pressing** and verifies strictly:

> Only a `.bin/.cue` with **SHA1 `1e08ae8df01acf7ee5d9cb6931b5f8c1bc905fcb`**
> or **SHA256 `95f03abf97c9ff0b2a64888ed7dbbb4b59a7b4363cf188cd0a562b95cfd4809f`**
> is supported (Redump disc [#576](http://redump.org/disc/576/), SCUS-94228).

The user's Spyro USA dumps do **not** match (verified 2026-08-13):

| Source | SHA1 |
|---|---|
| `psx/Spyro the Dragon (USA).chd` (extracted) | `cf3ce6bedeb89dfbc40990336180f3b9b0f40d9f` |
| `psx-usa/Spyro the Dragon (USA)/…bin` | `cf3ce6…` (same) |
| a 3rd re-download (`psx/Spyro the Dragon (USA)/`) | `cf3ce6…` (same) |
| **OpenPete requires** | **`1e08ae8…`** |

All three are the **ubiquitous `cf3ce6` dump** (what every ROM site serves) —
single-track `MODE2/2352`, SHA1 **and** SHA256 both mismatch, so no track/format
ambiguity. It's a **different pressing/dump** than OpenPete's target (likely a
Greatest Hits reprint or a non-Redump dump). A different byte-exact image cannot
be converted from another — only the matching disc produces `1e08ae8`.

## To unblock (needs the physical disc)

**Re-dump the physical Spyro disc with [Redumper](https://github.com/superg/redumper)**
(Redump-standard). If the physical copy is the pressing OpenPete matched to, it
yields the `1e08ae8` image; if it's a different pressing, even a perfect re-dump
won't match and OpenPete cannot run on that copy. Once a matching image exists,
the rest of the install (Wine prefix, native-Vulkan → RTX 5090, gamescope/DP-1
launcher, desktop entry, Ansible role) is straightforward and was already
scoped — finish in one pass.
