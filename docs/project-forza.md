# Project Forza Plus (FM2 / FM3 / FM4) on Xenia

Community-made overhaul packs for the three Xbox 360 Forza Motorsport titles,
by u/Gas-and-Games on Reddit. They retune physics, turbo/supercharger
behaviour, classes, AI, fuel/tire wear, include all DLC content, and ship
four career modes (Normal / Hard / Sandbox / Vanilla).

- **Reddit thread:** https://www.reddit.com/user/Gas-and-Games/comments/17b9k70/the_project_forza_plus_motorsport_collection_is/
- **Engine/turbo spreadsheet:** https://docs.google.com/spreadsheets/d/1vJUIEwg9lau_pUKfdCLb0hYN1nz4JMHLXVGEfJUPSMY/edit
- **Install guide for Xenia generally:** https://gist.github.com/DustinEdenYT/5ec0e3f13a68fd848715a1f1821da9d7 (referenced in comments)
- **Donate:** `@projectforzaplus` on Venmo

This repo already provides Xenia Manager via `install-xenia.yml`. Project
Forza runs against the extracted Xbox 360 game files inside the Xenia prefix,
not through a Steam install.

## Local file layout

```
/mnt/terachad/Emulators/
├── Project Forza 2/
│   ├── Project Forza Plus 2/            # base v1.0 — first time install
│   │   ├── Main Game Changes/           # default.xex + Media/ + PhysicsSettings.ini samples
│   │   ├── DLC Cars and Tracks/Media/   # merge into game files
│   │   ├── Game Mode DBs/               # Normal / Hard / Sandbox / Vanilla (gamedb.slt each)
│   │   ├── Information and Instructions/# six .txt docs
│   │   └── xenia-canary.config.toml     # pack-specific Xenia config
│   ├── Project Forza Plus 2 Update/     # v1.2 update (for existing installs)
│   ├── Project Forza Plus 2 v1.2.zip    # zipped base
│   └── Project Forza Plus 2 v1.2 Update.zip
│
├── Project Forza 3/
│   ├── isoextract/ + isoextract.rar     # Xbox 360 XISO Extract tool
│   ├── Project Forza Plus 3/            # Main Game Changes/ + Disc 2 and DLCs/00000002/ + Game Mode DBs/ + toml
│   ├── Project Forza Plus 3 Update/
│   ├── Project Forza Plus 3 v1.2.zip + v1.2 Update.zip
│
└── Project Forza 4/
    ├── FM4-Fix_byAlexwpi/               # Alex's separate shadow/lighting fix (unused if using PFP-4)
    ├── Forza 4 disc 1/                  # pre-extracted disc 1 ISO
    ├── Forza 4 disc 2/                  # pre-extracted disc 2 ISO
    ├── Project Forza Plus 4/            # Main Game Changes/ + Disc 2 and DLCs/00000002/ + Game Mode DBs/ + toml
    ├── Project Forza Plus 4 Update/
    ├── xenia_master/                    # bundled portable Xenia (alternative to Xenia Manager)
    └── Project Forza Plus 4 v1.2.zip + v1.2 Update.zip
```

## Xenia requirements

Pack readmes explicitly say:
> *Xenia Canary Experimental build `50fce8b` from **Oct 5, 2022** is
> recommended.*

