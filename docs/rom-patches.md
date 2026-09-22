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
| **F-Zero Community Grand Prix P1/P2/P3 (CGP)** — 55 tracks (the 15 main, both BS leagues, 30 new), improved CPU, free boosting from lap 2, LEGEND difficulty. Three packs differing only in vehicle roster (see the group_vars comment); all three coexist. **MSU-1 audio** — see below. | headerless No-Intro `F-Zero (USA).sfc` — `d3efd32b…` (CRC `aa0e31de`), from `roms/snes/originals/` (the 1 MiB `roms/snes/F-Zero (USA).sfc` is a different dump — don't use it). | `F-Zero Community Grand Prix P1 (CGP).sfc` (`be5fc510…`), `…P2…` (`bf288290…`), `…P3…` (`b4dc5f38…`), each 2.5 MiB |

### F-Zero CGP — MSU-1 audio sidecars

The CGP packs ship MSU-1 CD-audio (61 `.pcm` tracks + a `.msu` marker per pack,
~1.1 GB each; zips + extracted folders archived at
`ROMS_FINAL/snes/romhack-patches/F-Zero CGP P*/`). MSU-1 emulators find audio
**by ROM basename**, so the entries set `msu_src` + `msu_prefix` and the role
**hardlinks** every sidecar next to the patched ROM, renamed from the pack
prefix (`F-Zero CGP P1-7.pcm`) to the ROM basename
(`F-Zero Community Grand Prix P1 (CGP)-7.pcm`). Hardlinks cost no extra space
(same NAS filesystem) and survive either path being moved/deleted. Verified
2026-09-22: RetroArch Snes9x reports `ROM+RAM+BAT+MSU-1` on the P1 ROM (music
needs an MSU-1 core — bsnes/Snes9x; on other cores the game plays silent).
Reverting (`dg_rom_patches_revert=true`) removes the sidecars too.

The archives also ship JP/Europe patch variants; only the International (EN/US)
patches are committed, matching the box's dumps. The two F-Zero hacks are kept as
separate ROMs alongside the untouched `F-Zero - Maximum Velocity` original, so
all three coexist in the library.

### Return to Yoshi's Island — emulator caveat

This is a **very heavy Kaze Emanuar hack** with custom rendering. Per the
author, **Mupen64Plus-Next won't boot it**; **ParaLLEl** only "kind of works,
NEWEST version only, with parallel RDP + parallel CPU core". On the box's
RetroArch **ParaLLEl-N64** core (Vulkan parallel-RDP + LLE ParaLLEl-RSP — the
seeded default for heavy SM64 hacks) it boots and the game logic runs, **but the
3-D world renders black**: RetroArch's bundled parallel-rdp is older than the
"newest only" the hack requires.

**Solved** by the **standalone Parallel Launcher** (`install_parallel_launcher`,
see [parallel-launcher.md](parallel-launcher.md)) — its own newer RetroArch
AppImage + the newest ParaLLEl core render RTYI Demo 2 correctly on the RTX. In
ES-DE, pick the **"Parallel Launcher (standalone)"** alt-emulator for this game
(not Mupen or the RetroArch ParaLLEl core).

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
3. **MSU-1 hacks (SNES CD-audio packs):** also set `msu_src` (directory with
   the extracted pack) and `msu_prefix` (the pack's original file prefix). The
   role hardlinks every `<prefix>.msu` / `<prefix>-*.pcm` beside the patched
   ROM, renamed to the ROM's basename — MSU-1 pairs audio by filename, so if
   you rename `out`, the sidecars follow automatically.
4. Run the playbook. The base and output are both hash-checked.
