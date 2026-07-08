# ROM hack patching (xdelta / IPS)

How ROM hacks are applied to the NAS library, using the Sonic
Advance 3 SP install as the reference case (v1.02 → v1.03 upgrade,
2026-07-08).

## The golden rules

1. **Patches apply to the pristine base ROM, not a patched one.**
   xdelta (VCDIFF) embeds a source checksum and refuses the wrong
   base; IPS doesn't check anything and silently corrupts. Never patch
   on top of an already-patched file.
2. **Detect an already-patched ROM by size.** Stock GBA ROMs are
   powers of two (8 MiB / 16 MiB / 32 MiB). Any other size means a
   hack is already applied (SA3 stock = 16 777 216; SP-patched ≈
   17 284 5xx). Console discs vary; compare against No-Intro/Redump
   sizes when in doubt.
3. **Recover pristine bases from NAS snapshots.** The NAS keeps
   btrfs-style snapshots at `/mnt/terachad/#snapshot/<GMT-...>/` —
   2-hourly for ~2 days, then weekly/monthly. A pre-hack snapshot
   holds the clean file at the same relative path
   (`.../Emulators/EmuDeck/roms/gba/...`). This avoids re-sourcing
   ROMs entirely.
4. **Replace under the same filename.** ES-DE gamelists, scraped
   artwork (`images/<name>-*.png`), and collections all key off the
   filename — keep it identical and everything keeps working.
5. **Never delete the previous ROM.** Keep it beside the new one with
   a non-`.gba` suffix so ES-DE doesn't double-list, e.g.
   `<name>.gba.sp1.02.bak`. Reverting is a single rename.
6. **Archive the patch file** in `/mnt/terachad/Downloads/` next to
   any earlier versions, for provenance and future re-application.

## Verification chain (what "applied correctly" means)

For the SA3 SP 1.03 upgrade this was verified end-to-end; repeat the
same pattern for any hack:

```sh
# 1. Confirm the story: pristine base + old patch == current file
xdelta3 -f -d -s "<base>" "old.xdelta" /tmp/repro.gba
cmp /tmp/repro.gba "<current rom>"        # byte-identical → story holds

# 2. Build the new ROM from the pristine base
xdelta3 -f -d -s "<base>" "new.xdelta" /tmp/new.gba

# 3. Sanity: header still valid (GBA title+code at offset 0xA0)
dd if=/tmp/new.gba bs=1 skip=160 count=16 | od -c   # e.g. SONICADVANC3 B3SE

# 4. Swap with backup
mv "<rom>" "<rom>.spX.XX.bak" && cp /tmp/new.gba "<rom>"
```

`xdelta3` is installed on the host and in the box. If a patch is
suspiciously small for an overhaul (tens of KB), it may be an
*upgrade* patch targeting the previous hack version instead of the
base — xdelta's source checksum sorts it out: just try both sources;
the wrong one fails with `XD3_INVALID_INPUT`.

## Save compatibility

- **In-game (battery) saves** normally survive hack upgrades — mods
  keep the standard save format unless the author says otherwise.
- **Savestates do not** — they snapshot the whole ROM+RAM and break
  across any ROM change. Finish with an in-game save before
  upgrading a hack.

## Current hacked ROMs in the library

| ROM | Hack | Base recovered from | Backup |
| --- | --- | --- | --- |
| `roms/gba/Sonic Advance 3 (USA) (...).gba` | Sonic Advance 3 SP v1.03 ([astromuseum.org](https://astromuseum.org/sonicZone/sonicmods/sonicadvance3)) | `#snapshot/GMT-03-2026.06.20-22.00.01` | `<name>.gba.sp1.02.bak` (SP v1.02) |

CRCs: pristine base 16 777 216 B; SP 1.02 = `740D245C`;
SP 1.03 = `B4EE8EA9` (17 284 532 B).
