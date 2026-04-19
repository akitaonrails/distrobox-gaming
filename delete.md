# Stale / redundant Forza directories — candidates for deletion

Generated 2026-04-19 after PFP-2/3/4 installs to `/mnt/terachad/Emulators/Project Forza Plus/`.

All sizes live on the NAS (`/mnt/terachad/Emulators/`). Review each entry, then delete from a host with RW access to the NAS.

## Safe to delete (incomplete/broken extractions)

These are old partial xiso extracts with **no `default.xex`** — they cannot boot and the content is already covered by complete extractions elsewhere:

| Path | Size | Reason |
|------|-----:|--------|
| `ROMS_FINAL/xbox360/Forza 2/` | 7.0G | Only `Media/` — no default.xex, no $SystemUpdate. Broken. We have PFP-2 extracted at `Project Forza Plus/FM2/`. |
| `ROMS_FINAL/xbox360/Forza 3/` | 6.8G | Only `Media/` + `nxeart` — no default.xex. Broken. We have PFP-3 extracted at `Project Forza Plus/FM3/`. |

## Safe to delete (confirmed duplicates by size)

| Path | Size | Duplicates |
|------|-----:|-----------|
| `ROMS_FINAL/xbox360/Forza 4/Forza 4 [NTSCU][DVD1].iso` | 8.7G | Same size (8 738 846 720 B) as `ROMS_FINAL/xbox360/Forza Motorsport 4 (USA) … (Disc 1) (Play Disc).iso`. Byte-for-byte likely identical — verify with `md5sum` if paranoid. |
| `ROMS_FINAL/xbox360/Forza 4/Forza 4 [NTSCU][DVD2].iso` | 8.7G | Same size (8 738 846 720 B) as `… (Disc 2) (Content Install Disc).iso`. Older copies from May 2021. |
| `ROMS_FINAL/xbox360/F3/Forza Motorsport 3 - Ultimate Collection (USA) (Disc 1) (Play Disc).iso` | 7.8G | Byte-identical size (7 838 695 424 B) to the one at `ROMS_FINAL/xbox360/` root. |
| `ROMS_FINAL/xbox360/F3/Forza Motorsport 3 - Ultimate Collection (USA) (Disc 2) (Content Install Disc).iso` | 7.8G | Duplicate of root `… (Disc 2) (Content Install Disc).iso`. |
| `ROMS_FINAL/xbox360/F3/Forza Motorsport 3 - Ultimate Collection (USA) (En,Ja,Fr,De,Es,It,Zh,Ko,Pl,Ru,Cs,Hu) (Disc 1) (Play Disc).iso` | 7.8G | Multi-language redump — keep at root only (already there). |
| `ROMS_FINAL/xbox360/Forza 4 disc 1/` | 7.5G | Pre-extracted disc 1. **Identical content** to `Project Forza 4/Forza 4 disc 1/` which is the one we used for the PFP-4 install. Keep that one, delete this. |
| `ROMS_FINAL/xbox360/Forza 4 disc 2/` | 2.9G | Pre-extracted disc 2. Duplicate of `Project Forza 4/Forza 4 disc 2/`. |

**Top-level `ROMS_FINAL/xbox360/F3/` folder** (22G total): safe to delete entirely once the 3 ISOs above are confirmed duplicated at the root.

**Top-level `ROMS_FINAL/xbox360/Forza 4/` folder** (17G total): safe to delete entirely once the 2 `[NTSCU][DVDx]` ISOs are confirmed as duplicates of the USA-redump names at the root.

## Safe to delete (mod source zips — already extracted)

| Path | Size | Reason |
|------|-----:|--------|
| `Project Forza 2/Project Forza Plus 2 v1.2.zip` | 546M | Source zip for the PFP-2 mod. Already extracted to `Project Forza Plus 2/`. |
| `Project Forza 2/Project Forza Plus 2 v1.2 Update.zip` | 9.1M | Source zip for PFP-2 update. Already extracted to `Project Forza Plus 2 Update/`. |
| `Project Forza 3/Project Forza Plus 3 v1.2.zip` | 4.9G | Source zip for PFP-3 mod. Already extracted. |
| `Project Forza 3/Project Forza Plus 3 v1.2 Update.zip` | 30M | Source zip for PFP-3 update. Already extracted. |
| `Project Forza 3/isoextract/` + `isoextract.rar` | ~400K | Windows-only ISO extractor from the mod bundle. Useless on Linux (we use `extract-xiso`). |
| `Project Forza 4/Project Forza Plus 4 v1.2.zip` | 5.1G | Source zip for PFP-4 mod. Already extracted. |
| `Project Forza 4/Project Forza Plus 4 v1.2 Update.zip` | 64M | Source zip for PFP-4 update. Already extracted. |
| `Project Forza 4/FM4-Fix_byAlexwpi.rar` | 184K | Alt FM4 fix packaged rar; the extracted `FM4-Fix_byAlexwpi/` folder is 1.1M (just Media tweaks + Read Me). Rar is redundant once the folder exists. |

## Review before deleting (may still be useful)

| Path | Size | What it is |
|------|-----:|-----------|
| `Project Forza 4/xenia_master/` | 19G | A pre-configured Xenia Master build + its caches/content. We're managing Xenia via Xenia Manager from the Ansible `install_xenia` role — this directory is likely obsolete. But it holds `content/` (possibly save data from prior play) and cache — **inspect `content/` before deleting**. |
| `Project Forza 4/FM4-Fix_byAlexwpi/` | 1.1M | Alternative FM4 community fix. Not used by the PFP-4 install flow. Probably redundant; keep the `Read Me.txt` if curious, drop the rest. |
| `ROMS_FINAL/xbox360/5841123E/` | 2.0G | Xbox 360 TID-named dir with a single big GUID-named file under `000D0000/`. Not Forza (FM3=4D53084D, FM4=4D530910). Unknown title — inspect before deleting. |

## Safe to keep

- `Project Forza Plus/` (20G+7G+16G = ~43G) — the freshly installed PFP-2/3/4 trees.
- `ROMS_FINAL/xbox360/Forza Motorsport 3 … (USA) (Disc 1/2) ….iso` (root copies) — source ISOs.
- `ROMS_FINAL/xbox360/Forza Motorsport 4 (USA) … (Disc 1/2) ….iso` (root copies) — source ISOs.
- `ROMS_FINAL/xbox360/Forza 4 title update/` — needed for FM4 Title Update 8 (already staged inside `Project Forza Plus/FM4/`).
- `Project Forza 2/Project Forza Plus 2/`, `…/Project Forza Plus 2 Update/` — extracted mod files.
- `Project Forza 3/Project Forza Plus 3/`, `…/Project Forza Plus 3 Update/`.
- `Project Forza 4/Project Forza Plus 4/`, `…/Project Forza Plus 4 Update/`.
- `Project Forza 4/Forza 4 disc 1/`, `…/Forza 4 disc 2/` — canonical complete extractions (the `ROMS_FINAL/xbox360/Forza 4 disc 1|2/` duplicates can go).

## Potential space reclaimed

If you delete everything in the "safe to delete" sections:
- Broken extractions: **~13.8 GB**
- Duplicate ISOs + pre-extractions (F3/, Forza 4/, Forza 4 disc 1/, Forza 4 disc 2/): **~49 GB**
- Mod source zips + isoextract: **~10.6 GB**
- Total: **~73 GB**

Plus up to 19 GB more if `Project Forza 4/xenia_master/` is confirmed obsolete.
