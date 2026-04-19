# Required external assets

Paths + filenames that the Ansible roles expect to find for mods,
texture packs, cheat DBs, and DLC PKGs. None of these are shipped with
the repo — legal distribution rules — so copy them onto your NAS /
host disk and then point the relevant `dg_*` variable at your layout
via `ansible/host_vars/localhost.yml`.

**Everything here is optional.** If the source path doesn't exist,
the deploy task either warns and moves on, or the feature stays dark
until you add the asset. Nothing hard-fails.

## How paths are resolved

The defaults in `ansible/group_vars/all/main.yml` point at a
terachad-NAS layout (our machine). To remap for yours, copy
`ansible/host_vars/localhost.yml.example` to `localhost.yml` and set
the root variables. Each variable below lists the *default* path; its
override knob is the first-level `dg_*` root it derives from.

```sh
cp ansible/host_vars/localhost.yml.example ansible/host_vars/localhost.yml
$EDITOR ansible/host_vars/localhost.yml
ansible-playbook site.yml
```

## PS1 / PS2 / PS3 / PS4 game discs (BIOS, ROMs)

**Default roots** (derived from `dg_emudeck_root`):

```
dg_rom_root         → EmuDeck/roms/{psx,ps2,ps3,...}     # .chd/.iso game discs
dg_rom_heavy_root   → EmuDeck/roms_heavy/{xbox360,ps3}  # large ISOs, PKG staging
dg_rom_rare_root    → EmuDeck/roms_rare/{ps4}           # infrequently played
dg_bios_root        → EmuDeck/Emulation/bios            # per-emulator BIOS files
```

You source and copy ROMs into these trees yourself.

## PCSX2 texture packs — GT4 & friends

**Variable:** `dg_pcsx2_ps2_root` (default `/mnt/terachad/Emulators/ps2`).

The `pcsx2_textures` role symlinks from this root into PCSX2's
per-game texture replacements dir. Expected subdir layout:

```
$dg_pcsx2_ps2_root/
├── Gran Turismo 4 Remaster/
│   ├── Gran Turismo 4 HD HUD & UI Texture pack by Silentwarior112/
│   │   └── replacements/                    ← symlinked as hd-hud-ui
│   ├── update 2.1/
│   │   └── replacements/                    ← symlinked as hd-hud-ui-update-2.1
│   ├── HD HUD & U.I. blocky haze fix v2/
│   │   └── text files jap kor usa pal shared/  ← symlinked as blocky-haze-fix
│   ├── 06AD9CA0.pnach                       ← auto-detected .pnach patches
│   └── 44A61C8F.pnach
├── Enthusia/
│   └── SLUS-20967/
│       └── replacements/                    ← symlinked as hd-textures
└── cheats/                                   ← auto-scan for *.pnach
    └── *.pnach
```

### Downloads

