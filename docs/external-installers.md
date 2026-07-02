# External installers & downloads — consolidated inventory

Every role that pulls something from outside this repo, split by how
reproducible the source is. Game *assets* (ROMs, BIOS, texture pack
layouts, DLC PKGs) are detailed in [setup-assets.md](setup-assets.md);
this page is the tool/installer/mod view across all roles.

Legend: **AUTO** = the playbook downloads it; **MANUAL** = you download
it and stage it where the `dg_*` variable points.

## 1. AUTO — pinned URL + checksum (fully reproducible)

These download a fixed release verified by SHA256. They break only if
the upstream release is deleted.

| What | Source | Role / var prefix |
|---|---|---|
| MateriaForge (7th Heaven installer) | github.com/dotaxis/MateriaForge-rs releases | `install_7th_heaven` / `dg_7th_heaven_release_*` |
| HedgeModManager | github.com/hedge-dev/HedgeModManager releases | `install_hedgemodmanager` / `dg_hmm_*` |
| Xidi (DirectInput→XInput wrapper) | github.com/samuelgr/Xidi releases | `install_pc_racing` / `dg_pc_racing_xidi_*` |
| Render96ex source + DynOS model pack + HD textures | github.com/Render96/* (git ref + release) | `install_render96ex` / `dg_render96ex_*` |
| Ship of Harkinian + OoT Reloaded HD | github.com/HarbourMasters/Shipwright, GhostlyDark/OoT-Reloaded-SoH | `install_ship_of_harkinian` |
| 2Ship2Harkinian + MM Reloaded HD | HarbourMasters/2ship2harkinian, GhostlyDark/MM-Reloaded-2S2H | `install_2ship2harkinian` |
| SpaghettiKart + MK64 Reloaded HD | HarbourMasters/SpaghettiKart, GhostlyDark/MK64-Reloaded | `install_spaghettikart` |
| Starship (Star Fox 64) | HarbourMasters/Starship releases | `install_starship` |
| MGSM2Fix, MGSHDFix, MGS2/MGS3 Bugfix Compilations | github.com/nuggslet + ShizCalev releases | `metal_gear_master_collection` |
| Eden Cheats Manager | github.com/ChrisA95G/eden-cheats-manager releases | `install_eden_cheats_manager` |
| lib32-nvidia-utils (32-bit driver extract) | archive.archlinux.org (version-matched to host driver) | `bootstrap_packages` / `dg_nvidia_lib32_*` |
| Wine 9.19 (CMR experiments) | archive.archlinux.org | `install_pc_racing` |

## 2. AUTO — "latest" via API (moving target)

Reproducible *today*, but not pinned — a re-run months later fetches a
newer build. Acceptable for actively developed emulators.

| What | Source | Role |
|---|---|---|
| shadPS4 + QtLauncher | GitHub API (`shadps4-emu/*` releases) | `refresh_shadps4` |
| Dusk (Twilight Princess port) | GitHub API (`TwilitRealm/dusk` latest) | `install_dusk` |
| Xenia Manager (+ Xenia Canary via XM) | GitHub API (`xenia-manager` latest) | `install_xenia` |
| Unleashed Recomp app | GitHub API (`hedge-dev/UnleashedRecomp` latest) | `install_unleashed_recomp` |
| RetroArch cores + assets | buildbot.libretro.com | `retroarch_extras` |
| .NET Desktop Runtime, VC++ redist (Xenia prefix) | aka.ms evergreen links | `install_xenia` |
| GT5 official patch chain 1.05→1.13 | Sony CDN (`b0.ww.np.dl.playstation.net` — still online) | `install_gt5_master_mod` / `dg_gt5_pkg_chain` |
| SMM2 popular courses | tgrcode.com MariOver API (mirrors live Nintendo servers) | `install_smm2_levels` |
| yay-bin, flathub remote | AUR git / dl.flathub.org | `bootstrap_packages` |

## 3. AUTO — known URL but fragile

Downloads work today but the URL scheme is hostile to automation.

| What | Source | Fragility | Role |
|---|---|---|---|
| FLiNG trainers (21 titles) | flingtrainer.com tokenized `downloads/…` URLs | Tokens rotate when the trainer updates; re-pin `source_url` per title when a download 404s | `steam_trainers` |
| GT5 Master Mod 2.11 data | mediafire folder (URL in role comments) | Mediafire is session-gated; treat as MANUAL if `get_url` fails | `install_gt5_master_mod` |

## 4. MANUAL — known public source, you download

Stage these at the listed variable; the role verifies and warns/fails
with guidance if absent.

| What | Get it from | Stage at |
|---|---|---|
| Cheat Engine Linux zip (`CheatEngineLinux766-4.zip`) | cheatengine.org/downloads.php | `dg_cheatengine_linux_zip` |
| Cheat Engine Windows installer (`CheatEngine76.exe`, for Proton prefixes) | cheatengine.org/downloads.php | `dg_cheatengine_win_installer` |
| libretro cheat DB (GT2 widescreen) | `git clone github.com/libretro/libretro-database` | `dg_libretro_cheats_dir` |
| GT4 HD HUD/UI + Spec II + Enthusia packs | GTPlanet threads (links in [setup-assets.md](setup-assets.md)) | `dg_pcsx2_ps2_root` layout |
| Dolphin/Azahar HD texture pack zips (8 packs) | per-pack community threads (see [hd-textures.md](hd-textures.md)) | `dg_hd_dolphin_archive_root`, `dg_hd_azahar_archive_root` |
| Project Forza Plus (FM2/3/4 mods) | author's Google Drive (links in [project-forza.md](project-forza.md)) | `dg_rom_heavy_root/xbox360/` |
| PS3 update PKGs | nopaystation / ps3.aldostools.org (helper: `install_dlcs/files/check_ps3_updates.py`) | `dg_ps3_dlc_source` |

## 5. MANUAL — no reliable public URL (source yourself)

Not redistributable and/or no stable link; the repo only detects,
links, and configures them (see the Safety section in CLAUDE.md).

| What | Stage at | Consumed by |
|---|---|---|
| xemu BIOS trio: `mcpx_1.0.bin`, `Complex_4627.bin`, `xbox_hdd.qcow2` | `dg_bios_root` | `seed_configs` (xemu) |
| N64 ROMs for the 5 native ports (SM64, MK64, OoT, MM, SF64 — SHA1-verified) | `dg_rom_mid_root/n64/` | `n64_rom_prepare` via each port role |
| CMR 2.0 / CMR3 / CMR04 installers (CD extracts / repacks) | `dg_pc_racing_source_root` | `install_pc_racing` |
| Sonic P-06 release build | `dg_pc_racing_source_root` | `install_sonic_p06` |
| Sonic Unleashed game files (X360 ISO + title update + DLC) | `dg_unleashed_recomp_*_source` (empty defaults) | `install_unleashed_recomp` |
| PS4 game dumps + firmware sys modules | `dg_ps4_rom_root`, `dg_ps4_firmware_modules` | `refresh_shadps4`, shadPS4 |
| Switch update/cheat NSPs, prod.keys | `dg_switch_updates_source`, `dg_switch_cheats_source`, Eden keys dir | `install_dlcs`, `switch_cheats` |
| Wii U / Xbox 360 / everything-else ROMs & ISOs | EmuDeck ROM tiers | ES-DE catalog + emulators |

## Maintenance rules

- New role with a download → add a row here **in the same commit**
  (same discipline as the `localhost.yml.example` rule).
- Category 1 entries: bump version + SHA together in the role's
  group_vars file; never point a pinned URL at a moving tag.
- When a Category 3 URL dies, fix the var and note the date in the
  role's group_vars comment.
