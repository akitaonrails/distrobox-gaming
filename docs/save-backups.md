# Save-data backup & restore

Emulators and PC ports scatter their save games, memory cards, save states and
NAND user-saves across `~/.config` and `~/.local/share` inside the box (and, for
libultraship ports, next to the app). Because the box's `$HOME` is a bind-mount
that survives a container rebuild, those saves usually persist — but if you ever
wipe or re-provision from scratch you'd lose them. This system mirrors them to
the NAS and restores them on demand.

## Where it goes

`dg_backup_root` (default **`/mnt/terachad/Emulators/distrobox-gaming/backup/saves`**,
= `{{ dg_external_games_root }}/distrobox-gaming/backup/saves`) — one subdirectory
per save set. Override in `host_vars/localhost.yml` if your NAS differs.

## Back up (run from time to time)

Best with games closed. From the host:

```sh
distrobox enter gaming -- bash -lc '$HOME/bin/backup-saves'            # back up everything
distrobox enter gaming -- bash -lc '$HOME/bin/backup-saves --dry-run'  # preview
```

It rsyncs every save set that has local data to `dg_backup_root/<name>/`. Sets
with no data yet are skipped. Nothing is deleted from the backup, so it only
accumulates — a deleted local save stays recoverable.

## Scheduled weekly backup (systemd user timer)

A **systemd user timer** runs the backup every **Tuesday at 23:00** (with a small
randomized delay, `Persistent=true` so a missed run — machine off/asleep — fires
at next login). Install/update it from the host:

```sh
scripts/install-save-backup-timer.sh            # install + enable
scripts/install-save-backup-timer.sh --uninstall
```

It deploys `~/.local/bin/dg-save-backup` (an env-robust wrapper: absolute PATH,
NAS-mount guard, `distrobox enter gaming -- backup-saves`) plus the
`dg-save-backup.{service,timer}` user units, then enables the timer. Check /
run / read it:

```sh
systemctl --user list-timers dg-save-backup.timer   # next run
systemctl --user start dg-save-backup.service       # run now
journalctl --user -u dg-save-backup.service -e       # logs
```

User timers fire while you're logged in; since it's a desktop that's normally
the case, and `Persistent=true` covers the rest. To run even when logged out,
`sudo loginctl enable-linger $USER`. The units live in
`scripts/systemd/` in this repo, so a rebuild just re-runs the installer.

## Restore (after a from-scratch remount)

```sh
cd ansible
ansible-playbook site.yml                    # rebuild the box first
ansible-playbook restore-saves.yml           # then pull saves back from the NAS
# or directly:
distrobox enter gaming -- bash -lc '$HOME/bin/restore-saves'
```

**Safe by default:** `restore-saves` uses `--ignore-existing`, so a save already
on the box is never overwritten (a fresh box gets everything; an existing box
only gains what it's missing). Flags:

- `--update` — replace a local save only if the backup copy is newer
- `--force` — overwrite local saves with the backup unconditionally
- `--dry-run` — preview

`ansible-playbook site.yml` also restores automatically when you set
`dg_restore_saves_on_setup: true` (host_vars or `-e`); it's off by default so a
normal run never touches saves.

## What's covered

The inventory is **data-driven** — `dg_save_sets` in
`ansible/group_vars/all/backups.yml`, one `{name, src}` per directory (src is
relative to the box `$HOME`). Currently: RetroArch (saves + states), PCSX2,
DuckStation, Dolphin (GC/Wii/states), Flycast VMU, xemu, RPCS3 (`dev_hdd0/home`),
PPSSPP, Azahar (sdmc + nand), melonDS, Eden (`nand/user/save` only — **not** the
79 GB nand), Cemu, shadPS4 savedata, Supermodel NVRAM, Xenia content (per-title
`00000001` savegames + installed TUs/DLC; the big DLC entries are symlinks and
stay symlinks), and the native ports/recomps/fan games (Ship of Harkinian &
family, DK64 / GoldenEye / Unleashed recomps, Perfect Dark, DUDE, PrBoom+ RT,
Sonic 3 A.I.R., Star Fox Enhanced, SMW Remastered, SoRR, …).

The `backup_saves` role renders the manifest to
`~/.config/distrobox-gaming/save-manifest.tsv` and the root to `backup.env`,
then deploys the two helpers — it runs as part of `site.yml` (tag
`backup_saves`), so the tooling is always present.

## Adding a new emulator or game

When you install anything with save data, **add its save dir(s) to
`dg_save_sets`** in `group_vars/all/backups.yml` and re-run
`ansible-playbook site.yml --tags backup_saves`. A wrong or not-yet-created path
is harmlessly skipped, so err toward listing it. This keeps the backup complete
as the library grows.

## Notes / gaps

- Entries must be **directories**. All current ones are.
- **Wine/Proton game saves** (PC racing, DriveClub, etc.) live inside their
  wineprefixes' `drive_c/users/.../Documents` / `Saved Games` and are **not**
  covered yet — add specific prefix subpaths to `dg_save_sets` if you want them.
- The helpers need the NAS mounted; they abort cleanly if `dg_backup_root`
  isn't reachable.
