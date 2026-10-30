# Neo Geo and Mega Drive library import (2026-10-30)

The user-provided archives in `~/Downloads/games` were checked with `7z t`.
The playable files are filed under `dg_emudeck_root`; original archives remain
in Downloads, including the NeoSD, Darksoft and BackBit hardware variants that
ES-DE does not use.

| System | EmuDeck path | Imported game |
|---|---|---|
| Mega Drive | `roms/genesis/Hang-On (Mega Drive) (v1.12).bin` | Hang-On v1.12, 4 MiB SEGA-header ROM |
| Neo Geo AES/MVS | `roms/neogeo/hangonng.zip` | Hang-On v2.1, MAME chip ZIP |
| Neo Geo AES/MVS | `roms/neogeo/doubled1.zip` | Double Dragon One beta 3.2 |
| Neo Geo AES/MVS | `roms/neogeo/outrunng.zip` | OutRun beta 0.3.3, MAME chip ZIP |
| Neo Geo AES/MVS | `roms/neogeo/robocop.zip` | RoboCop beta 9, ZIP made from the supplied BackBit chips |
| Neo Geo CD | `roms/neogeocd/Altered Beast (Neo Geo CD) (Beta 18)/` | Altered Beast beta 18 |
| Neo Geo CD | `roms/neogeocd/Ghouls 'n Ghosts (Neo Geo CD) (Beta 4.1b)/` | Ghouls'n Ghosts beta 4.1b |
| Neo Geo CD | `roms/neogeocd/Hang-On (Neo Geo CD) (v1.0)/` | Hang-On v1.0 |
| Neo Geo CD | `roms/neogeocd/RoboCop (Neo Geo CD) (Beta 17)/` | RoboCop beta 17 |

Each CD game has its own CUE and matching tracks; macOS `__MACOSX` metadata and
Windows launchers were excluded. The managed ES-DE catalog now includes
`neogeocd`, using MAME's `neocdz` driver by default and the NeoCD libretro core
as an alternate. All four CUEs completed a short headless MAME boot with the
existing `neocdz.zip` BIOS.

For cartridges, `neogeo-launch` runs FB Neo normally. If a matching custom
`neogeo.xml` exists under `Emulation/bios/mame/custom-neogeo/<set>/`, it runs
MAME with that software list instead. The supplied XML and all chip CRCs were
checked for Hang-On, OutRun and RoboCop; each completed a short headless MAME
boot. FB Neo initialized `doubled1` and `hangonng` in a headless core test.
Genesis Plus GX also loaded the Mega Drive ROM in a headless core test.
Real gameplay, audio and gamepad input were not exercised in these tests.

The existing Neo Geo BIOS ZIP in both `Emulation/bios/neogeo/` and
`roms/neogeo/` retained all 33 prior members. The archives supplied two
additional members, `uni-bios_4_0.rom` and `neodebug.rom`; both were merged and
the resulting ZIPs passed a CRC check. Existing Neo Geo CD BIOS files were
already present and were left intact. MAME's `neogeo` and `neocdz` NVRAM
directories are registered in `dg_save_sets`.

## Additional files (same day)

Three further downloads were filed without changing existing games:

| Archive/file | EmuDeck path | Check |
|---|---|---|
| `Midnight_Wanderers_Neogeo.zip` | `roms/neogeo/midnight_neo_0035.zip` | Six chip sizes and CRCs match the included software-list XML; MAME headless boot passed. The XML is in `Emulation/bios/mame/custom-neogeo/midnight_neo_0035/`. |
| `Midnight_Wanderers_Neogeo_Cd.zip` | `roms/neogeocd/Midnight Wanderers (Neo Geo CD) (2026)/midnight_neo_0035.chd` | CHD raw and overall SHA-1 verification passed; MAME `neocdz` headless boot passed. |
| `DoAGBA_ROM.gba` | `roms/gba/Demons of Asteborg DX (Prototype).gba` | 33,400,320-byte GBA ROM with a valid fixed header byte; identified by the developer's download filename; loaded in a headless mGBA core test. |

The CD archive also contains an ISO/CUE/WAV version of the same disc; the CHD
is the EmuDeck copy. The cartridge archive's NeoSD and Darksoft variants remain
in the original download. The existing `neogeo-launch` dispatcher finds the new
software-list XML by ZIP basename, so this cartridge uses MAME automatically.