| Asset | Link | What you download |
|---|---|---|
| **GT4 HD HUD & UI (Silentwarior112)** | [GTPlanet thread 417873](https://www.gtplanet.net/forum/threads/gt4-hd-hud-and-user-interface-texture-pack-for-pcsx2.417873/) | Base pack, version 2.x-era zips. Extract into `Gran Turismo 4 Remaster/` keeping the `replacements/` subdir. |
| **GT4 HD HUD update 2.1** | same thread, later post | The incremental update; extract as `Gran Turismo 4 Remaster/update 2.1/replacements/`. |
| **GT4 HD HUD blocky haze fix v2** | same thread, fix post | Extract as `Gran Turismo 4 Remaster/HD HUD & U.I. blocky haze fix v2/text files jap kor usa pal shared/`. |
| **GT4 Retexture Mod v3.0.4 (cars/tracks)** | [GTPlanet thread 408852](https://www.gtplanet.net/forum/threads/gran-turismo-4-retexture-mod-v3-0-4.408852/) | Drop into PCSX2's texture dir OR merge into the HD HUD pack — PCSX2 scans all subdirs of `textures/<SERIAL>/replacements/` for hash-named PNGs regardless of subfolder layout. |
| **Silent's GT4 mods** (cameras, triggers, deinterlace) | [Silent's blog](https://silentsblog.com/mods/gran-turismo-4/) | Already pulled from a git raw URL at deploy time — no manual download needed. |
| **Spec II (GT4 community patch, v1.04 Full)** | [TheAdmiester install guide](https://www.theadmiester.co.uk/specii/install.html) | Download `Gran Turismo 4 Spec II (1.04 Full).xdelta` + base **USA Online Public Beta** ISO (MD5 `3306538778dda2ded87ceaf52c944a98`). Patch with xdelta. Output serial `SCUS-97436`, CRC `4CE521F2`. |
| **Enthusia Professional Racing HD textures** | community-sourced | Extract into `Enthusia/SLUS-20967/replacements/`. |

See `docs/gt4-spec-ii.md` and `docs/project-forza.md` for per-mod
usage details.

## DuckStation widescreen cheats for GT2

**Variable:** `dg_libretro_cheats_dir` (default derives from the
terachad mount). The DuckStation `seed_configs` task copies one
`.cht` file per game out of this tree.

Required file: `$dg_libretro_cheats_dir/Sony - PlayStation/Gran Turismo 2 USA (v1.2) (Duckstation).cht`

### Download

Clone the full libretro cheat DB:
```sh
git clone --depth 1 https://github.com/libretro/libretro-database.git /path/to/libretro-database
# then in host_vars/localhost.yml:
# dg_libretro_cheats_dir: /path/to/libretro-database/cht
```

The task enables the 12 widescreen-related cheats automatically; leave
the rest off. See `docs/gt2-duckstation.md` for details.

## PS3 PKG DLC/patches

**Variable:** `dg_ps3_dlc_source` (default
`{{ dg_rom_heavy_root }}/ps3-DLC`).

Layout: one subdir per title ID, each containing update PKG files.
```
$dg_ps3_dlc_source/
├── BCES01893/                        ← Gran Turismo 6 (EU)
│   └── EP9001-BCES01893_00-*.pkg   ← one per version (1.02 → 1.22)
├── BCUS98114/                        ← Gran Turismo 5 (US)
│   └── *.pkg
├── BLES00246/                        ← Metal Gear Solid 4
│   └── *.pkg
└── ...
```

The `install_dlcs` role detects patch version from the filename
(`-A<major><minor>-` pattern) and routes patches to the title-ID dir
(`/dev_hdd0/game/<TID>/`), DLC PKGs to the content-ID dir. The
`PER_GAME_MAX_VERSION` dict in `extract_ps3_dlc.py` caps GT6 at v1.05
regardless of what PKGs you have.

### Where to get PKGs

- Official updates (through 2018 when PSN GT6 servers closed): use
  `nopaystation.com` / community archives. The repo's
  `install_dlcs/files/check_ps3_updates.py` can list the expected PKG
  filenames per serial from `ps3.aldostools.org`.
- Paid DLC requires RAP files — `extract_ps3_dlc.py` only handles
  unencrypted/free PKGs (type 0x0001 without RAP dependency).

## Switch NSP updates

**Variable:** `dg_switch_updates_source` (default
`{{ dg_rom_heavy_root }}/switch_updates`).

Drop `.nsp` update files into subdirs; the `install_dlcs` role
extracts them into Eden's NAND tree. BIOS files (prod.keys,
title.keys) go into Eden's firmware dir — see Eden docs.

## Xbox 360 / Forza assets

**Variable:** `dg_rom_heavy_root` + its `xbox360/` subdir.

```
$dg_rom_heavy_root/xbox360/
├── FM2 (Project Forza Plus Modded)/   ← extracted from ISO, PFP patch applied
├── FM3 (Project Forza Plus Modded)/
├── FM4 (Project Forza Plus Modded)/
├── Forza Horizon*.iso
└── <regular ISOs for other 360 titles>
```

Xenia Manager auto-indexes `xbox360/`. See `docs/project-forza.md` for
the PFP install flow — downloads are from the PFP author's Google
Drive links (listed at the end of that doc).

## Xbox (original) BIOS

**Variables:** `dg_xemu_bootrom_source`, `dg_xemu_flashrom_source`,
`dg_xemu_hdd_source` (all under `{{ dg_bios_root }}/`).

Files:
- `mcpx_1.0.bin` — MCPX boot ROM
- `Complex_4627.bin` — flashrom (modded BIOS)
- `xbox_hdd.qcow2` — pre-populated HDD image

Source separately — these are not redistributable.

## shadPS4 (Driveclub)

See `docs/driveclub-shadps4.md` for the full flow. The game lives
under `dg_ps4_rom_root/CUSA00003/` by default.

## Troubleshooting

If an Ansible task logs `WARNING: missing texture source for ...` or
`WARNING: PS3 DLC source not found: ...` etc., the source path
doesn't exist. Either:

1. Point the variable at your actual path in `host_vars/localhost.yml`, OR
2. Leave it — the role skips that asset and moves on, nothing else
   breaks.
