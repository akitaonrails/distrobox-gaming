# ROM romhack patches (`install_rom_patches`)

Data-driven patcher for GBA/console romhacks distributed as **IPS** patches. Each
entry hard-patches a hash-verified base ROM and writes a finished `.gba` into a
library the emulators already scan (EmuDeck `roms/gba`, i.e. `dg_rom_root`), so
it plays on the box's mGBA core with nothing to load at runtime.

The applier (`files/apply_ips.py`) asserts the **base** SHA-1 before touching a
byte and the **output** SHA-1 after, so a wrong-region/revision base or a corrupt
patch fails loudly instead of producing a broken ROM. The role is idempotent: a
patch runs only when its output is missing or not the expected build.

## Current patches (`dg_rom_patches`)

| Hack | Base ROM (SHA-1) | Output |
| --- | --- | --- |
| **Donkey Kong Country (GBA) SNES colour restoration** — marc_max v1.1, re-palettes the washed-out GBA port toward the SNES original (in-game palettes only; minigame/map screens untouched). | `Donkey Kong Country (Europe) (En,Fr,De,Es,It).gba` — `8995f0be…`. **EU only**; the USA dump doesn't match. | `…(SNES Restoration).gba` (`005b5571…`) |
| **Final Fight ONE: Arcade Edition v3.0 (USA)** — restores the arcade roster/moves over the GBA port. | `Final Fight One (USA).gba` — No-Intro `17918e12…` (CRC `052c9997`). | `Final Fight One - Arcade Edition (USA) [v3.0].gba` (`e189ae8a…`) |
| **F-Zero: Vintage Velocity I (EN v2.1)** — remakes the 15 SNES courses in the Maximum Velocity engine. | `F-Zero - Maximum Velocity (USA, Europe).gba` — `8a08e29e…` (CRC `bd5e9798`). | `F-Zero - Vintage Velocity I (v2.1).gba` (`40aab9df…`, expands to 8 MiB) |
| **F-Zero: Vintage Velocity Ace (EN v3.0)** — F-Zero 99 course layouts + larger Mute City tracks. | same Maximum Velocity base (`8a08e29e…`). | `F-Zero - Vintage Velocity Ace (v3.0).gba` (`962f357d…`, expands to 8 MiB) |

The archives also ship JP/Europe patch variants; only the International (EN/US)
patches are committed, matching the box's dumps. The two F-Zero hacks are kept as
separate ROMs alongside the untouched `F-Zero - Maximum Velocity` original, so
all three coexist in the library.

## Install / revert

```sh
cd ansible
ansible-playbook install-rom-patches.yml            # or: site.yml --tags rom_patches
ansible-playbook install-rom-patches.yml -e dg_rom_patches_revert=true   # remove patched ROMs
```

Reverting deletes only the patched outputs; base/original dumps on the NAS are
untouched. After a run, rescan the GBA gamelist in ES-DE to pick up new entries.

## Adding a hack

1. Drop the `.ips` into `roles/install_rom_patches/files/` (give it a clear name).
2. Append an entry to `dg_rom_patches` in `group_vars/all/rom_patches.yml`:
   `name`, `base` (path), `base_sha1`, `ips` (filename), `out` (path),
   `out_sha1`. Get `out_sha1` by applying the patch once and hashing the result.
3. Run the playbook. The base and output are both hash-checked.
