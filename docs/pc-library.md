# PC library layout (`ROMS_FINAL/PC`)

The PC side of the library is not a ROM set — it holds community PC
builds, mods and the game installs the playbooks consume. It is split
into five buckets so a path says what the thing *is*:

| Bucket | Holds | Examples |
|---|---|---|
| `PC/ports/` | Native/exe ports, static recompilations and decompilation projects of **console** games, plus their staged source archives | `ports/DKLR`, `ports/project-r`, `ports/Sonic Legends.zip`, `ports/Project 06 - Silver Release (Patch v1.45)` |
| `PC/games/` | **PC** game installs, repacks and disc extracts (the games themselves) | `games/Richard Burns Rally`, `games/DiRT-2007-RELOADED_Extracted`, `games/SEGA RALLY 2.exe` |
| `PC/mods/` | Mods, texture packs, romhacks, patch kits for a game that lives elsewhere | `mods/NexusMods`, `mods/romhacks`, `mods/RE4HDproject1.1`, `mods/FH2_Extra_Options_*.zip` |
| `PC/releases/` | Upstream release assets a role downloads/verifies (zips, tarballs, installers) | `releases/DOA2U-0.1.6-Alpha-Linux.zip`, `releases/driveclub-recomp-0.3.2-win64.zip`, `releases/GT4Recomp-1.3.0-rc6-portable.zip` |
| `PC/tools/` | Utilities, trainers and installers used across games | `tools/CheatEngine`, `tools/dgVoodoo2_87_2.zip` |

Rules of thumb:

- **Nothing stays in the `ROMS_FINAL/PC` root.** Browser downloads land
  there by default. File every new archive, installer, port or mod into
  its bucket *in the same change that installs it* — never leave it in
  the root "for later", and never point a `dg_*` path at the root.
  `scripts/check-pc-layout.sh <ROMS_FINAL/PC>` flags leftovers and is the
  quick check after any PC install:

  ```sh
  ./scripts/check-pc-layout.sh /mnt/terachad/Emulators/ROMS_FINAL/PC
  # PC layout OK: only ports/ games/ mods/ releases/ tools/ at the root
  ```

- **Leaf names never change.** Directories and files keep their upstream
  names so a path rewrite is mechanical (`PC/<name>` → `PC/<bucket>/<name>`).
- **A role that ships its own release archive** points at
  `PC/releases/…` (`dg_*_zip`, `dg_*_asset`); the extracted, playable
  copy belongs in `PC/ports/…` (console port) or `PC/games/…` (PC game).
- **Mods follow the target game**, not the mod's format: a texture pack
  for a Steam game still goes in `PC/mods/`, ideally under the
  `mods/NexusMods/<game>` tree when it comes from Nexus.
- **Never delete game data on re-org.** Duplicate archives that are
  already unpacked next to their tree, and nothing else, are the only
  safe deletions.
- When you move anything, update every `dg_roms_final_root }}/PC/...`
  reference in `ansible/`, plus the prose in `docs/`, in the same change.
