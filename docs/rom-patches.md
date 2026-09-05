# ROM romhack patches (`install_rom_patches`)

Data-driven patcher for GBA/console romhacks distributed as **IPS** or **BPS**
patches. Each entry hard-patches a hash-verified base ROM and writes a finished
ROM into a library the emulators already scan (EmuDeck `roms/`, `roms_mid/…`),
so it plays with nothing to load at runtime.

The applier asserts the **base** SHA-1 before touching a byte and the **output**
SHA-1 after, so a wrong-region/revision base or a corrupt patch fails loudly
instead of producing a broken ROM. It is chosen by the patch extension:
`files/apply_ips.py` for IPS; `files/apply_bps.py` for BPS (which additionally
verifies the format's built-in source/target/patch CRC32s). The role is
idempotent: a patch runs only when its output is missing or not the expected
build.

**Small patches** live committed in `roles/install_rom_patches/files/`. A
**large** patch (a multi-MB BPS is effectively the whole hacked ROM) is instead
**NAS-staged** and referenced by an absolute `patch_src` on the entry, so it
never bloats the repo — `out_sha1` plus the BPS's own CRC32 still guarantee a
correct result.

> This role writes each hack to a **separate** hardpatched ROM and leaves the
> base untouched. For the manual/one-off flow — xdelta hacks, in-place swaps
> that reuse the original's ES-DE entry and artwork, recovering a pristine base
> from NAS snapshots, and save-compatibility caveats — see
> [rom-hack-patching.md](rom-hack-patching.md).

## Current patches (`dg_rom_patches`)

| Hack | Base ROM (SHA-1) | Output |
| --- | --- | --- |
| **Donkey Kong Country (GBA) SNES colour restoration** — marc_max v1.1, re-palettes the washed-out GBA port toward the SNES original (in-game palettes only; minigame/map screens untouched). | `Donkey Kong Country (Europe) (En,Fr,De,Es,It).gba` — `8995f0be…`. **EU only**; the USA dump doesn't match. | `…(SNES Restoration).gba` (`005b5571…`) |
| **Final Fight ONE: Arcade Edition v3.0 (USA)** — restores the arcade roster/moves over the GBA port. | `Final Fight One (USA).gba` — No-Intro `17918e12…` (CRC `052c9997`). | `Final Fight One - Arcade Edition (USA) [v3.0].gba` (`e189ae8a…`) |
| **F-Zero: Vintage Velocity I (EN v2.1)** — remakes the 15 SNES courses in the Maximum Velocity engine. | `F-Zero - Maximum Velocity (USA, Europe).gba` — `8a08e29e…` (CRC `bd5e9798`). | `F-Zero - Vintage Velocity I (v2.1).gba` (`40aab9df…`, expands to 8 MiB) |
| **F-Zero: Vintage Velocity Ace (EN v3.0)** — F-Zero 99 course layouts + larger Mute City tracks. | same Maximum Velocity base (`8a08e29e…`). | `F-Zero - Vintage Velocity Ace (v3.0).gba` (`962f357d…`, expands to 8 MiB) |
| **Super Metroid Redux (v1.5)** — large overhaul (map system, Project Base features, bugfixes). Main IPS only; the zip's optional add-on patches are not applied. | headerless No-Intro `Super Metroid (Japan, USA) (En,Ja).sfc` — `da957f0d…` (CRC `d63ed5f8`). | `Super Metroid Redux.sfc` (`0f4133f2…`, matches the author's prebuilt Redux ROM) |
| **Return to Yoshi's Island — Demo 2 (Kaze Emanuar, N64)** — a **BPS** patch (NAS-staged `patch_src`), output into `roms_mid/n64` alongside the stock Mario ROMs. **HEAVY hack — emulator-picky** (see below). | `Super Mario 64 (USA) [!]` `.z64` — `9bef1128…` (read from the SM64 decomp-port baserom, the only verified copy on the box; never modified). | `Return to Yoshi's Island (Demo 2 v1.06).z64` (`4e91e237…`) |

The archives also ship JP/Europe patch variants; only the International (EN/US)
patches are committed, matching the box's dumps. The two F-Zero hacks are kept as
separate ROMs alongside the untouched `F-Zero - Maximum Velocity` original, so
all three coexist in the library.

### Return to Yoshi's Island — emulator caveat

This is a **very heavy Kaze Emanuar hack** with custom rendering. Per the
author, **Mupen64Plus-Next won't boot it**; **ParaLLEl** only "kind of works,
NEWEST version only, with parallel RDP + parallel CPU core". On the box's
RetroArch **ParaLLEl-N64** core (Vulkan parallel-RDP + LLE ParaLLEl-RSP — already
the seeded default for heavy SM64 hacks) it **boots and runs (the HUD renders and
the game logic ticks), but the 3-D world renders black**: RetroArch's bundled
parallel-rdp is older than the "newest only" the hack requires. The confirmed
fully-working setups are **Project64 + ANGLE GlideN64 with "Enable Fragment Depth
Write"** (Windows/Wine) or the **standalone ParaLLEl Launcher** with the newest
parallel-rdp (native Linux) — neither is installed here yet. So the ROM is staged
and hash-verified in the library, but a playable renderer is still pending.

## Install / revert

```sh
cd ansible
ansible-playbook install-rom-patches.yml            # or: site.yml --tags rom_patches
ansible-playbook install-rom-patches.yml -e dg_rom_patches_revert=true   # remove patched ROMs
```

Reverting deletes only the patched outputs; base/original dumps on the NAS are
untouched. After a run, rescan the GBA gamelist in ES-DE to pick up new entries.

## Adding a hack

1. Drop the patch into `roles/install_rom_patches/files/` (IPS **or** BPS; give
   it a clear name). If it is large (multi-MB BPS), stage it on the NAS instead
   and point `patch_src` at it.
2. Append an entry to `dg_rom_patches` in `group_vars/all/rom_patches.yml`:
   `name`, `base` (path), `base_sha1`, `ips` (filename — its extension picks the
   IPS vs BPS applier), optional `patch_src` (absolute path for a NAS-staged
   patch), `out` (path), `out_sha1`. Get `out_sha1` by applying the patch once
   and hashing the result.
3. Run the playbook. The base and output are both hash-checked.
