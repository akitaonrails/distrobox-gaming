# WRC 4 mods — `install_wrc4_mods`

Opt-in NexusMods set for **WRC 4 FIA World Rally Championship** (Steam appid
`256330`, delisted — lives in the USB Steam library). Built via the
`nexus-mod-set` skill. Installed 2026-08-08.

## What it installs

| Mod | Type | Notes |
|---|---|---|
| [1 Loose camera + realistic tyres](https://www.nexusmods.com/wrc4fiaworldrallychampionship/mods/1) (Sal, based on themoddingsal) | `DATA.MIX` replace | More realistic tyre physics for all cars, rebalanced grip/difficulty, untilted cockpit cams, slightly lowered chase cams |

The mod is a single **`DATA.MIX`** container that replaces the game's own — no
loader, no script hook, no anti-cheat. The role backs the stock file up to
`DATA.MIX.dg-orig`, drops the mod's `DATA.MIX` into the game root, and writes a
`.dg-wrc4-1` marker (idempotent).

### Camera variant

Mod 1 ships two MAIN downloads — camera-looseness levels:

- **file 2 = "Loose camera 0.7"** — the default; looser, best for the mod's
  stated motion-sickness goal.
- **file 4 = "Loose camera 0.78"** — much stricter / tighter.

Switch by setting `file: "4"` on the entry in
`group_vars/all/wrc4_mods.yml`, then re-run with `dg_wrc4_revert=true` once to
restore stock before reinstalling the other variant.

## Install / revert

```sh
cd ansible
# Premium key auto-downloads; else stage the .rar under
# ROMS_FINAL/PC/NexusMods/wrc4/1/ and re-run.
NEXUS_MODS_API_KEY=... ansible-playbook install-wrc4-mods.yml

# restore the stock DATA.MIX
ansible-playbook install-wrc4-mods.yml -e dg_wrc4_revert=true
```

The exe version is gated to `1.0.0.0` (`scripts/pe-version.py`). The mod archive
is preserved on the NAS under `ROMS_FINAL/PC/NexusMods/wrc4/` and reused on
rebuild. Override the game location with `dg_wrc4_steam_library_root` if your
USB library mounts elsewhere.

## Excluded

**WRC 5 "all DLC unlock"** (`wrc5` mod 3) is intentionally **not** included — it
unlocks paid DLC (concept cars, esports/season packs) without purchase, i.e.
piracy of paid content, not a compatibility fix.
