# HD texture packs (Dolphin + Azahar)

Optional Ansible flow that takes the HD texture zips you keep on the
NAS, extracts just the texture subtree (skipping the bundled
Windows-portable-emulator install each pack ships with), and symlinks
the per-game-ID dirs into the emulators' user data trees inside the
gaming distrobox.

Twilight Princess is handled separately by `install-dusk.yml` — the
ZTP "PC Version" pack targets Dusk specifically, not Dolphin.

```sh
ansible-playbook install-hd-textures.yml
```

## Source: Henriko Magnifico's Patreon

The Dolphin and Azahar packs this playbook expects are Henriko
Magnifico's 4K AI-upscaled releases, distributed via his Patreon:

  https://www.patreon.com/cw/henrikomagnifico

The free tier ships older revisions; the paid tiers ship the latest
revisions and access to the WIP packs. The archives are large
(1–5 GB each) and ship as Windows-portable emulator installs — the
texture subtree is buried under `<wrapper>/(User/)?Load/Textures/<id>/`
and the rest of the zip is a redistributed Citra/Dolphin binary we
don't need on Linux. The role's `unzip_pattern` extracts only the
texture subtree.

To add a pack: download the zip from Patreon, drop it at the
configured `archive:` path on the NAS (see `dg_hd_texture_packs` in
`ansible/group_vars/all/hd_textures.yml`), re-run the playbook.

## Storage model

