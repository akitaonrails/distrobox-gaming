# NKIT → redump ISO recovery (GameCube)

How to turn an **NKIT-compressed** GameCube dump (`*.nkit.iso`) back into a
byte-exact **Redump** ISO, so xdelta romhacks that demand the pristine disc
(e.g. Super Mario Sunburn, Super Mario Eclipse) will apply. First done
2026-08-07 for the Super Mario Sunshine hacks.

Path roots used below (all under the NAS `dg_roms_final_root` /
`dg_emudeck_root`):

- `<RF>`  = `ROMS_FINAL` root (`dg_roms_final_root`)
- `<GC>`  = `<EmuDeck>/roms_heavy/gc` — the ES-DE `gc` scan dir
- `<NKIT>` = `<RF>/PC/tools/nkit-v1.4` — where the NKit toolchain is staged

## Why this is needed

Many GameCube hacks ship as an **xdelta3 patch** plus a drag-and-drop `.bat`
that patches *your* Sunshine copy into the hack. The patcher hard-checks the
source MD5 and **explicitly rejects NKIT / RVZ / CISO** — it wants the exact
Redump image. Example target (SMS USA/Canada, `GMSE01`):

```
size=1459978240  crc=771ad977  md5=0c6d2edae9fdf40dfc410ff1623e4119
```

An NKIT dump is smaller because NKit removed the disc's **junk/padding** (the
pseudo-random data the SDK writes into unused sectors). Games never read it, so
NKIT plays fine in Dolphin — but xdelta's per-window source checksums cover the
junk regions, so a scrubbed source fails to patch.

## What does NOT work (and why)

- **`dolphin-tool convert -f iso`** — refuses to expand NKIT: *"Warning:
  Converting an NKit file, output will still be NKit!"*. Dolphin reads NKIT as a
  trimmed plain file; its junk generator (`LaggedFibonacciGenerator`) only ever
  *recovers* seeds from junk that is already present (for RVZ), never derives
  junk from the disc ID. RVZ→ISO **does** regenerate junk correctly — but only
  because the seeds are stored in the RVZ.
- **`wit` (Wiimms ISO Tools)** — reads NKIT and extracts the FST with original
  offsets, but its FST→ISO *compose* always emits a **Wii** disc (4.7 GB) and it
  does not write Nintendo junk (no junk code in its source). Copy preserves the
  scrub.
- **`nod` / `nodtool`** — builds discs but writes zeros in junk regions.

The junk for some first-party discs (SMS USA included) is **"not generated with
the image ID"** — it can't be reproduced algorithmically at all. Only **NKit**
knows how to restore it, using a small per-game **recovery file**.

## The toolchain (staged under `<NKIT>`, preserved on the NAS)

NKit v1.4 is a .NET Framework app; run the CLI wrappers under **Mono** (no Wine
needed). Staged so a rebuild never re-downloads:

| Piece | Location | Source |
| --- | --- | --- |
| NKit binaries (`RecoverToISO.exe`, `NKit.dll`, `SharpCompress.dll`, …) | `<NKIT>/` | archive.org `nkit-v1-4` (open) |
| Redump GameCube datfile | `<NKIT>/Dats/Redump/GameCube/Redump.dat` | `redump.org/datfile/gc/` |
| Per-game GC **recovery files** (598 × `fst[ID…].bin`, ~26 MB) | `<NKIT>/Recovery/Redump/GameCube/` | archive.org `nkit-1.4-collection` → *"NKit 1.4 + GameCube Partitions.7z"* (6 MB; needs a free archive.org login) |

`mono` is installed in the `gaming` box (`sudo pacman -S mono`). The recovery
files are the crucial bit: without them NKit reaches full size but produces the
**wrong** junk (`MatchFail`, wrong CRC) and warns *"GameCube relies on them
heavily!"*. The GC-only recovery set is 6 MB; the Wii set (4 GB) and the
"Fully Loaded" bundle (15 GB, throttled to ~1 MB/s anonymously) are **not**
needed for GameCube.

## The recovery procedure

```sh
# inside the gaming box (has mono + the NAS mounts)
cd "<NKIT>"
mono RecoverToISO.exe "<EmuDeck>/roms_heavy/gc/Super Mario Sunshine/Super Mario Sunshine (USA).nkit.iso"
```