Newer Canary builds may crash on loading screens (the Alps map right after
Clarkson's intro is a known crash point on current Canary) and may have
audio issues (verified in the thread). The bundled `xenia-canary.config.toml`
ships with settings tuned for that old build.

Xenia Manager (installed by this repo's `install-xenia.yml`) lets you
manage multiple Canary versions — install Canary from the Manage page, then
either pick the Oct-2022 build if it's selectable or use Xenia Manager to
install a historic build manually. The bundled `/mnt/terachad/Emulators/Project Forza 4/xenia_master/`
is a portable Xenia that can be used directly as a fallback.

## Install procedure per game

### Forza Motorsport 2 (Project Forza Plus 2)

Game files already live in the user's `Project Forza 2` NAS dir. If starting
fresh with only the ISO, the prep step is:

1. Use `Xbox 360 XISO Extract` (see the
   https://digiex.net/threads/xbox-360-xiso-extract-best-an-easiest-xdg3-extraction-tool-with-gui-ftp.9711/
   link in the readme; the tool is also in the user's `Project Forza 3/isoextract/` dir).
2. Extract `FM2.iso` into a folder somewhere under `$DG_BOX_HOME/wineprefixes/xenia-manager/`
   or another path accessible to Xenia.
3. Keep a copy of the vanilla extracted files — the mod is destructive
   (overwrites `default.xex` and merges into `Media/`).

Apply the mod (from `Project Forza Plus 2/`):

1. Copy `Main Game Changes/default.xex` over the extracted game's `default.xex`.
2. Copy `Main Game Changes/Media/*` over the extracted game's `Media/`, letting
   files replace.
3. Copy `DLC Cars and Tracks/Media/*` over the extracted game's `Media/`.
4. Replace Xenia's `xenia-canary.config.toml` with the one bundled in the
   pack (save a copy of your existing one first if you share Xenia with
   other games).

Run `default.xex` through Xenia.

### Forza Motorsport 3 (Project Forza Plus 3)

Same prep (ISO → extract → back up vanilla files). Then:

1. Copy `Main Game Changes/default.xex` and `Main Game Changes/Media/*` over
   the extracted game.
2. Replace Xenia's `xenia-canary.config.toml` with the bundled one.
3. Boot FM3 **once** in Xenia (File → Open `default.xex`) so Xenia creates
   its `content/` folder.
4. Close Xenia.
5. Copy `Disc 2 and DLCs/00000002/` into
   `<Xenia>/content/4D53084D/00000002/`.
   (`4D53084D` is FM3's title ID.)
6. Launch the game.

Per the readme: *"Even if you have the DLC already, using my versions of the DLC
is necessary for the changes to be applied."*

### Forza Motorsport 4 (Project Forza Plus 4)

Same prep. FM4 USA release needs BOTH discs extracted (the user already has
them as `Forza 4 disc 1/` and `Forza 4 disc 2/` on the NAS). Disc 1 carries
`default.xex`; disc 2 carries extra tracks and cars.

1. Copy `Main Game Changes/default.xex` and `Main Game Changes/Media/*` over
   the extracted game.
2. Replace Xenia's `xenia-canary.config.toml` with the bundled one.
3. Boot FM4 once so Xenia creates `content/4D530910/` (FM4's title ID).
4. Close Xenia.
5. Copy `Disc 2 and DLCs/00000002/` into
   `<Xenia>/content/4D530910/00000002/`.
6. Launch.

## Applying the v1.2 update (for existing installs)

Separate ZIP per game. Replace the listed files in your already-installed
game — do not re-apply the base:

- **PFP-2**: replace `Game Mode DBs/*/gamedb.slt` in your `db/` folder.
- **PFP-3**: replace `Game Mode DBs/*` in `db/`, and replace `PI.xml` in the
  game's `physics/` folder.
- **PFP-4**: same as PFP-3, plus replace `GameTunableSettings.ini`.

See each pack's `Instructions and Info/Instructions - Update Install.txt`
for the exact list; the v1.2 notes mention tire physics, PI value
rebalance, X-class 1-point-range, and the "Skip Intro Saves" ForzaProfile
that lets you skip the opening intro race. **Important: the update zips are
NOT redistributable replacements of the base** — a fresh install uses the
base v1.2 zip directly.

## Four career modes

Switch by **copying** (not moving) the chosen mode's `gamedb.slt` file into
the game's `db/` folder.

| Mode | Behaviour |
|---|---|
| **Normal** | Default. All events/cars unlocked, no reward cars, AI braking/cornering buffed. |
| **Hard** | Start in F (PFP-3/4) or D (PFP-2) class only. Unlock next class every 5 levels (PFP-2/3) or 8 levels (PFP-4). Events 50% longer. Earnings halved (PFP-3/4). |
| **Sandbox** | All cars and upgrades cost 1 credit. Build whatever. |
| **Vanilla** | Vanilla career, only the car-stat changes retained. |

FM3 and FM4 also have per-mode DLC DB folders that need to be copied into
`content/<TID>/00000002/` alongside the base files when switching modes.

For separate save slots per mode, keep separate copies of `00000001` per
mode and swap in as needed.

## Recommended Xenia settings (for the old Oct 2022 build)

From the pack's `Instructions - Best Visual Quality.txt`:

Edit `xenia-canary.config.toml` `[Display]` section:

- `internal_display_resolution = 16` (higher internal resolution, the value
  `16` is explicitly documented as a 16x mode)
- `postprocess_scaling_and_sharpening = "fsr"`
- `postprocess_ffx_fsr_sharpness_reduction = 0.15`

Hardware reference: author tested at 100 fps with Ryzen 7 3700X + RTX 3060
+ 32 GB DRAM at ~30% CPU / ~50% GPU.

For higher frame rates, set `vsync_interval` to a value from the following
table — **and** also replace `PhysicsSettings.ini` with the matching
`Main Game Changes/PhysicsSettings.ini for higher fps/<fps>/PhysicsSettings.ini`
variant, otherwise AI and physics break.

| `vsync_interval` | Target fps |
|---|---|
| 6 | 166 |
| 7 | 133 |
| 8 | 111 |
| 10 | 95 |
| 12 | 83 |
| 13 | 74 |
| 14 | 67 |
| 16 | 62 (default) |

For a rate **between** rows, pick the nearest-above value and cap fps with
NVIDIA Control Panel / MangoHud.

## Known issues (per-game)

### PFP-2
- Some factory forced-induction cars' torque/power numbers don't match what
  the buy-car menu shows.
- Factory wheel options have no thumbnails.
- Buy-menu car stats don't match post-purchase stats (tire-grip change side
  effect).
- DLC cars may be missing model names and DLC tracks may be missing preview
  maps (version-dependent).
- Tires sometimes clip through body on hard bumps.
- DLC cars are **locked in Arcade mode**. Workaround: buy the car in career
  mode first.

### PFP-3
- Factory supercharged cars make slightly more horsepower than listed
  (physics tradeoff: accurate-torque vs accurate-power).
- Factory wheels have no thumbnails; DLC car wheels may be doubled.
- Buy-menu stats vs real stats mismatch.
- Street forced-induction upgrades show an "aspiration conversion" that's
  effectively a no-op.
- **Game Station Mitsubishi Evo X pre-order car has corrupted body panels
  and causes infinite loading screen. Do not select it.**

### PFP-4
- Same factory-SC horsepower story as PFP-3.
- Factory wheel thumbnails missing.
- Buy-menu stats mismatch.
- Street FI upgrades show a no-op aspiration conversion.
- **Race transmissions + Automatic shifting difficulty → CVT-like
  behaviour.** Use Manual or Manual+Clutch instead.

### All three
- Any graphical glitch is Xenia-side, not a pack bug.

## FM4 Xenia Canary settings (April 2026)

This repo's FM4 setup runs on current **Xenia Canary** (post-Oct-2022,
fully-updated April 2026) under Wine+Vulkan on NVIDIA. The Oct-2022
`50fce8b` build is no longer required. Set all of these in the Xenia
Manager per-game toml for FM4 (NOT in the root `xenia-canary.config.toml`
— see below for why):

| Key | Value | Fixes |
|---|---|---|
| `gpu` | `"vulkan"` | Required under Wine (no VKD3D path) |
| `render_target_path_vulkan` | `"fsi"` | **Fixes psychedelic magenta/pink dither on car paint and windows** — FSI handles all pixel formats correctly in-shader; default `fbo` is documented as lower accuracy |
| `snorm16_render_target_full_range` | `false` | Part of the same paint fix — stops -32..32 → -1..1 remap that breaks multiplicative blending on 16_16 RTs |
| `use_fuzzy_alpha_epsilon` | `true` | Part of the same paint fix — documented as "prevent flickering on NVIDIA graphics cards" |
| `gpu_allow_invalid_fetch_constants` | `true` | Fixes black/glitched rear-view + side mirrors |
| `query_occlusion_sample_lower_threshold` | `-1` | Stops lights rendering through walls |
| `apu` | `"sdl"` | Fixes choppy audio on newer Canary |
| `apu_max_queued_frames` | `3` | Reduces audio delay (PFP-recommended) |
| `use_dedicated_xma_thread` | `false` | Better XMA decoding results |
| `xma_decoder` | `"new"` | Default in recent Canary |
| `postprocess_scaling_and_sharpening` | `"fsr"` | PFP "Best Visual Quality" |
| `postprocess_ffx_fsr_sharpness_reduction` | `0.15` | PFP value |
| `postprocess_antialiasing` | `"fxaa"` | Recommended when FSR is on |
| `internal_display_resolution` | `16` | 1080p internal (PFP doc) |
| `logged_profile_slot_0_xuid` | `"<your XUID>"` | Auto-signs-in profile so saves get confirmed (games reported "can't save" without this) |
| `apply_title_update` | `true` | Loads Title Update 8 |
| `mount_cache` | `true` | Stops crash when starting a race |

The **FSI / snorm16 / fuzzy alpha** combo is the critical car-paint fix
confirmed under current Canary on NVIDIA. Reproduces in vanilla
Essentials Edition too — the bug is not PFP-4-related.

**Xenia Manager's two FM4 config files trap**: when Xenia Manager adds
a game whose title already exists, it appends ` (1)`, `(2)` etc. and
creates a distinct per-game toml per suffix. `games.json`'s
`file_locations.config` field tells you the exact filename the active
entry uses — always check it before editing, otherwise you edit a file
XM never loads.

**Asset layout (FM4 specifically)**: the disc-1 extract gives you the
bulk of `Media/` but `Media/xui/` (fonts), `Media/ui/` (marketplace
textures), and the lowercased-language `Media/stringtables/` come from
disc 2. Without disc 2's `media/*` merged in, FM4 hangs at main-menu
load with the log repeatedly emitting `Stub XFileSectorInformation!`.
Extract disc 2 separately and `rsync` its `media/` into the install's
`Media/` (renaming `UI` → `ui` and `StringTables` → `stringtables` on
the install side first, to avoid case-duplicated dirs on Linux). The
`content/0000000000000000/4D530910/00000002/` and TU8
`000B0000/tu00000008_00000000` also need to be dropped into Xenia's
content tree (can be symlinks to the staged dirs in the install).

## Community-reported fixes (from Reddit comments)

- **Audio is choppy on newer Canary**: set `apu = "sdl"` and
  `apu_max_queued_frames = 3` in the toml. Already baked into the bundled
  toml.
- **Crash on Alps map after Clarkson intro on current Canary**: confirmed
  by author. Two options:
  1. Use the recommended Oct-2022 Canary build.
  2. Use the "Skip Intro Saves" from the v1.2 update — drag a
     `ForzaProfile/` folder from the update into FM4's
     `content/4D530910/00000001/` (pick the starter car you want).
- **"PIs are wrong / starter car shows class E"**: the `PI.xml` from the
  v1.2 update pack wasn't copied into the game's `physics/` folder. Re-run
  the update install step 2 for PFP-3 and PFP-4.
- **Square shadows / bright track textures**: the `Media/tracks/` folder
  wasn't properly merged. Re-copy `Main Game Changes/Media/` over the
  extracted game. One user also reported `readback_resolve` toml option
  helped them — read the trailing value from the thread if needed.
- **Save transfer across installs**: copy the `00000001` folder from the
  old `content/<TID>/` to the new one. The content folder itself is not
  recreated on a fresh game install.

## FOV tweaks

Per `Instructions - Changing Camera FOV.txt`: edit
`Media/Camera/CameraSettings.ini` in the extracted game files. Keys by
speed band (0 = 20–100 mph, 1 = 100–150, 2 = 150+):

- `FollowLowCam\FOV0,1,2` — Chase close
- `FollowHighCam\FOV0,1,2` — Chase far
- `HoodCam\FOV0,1,2` — Hood
- `BumperHighCam\FOV0,1,2` — Bumper

## FM4-Fix by alexwpi (separate, optional)

The Forza 4 dir also contains `FM4-Fix_byAlexwpi/` — a separate community
fix by Alex from
https://www.youtube.com/channel/UCuLIiCzUfWYS67hXBjIEAdA that overrides
`Media/RenderScenarios/` and `Media/tracks/` to address shadow/lighting
issues. **Not compatible with PFP-4 by default** since PFP-4 also ships a
`Media/` tree that touches those dirs. Pick one or merge carefully by
hand. Alex's Patreon: https://www.patreon.com/alexwpigame.

## Not automating in Ansible

Unlike the PCSX2 texture packs (which we data-drove into
`group_vars/all/pcsx2.yml`), Project Forza is intentionally left as a
manual install workflow because:

1. **Destructive file merges**: the mod overwrites parts of extracted game
   data (`default.xex`, `Media/`). Automating destructive merges on NAS
   paths is risky.
2. **Per-user game-mode choice**: which of the four modes you want is a
   runtime preference, not something to pre-commit.
3. **Xenia Manager owns the version story**: using a specific Canary
   build (Oct 2022 or current) is handled through Xenia Manager's GUI,
   not our Ansible layer.
4. **The pack already ships its own `xenia-canary.config.toml`** — just
   drop it in the Xenia directory.

If you later want per-game Xenia config automation, the handle is the
bundled TOML in each pack dir — the Ansible flow would be: symlink the
pack's toml over the portable Xenia's active config when launching that
game. Not worth the complexity for three games you install once.

## References

- Reddit OP: https://www.reddit.com/user/Gas-and-Games/comments/17b9k70/the_project_forza_plus_motorsport_collection_is/
- Engine/turbo data spreadsheet: https://docs.google.com/spreadsheets/d/1vJUIEwg9lau_pUKfdCLb0hYN1nz4JMHLXVGEfJUPSMY/edit
- Project Forza Plus 2 Drive: https://drive.google.com/drive/folders/1BgE2vpcPsV9jJljtyQxHxC8cTqT_VWu2
- Project Forza Plus 3 Drive: https://drive.google.com/drive/folders/1Y5tMoUlGCW4D7bQclb6oYDjZoUkMl6nN
- Project Forza Plus 4 Drive: https://drive.google.com/drive/folders/1MRU5_j-atZquvy4iEXOdYfXiNvzlsPqy
- ISO extraction tool: https://digiex.net/threads/xbox-360-xiso-extract-best-an-easiest-xdg3-extraction-tool-with-gui-ftp.9711/
- DustinEden's general Xenia install guide: https://gist.github.com/DustinEdenYT/5ec0e3f13a68fd848715a1f1821da9d7
- ROM archive referenced by OP: https://archive.org/download/microsoft_xbox360_f_part2
