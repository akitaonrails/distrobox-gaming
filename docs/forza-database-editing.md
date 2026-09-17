# Forza game database editing + "easy mode" (Xenia)

Forza Motorsport stores car data — **prices**, stats, upgrades, event payouts —
in a plain **SQLite** database, `gamedb.slt`. That means the economy is fully
editable, and the Project Forza Plus (PFP) modded installs on this box ship
ready-made **career-mode DBs** you can hot-swap, including a **Sandbox
("easy") mode** where every car and upgrade costs **1 credit**.

This page is the reference for swapping those DBs, editing prices directly, and
**reverting** to the shipped state.

> **Applied now (2026-09-16):** Sandbox (easy) mode is swapped into **FM4, FM2
> and FM3** — every base car and upgrade costs 1 credit. Pre-swap Normal DBs are
> backed up alongside the actives as `gamedb.slt.bak` (FM4 `Media/db/`, FM2 &
> FM3 `Media/DB/`). **DLC cars are also $1 on FM4 and FM3** (their DLC patch DBs
> were swapped in each game's per-install staged content copy); FM2 has no DLC
> layer. FH (XE Mod) has no Sandbox DB and is untouched. To go back to normal
> prices, see [Revert](#revert).

> All paths below hang off the roms_heavy Xbox 360 dir. Set once:
> ```sh
> HEAVY="/mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360"   # = {{ dg_rom_heavy_root }}/xbox360
> FM4="$HEAVY/FM4 (Project Forza Plus Modded)"
> ```
> **Always close Xenia before touching these files** (an open SQLite DB can
> corrupt), and keep a backup (below). FM4 does **not** checksum `gamedb.slt`,
> so edits/swaps load fine — PFP relies on this.

## Where the databases live (FM4)

| File | What it is |
|---|---|
| `$FM4/Media/db/gamedb.slt` | **Active** DB the game reads. Swapping career/easy modes = replacing this file. |
| `$FM4/_game_mode_dbs/<Mode>/gamedb.slt` | **Pristine** PFP master for each mode (Normal / Hard / Sandbox / Vanilla) — the canonical source to swap in or revert to. Never touched by play. |
| `$FM4/_game_mode_dbs/<Mode>/DLC DBs/<hash>4D/` | Per-mode **DLC car** DBs — copy into the content `00000002/` so DLC cars follow the mode too. |
| `…/Xenia Canary/content/0000000000000000/4D530910/00000002/…/Media/db/patch/*_merge.slt` | The **live DLC car** patch DBs (76 of them), reached via the `00000002` content symlink → `$FM4/_post_boot_to_content_4D530910/00000002`. DLC-car prices live here, not in the base `gamedb.slt`. |

`Database.xmplr` (top level) is a **separate proprietary Forza format, not
SQLite** — the prices you care about are all in the `.slt` files.

FM2 and FM3 have the same PFP layout (`FM2 (Project Forza Plus Modded)`,
`FM3 (Project Forza Plus Modded)`; note FM2/FM3 use `Media/DB/` with a capital
DB). `FH (XE Mod)` is a separate Forza Horizon 1 mod with its own
`media/db/gamedb.slt`.

### FM3 note

FM3's install originally had **no `_game_mode_dbs/`** — only its active DB. The
four mode DBs were **staged from the local extracted PFP source** at
`/mnt/terachad/Emulators/Project Forza Plus/_extracted/PFP3/Project Forza Plus 3/Game Mode DBs/`
(the whole PFP2/3/4 + Update packs live under
`Project Forza Plus/_extracted/`). FM3 now has the same swappable
`_game_mode_dbs/{Normal,Hard,Sandbox,Vanilla} Mode/` layout as FM2/FM4.

FM3 mode `gamedb.slt` md5s: Normal `eae89760369d1356b98f41ecfe4448c9`
(= the shipped default), Sandbox `36b97d4452875729c67615a2fe75e4aa`
(415 cars, all $1). Swap/revert exactly like FM4 but with the FM3 paths
(`Media/DB/`).

**FM3 DLC cars are also on Sandbox pricing** (done the clean FM4 way). FM3's
Xenia content `…/4D53084D/00000002` originally symlinked straight to the
**shared** 9.2 GB PFP3 pack (`…/_extracted/PFP3/…/Disc 2 and DLCs/00000002`).
To avoid mutating that shared source, the 9.2 GB content was copied to a
**per-install** dir, `FM3 (Project Forza Plus Modded)/_post_boot_to_content_4D53084D/00000002`,
the Sandbox `DLC DBs/.` were overlaid onto it (the DLC `*_merge.slt` patches now
read `BaseCost 1`), and the content symlink was re-pointed to that copy. The
shared `_extracted/PFP3` pack is untouched.

**Revert FM3 DLC** to normal prices — either restore the pristine patches into
the staged copy, or point the symlink back at the shared pack:
```sh
XC="/mnt/data/distrobox/gaming/tools/xenia-manager/current/Emulators/Xenia Canary/content/0000000000000000/4D53084D"
# option 1: restore Normal DLC prices in the staged copy
cp -rf "$FM3/_game_mode_dbs/Normal Mode/DLC DBs/." "$FM3/_post_boot_to_content_4D53084D/00000002/"
# option 2: point back at the untouched shared pack
ln -sfn "/mnt/terachad/Emulators/Project Forza Plus/_extracted/PFP3/Project Forza Plus 3/Disc 2 and DLCs/00000002" "$XC/00000002"
```

## The career/easy modes (FM4)

Verified profile of each mode's `Data_Car.BaseCost` (car purchase price) and
upgrade prices:

| Mode | Cars | Car price range | Upgrades | md5 of `gamedb.slt` |
|---|---|---|---|---|
| **Normal** (PFP shipped default) | 502 | $5,000 – $10,000,000 | real | `2ac7b3f892989dc58d9921cf32e0600e` |
| **Hard** | 502 | $5,000 – $10,000,000 | real | `e8d26c4276f62619233084f87531f5e3` |
| **Sandbox = "easy"** | 503 | **$1 flat** | **$1 flat** | `d3b087ab07fd5713ba0e6d7ebb7dd640` |
| **Vanilla** | 502 | $5,000 – $10,000,000 | real | `d2e942e53ce35c8258a3e00a9cc103a0` |

(Modes differ in more than price — AI skill, event structure, starter cars,
unlocks; see `$FM4/_instructions/Information - List of Changes.txt`.)

To check which mode is **live right now**, md5 the active DB and compare against
the table above:
```sh
md5sum "$FM4/Media/db/gamedb.slt"
```

FM2 mirrors this (Normal active). Its pristine mode md5s: Normal
`9860df6b015598f042fd0f12da1e4fb6`, Hard `50668071a356923ba76c9a9356b10f95`,
Sandbox `b7523a41a0a8eb4772c67823b6e65844`, Vanilla `164db7d8c3d72d346b533c0ee23cecbd`.

## Switch to "easy" mode (Sandbox) in Xenia

Close Xenia first. Back up the active DB, then swap in Sandbox:

```sh
cp -f "$FM4/Media/db/gamedb.slt" "$FM4/Media/db/gamedb.slt.bak"     # backup
cp -f "$FM4/_game_mode_dbs/Sandbox Mode/gamedb.slt" "$FM4/Media/db/gamedb.slt"
```

That makes **base** cars/upgrades cost $1. To make **DLC** cars $1 too, also
copy Sandbox's DLC DBs into the live content folder (matching hash dirs):

```sh
XC="/mnt/data/distrobox/gaming/tools/xenia-manager/current/Emulators/Xenia Canary/content/0000000000000000/4D530910"
cp -rf "$FM4/_game_mode_dbs/Sandbox Mode/DLC DBs/." "$FM4/_post_boot_to_content_4D530910/00000002/"
# ($XC/00000002 is a symlink to that staged dir, so this updates the live DLC set)
```

Launch FM4. (PFP's own `_instructions/Instructions - Switching Career Modes.txt`
documents the same swap.)

## Revert

Copy the shipped mode's pristine master back over the active DB (Normal is the
default; verify with the md5 table), or restore the backup you made:

```sh
cp -f "$FM4/_game_mode_dbs/Normal Mode/gamedb.slt" "$FM4/Media/db/gamedb.slt"   # or: gamedb.slt.bak
cp -rf "$FM4/_game_mode_dbs/Normal Mode/DLC DBs/." "$FM4/_post_boot_to_content_4D530910/00000002/"
md5sum "$FM4/Media/db/gamedb.slt"     # expect 2ac7b3f892989dc58d9921cf32e0600e (Normal)
```

The `_game_mode_dbs/` masters are never modified by playing, so they are always
a clean restore source even if you've been editing.

## Editing prices directly (sqlite3)

`sqlite3` is on the host and in the box. Work on a **backup** with Xenia closed.
Key columns:

| What | Table.Column |
|---|---|
| Car purchase price | `Data_Car.BaseCost` |
| Upgrade part prices | `List_Upgrade*.Price` (brakes, body, drivetrain, anti-sway, …) |
| Tyre pricing | `Combo_TireBrandCompound.PriceScale/PriceDisplay`, `List_PartAttribute.Price` |
| Event / career payouts | `Events.CashPrize`, `EventScoring.Credits`, `AffinityLevelDef.BonusCredits` |

Car display/model **names are string-table tokens** (`_&<id>`, resolved at
runtime from `Media/stringtables/`), so target cars by **make + year** rather
than name. Make is readable via `List_CarMake.IconPathBase` (e.g. `Ferrari`).

Examples (edit `$FM4/Media/db/gamedb.slt`):
```sh
DB="$FM4/Media/db/gamedb.slt"; cp -f "$DB" "$DB.bak"

# all base cars cost 1 credit (this is basically what Sandbox does)
sqlite3 "$DB" "UPDATE Data_Car SET BaseCost=1 WHERE BaseCost>0;"

# one car: every Ferrari from 1964 -> $100
sqlite3 "$DB" "UPDATE Data_Car SET BaseCost=100
               WHERE Year=1964 AND MakeID=(SELECT ID FROM List_CarMake WHERE IconPathBase='Ferrari');"

# double every event cash payout
sqlite3 "$DB" "UPDATE Events SET CashPrize=CashPrize*2;"

# free upgrades (brakes shown; repeat per List_Upgrade* table)
sqlite3 "$DB" "UPDATE List_UpgradeBrakes SET Price=0;"
```

To also cover **DLC cars**, apply the same to the `*_merge.slt` patch DBs under
the live `00000002/…/Media/db/patch/` tree (they carry the DLC-car rows). A full
readable `make / model / year / price` dump (model names resolved from the
string tables) can be generated on request.

Reverting a direct edit = restore the `.bak`, or copy the relevant pristine
`_game_mode_dbs/<Mode>/gamedb.slt` back.
