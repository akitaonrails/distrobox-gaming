# Xbox 360 Title Updates for Xenia

Xbox 360 games often require one or more **Title Updates** (TUs) to
boot under Xenia. A game asks Xenia for an asset under the `update:`
virtual device; without the TU staged in the content tree, Xenia
returns `ResolvePath(update:\<file>) failed - device not found` and
the game quits or errors out.

Real-world effect in our library:

| Game | TU requirement | Symptom without TU |
|---|---|---|
| **Forza Motorsport 3** | **HARD** | Won't boot — errors on `update:\media.zip` |
| Forza Motorsport 4 | Recommended | Boots without, but some DLC requires TU8 |
| Forza Motorsport 2 | Recommended | Boots without (rare missing UI polish) |
| Forza Horizon | Recommended | PFP/patches interact; TU4 safest |
| Forza Horizon 2 | Recommended | Similar |
| Most other Xbox 360 titles | Varies | Some hard-fail, most don't |

This repo ships a **batch downloader** (`scripts/download-xbox360-tus.py`)
that fetches TUs from archive.org's `microsoft_xbox360_title-updates`
collection and picks the best version per region automatically. Manual
workflow covered at the end of this doc for cases the script can't
handle.

## Prerequisites (one-time setup)

### 1. archive.org account

TU downloads from archive.org require a free account + login — the
collection files redirect through authenticated CDN URLs.
Sign up at <https://archive.org/account/signup>.

### 2. `internetarchive` CLI

Handles auth, CDN redirects, signed download tokens, retries, and
checksum verification that cookies alone cannot.

Installed in this repo's distrobox already via:
```sh
# in the gaming distrobox:
sudo pacman -S --needed python-internetarchive
# or:
pip install --user internetarchive
```

Verify:
```sh
distrobox enter gaming -- ia --version   # → 5.x.x
```

### 3. Configure credentials (stores token at `~/.config/ia.ini`)

```sh
distrobox enter gaming -- ia configure
# prompts:
#   Email address: your-archive-org-email@example.com
#   Password: ****
```

One-time step. The token persists.

## Downloader usage

From the repo root, run the script **from inside the distrobox** (so
`ia` is in PATH):

```sh
# Preview what would be fetched (safe; no downloads, no auth required)
distrobox enter gaming -- python3 scripts/download-xbox360-tus.py \
    --src  /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360 \
    --dest /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360-updates \
    --dry-run

# Real run — 3 parallel downloads (archive.org rate-limits free accounts)
distrobox enter gaming -- python3 scripts/download-xbox360-tus.py \
    --src  /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360 \
    --dest /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360-updates \
    --concurrency 3
```

What it does:

1. Caches the collection manifest (~560 KB XML) at `<dest>/_manifest.xml`.
2. Scans `<src>` for game folders and loose ISOs. One level of recursion
   into `xbla/` dirs (configurable via `RECURSE_INTO` in the script).
3. Normalizes each name (`Forza Motorsport 4 (USA) ....iso` →
   `Forza Motorsport 4`).
4. For each game, finds matching TU zips in the manifest. Sorts by
   region preference **USA > World > Europe > Japan > other**, then by
   highest version. Ties lose to USA.
5. Downloads each match via `ia download --no-directories --checksum`.
6. Skips downloads whose target file already exists at expected size.

Outputs go to `<dest>/<GameName>/<OriginalFilename>.zip`. The
manifest is reused on re-runs — delete it to refresh.

### What games are skipped by design

The script skips these to avoid false matches (see
`SKIP_LOCAL_SUBSTRINGS` in the script):

- `Forza Horizon*` / `Forza Motorsport*` / `FM[234] (` — user manages
  these manually because of PFP modded installs (see
  `docs/project-forza.md`).
- `RidgeRacerCollection/` — compilation disc, no per-title TU.

If you want Forza TUs via the script anyway, remove those lines from
`SKIP_LOCAL_SUBSTRINGS`.

### Reading the dry-run output

```
Matched 21 games to TUs:
  Banjo-Kazooie - Nuts & Bolts  →  Banjo-Kazooie - Nuts & Bolts (USA) (v3).zip  (USA v3)
  Gears of War 2                →  Gears of War 2 (USA) (v6).zip                (USA v6)
  ...

No TU found (or none exists) for 46 games:
  - Ace Combat 6 - Fires of Liberation
  - DoDonPachi Resurrection
  - ...
```

"No TU found" means one of:

1. The game genuinely never shipped a TU (common for small XBLA
   titles, early releases).
2. Your local dir/ISO name doesn't match the archive.org collection's
   game-name form — happens with heavy renames or fan translations.
   Fix by adding a one-line alias to `GAME_ALIASES` in the script
   (commented template in the source), or rename the local dir.
