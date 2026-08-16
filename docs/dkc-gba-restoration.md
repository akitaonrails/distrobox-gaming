# Donkey Kong Country GBA — SNES Colour Restoration (`install_dkc_gba_restoration`)

marc_max's [restoration patch](https://www.romhacking.net/hacks/4051/) (v1.1)
re-palettes the 2003 Game Boy Advance port of *Donkey Kong Country* back toward
the SNES original. Rare shrank every sprite and tileset for the GBA's screen and
the palettes never matched; this hack repaints them manually. Opt-in role;
installed 2026-08-16.

- **Form:** a hard-patch. The role applies the committed **IPS** patch to the
  base ROM and writes a finished `.gba` into the EmuDeck GBA library — nothing
  to load at runtime, no soft-patch, plays on the box's mGBA core as-is.
- **What it fixes:** in-game colours (levels, HUD, characters). What it does
  *not* touch: minigame/map palettes and possibly a few bonus rooms (they don't
  come from the SNES version).

## Required base ROM (strict)

The patch is offset-specific to **one** revision and the applier verifies it by
hash before touching a byte:

- **`Donkey Kong Country (Europe) (En,Fr,De,Es,It).gba`** — 8 MiB,
  **SHA-1 `8995f0be99a9cff66474a8975b8499bd69fb4c45`**
  (MD5 `c1fb9badf816b6d7836f4990f8119815`, CRC32 `41d277fe`).
- The **USA** dump (`fcc62356…`) is a *different* revision — it fails the check
  rather than producing a broken ROM. Only the EU multi-language dump works.

The base ROM lives on the NAS at `dg_dkc_gba_base_rom`
(`ROMS_FINAL/gba/…`). If you only have it zipped, extract the `.gba` first.
The patched result is `dg_dkc_gba_out`
(`Donkey Kong Country (Europe) (SNES Restoration).gba`, SHA-1
`005b5571e169c45a0649fdb2cc52729f9d6b4116`) in the EmuDeck `roms/gba` library.

## Install / revert

```sh
cd ansible
ansible-playbook install-dkc-gba-restoration.yml     # or: site.yml --tags dkc_gba_restoration
ansible-playbook install-dkc-gba-restoration.yml -e dg_dkc_gba_revert=true   # remove patched ROM
```

Idempotent: it re-patches only when the output is missing or not the expected
build. `apply_ips.py` (in the role's `files/`) asserts the base SHA-1 before
patching and the output SHA-1 after, so a wrong-region base or a corrupt patch
fails loudly.

## Updating

Drop a newer `.ips` into `roles/install_dkc_gba_restoration/files/`, bump
`dg_dkc_gba_ips` and `dg_dkc_gba_out_sha1` in
`group_vars/all/dkc_gba_restoration.yml`, and re-run.
