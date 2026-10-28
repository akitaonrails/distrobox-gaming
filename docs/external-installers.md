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
| Virtua Fighter 3 Recomp v0.1.10-alpha | [mr-finster/vf3-recomp](https://github.com/mr-finster/vf3-recomp/releases/tag/v0.1.10-alpha) native Linux tarball, SHA256-pinned | `install_vf3_recomp` / `dg_vf3_*` |
| OpenCMR2 v1.6.0 | [pablocpas/OpenCMR2](https://github.com/pablocpas/OpenCMR2/releases/tag/v1.6.0) Linux tarball, SHA256-pinned | `install_opencmr2` / `dg_opencmr2_*` |
| RyGT GT Sport 2026-10-22 prerelease | [mlgprorektm8/RyGT](https://github.com/mlgprorektm8/RyGT/releases/tag/gt-sport-2026-10-22) Windows ZIP, SHA256-pinned | `install_rygt` / `dg_rygt_*` |
| God of War III SpartanPort v2.7.0 | [FelipePrado0/gow3_pc](https://github.com/FelipePrado0/gow3_pc/releases/tag/windows-v2.7.0) Linux AppImage, SHA256-pinned | `install_gow3_pc` / `dg_gow3_pc_*` |
| DekUI v1.0.0 | [tgacquin/mm3d-dekui](https://github.com/tgacquin/mm3d-dekui/releases/tag/v1.0.0) Linux tarball, SHA256-pinned | `install_dekui` / `dg_dekui_*` |
| MateriaForge v0.5.0 (7th Heaven installer) | [dotaxis/MateriaForge-rs](https://github.com/dotaxis/MateriaForge-rs/releases/tag/0.5.0) ZIP, SHA256-pinned | `install_7th_heaven` / `dg_7th_heaven_release_*` |
| DUDE v0.9.6 source | [Inkub0/dude](https://github.com/Inkub0/dude/releases/tag/v0.9.6) exact git commit; native build | `install_dude` / `dg_dude_*` |
| DKR-R v1.0.8 | [ThatGuyMcd/DKR-R](https://github.com/ThatGuyMcd/DKR-R/releases/tag/Version1.0.8) Linux AppImage, SHA256-pinned | `install_dkr_recomp` / `dg_dkr_*` |
| Road Rash 64 Recompiled v1.4.8 | [linkssy2/RoadRash64Recompiled](https://github.com/linkssy2/RoadRash64Recompiled/releases/tag/v1.4.8) experimental Linux ZIP, SHA256-pinned | `install_roadrash64_recomp` / `dg_rr64_*` |
| Lighthouse v1.2.0 | [HarbourMasters/Lighthouse](https://github.com/HarbourMasters/Lighthouse/releases/tag/1.2.0) Linux AppImage, SHA256-pinned | `install_lighthouse` / `dg_lighthouse_*` |
| Perfect Dark v3.15.1 | [DabDavis/perfect-dark-dabs-mod](https://github.com/DabDavis/perfect-dark-dabs-mod/releases/tag/v3.15.1) Linux tarball, SHA256-pinned | `install_perfect_dark` / `dg_pd_*` |
| Star Fox Enhanced v0.0.8.8.1 | [kandowontu2/starfox-enhanced](https://github.com/kandowontu2/starfox-enhanced/releases/tag/v0.0.8.8.1) Linux ZIP, SHA256-pinned | `install_starfox_enhanced` / `dg_sfe_*` |
| Wind Waker HD Recompiled v0.4.0 | [ZeldaWWHDRecomp release](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp/releases/tag/v0.4.0) Linux ZIP, SHA256-pinned | `install_wwhd_recomp` / `dg_wwhd_*` |
| HedgeModManager | github.com/hedge-dev/HedgeModManager releases | `install_hedgemodmanager` / `dg_hmm_*` |
| Xidi (DirectInput→XInput wrapper) | github.com/samuelgr/Xidi releases | `install_pc_racing` / `dg_pc_racing_xidi_*` |
| Render96ex source + DynOS model pack + HD textures | github.com/Render96/* (git ref + release) | `install_render96ex` / `dg_render96ex_*` |
| Ship of Harkinian v9.3.1 AppImage + OoT Reloaded HD | [Shipwright release](https://github.com/HarbourMasters/Shipwright/releases/tag/9.3.1), GhostlyDark/OoT-Reloaded-SoH; SHA256-pinned | `install_ship_of_harkinian` |
| 2Ship2Harkinian + MM Reloaded HD | HarbourMasters/2ship2harkinian, GhostlyDark/MM-Reloaded-2S2H | `install_2ship2harkinian` |
| Nebula setup + NKit CLI (Super Mario Galaxy recompilation) | github.com/keepvaibin/nebula v1.0.1 and github.com/Nanook/NKit v3.1.0; both SHA256-pinned. Needs the owned RMGE01 revision 0 Wii image. See [Nebula notes](nebula-galaxy.md). | `install_nebula` / `dg_nebula_*` |
| RalliSport Challenge 2 native Linux recompilation | [Mortify7612/RallisportChallenge2-decomp](https://github.com/Mortify7612/RallisportChallenge2-decomp) v0.7.0, SHA256-pinned. Extracts the owned Xbox ISO with the box's `extract-xiso`; see [RSC2 notes](rsc2.md). | `install_rsc2` / `dg_rsc2_*` |
| GT4 static recompilation and GS renderer | [moesuito/gt4-staticrecomp](https://github.com/moesuito/gt4-staticrecomp/releases/tag/v1.3.0-rc6) v1.3.0-rc6 portable ZIP and [moesuito/gt4recomp-gs](https://github.com/moesuito/gt4recomp-gs/releases/tag/gt4gs-v1.2.1) v1.2.1 ZIP, both SHA256-pinned (reuses a copy already staged in `PC/releases`). The upstream Tauri launcher needs WebView2 and is bypassed: the role runs `game/gt4.exe --fullscreen` directly. The Rust disc helper uses an exact upstream git commit. See [GT4 notes](gt4-recomp.md). | `install_gt4_recomp` / `dg_gt4r_*` |
| Conker's Bad Fur Day Recompiled v0.1.6 | [sciaschi/CBFD-Recompiled](https://github.com/sciaschi/CBFD-Recompiled/releases/tag/V0.1.6) Linux tarball, SHA256-pinned | `install_cbfd_recomp` / `dg_cbfd_*` |
| Donkey Kong 64 Recompiled v1.0.3 | [Rainchus/Donkey-Kong-64-Recompiled](https://github.com/Rainchus/Donkey-Kong-64-Recompiled/releases/tag/v1.0.3) Linux x64 ZIP, SHA256-pinned | `install_dk64_recomp` / `dg_dk64_*` |
| Banjo-Tooie Recompiled Alpha 4.3 | [some-scurvy-dog release](https://github.com/some-scurvy-dog/banjo-tooie-scurvy-dog-port/releases/tag/v0.1.0-alpha.4.3) Windows ZIP, SHA256-pinned | `install_banjotooie_recomp` / `dg_btooie_*` |
| Mickey & Donald Collection Windows port | [Darhkfox/MickeyAndDonaldCollection](https://github.com/Darhkfox/MickeyAndDonaldCollection) v1.1 win64 ZIP, SHA256-pinned. Links three hash-verified Genesis ROMs; see [collection notes](mickey-donald-collection.md). | `install_mickey_donald` / `dg_mdc_*` |
| I Could Have Given You The World Linux recompilation | [riseio/TWIPE_00Sheven](https://github.com/riseio/TWIPE_00Sheven) ICHGYTW_0.1.96 AppImage, SHA256-pinned. Normalizes the owned USA revision 0 ROM; see [007 notes](twine-007.md). | `install_twine` / `dg_twine_*` |
| SpaghettiKart + MK64 Reloaded HD | HarbourMasters/SpaghettiKart, GhostlyDark/MK64-Reloaded | `install_spaghettikart` |
| Star Fox 64 Recompiled | sonicdcer/Starfox64Recomp releases (native Linux) | `install_starfox64_recomp` |
| MGSM2Fix, MGSHDFix, MGS2/MGS3 Bugfix Compilations | github.com/nuggslet + ShizCalev releases | `metal_gear_master_collection` |
| Eden Cheats Manager | github.com/ChrisA95G/eden-cheats-manager releases | `install_eden_cheats_manager` |
| lib32-nvidia-utils (32-bit driver extract) | archive.archlinux.org (version-matched to host driver) | `bootstrap_packages` / `dg_nvidia_lib32_*` |
| Wine 9.19 (CMR experiments) | archive.archlinux.org | `install_pc_racing` |
| Streets of Rage Remake v5.2 rev550 (SorR.exe under Wine) | Internet Archive mirror `sorrv-52-rev-550_202401/SORRv52_rev550.rar` (sha1-pinned; the official MEGA link isn't checksummable, and the AUR pkg is only v5.1) | `install_sorr` / `dg_sorr_*` |
| Streets of Rage 4: REIGNITED gameplay mod (modded `bigfile`) | gitlab.com/fuzzyetdeadly/sor4-reignited (`assets/SOR4-Reignited-v1.0.0.zip`, sha256-pinned). Replaces `Streets of Rage 4/data/bigfile`; keeps a `bigfile.vanilla-backup`; needs the game's v8 patch | `install_sor4_reignited` / `dg_sor4_reignited_*` |
| GTA IV FusionFix (ASI loader + Overloader foundation for the GTA IV mod set) | github.com/ThirteenAG/GTAIV.EFLC.FusionFix releases (`v5.0.1`, sha256-pinned); cached under `dg_gta4_staging_root` | `install_gta4_mods` / `dg_gta4_fusionfix_*` |

## 2. AUTO — "latest" via API (moving target)

Reproducible *today*, but not pinned — a re-run months later fetches a
newer build. Acceptable for actively developed emulators.

| What | Source | Role |
|---|---|---|
| shadPS4 + QtLauncher | GitHub API (`shadps4-emu/*` releases) | `refresh_shadps4` |
| Dusk (Twilight Princess port) | [TwilitRealm/dusklight](https://github.com/TwilitRealm/dusklight/releases/tag/v2.0.3) v2.0.3 Linux AppImage as of 2026-10-23; role follows the latest release | `install_dusk` |
| Xenia Manager (+ Xenia Canary via XM) | GitHub API (`xenia-manager` latest) | `install_xenia` |
| Unleashed Recomp app | GitHub API (`hedge-dev/UnleashedRecomp` latest) | `install_unleashed_recomp` |
| WipEout Phantom Edition (Windows x64 binary, run under Wine) | github.com/wipeout-phantom-edition release (pinned + sha256; AUTO). Needs a WipEout **USA** PSX rip — this box's `psx/WipEout (USA).chd`, converted to multi-bin. See `docs/wipeout-pe.md`. | `install_wipeout_pe` / `dg_wipeout_pe_*` |
| CannonBall (OutRun engine) — built from source | github.com/djyt/cannonball (pinned commit; AUTO clone+build). Needs the **OutRun Rev B** arcade romset — this box's `arcade/mame/outrun_dup2.zip`. See `docs/cannonball.md`. | `install_cannonball` / `dg_cannonball_*` |
| Super Mario Bros. Remastered (native Linux Godot build) | github.com/JHDev2006 release (pinned + sha256; AUTO). Needs an **SMB1 NES ROM** — this box's `nes/Super Mario Bros. (1985-09-13)(Nintendo)(JP-US).zip` (auto-imported). See `docs/smb-remastered.md`. | `install_smb_remastered` / `dg_smb_remastered_*` |
| F-Zero Recomp (SNES F-Zero static recompilation, native Linux) | github.com/mstan/FZeroSNESRecomp release (pinned + sha256; AUTO). Needs the owned SNES **F-Zero (USA)** ROM. See [F-Zero notes](fzero-recomp.md). | `install_fzero_recomp` / `dg_fzero_*` |
| OpenSC2K (SimCity 2000 reimplementation, native Linux) | github.com/nicholas-ochoa/OpenSC2K release plus the pinned Godot build it runs on, both SHA256-pinned (AUTO). Needs your own SimCity 2000 data, fetched by the role from the original archive. See [OpenSC2K notes](opensc2k.md). | `install_opensc2k` / `dg_opensc2k_*` |
| Forza Horizon 1 ReImagined (native Linux static recompilation) | github.com/FH1-ReImagined/ForzaHorizon1-ReImagined v0.2.0 Linux tarball (pinned + sha256; AUTO). Builds the game from the owned FH1 disc (title 4D5309C9) via its launcher. See [FH1 notes](fh1-reimagined.md). | `install_fh1_reimagined` / `dg_fh1r_*` |
| G-Diffuser (F-Zero X PC port, libultraship, native Linux) | github.com/Zorkats/G-Diffuser release (pinned + sha256; AUTO). Needs 3 dumps: F-Zero X US rev0 ROM, the translated 64DD EK disk, and a 64DD IPL ROM — all present on this box. See `docs/gdiffuser.md`. | `install_gdiffuser` / `dg_gdiffuser_*` |
| Fukami (Ridge Racer V static recomp, native Linux) | github.com/danisandoval/fukami release (pinned + sha256; AUTO). Needs **Ridge Racer V USA** (`SLUS-20002`) `.cue`/`.bin` — this box's `ps2/Ridge Racer V (USA)`. See `docs/fukami-rrv.md`. | `install_fukami` / `dg_fukami_*` |
| Project Midas (GoldenEye 007 PC port; 32-bit i386, SDL2 bundled) | github.com/murkantor/Project-Midas release (pinned + sha256; AUTO). Needs the **stock NTSC-U GoldenEye cart** — this box's `n64/originals/007 - GoldenEye (USA).n64` (v64 read by content; the non-originals `n64/` copy is a bad dump). Audio needs `lib32-libpulse`. See `docs/project-midas.md`. | `install_project_midas` / `dg_midas_*` |
| FM4 PC Port (Forza Motorsport 4 native port; win-x64 via GE-Proton) | github.com/0herculabs/hl360-forza4 release (pinned + sha256; AUTO). Needs the **USA Rev 1** play disc (Disc 1 md5 2470358…, Disc 2 md5 9915d1ad…); the library's USA originals do NOT match. Superseded Alexbeav/fm4-recomp (EU-only). See `docs/fm4-hl360.md`. | `install_hl360_fm4` / `dg_hl360_*` |

| Gravity Rush PC (Gravity Rush Remastered native port; win-x64 via GE-Proton) | github.com/LucaPazienza/gravityrush_pc release (pinned + sha256; AUTO). Needs the **unpacked European CUSA01113 v01.00** game folder — this box's `roms_rare/ps4/CUSA01113` (an ISO is not usable). See `docs/gravity-rush.md`. | `install_gravity_rush` / `dg_gr_*` || RetroArch cores + assets | buildbot.libretro.com | `retroarch_extras` |

| KytyPS5-GT7 (PS5 emulator for Gran Turismo 7; native Linux) | github.com/usa-ratt/KytyPS5-GT7 releases (pinned + sha256; AUTO, daily tag cadence). Needs the **extracted** GT7 PPSA01317 v01.710 game folder — built from this box's 134 GB FIH FPKG with `pkg-to-anyps5` (see `docs/kyty-gt7.md`). | `install_kyty_gt7` / `dg_kyty_*` || .NET Desktop Runtime, VC++ redist (Xenia prefix) | aka.ms evergreen links | `install_xenia` |

| DOA2U PC Port (Dead or Alive 2 Ultimate recomp; native Linux SDL_GPU/Vulkan) | github.com/NoRain211/doa2u-re release ZIP (pinned + sha256; MANUAL-build hybrid: the ZIP is staged, the runner is compiled in the box from the game dump). Needs the **DOA Ultimate (Xbox, USA) Disc 2** ISO — this box's `roms_heavy/xbox/Dead or Alive 2 Ultimate (USA, Japan) (En,Ja).iso`; XBE hash-verified, other discs refused. See `docs/doa2u-re.md`. | `install_doa2u_re` / `dg_doa2u_*` || GT5 official patch chain 1.05→1.13 | Sony CDN (`b0.ww.np.dl.playstation.net` — still online) | `install_gt5_master_mod` / `dg_gt5_pkg_chain` |

| GT3 Revisited (GT3 engine reimplementation; native Linux Vulkan) | github.com/matt-pulsipher/GT3-revisited releases (pinned + sha256; AUTO). Needs a **GT3 NTSC-U .iso** — this box's `roms_heavy/ps2/Gran Turismo 3 - A-spec (USA) (v1.10).iso` (PBPX-95503, verified by gt3tool). See `docs/gt3-revisited.md`. | `install_gt3_revisited` / `dg_gt3r_*` || SMM2 popular courses | tgrcode.com MariOver API (mirrors live Nintendo servers) | `install_smm2_levels` |

| GT2 PC Port (GT2 decompilation + mod kit; win-x64 via GE-Proton) | github.com/CurtisSlone/GT2-PC-Port-Mod-Kit (repo zipball, pinned + sha256; release tags carry no assets). Needs the **exact GT2 (USA) Simulation Mode v1.0** cue/bin (redump disc/85, md5 7f3e9b95…) — Rev 1/Rev 2/patched v1.2 all refused; one-time Proton install from the disc. See `docs/gt2-pc-port.md`. | `install_gt2_pc` / `dg_gt2_*` || yay-bin, flathub remote | AUR git / dl.flathub.org | `bootstrap_packages` |

| SOTC PC Port (Shadow of the Colossus PS4 remake; win-x64 via GE-Proton) | github.com/AjncSystem/ShadowOfTheColossus-PC releases (`SotC-PC.zip`, pinned + sha256; AUTO). Needs the **CUSA08809 EU 1.01 / CUSA08034 US 1.00** dump folder — this box's merged extraction at `ROMS_FINAL/ps4/sotc-kyty` (base + update PKG via shadPKG). **Sound needs two decrypted firmware sprx from the user's own PS4** (not on this box yet). See `docs/sotc-pc.md`. | `install_sotc_pc` / `dg_sotc_*` |
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
| DriveClub Recomp v0.3.1 Windows ZIP (SHA256-pinned) | [OverkillLabs3 release](https://github.com/OverkillLabs3/driveclub-recomp/releases/tag/v0.3.1) | `dg_dcr_archive` under `dg_roms_final_root/PC/`; `install_driveclub_recomp` |
| Dolphin/Azahar HD texture pack zips (8 packs) | per-pack community threads (see [hd-textures.md](hd-textures.md)) | `dg_hd_dolphin_archive_root`, `dg_hd_azahar_archive_root` |
| Project Forza Plus (FM2/3/4 mods) | author's Google Drive (links in [project-forza.md](project-forza.md)) | `dg_rom_heavy_root/xbox360/` |
| PS3 update PKGs | nopaystation / ps3.aldostools.org (helper: `install_dlcs/files/check_ps3_updates.py`) | `dg_ps3_dlc_source` |
| RE4 HD Project 1.1 (BIO4 HD assets + re4_tweaks, ~34 GB) — for Steam RE4 2005 / appid 254700, NOT the remake | [re4hd.com](https://www.re4hd.com/) (official) or crack-free mirror [archive.org/details/re4HDProject.7z](https://archive.org/details/re4HDProject.7z). Do NOT use a scene repack. | `dg_re4_hd_source` |
| GTA IV mod set — 8 NexusMods (282/195/716→GitHub/263/357/272/702/311/258) for CE 1.2.0.59 | nexusmods.com/gta4 (free account = manual per-mod download; role prints a staging manifest). Preserved on the NAS. | `dg_gta4_staging_root` (`ROMS_FINAL/PC/mods/NexusMods/gta4/`) |
| WRC 4 mod (1 NexusMods: loose camera + realistic tyres, a `DATA.MIX` replace) for appid 256330 (delisted; USB lib) | nexusmods.com/wrc4fiaworldrallychampionship mod 1 (Premium key auto-downloads, else manual). Preserved on the NAS. See `docs/wrc4-mods.md`. | `dg_wrc4_staging_root` (`ROMS_FINAL/PC/mods/NexusMods/wrc4/`) |

## 5. MANUAL — no reliable public URL (source yourself)

Not redistributable and/or no stable link; the repo only detects,
links, and configures them (see the Safety section in CLAUDE.md).

| What | Stage at | Consumed by |
|---|---|---|
| xemu BIOS trio: `mcpx_1.0.bin`, `Complex_4627.bin`, `xbox_hdd.qcow2` | `dg_bios_root` | `seed_configs` (xemu) |
| N64 ROMs for the 5 native ports (SM64, MK64, OoT, MM, SF64 — SHA1-verified) | `dg_rom_mid_root/n64/` (OoT and MM specifically under `dg_rom_mid_root/n64/originals/` — the `n64/` top level holds romhacks) | `n64_rom_prepare` via each port role |
| CMR 2.0 / CMR3 / CMR04 installers (CD extracts / repacks) | `dg_pc_racing_source_root` | `install_pc_racing` |
| Prince of Persia: The Sands of Time — GOG v2 installer (`setup_..._(92028).exe` + `-1.bin`) | `dg_pc_racing_source_root/prince of persia` | `install_pc_racing` (`prince-of-persia-sot`, `install-prince-of-persia-sot.yml`) — innoextract; runs on rootful Xwayland :12 + wined3d |
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