3. Game exists in the collection under a region not in the manifest
   snapshot you cached — delete `<dest>/_manifest.xml` and re-run.

## Installing a downloaded TU into Xenia

**Use Xenia Manager's GUI — don't drop raw files into the content tree.**
Xenia Canary's TU scanner (`content_manager.cc:ListContent`) only recognizes
**directories** in `<TID>/000B0000/`, not raw STFS files. A dropped-in file
is silently skipped, which shows up as zero "title update" lines in
`xenia.log` and the game hard-fails if it calls the `update:` device.

### The correct flow

1. **Extract the downloaded zip** so you have the raw STFS file (no
   extension, name looks like `tu00000001_00000000` or
   `TU_16L622D_000000G000000.0000000000104`). Xenia Manager rejects zips.
2. Open Xenia Manager → **Manage** tab (left sidebar, *not* the per-game
   Library view — the per-game context menu has no install option).
3. Scroll past the "Manage Emulator" cards to the **"Install Content"**
   card. Click **Install Content**.
4. In the dialog, click **Add Content**, pick the raw STFS file (multi-select
   is fine for batch DLC installs), then **Install**.
5. Xenia Manager reads the STFS header and routes each file to the right
   subdir (`000B0000` for TUs, `00000002` for DLCs, etc.) plus writes a
   matching `Headers/<type>/<name>.header` file.

If you try to install a TU that's already present, Xenia Manager refuses
with an "already exists" error. Delete the existing entry first.

### Why dropping files doesn't work

From Xenia Canary source (`src/xenia/kernel/xam/content_manager.cc:218-222`):

```cpp
if (file_info.type != xe::filesystem::FileInfo::Type::kDirectory) continue;
```

Xenia expects TUs pre-extracted into `000B0000/<packagename>/default.xexp`
+ friends, with a 16-byte `XCONTENT_AGGREGATE_DATA` file at
`Headers/000B0000/<packagename>.header`. Xenia Manager does this
extraction via `StfsFile.ExtractToXeniaStructure`; loose files are skipped
because they're not directories.

Xenia's content root in this repo's default install:
```
/mnt/data/distrobox/gaming/tools/xenia-manager/current/Emulators/Xenia Canary/content/0000000000000000/<TID>/000B0000/
```

### Per-game toml after install

Xenia Manager sets `apply_title_update = true` by default when a TU is
present. **Exception:** games with community-modified xex files where the
TU's xex patch delta would corrupt the modded code. For those, set
`apply_title_update = false` — Xenia still mounts the `update:` device
(serving `media.zip` etc.) but skips the xex binary patch. Known case in
this repo: FM3 with PFP-3. See `docs/project-forza.md` for details.

## Manual fallback — single TU by filename

For games the script can't auto-match, use the `ia` CLI directly:

```sh
# 1. Browse the collection visually
#    https://archive.org/details/microsoft_xbox360_title-updates

# 2. Once you find the exact filename (e.g. "Some Game (USA) (v3).zip"):
distrobox enter gaming -- ia download \
    microsoft_xbox360_title-updates \
    "Some Game (USA) (v3).zip" \
    --destdir /mnt/terachad/Emulators/EmuDeck/roms_heavy/xbox360-updates/SomeGame \
    --no-directories --checksum
```

## Verifying a downloaded TU

libretro-database ships per-TU hashes in
[`Microsoft - XBOX 360 (Title Updates).dat`](https://github.com/libretro/libretro-database/blob/master/metadat/no-intro/Microsoft%20-%20XBOX%20360%20(Title%20Updates).dat)
— CRC32, MD5, SHA1 for every region/version.

Quick CRC32 check on an extracted TU file:
```sh
crc32 <path-to-tu-file>
# or
python3 -c "import zlib; print(hex(zlib.crc32(open('<path>','rb').read()) & 0xffffffff))"
```

Compare against the `crc` field in the DAT for that region+version
entry.

## Diagnostic: know when you need a TU

Run the game in Xenia. If it errors out with something like:
```
!> ResolvePath(update:\...) failed - device not found
```
in `Emulators/Xenia Canary/xenia.log`, that's the TU-missing signature.

Install the TU following the instructions above and relaunch. If the
`update:` error stops appearing and a different error happens, the TU
was the right fix.

## References

- [archive.org microsoft_xbox360_title-updates collection](https://archive.org/details/microsoft_xbox360_title-updates)
- [libretro-database No-Intro TU DAT (hashes)](https://github.com/libretro/libretro-database/blob/master/metadat/no-intro/Microsoft%20-%20XBOX%20360%20(Title%20Updates).dat)
- [internetarchive Python CLI](https://archive.org/developers/internetarchive/)
- [Xenia wiki: Title Updates](https://github.com/xenia-project/xenia/wiki/FAQ)
