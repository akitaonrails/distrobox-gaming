# PS3 library (ES-DE + RPCS3)

ES-DE's `ps3` system (added in `dg_esde_systems`) scans
`roms_heavy/ps3` for **directories named `<Title>.ps3`** — ES-DE treats
a directory whose name matches a listed extension as one launchable
entry — and boots them with `rpcs3 --no-gui %ROM%`. RPCS3 accepts the
folder path directly for both disc dumps (`PS3_GAME/USRDIR/EBOOT.BIN`)
and hdd/PSN layouts (`USRDIR/EBOOT.BIN`).

## Game format rules

| Format on hand | Playable? | What to do |
| --- | --- | --- |
| Extracted disc folder | ✅ | Name the dir `<Title>.ps3`, done |
| PSN `.pkg` | after install | Install via RPCS3 (see below), then symlink |
| PS3 `.iso` (decrypted) | after extract | `7z x -o'<Title>.ps3' file.iso` |
| PS3 `.iso` (encrypted) | no | Needs the disc key (`ps3dec`) first |

Check whether an ISO is decrypted: extract `PS3_GAME/USRDIR/EBOOT.BIN`
and look at the first bytes — `53 43 45 00` (`SCE\0`) means decrypted;
random bytes mean encrypted. The `Headers Error` + 64 KiB tail 7-Zip
reports on PS3 UDF images is cosmetic; extraction is still complete.

## PSN packages (dev_hdd0 games)

PSN games can't be launched from a `.pkg`; they must be installed into
RPCS3's virtual HDD (box-local, `~/.config/rpcs3/dev_hdd0/game/<ID>`):

```sh
# close any running RPCS3 first — a second instance silently
# swallows the CLI arg and nothing installs
rpcs3 --installpkg <Game>.Install.pkg   # then the Crack/NoDRM pkg too
```

Then expose it to ES-DE with a symlink in the roms tree:

```sh
ln -sfn ~/.config/rpcs3/dev_hdd0/game/<ID> \
  "<roms>/ps3/<Title> (<ID>).ps3"
```

**Caveat:** dev_hdd0 lives in the box home on the NVMe, so a box
rebuild wipes the installed game and leaves the symlink dangling —
reinstall the pkgs (kept on the NAS) and the link comes back to life.
This is deliberately **not** automated in Ansible: `--installpkg`
needs a GUI session and fails silently under contention, so it's a
poor fit for an idempotent playbook task. The pkg sources stay on the
NAS; reinstalling is a one-minute manual step.

## Library fixes applied (2026-07-07)

- Renamed 3 disc dumps missing the `.ps3` suffix (DiRT, DiRT 2,
  Ultimate Marvel vs. Capcom 3).
- **18 Wheeler - American Pro Trucker** was not a PS3 game at all —
  bin/cue with `SLUS_202.10` header, i.e. the **PS2** release; moved to
  `roms_heavy/ps2` (bin renamed to match its cue).
- **Splinter Cell Pandora Tomorrow HD** (NPEB00528): installed both
  PSN pkgs into dev_hdd0, symlinked into the roms tree. Boot verified
  (reached the rendering thread; the "reconnect controller" dialog was
  just the pad being asleep).
- **Ultra Street Fighter IV**: 19 GB decrypted ISO extracted to
  `<Title>.ps3` folder form (RPCS3 doesn't read PS3 ISOs). Boot
  verified — LLVM PPU/SPU compilation started from the extracted
  files. The original `.iso` dir remains alongside (unsuffixed, so
  ES-DE ignores it); delete it manually if the space matters.

## Debugging notes

- RPCS3's process comm is **`AppRun.wrapped`** (AppImage), so
  `pgrep -x rpcs3` never matches — check `AppRun.wrapped`, the window
  class, or `~/.cache/rpcs3/RPCS3.log` (box home).
- `--no-gui` boots print little to stdout; the real verdict is always
  in `RPCS3.log` (`Boot path:`, PPU compile lines, `·E` entries).