```
NAS (canonical):
  /mnt/terachad/Emulators/HD-textures/dolphin-textures/
    *.zip                                  ← source archives from Patreon
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
| A Link Between Worlds 4K 2.0b | Azahar | `00040000000EC200`, `EC300`, `EC400` |
| Majora's Mask 3D 4K 3.0b-1 | Azahar | `00040000000D6E00`, `0004000000125500`, `125600` |
| Ocarina of Time 3D 4K 4.0 | Azahar | `0004000000033400`, `033500`, `033600` |
| Super Mario 3D Land 4K 1.2.0b | Azahar | `0004000000053F00`, `054000` |

Dolphin's 3-char IDs are "match-any-region" — Dolphin matches the
prefix against the full 6-char `<GameID><Region><Maker>` form of the
running disc. Azahar uses Citra's full 16-hex TitleID, but Henriko's
packs only populate one region's dir (the other region dirs in the
zip are 0-file placeholders, see below).

## "Populated dir" symlink strategy (Azahar)

Each Henriko Azahar pack only ships actual textures for **one region**
(typically the maintainer's primary build); the other region dirs in
the zip are empty placeholders. Which region is populated is
inconsistent across packs:

| Pack | Populated region |
|---|---|
| OoT3D | `0004000000033500` |
| MM3D  | `0004000000125500` |
| ALBW  | `00040000000EC300` |
| SM3DL | `0004000000054000` |

The role detects the most-populated dir per pack (by file count) and
points **every** region TitleID's symlink at that single dir. Texture
lookup inside Citra/Azahar is hash-keyed on the runtime texture
contents — not on TitleID matching — so once the emulator opens its
`load/textures/<your-runtime-TitleID>/` dir, the hashes match
regardless of which region the pack was authored for.

Without this collapse, dumps that didn't happen to match the
maintainer's region would silently fail to load (the symlink resolved
to an empty placeholder dir).

## Per-emulator enable knobs

- **Dolphin** — `~/.config/dolphin-emu/GFX.ini` already has
  `HiresTextures = True` + `CacheHiresTextures = True`. Nothing for
  the role to flip.

- **Azahar** — texture toggles live in `[Utility]` in
  `~/.config/azahar-emu/qt-config.ini` (Citra/Azahar convention) —
  **not** `[Renderer]`. The role:

  - Writes to `[Utility]`:
    - `custom_textures = true` — enable replacement
    - `preload_textures = false` — see below
    - `async_custom_loading = true` — non-blocking load on first
      texture encounter
  - Scrubs any stale duplicates these keys may have left in
    `[Renderer]` (earlier role versions wrote there by mistake, and
    Azahar reads them from `[Utility]`).

  These flips only happen when at least one Azahar pack symlink
  actually landed under `dg_hd_azahar_textures_dir`; re-runs without
  packs leave the config untouched.

## Why `preload_textures = false`

The 4K Zelda packs are 3+ GB each (3.6 GB for OoT3D, 3.4 GB for MM3D).
With `preload_textures = true`, Azahar tries to load every PNG into
memory at game start; on the 4K packs this either takes minutes or
deadlocks Azahar at a black screen after the progress bar finishes
(VRAM/RAM ceiling, depending on driver and pack).

`preload_textures = false` + `async_custom_loading = true` makes
Azahar stream textures on-demand — small one-time stutter the first
time the game touches each texture, then cached for the session. This
is the trade-off that actually works for these pack sizes.

The Super Mario 3D Land pack is small enough (161 MB) that
preload would work fine for it, but the role uses one global setting
across all Azahar packs.

## Idempotency

- Extraction skipped per-pack when `<pack-extract-dir>/.dg-extracted`
  exists — the marker is touched after a successful first extract.
- Symlinks use `state: link, force: true` — Ansible only marks them
  changed when the target actually differs.
- Azahar's `ini_file` calls use `no_extra_spaces: true` so re-runs
  don't churn the file fighting against Qt's no-spaces format.

## Known issue — Henriko's Azahar packs don't load on this setup

As of May 2026, the four Azahar packs (OoT3D 4.0, MM3D 3.0b, ALBW 2.0b,
SM3DL 1.2.0b) do **not** actually replace textures on this box despite
the role putting everything in place. Diagnostic evidence:

- Pack `pack.json` is read successfully (Azahar's `ReadConfig` doesn't
  log the "using legacy defaults" fallback).
- `material_map` is populated (texture files parsed; only the expected
  ~4 inner-pack hash-collision warnings fire — not parse failures).
- `dump_textures = true` test: Azahar dumps surfaces at runtime using
  the same hash function it uses for lookup (proven — 30 of 44 dumped
  hashes are exactly the hashes from the "Unable to find replacement"
  warnings).
- 0 of those runtime hashes appear in the pack's filenames, across
  USA Rev 0, USA Rev 1 (OoT3D) and Japan Rev 2 (SM3DL) dumps.

All three current Citra-lineage forks (Azahar, Lime3DS, Mandarine) use
CityHash64 for texture hashing — verified in source — so it isn't a
fork-algorithm mismatch. The Citra original repo has been deleted, so
it's no longer possible to verify whether the original Citra release
used a different algorithm Henriko built against.

**Working theory:** Henriko's pack was authored from ROM dumps that
produce different texture-byte layouts than No-Intro / publicly
available dumps. Setup is correct end-to-end, but the bytes don't
match. The fix path is contacting Henriko on Discord with the
"0 of N runtime hashes match the pack" evidence; he'll know what
dump source he used.

**What works for these games today**: the Ansible setup still gives
you the games running at 4× internal resolution via Azahar's
`resolution_factor`, anisotropic filtering, and the anime4k texture
filter. That alone gives a substantial sharpness boost over native
400×240, just without the hand-painted Henriko textures.

## Caveats

- The `unzip_pattern: "*/Load/Textures/*"` (or `*/load/textures/*` for
  Azahar) filter pulls only the texture subtree — about 1/3 of the
  archive size on average.
- If a pack's Wii/GameCube ID is `RVZ`/`WBFS`-only on your disc dump
  (e.g. Dolphin recognises the dump but its game ID enumeration
  differs), the symlink target won't load. Verify by launching the
  game in Dolphin and checking `~/.local/share/dolphin-emu/Logs/`
  for "loaded N hires textures" messages.
- Storage cost on NVMe is zero (all symlinks); NAS cost is the
  unpacked footprint of the texture subtrees (~12–16 GB total
  across all 8 packs).
- If you switch the SDL controller GUID for Azahar's bindings (or use
  a different pad), the `dg_azahar_controller_guid` in
  `group_vars/all/azahar.yml` is the override knob — that's an Azahar
  concern, not a textures concern, but they share the same qt-config.
