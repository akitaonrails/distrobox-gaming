# HD texture packs (Dolphin + Azahar)

Optional Ansible flow that takes the Henriko Magnifico HD texture
zips you keep on the NAS, extracts just the texture subtree (skipping
the bundled Windows-portable-emulator install each pack ships with),
and symlinks the per-game-ID dirs into the emulators' user data
trees inside the gaming distrobox.

Twilight Princess is handled separately by `install-dusk.yml` — the
ZTP "PC Version" pack targets Dusk specifically, not Dolphin.

```sh
ansible-playbook install-hd-textures.yml
```

## Storage model

```
NAS (canonical):
  /mnt/terachad/Emulators/HD-textures/dolphin-textures/
    *.zip                                  ← source archives
    extracted/<pack-slug>/                 ← unpacked texture tree (NAS-resident)
      <wrapper-dir>/Load/Textures/<GAMEID>/...
  /mnt/terachad/Emulators/HD-textures/citra-textures/
    *.zip
    extracted/<pack-slug>/
      <wrapper-dir>/load/textures/<TITLEID>/...

Box (inside the distrobox):
  ~/.local/share/dolphin-emu/Load/Textures/<GAMEID>  → symlink to NAS
  ~/.local/share/azahar-emu/load/textures/<TITLEID>  → symlink to NAS
```

Symlinks (rather than copies) keep ~16 GB of texture data off the
NVMe; the kernel page cache absorbs the NFS read latency after the
first time each texture is touched.

## Per-pack catalog

| Pack | Emulator | Game IDs |
|---|---|---|
| Luigi's Mansion 4K 1.1.0b | Dolphin | `GLM` |
| Super Mario Sunshine 4K 2.0c | Dolphin | `GMS` |
| Skyward Sword 4K 1.0.5 | Dolphin | `SOU` |
| Wind Waker 4K 1.0.0d | Dolphin | `GZL` |
| A Link Between Worlds 4K 2.0b | Azahar | `00040000000EC200` (USA), `EC300` (EUR), `EC400` (JPN) |
| Majora's Mask 3D 4K 3.0b-1 | Azahar | `D6E00` (USA), `125500` (EUR), `125600` (JPN) |
| Ocarina of Time 3D 4K 4.0 | Azahar | `033400` (USA), `033500` (EUR), `033600` (JPN) |
| Super Mario 3D Land 4K 1.2.0b | Azahar | `053F00` (USA), `054000` (JPN) |

Dolphin's 3-char IDs are "match-any-region" — Dolphin matches the
prefix against the full 6-char `<GameID><Region><Maker>` form of the
running disc. Azahar uses Citra's full 16-hex TitleID, so each pack
ships separate texture dirs per region; the role symlinks them all.

## Adding a pack

One entry in `dg_hd_texture_packs` (in
`ansible/group_vars/all/hd_textures.yml`), drop the zip at the
referenced `archive:` path on the NAS, re-run the playbook. Examples
above cover both naming conventions; copy whichever line looks
closest to the new pack's emulator.

## Per-emulator enable knobs

- **Dolphin** — `~/.config/dolphin-emu/GFX.ini` already has
  `HiresTextures = True` + `CacheHiresTextures = True`. Nothing for
  the role to flip.
- **Azahar** — `~/.config/azahar-emu/qt-config.ini` ships with
  `custom_textures = false` / `preload_textures = false`. The role
  flips both to `true` only when at least one Azahar pack symlink
  actually landed under `dg_hd_azahar_textures_dir`, so re-runs
  without packs don't churn the config.

## Idempotency

- Extraction skipped per-pack when `<pack-extract-dir>/.dg-extracted`
  exists — the marker is touched after a successful first extract.
- Symlinks use `state: link, force: true` — Ansible only marks them
  changed when the target actually differs.
- Azahar's `ini_file` calls only change when the keys aren't already
  at the desired value.

## Caveats

- The Henriko packs are 1–5 GB each and ship as Windows-portable
  emulator installs. The `unzip_pattern: "*/Load/Textures/*"` (or
  `*/load/textures/*` for Azahar) filter pulls only the texture
  subtree — about 1/3 of the archive size on average.
- If a pack's Wii/GameCube ID is `RVZ`/`WBFS`-only on your disc dump
  (e.g. Dolphin recognises the dump but its game ID enumeration
  differs), the symlink target won't load. Verify by launching the
  game in Dolphin and checking `~/.local/share/dolphin-emu/Logs/`
  for "loaded N hires textures" messages.
- Storage cost on NVMe is zero (all symlinks); NAS cost is the
  unpacked footprint of the texture subtrees (~12–16 GB total
  across all 8 packs).
