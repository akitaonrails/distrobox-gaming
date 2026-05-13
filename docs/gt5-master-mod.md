# GT5 Master Mod (Nenkai 1.9.2) for RPCS3

Optional Ansible flow that downgrades a Gran Turismo 5 install to
**Spec 2.11** via the official Sony CDN PKG chain, then overlays
Nenkai's Master Mod 1.9.2 onto the resulting `PDIPFS/` tree.

```sh
ansible-playbook install-gt5-master-mod.yml
```

## What the mod adds

Full feature list in the mod's `readme_instructions_misc.txt` (extracted
to `dg_gt5_mod_extract_dir` after the first run). Highlights:

- 42 PS2-era tracks (Trial Mountain, Nürburgring Nordschleife PS2, Côte
  d'Azur, Tsukuba, Apricot Hill, El Capitan, etc.).
- LAN play enabled, with broadened car classes and rebalanced shuffle.
- Debug menu (SELECT on main menu), R1-hold unlocks for Photo Travel.
- Scrapped cars restored (Polyphony Digital X1 fan, GT Academy Skyline).
- Main-menu framerate target raised to 60.
- Race Editor / Course Maker QA features unlocked.
- All cars in dealership (rebalanced prices).
- Optional Debug Cam Addon overlays free-cam in Photo Mode replays.

## Source

| Item | URL |
|---|---|
| GTPlanet thread | https://www.gtplanet.net/forum/threads/1-9-2-gt5-master-mod.395844/ |
| Mod author hub | https://nenkai.github.io/gt-modding-hub/ |
| Mod download (MediaFire) | https://www.mediafire.com/folder/6ye4yod7voapb/Gran+Turismo+5+Master+Mod+(2.11) |

MediaFire serves a JS-protected download page; grab the `(US-BCUS98114)`
zip manually in a browser and drop it at `dg_gt5_mod_archive`
(default: `{{ dg_external_games_root }}/ps2/GT5_2.11_Master_Mod_1.9.2_(US-BCUS98114).zip`).

## Version requirement — and why this is involved

The mod's readme is explicit:

> *"You need Gran Turismo 2.11, not higher, not lower. Again, make
> double SURE you are on GT5 2.11. Patches need to be installed one
> by one until 2.11. You can NOT directly install 2.11."*

GT5 update PKGs are **incremental, not cumulative**. The most common
final user state is 2.17 (the last official patch), which the mod
won't run on. To get to 2.11 you have to replay the entire patch
chain from `1.05 → 2.11` in order — 21 PKGs, ~4.2 GB total.

The role does this automatically via Sony's PSN CDN (still live, still
serving 200 OK for legacy PS3 catalog titles via Akamai). Each PKG is
fetched once to NAS staging, then `rpcs3 --no-gui --installpkg` walks
them in version order. Wall time ≈ 30–45 minutes.

## Storage layout

```
NAS (canonical):
  {{ dg_external_games_root }}/ps2/
    GT5_2.11_Master_Mod_1.9.2_(US-BCUS98114).zip      ← user-downloaded
    gt5-update-pkgs/                                   ← role downloads here
      A0105-V0100.pkg ... A0211-V0100.pkg              (~4.2 GB)
    gt5-master-mod-1.9.2/                              ← unpacked mod
      PDIPFS/                                          ← payload (overlay)
      PDIPFS_ORIGINAL/                                 ← rollback files
      Debug_Cam_Addon/PDIPFS/                          ← optional addon
      readme_instructions_misc.txt
    gt5-backups/
      pre-downgrade-<old-version>.tar.zst              ← e.g. 2.17 snapshot
      pre-mod-v211-pdipfs.tar.zst                      ← clean 2.11 snapshot

Box (inside the distrobox):
  ~/.config/rpcs3/dev_hdd0/game/BCUS98114/
    PARAM.SFO              ← APP_VER=02.11 after the chain
    USRDIR/PDIPFS/         ← mod files overlaid here
    .dg-master-mod-1.9.2-installed   ← role's apply marker
```

## Tags

- `--tags downgrade` — only the PKG-chain replay (skip if PARAM.SFO
  already reports 02.11).
- `--tags apply` — only the mod overlay (assumes 2.11 is in place).

The default (no tag) runs both passes in the right order, with the
downgrade pass skipped automatically when not needed.

## Preconditions enforced by the role

- Mod zip present at `dg_gt5_mod_archive`. Fails with the MediaFire
  URL in the error message if absent.
- RPCS3 not currently running. The PKG installer and the mod-overlay
  step would both corrupt state if RPCS3 holds file handles open. The
  role aborts with the offending PIDs listed.
- Base disc directory present on the NAS (warning, not fatal — RPCS3
  can boot from the update tree alone, but the disc registration is
  what makes the game appear in the list).

## Idempotency + reversibility

| State | Behavior on re-run |
|---|---|
| `PARAM.SFO` already at 02.11 | downgrade pass skipped; only `apply_mod` runs (cheap rsync) |
| Mod extracted, marker present | re-extraction skipped, rsync re-applies (idempotent on file mtime) |
| Backup tarballs already exist | `creates:` guards skip the re-tar |
| RPCS3 running | role aborts before touching anything |

Rollbacks the role records paths for in the final debug summary:

1. **Mod → pristine 2.11**: rsync `PDIPFS_ORIGINAL/` onto the install,
   *or* untar `pre-mod-v211-pdipfs.tar.zst`.
2. **Pristine 2.11 → prior 2.17 (or whatever was there)**: untar
   `pre-downgrade-<old-version>.tar.zst` from `dg_gt5_backup_dir`.

## Caveats

- **Online play is locked.** PSN servers for GT5 have been off since
  2014. The mod's LAN enable is real LAN over the box's network, not
  PSN matchmaking.
- **First boot is slow.** GT5 rebuilds its game databases on the first
  launch after a major file overlay — a long black screen at the boot
  logo is expected, per Nenkai's readme.
- **Save sets break with added cars.** If you add scrapped cars to a
  pre-existing save and later revert to vanilla, the save will
  softlock at boot. The readme advises removing the new cars from the
  garage before any revert, or just keeping a separate modded save.
- **Region lock**: this role and these vars are scoped to **US
  (BCUS98114)**. For EU (BCES00569), JP (BCJS30001), or ASIA
  (BCAS20108) you'd swap `dg_gt5_title_id`, the matching mod zip name,
  and the CDN base URL (the title hash component differs per region).