Success looks like:

```
Recover ISO:  ... [MiB: 1392.3]  Match Redump
  |Recovery:   .../Recovery/Redump/GameCube/fst[GMSE010000][DE48500A][7BC2D228][EC61FB81].bin
  |Replacing fst.bin crc 219765C8 with Recovery fst 7BC2D228
  |Header brute forced to match
  |MD5: 0C6D2EDAE9FDF40DFC410FF1623E4119        ← matches Redump
```

Output lands in `<NKIT>/Processed/GameCube/<Redump name>.iso`. **Verify** before
trusting it:

```sh
md5sum "<NKIT>/Processed/GameCube/Super Mario Sunshine (USA, Canada).iso"
# must equal the dat entry: 0c6d2edae9fdf40dfc410ff1623e4119
```

If it says `MatchFail` / wrong CRC: the per-game recovery file for that disc ID
is missing from `<NKIT>/Recovery/Redump/GameCube/` — the filename starts with
`fst[<ID6>0000]…`, e.g. `fst[GMSE010000]…` for SMS USA.

## Applying the hack (xdelta) and installing into ES-DE

The recovered ISO is the pristine base. Apply each hack's xdelta on the host
(`xdelta3 -d -f -s <base> <patch> <out>`), then drop the standalone ISO into the
`gc` scan dir — each file is one ES-DE entry, launched with plain
`dolphin-emu -b -e %ROM%` (no Riivolution needed).

```sh
BASE="<RF>/PC/romhacks/sms/_base_SMS_USA_redump.iso"   # the verified redump
7z e -so "<RF>/PC/romhacks/sms/super_mario_sunburn_v2.7z" patches/console.xdelta > /tmp/sb.xdelta
xdelta3 -d -f -s "$BASE" /tmp/sb.xdelta "<GC>/Super Mario Sunburn (v2).iso"     # GMSE03
7z e -so "<RF>/PC/romhacks/sms/super_mario_eclipse_106_de_10.7z" patches/v1.0.6.xdelta > /tmp/ec.xdelta
xdelta3 -d -f -s "$BASE" /tmp/ec.xdelta "<GC>/Super Mario Eclipse (v1.0.6).iso" # GMSE04
```

xdelta's source checksum is the correctness oracle — if the patch applies, the
base was byte-exact. Add `<game>` entries to `<GC>/gamelist.xml` for clean names
(ES-DE otherwise shows the filename).

## What is preserved for a from-scratch rebuild

Under `<RF>/PC/`, so nothing is re-downloaded or re-derived by hand:

- `PC/tools/nkit-v1.4/` — NKit + Redump.dat + GC recovery files (the whole
  restore toolchain).
- `PC/romhacks/sms/` — the hack archives (`*.7z`, which contain the xdelta) and
  `_base_SMS_USA_redump.iso` (the verified pristine base, so re-patching skips
  the recovery step).

The recovery is deterministic: same NKIT + same recovery file → same Redump MD5
every time. This is a **manual runbook**, not baked into `site.yml`, because it
needs the user's NKIT dump and the (login-walled) recovery set — but every input
is staged on the NAS so it can be repeated verbatim.

## The 3 Super Mario Sunshine entries (reference)

| ES-DE entry (`<GC>/…`) | Disc ID | Built from |
| --- | --- | --- |
| `Super Mario Sunshine/…(USA).nkit.iso` | GMSE01 | original NKIT dump (plays as-is) |
| `Super Mario Sunburn (v2).iso` | GMSE03 | redump base + `super_mario_sunburn_v2.7z` |
| `Super Mario Eclipse (v1.0.6).iso` | GMSE04 | redump base + `super_mario_eclipse_106_de_10.7z` |

Eclipse also has a **9.2 GB HD texture pack** (v5.0.0, from
`iZePlayzYT/SuperMarioEclipse-TexturePacks`, hosted on Dropbox). It's extracted
to the NAS under `HD-textures/dolphin-textures/extracted/super-mario-eclipse/…/
Load/Textures/GMSE04/` and symlinked into `~/.local/share/dolphin-emu/Load/
Textures/GMSE04` (Dolphin's global `HiresTextures = True` loads it). See
`docs/hd-textures.md`.

See also [rom-hack-patching.md](rom-hack-patching.md) for the general
xdelta/IPS rules.
