# NexusMods inventory

Every NexusMods mod set installed on this box via the `nexus-mod-set` skill,
one section per game. Source wishlist: `tmp/nexusmods.txt`. Processed **one
game at a time** — each game gets its own `install_<game>_mods` role, and lands
here only once its mods actually install.

Legend: ✅ landed · 🔧 in progress · ⏳ queued · ⛔ skipped (not installed / not
on Steam).

## Roster & Steam status

Steam appids resolved 2026-08-06 by scanning all libraries (189 apps).

| Game | Nexus domain | Steam | Mods listed | Status |
|---|---|---|---|---|
| GTA IV: Complete Edition | gta4 | `12210` | 9 | ✅ (see below) |
| Art of Rally | artofrally | `550320` | 4 | 🔧 built — verify in-game |
| Alex Kidd in Miracle World DX | alexkiddinmiracleworlddx | `1333470` | 1 | ✅ (see below) |
| Ace Combat 7 | acecombat7skiesunknown | `502500` | 1 | ✅ (see below) |
| Batman: Arkham Knight | batmanarkhamknight | `208650` | 2 | ⏸️ deferred (TFC GUI) |
| Batman: Arkham City GOTY | batmanarkhamcity | `200260` | 3 | ⏸️ deferred (TFC GUI) |
| Batman: Arkham Asylum GOTY | batmanarkhamasylum | `35140` | 2 | ⏸️ deferred (TFC GUI) |
| Black Myth: Wukong | blackmythwukong | `2358720` | 1 | ✅ (see below) |
| Bloodstained: RotN | bloodstainedritualofthenight | `692850` | 7 | ✅ (see below) |
| Dark Souls Remastered | darksoulsremastered | `570940` | 3 | ✅ #293 (see below); #220 deferred, #7 dropped |
| Elden Ring | eldenring | `1245620` | 1 | ✅ (see below) |
| FINAL FANTASY VII REMAKE Intergrade | finalfantasy7remake | `1462040` | 5 | ✅ (see below) |
| FINAL FANTASY VII REBIRTH | finalfantasy7rebirth | `2909400` | 7 | ✅ 6/7 (see below) |
| Grand Theft Auto V Enhanced | gta5enhanced | `3240220` | 7 | ⏸️ deferred (OpenIV/CodeWalker + SHV toolchain) |
| GRANDIA HD Remaster | grandiahdremaster | `1034860` | 2 | ✅ (see below) |
| Metal Gear Rising: Revengeance | metalgearrisingrevengeance | `235460` | 4 | ⏸️ deferred (TexMod/patcher/CE) |
| MGS Δ: Snake Eater | metalgearsoliddeltasnakeeater | `2417610` | 3 | ✅ (see below) |
| MGS3 (Master Collection) | metalgearsolid3mc | `2131650` | 3 | ✅ 3/3 (see below) |
| MGS2 (Master Collection) | metalgearsolid2mc | `2131640` | 6 | ✅ 5/6 (see below) |
| MGSV: Ground Zeroes | metalgearsolidvgz | `311340` | 2 | ⏸️ deferred (GzsTool/CE) |
| MGS1 (Master Collection) | metalgearsolidmc | `2131630` | 2 | ✅ 1/2 (see below) |
| MGSV: The Phantom Pain | metalgearsolidvtpp | `287700` | 5 | ⏸️ deferred (SnakeBite) |
| Red Dead Redemption | reddeadredemption | `2668510` | 11 | ✅ 5/11 (see below) |
| Red Dead Redemption 2 | reddeadredemption2 | `1174180` | 13 | ⏸️ deferred (ScriptHook/LML) |
| Resident Evil 4 (2023 Remake) | residentevil42023 | `2050650` | 2 | ✅ 2/2 (see below) |
| Resident Evil 2 (2019) | residentevil22019 | `883710` | 3 | ✅ 1/3 (see below) |
| Resident Evil 3 (2020) | residentevil32020 | `952060` | 1 | ✅ 1/1 (see below) |
| Resident Evil Requiem | residentevilrequiem | `3764200` | 3 | ✅ 3/3 (Fluffy + REFramework) |
| Resident Evil Village | residentevilvillage | `1196590` | 4 | ✅ 4/4 (Fluffy + REFramework + save) |
| Resident Evil 4 (2005) | residentevil4 | `254700` | 2 | ✅ re4_tweaks 1.9.1 via install_re4_hd (mod 306 dropped — 2007-port `game.exe`, not the Steam UHD `bio4.exe`) |
| Resident Evil 0 (HD Remaster) | residentevil0biohazard0hdremaster | `339340` | 2 | ✅ 1/2 (see below) |
| RoboCop: Rogue City | robocoproguecity | `1681430` | 8 | ✅ 7/8 (~mods + UE4SS + save; 7 config) |
| Sekiro: Shadows Die Twice | sekiro | `814380` | 2 | ✅ 2/2 (Weapon Wheel + Mod Engine) |
| Marvel's Spider-Man Remastered | marvelsspidermanremastered | `1817070` | 8 | ⏸️ deferred (Overstrike GUI) |
| Marvel's Spider-Man: Miles Morales | spidermanmilesmorales | `1817190` | 6 | ⏸️ deferred (Overstrike GUI) |
| Streets of Rage 4 | streetsofrage4 | `985890` | 1 | ✅ mod 133 (REIGNITED) via existing `install_sor4_reignited` |
| Tokyo Xtreme Racer | tokyoxtremeracer | `2634950` | 3 | ✅ 3/3 (~mods + UE4SS + save) |
| WRC 5 | wrc5 | `354160` | 1 | ⚠️ flagged — not installed (DLC-unlock crack, see below) |
| UNCHARTED: Legacy of Thieves | unchartedlegacyofthievescollection | `1659420` | 5 | ✅ 3/5 (see below) |
| Yakuza 0 (Director's Cut) | yakuza0 | `2988580` | 10 | ⏸️ deferred (edition mismatch / RMM) |
| The Witcher 3: Wild Hunt (Next-Gen) | witcher3 | `292030` | 12 | ✅ 11/12 (see below) |
| WRC 7 | wrc7 | `621830` | 1 | ✅ 1/1 (EVOlution Mod 4.0, see below) |

### ⛔ Skipped — not installed in Steam (as of the 2026-08-06 scan)

Re-check if you later install these; they're in `tmp/nexusmods.txt`.

| Game | Nexus domain | Reason |
|---|---|---|
| Resident Evil HD Remaster (RE1) | residentevilbiohazardhdremaster | not found in any Steam library |
| Metal Gear & Metal Gear 2 (MC) | metalgearandmetalgear2mc | not found in any Steam library |
| Colin McRae Rally 2 | colinmcraerally2 | not a Steam title (user-noted) — covered by `install_pc_racing` instead |

### 🔌 Shared loaders (revisited deferred games)

External mod-loaders that are proven under Proton, fetched from GitHub and dropped
in like the bundled `dinput8` hooks — these un-defer the loader-dependent mods.

| Loader | Role | Games / mods enabled |
|---|---|---|
| **REFramework** (praydog, universal RE Engine `dinput8.dll`) | `install_reframework` (tag `reframework`) | RE Village 651 Infinite Ammo; RE Requiem 25 Inf Ammo/HP (+aim-assist/auto-parry) & 100 Infinite CP. Loader staged on NAS under `NexusMods/_loaders/reframework/`; Lua drops into `<game>/reframework/autorun/`; launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%`. |
| **UE4SS** (RE-UE4SS, `dwmapi.dll` UE4/5 script loader) | `install_ue4ss` (tag `ue4ss`) | RoboCop 2 Ultra Plus (self-contained — the Steam file bundles UE4SS); TXR 87 Ultradynamic (UE4SS core v3.0.1 + mod `Mods/` overlay). Core staged under `NexusMods/_loaders/ue4ss/`; installs into `<game>/…/Binaries/Win64`; launch option `WINEDLLOVERRIDES="dwmapi=n,b" %command%`. Watch: use the game's **Steam/Win64** mod file, not the Game Pass/WinGDK one. |
| **Sekiro Mod Engine** (katalash, `dinput8.dll` + `modengine.ini`) | `install_sekiro_modengine` (tag `sekiro_modengine`) | Sekiro 418 The Easy (param override from `<game>/mods/`). ModEngine2 does **not** support Sekiro; this original ModEngine chainloads the Weapon Wheel (`chainDInput8DLLPath="\weaponwheel.dll"`) so both run. Revert before `install_sekiro_mods`. |
| **Ultimate ASI Loader** (ThirteenAG, x64 `dinput8.dll`) | `install_rdr_asi` (tag `rdr_asi`) | RDR 719 RDRFix (`.asi` next to `RDR.exe`). Loader staged under `NexusMods/_loaders/ualoader/`; launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%`. Generic ASI host — reusable for other `.asi` mods. |

### 🖱️ GUI mod-manager tools (staged; manual pass)

`install_modtools` (tag `modtools`) only **downloads + version-pins** the Windows
.NET GUI tools to `NexusMods/_loaders/` — their mod-install step is irreducibly
manual (no headless path). These are **one-time patchers, not launchers**:
SnakeBite and Overstrike **bake the mods into the game's own data archives**
(SnakeBite → `master/0/00.dat`; Overstrike → `asset_archive/*.toc`), so after one
successful Build/Install the game just runs normally through Steam — the tool is
not involved at runtime. Run each once under the game's Proton prefix
(`protontricks <appid> <tool>` or a wine prefix with `winetricks dotnet`), or even
on another PC, since the patched files then work under Proton. Revert = Steam →
Verify integrity. (RMM is the exception — it installs a persistent runtime loader,
not a baked patch.)

**Running a tool** (in the `gaming` box, in a game's Proton prefix):
```
distrobox enter gaming -- env WINEPREFIX="<lib>/steamapps/compatdata/<APPID>/pfx" WINEDEBUG=-all \
  "<box_home>/.local/share/Steam/compatibilitytools.d/GE-Proton11-1/files/bin/wine" "<TOOL.EXE>"
```
GE‑Proton's wine bundles the .NET/media bits these need. Alternative: add the
`.exe` as a Non‑Steam Game → set GE‑Proton → launch from Steam.

| Tool (staged under `_loaders/`) | Game(s) | Manual pass |
|---|---|---|
| **SnakeBite** `0.8` (`SnakeBite.Installer.exe`) | MGSV: The Phantom Pain (`287700`) | Install SnakeBite (installed ✅), point it at MGS_TPP, add the `.mgsv` files from `NexusMods/mgsvtpp/` (300, 316, 327, 406→Vibrant, 1011→Extreme), Build. |
| **Overstrike** `v1.7.5` (`overstrike/app/Overstrike.exe`) | Spider-Man Remastered (`1817070`) + Miles Morales (`1817190`) | Needs **.NET 7.0 Desktop Runtime** — the `dotnet7` installer is staged and was installed into the `1817070` prefix (`… /install /quiet /norestart`); do the same for `1817190`. Then run Overstrike, add the `.smpcmod`/`.mmpcmod` files from `NexusMods/spiderman-r/` + `spiderman-mm/`, Install. |
| **GzsTool** `v0.6.0` (`GzsTool.v0.6.0.zip`) | MGSV: Ground Zeroes (`311340`) | Unpack/repack the `data_02.dat` QAR archive for the Improved Max Settings mod. |
| **MagicRDR** `v1.3.10` (`MagicRDR_v1.3.10.zip`) | Red Dead Redemption (`2668510`) | Open `mapres.rpf`/`fonts.rpf`/`common.rpf` and inject the deferred RDR mods (525 minimap, 66 SMIC, 303 fast-horse, 140 deadeye). |
| **DSR-TPUP** `1.5` (`dsr-tpup/`) | Dark Souls Remastered (`570940`) | Run `DSR-TPUP.exe` → Repack, for the DSR 2020 Textures (mod 220, ~6 GB, fetch separately). |
| **Cheat Engine** | RE0 (`339340`), MGR (`235460`), MGSV GZ (`311340`) | ⚠️ **not staged** — gated behind cheatengine.org and its installer bundles adware; fetch manually and decline the offers. Load the `.CT` table + attach. |
| **OpenIV** | GTA V Enhanced (`3240220`) | ⚠️ **not staged** — manual EULA download from openiv.com. |
| **Ryu Mod Manager** (`mosamadeeb/RyuModManager`) | Yakuza 0 (`2988580`) | ⚠️ **not staged** — no release binary, and this box has the *Director's Cut* vs the original the `yakuza0` `.par` mods target (edition mismatch). |
| **TFC Installer / Advanced Launcher** | Batman Arkham Knight/City/Asylum | ships **inside** each mod's archive — run from there. |

### 💾 Save-file mods (placed manually, with backups)

Save mods are user progress, not code/assets — placed **directly** into each
game's save dir (NOT via a `site.yml` role, so a rebuild won't re-clobber saves),
with the original backed up alongside as `*.dg-save-backup`. The user authorised
overwriting on top of existing saves. **Caveat:** saves can be profile-ID-bound,
`SaveIndex`-dependent, or Steam-Cloud-managed, so some may not load even when
placed correctly — verify in-game; restore from the backup if not.

| Mod | Game | Placed at | Note |
|---|---|---|---|
| [TXR 5 All Perks + Money](https://www.nexusmods.com/tokyoxtremeracer/mods/5) | TXR (`2634950`) | prefix `…/TokyoXtremeRacer/Saved/SaveGames/<id>/UserData_00.sav` | ✅ clean single-file replace (hash-verified); fresh mtime for Steam Cloud |
| [RE Village 184 Newgame Plus](https://www.nexusmods.com/residentevilvillage/mods/184) | RE Village (`1196590`) | Steam Cloud `userdata/<id>/1196590/remote/win64_save/` | ✅ placed (`data00-1.bin`, `data001Slot.bin`) — non-standard filenames, verify it loads |
| [Uncharted 22 Save File](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/22) | Uncharted (`1659420`) | prefix `…/users/65294540/Uncharted4/saves/` (16 files) | ✅ placed — numbered slots may be profile-ID-bound |
| [RoboCop 49 New Game Plus](https://www.nexusmods.com/robocoproguecity/mods/49) | RoboCop (`1681430`) | prefix `…/RoboCop/Saved/SaveGames/` (50 `.sav`) | ✅ placed — may need `SaveIndex.sav` to list them |
| [MGS3 26 NG+ saves](https://www.nexusmods.com/metalgearsolid3mc/mods/26) | MGS3 MC (`2131650`) | — | ⏸️ **blocked** — Steam Cloud container files (`STE…`); no `userdata` save dir exists yet. Save once in-game, then re-run. |
| [RDR 114 Starter](https://www.nexusmods.com/reddeadredemption/mods/114) · [515 100%](https://www.nexusmods.com/reddeadredemption/mods/515) | RDR (`2668510`) | prefix `…/Documents/Rockstar Games/Red Dead Redemption/Profiles/<id>/` | ✅ placed once the save dir existed (114 → slot 0 + `RDR2EXTRAS`; 515 → slots 1–2 + Undead Nightmare `RDR2ZOMBIESAVE1/2`). Profile backed up as `Profiles/<id>.dg-save-backup`. |

### ⏸️ Deferred (blocked) — revisit at the end

Games whose mods need an interactive **Windows GUI tool** that isn't
headless-automatable. Mods are downloaded + preserved on the NAS; do these in a
manual pass (run the tool under Proton). The Arkham family uses the **TFC
Installer** / **Advanced Launcher** ecosystem — `GameProfile.xml`-driven .NET
GUIs that inject textures/patches into base UPKs; the role framework can't drive
an interactive GUI.

| Game | Blocker |
|---|---|
| Batman: Arkham Knight (`208650`) | Community Patch (mod 5) is **TFC Installer** format (`.upk.PackagePatch` + `GameProfile.xml`). Mod 50 (Batmobiles) alone IS a trivial `DLC/`-folder drop — do that one directly if wanted. |
| Batman: Arkham City GOTY (`200260`) | Community Patch (mod 1) is TFC. HD Texture Pack (407) / cheats (428) may be droppable — check in the manual pass. |
| Batman: Arkham Asylum GOTY (`35140`) | Both mods (Reborn HD 1, 4K Remastered 36) are TFC / `Advanced Launcher` (`BmLauncher.exe`) GUI-installed. |
| Dark Souls Remastered (`570940`) — **mod 220 only** | DSR 2020 Textures (~6 GB) needs the **DSR-TPUP** .NET WinForms tool to unpack/override/repack the game's dvdbnd archives. Mod 293 (Easy mode) IS installed; mod 7 dropped (ReShade). |
| Grand Theft Auto V Enhanced (`3240220`) | 5 of 7 (NextGen Euphoria 1 base, Better Fist Fighting 36, Addon Carpack 173, Real Vehicles 320, Skip Intro 216) inject into `.rpf` archives — need the **OpenIV / CodeWalker** GUI; the Script Hook V (Enhanced) + OpenRPF + mods/ toolchain is fragile under Proton. Headless-only: 354 Straight To Story (`.asi`, needs SHV) + 32 savegame (prefix profile). Carpack 173 needs game build v814.9+. |
| Metal Gear Rising: Revengeance (`235460`) | HD Textures (46) are **TexMod `.tpf`** (need the TexMod/uMod GUI wrapping the exe under Wine); File Limit Remover (444) is a **patcher `.exe`** run under Wine; Cheat Table (25) is a **Cheat Engine `.CT`** (manual CE under Proton). Only Skip Credits (66) is a trivial `winmm.dll` drop — do it + the tool steps in a manual pass. |

| MGSV: Ground Zeroes (`311340`) | Improved Max Settings (11) needs **GzsTool** to unpack/repack the `data_02.dat` QAR archive (a .NET build-time transform); Infinite Ammo (31) is a **Cheat Engine `.CT`** (manual CE under Proton). Neither is a clean file drop. |
| MGSV: The Phantom Pain (`287700`) | All 5 mods are **`.mgsv`** packages requiring the **SnakeBite Mod Manager** (.NET WPF GUI that merges into `master/0/00.dat` + tracks `snakebite.xml`) — no headless CLI. Game is v1.0.15.1; archives preserved under NAS `NexusMods/mgsvtpp/`. Manual SnakeBite pass — install these variants: **300** No More Timers (`nmt_115v3.mgsv`), **316** No Development Requirements, **327** New Female Faces & Hairs v2.4, **406** ICBINR → pick **`ICBINR - Vibrant.mgsv`**, **1011** Beyond Ultra → pick **`Beyond Ultra - EXTREME - With FXAA.mgsv`**. |
| Yakuza 0 — **Director's Cut** (`2988580`) | **Edition mismatch + loader risk.** The Nexus `yakuza0` mods target the **original Yakuza 0** (`638970`, *not installed here*); the user has the **Director's Cut** (`2988580`). All 10 are **Ryu Mod Manager (RMM)** mods (`bootpar/`, `mod-meta.yaml`, `.par` replacements) that need RMM's `d3d11.dll`/YakuzaParless loader in a `mods/` folder. The DC uses the same OoE `.par` engine but relocated under `runtime/`, is a newer build, and has **online features** — so RMM's exe hook + original-Y0 `.par` overrides may not apply and could break online/the account. Unverifiable headlessly → deferred for a careful manual pass (confirm intent, set up RMM against the DC exe under Proton, test offline). Mods: 459 5x Multiplier, 563, 7 4K Font, 9, 250, 120, 12 Rebalanced, 513, 8, 862. Archives preserved under NAS `NexusMods/yakuza0/`. |
| Marvel's Spider-Man Remastered (`1817070`) & Miles Morales (`1817190`) | Every listed mod is a **`.smpcmod`** / **`.mmpcmod`** / `.modular` package installed by the **Overstrike / "Modding Tool"** GUI, which patches the game's Insomniac-engine `asset_archive/*.toc`. The engine has **no loose-file loading**, so there's no headless path (unlike RE Engine natives). Archives preserved under NAS `NexusMods/spiderman-r/` + `spiderman-mm/`. Manual pass: run Overstrike under Proton, add the `.smpcmod`/`.mmpcmod` files, Install. Remastered: 1291 Real Brands, 3179 Expressive Combat, 3550 Tenacious, 2520 Infinite Web Gadget, 2868 Traversal Tweaks, 3200 Expressive Web Climbing, 634 NYC Lighting, 2524 Ultimate Spidey. Miles: 81 TaMT, 29 Unnerfed, 216 Realistic NYC, 26 Infinite Web Zip, 155 Infinite Camo, 317 Infinite Gadget Ammo. |
| Red Dead Redemption 2 (`1174180`) | No clean drop-in subset — every functional mod needs an external loader whose **Proton compatibility can't be verified headlessly**. **Script Hook RDR2** (`dinput8` ASI loader from dev-c.com) drives the `.asi` mods: 233 Rampage, 1662 Enhanced Brawling, 1675 A.E.M, 3465 Auto Looting, 1245 Reveal Map, 842 Better Horses, 1970 No Auto Horse Equipping, 3302 Auto Crafting, 1828 No VRAM Warning (Scripthook V2 file). **Lenny's Mod Loader (LML)** drives 1389 Remove Black Bars (`install.xml`), 2189 Terrain Textures Overhaul (**13.6 GB**), 5495 Spawns Fix (`gameconfig.xml`). 8 Intro Completed Save = user save data (manual). Manual pass: install ScriptHook RDR2 + LML under a GUI Proton session, verify they load, then drop each mod. |

### ✅ Follow-up review — FFVII 7th Heaven (reviewed 2026-08-06)

**Question:** can the FF7 mods be automated the `nexus-mod-set` way (direct file
placement), dropping the 7th Heaven / MateriaForge manager?

**Answer: no — keep `install_7th_heaven` (MateriaForge) as-is.** FF7 modding on
this box (FF7 2026 Steam Edition `3837340` is installed; 2013 `39140` is not) is a
**runtime mod-loader stack**, not a loose-file/pak overlay like the RE-Engine /
UE `~mods` games:

1. **FFNx is a mandatory runtime driver** — it replaces FF7's renderer and hooks
   asset loads (`ff7/workingdir/FFNx.toml`, which the role configures). It *is* the
   loader; there is no "no manager" path that keeps mods working.
2. **IRO mods layer at runtime** — 7th Heaven/MateriaForge resolves load order,
   per-mod settings, and conditional asset selection live. Static extraction loses
   that machinery.
3. **The mods come from the 7th Heaven catalog** (qhimm/iros), **not NexusMods** —
   there is no `nexus-download.py --game … --mod …` path, so the skill's
   download/preserve/verify pipeline doesn't apply.
4. A single pure-texture `.iro` *could* be hand-extracted into FFNx's loose
   `mods/Textures/` folder, but that still needs FFNx (same stack) and forfeits
   catalog updates + conditional settings — a net loss.

So the nexus-mod-set pattern (loose files / paks / IoStore triplets / natives)
doesn't replace a runtime IRO loader. `install_7th_heaven` already automates the
correct thing (bootstrapping FFNx + the manager); no change made.

---

## ✅ GTA IV: The Complete Edition — `install_gta4_mods`

Role: `install_gta4_mods` · appid `12210` (v1.2.0.59) · foundation: FusionFix
v5.0.1. Full write-up: [gta4-mods.md](gta4-mods.md). All 8 Nexus archives
downloaded (Premium API) + verified clean, staged at
`ROMS_FINAL/PC/NexusMods/gta4/`.

| Mod | File | Install |
|---|---|---|
| [716 Fusion Fix](https://www.nexusmods.com/gta4/mods/716) | GitHub v5.0.1 | foundation (loader + `update/` overloader) |
| [282 Higher-Res Vehicle Pack](https://www.nexusmods.com/gta4/mods/282) | 2627 (Complete Edition) | ✅ overloader |
| [357 Higher-Res Misc Pack](https://www.nexusmods.com/gta4/mods/357) | 1172 | ✅ overloader |
| [311 Higher-Res Radio Logos](https://www.nexusmods.com/gta4/mods/311) | 666 (CE) | ✅ overloader |
| [258 HD Protagonists](https://www.nexusmods.com/gta4/mods/258) | 513 | ✅ overloader |
| [263 Rivers of Blood](https://www.nexusmods.com/gta4/mods/263) | 2438 (Fusion Fix build) | ✅ overloader (not the OIV/RTX variant) |
| [195 Realistic Handling](https://www.nexusmods.com/gta4/mods/195) | 470 | ✅ overloader (applied last) |
| [272 Realistic Weapon Overhaul](https://www.nexusmods.com/gta4/mods/272) | 971 | 🔧 stats/models via overloader; **audio needs OpenIV** |
| [702 200+ Add-On Vehicles](https://www.nexusmods.com/gta4/mods/702) | 1602 | 🔧 **manual** (Liberty's Legacy framework) |

## 🔧 Art of Rally — `install_artofrally_mods`

Role: `install_artofrally_mods` · appid `550320` (on the USB library) ·
foundation: **Unity Mod Manager** v0.32.5a (Nexus `site/21`). These are UMM code
mods; UMM is deployed headlessly via DoorstopProxy (`winhttp.dll`), so the game
must run under **Proton** (`WINEDLLOVERRIDES="winhttp=n,b"`) and UMM's load must
be **verified in-game with Ctrl+F10** (option A — see the role header). No
ReShade; target build v1.5.5; mods land in `<game>/Mods/<Id>/`.

| Mod | UMM Id | Notes |
|---|---|---|
| [1 Camera Mod](https://www.nexusmods.com/artofrally/mods/1) (Thoxx) | CameraMod | extra cameras; pairs with FASTER |
| [10 Real car names](https://www.nexusmods.com/artofrally/mods/10) (MMike17) | RealCarNames | real names in menus |
| [15 FASTER](https://www.nexusmods.com/artofrally/mods/15) (MMike17) | FASTER | speed post-FX (Unity, not ReShade) |
| [4 era sponsorship](https://www.nexusmods.com/artofrally/mods/4) | aor.era.sponsorship | period sponsor branding |

## ✅ Alex Kidd in Miracle World DX — `install_alexkidddx_mods`

Role: `install_alexkidddx_mods` · appid `1333470` (USB library). A single
difficulty-rebalance mod — no loader, no deps, no ReShade — installed by
swapping the game's managed `Assembly-CSharp.dll` (stock backed up for revert).

| Mod | Type | Notes |
|---|---|---|
| [1 Enhanced (Nixos) v3.0](https://www.nexusmods.com/alexkiddinmiracleworlddx/mods/1) | difficulty rebalance (DLL swap) | after install, enable **Settings → reduced hitboxes** in-game; re-run after any Steam game update (it overwrites the DLL) |

## ✅ Ace Combat 7 — `install_ac7_mods`

Role: `install_ac7_mods` · appid `502500` (USB library). One mod, **Skies
Rebalanced v1.2E** — a plane/weapon rebalance shipped as UE4 `_P.pak` files;
installed by copying into `Game/Content/Paks/~mods/` (UE4 auto-mounts, no loader,
no ReShade). Choices baked as vars: **NON-DRIFT edition** (default; `DRIFT`
available) + one weapon-stats variant (default keeps vanilla TLS/MPBM).

| Mod | Type | Notes |
|---|---|---|
| [1400 Skies Rebalanced v1.2E](https://www.nexusmods.com/acecombat7skiesunknown/mods/1400) | plane/weapon rebalance (UE4 paks) | all plane paks + 1 weapon variant; `dg_ac7_edition` / `dg_ac7_weapon_variant` to change; Proton GE recommended for cutscenes |

## ✅ Black Myth: Wukong — `install_wukong_mods`

Role: `install_wukong_mods` · appid `2358720` (USB library) · loader: **RE-UE4SS**
(WukongUE4SS 1.3). Auto Regen is a UE4SS Lua mod; the role drops the loader
(`dwmapi.dll` + `ue4ss/`) into `b1/Binaries/Win64/`, installs the Lua mod, and
sets the Proton `WINEDLLOVERRIDES="dwmapi=n,b"` override. No ReShade.

| Mod | Type | Notes |
|---|---|---|
| [1289 Auto Regen](https://www.nexusmods.com/blackmythwukong/mods/1289) | UE4SS Lua (vital-stat regen) | tune rate in `ue4ss/Mods/BMWAutoRegen/Scripts/main.lua` (`VitalityConfig`, 5–50) |

## ✅ Bloodstained: Ritual of the Night — `install_bloodstained_mods`

Role: `install_bloodstained_mods` · appid `692850` (USB library). 7 UE4 `.pak`
DataTable mods copied into `BloodstainedRotN/Content/Paks/~mods/` (auto-mounted,
no loader/deps/ReShade). **Mods 67 & 38 conflict** (same drop asset) — role
installs one via `dg_bloodstained_droprate` (default `38` = 100%). **Caveat:**
these are launch-era ~v1.0 paks (overwrite whole DataTables); maintained v1.31+
successors exist if a table regresses on the current build.

| Mod | Type | |
|---|---|---|
| [68 Improved Descriptions](https://www.nexusmods.com/bloodstainedritualofthenight/mods/68) | UI text | ✅ |
| [64 Faster Movement](https://www.nexusmods.com/bloodstainedritualofthenight/mods/64) | +15% move | ✅ |
| [60 Fast Techniques](https://www.nexusmods.com/bloodstainedritualofthenight/mods/60) | quick mastery | ✅ |
| [65 Improved Crafting](https://www.nexusmods.com/bloodstainedritualofthenight/mods/65) | crafting economy | ✅ |
| [33 Max Stack Plus](https://www.nexusmods.com/bloodstainedritualofthenight/mods/33) | 999 stacks | ✅ |
| [38 Drop Rate Plus](https://www.nexusmods.com/bloodstainedritualofthenight/mods/38) | 100% drops | ✅ default |
| [67 Improved Drop Rates](https://www.nexusmods.com/bloodstainedritualofthenight/mods/67) | +10% drops | alt (`droprate=67`) — conflicts with 38 |

## ✅ Dark Souls: Remastered — `install_dsr_mods`

Role: `install_dsr_mods` · appid `570940` (in-box library). Swaps the game's
`param/GameParam/GameParam.parambnd.dcx` for the **Easy mode** (#293) variant
(stock backed up). No loader, no ReShade. **Play OFFLINE** — a modded character
online risks a FromSoftware soft-ban (DSR has no client anti-cheat, so it runs
modded under Proton fine).

| Mod | Type | Notes |
|---|---|---|
| [293 Easy mode](https://www.nexusmods.com/darksoulsremastered/mods/293) | difficulty (GameParam) | `dg_dsr_easymode_variant` = 50 (default) / 70 / 95 % damage reduction |
| [220 DSR 2020 Textures](https://www.nexusmods.com/darksoulsremastered/mods/220) | HD textures | ⏸️ deferred — needs the DSR-TPUP .NET repack GUI |
| [7 Enhanced Lighting](https://www.nexusmods.com/darksoulsremastered/mods/7) | ReShade preset | ⛔ dropped (no-ReShade rule) |

## ✅ Elden Ring — `install_eldenring_mods`

Role: `install_eldenring_mods` · appid `1245620` (USB library). Swaps
`Game/regulation.bin` for the **Easy Mode** (#146) variant (stock backed up).
No ReShade. **Play OFFLINE** (modded online = ban). Targets game **1.12.2 + SotE**;
for a clean EAC bypass, load via ModEngine2 on Proton (elden-proton) instead.

| Mod | Type | Notes |
|---|---|---|
| [146 Easy Mode](https://www.nexusmods.com/eldenring/mods/146) | difficulty (`regulation.bin`) | `dg_eldenring_variant` = `default` (10× rune, default) / `damage` / `personal` |

## ✅ FINAL FANTASY VII REMAKE Intergrade — `install_ff7remake_mods`

Role: `install_ff7remake_mods` · appid `1462040` (USB library). UE4 `.pak`
DataTable mods into `End/Content/Paks/~mods/` (auto-mounted, no loader/ReShade).
**Conflict: 85 ⟂ 586** (both rewrite equipment) — role uses the **Overhaul**
profile (586 + 251 + 630 + 479, **85 dropped**). Each mod ships many variants;
the pinned picks:

| Mod | Variant | |
|---|---|---|
| [586 Gameplay Enhancement](https://www.nexusmods.com/finalfantasy7remake/mods/586) | Full Package (All Items, v12-Final) | ✅ |
| [251 Lv99](https://www.nexusmods.com/finalfantasy7remake/mods/251) | "with other mods" (compat) | ✅ |
| [630 Summon Easy](https://www.nexusmods.com/finalfantasy7remake/mods/630) | Easy and Unlimited (v2) | ✅ |
| [479 Invincible Motorcycle](https://www.nexusmods.com/finalfantasy7remake/mods/479) | single file | ✅ |
| [85 Equipment Rebalance](https://www.nexusmods.com/finalfantasy7remake/mods/85) | — | ⛔ dropped (conflicts with 586) |

## ✅ FINAL FANTASY VII REBIRTH — `install_ff7rebirth_mods`

Role: `install_ff7rebirth_mods` · appid `2909400` (USB library). 5 UE4 IoStore
gameplay mods (`.pak`+`.ucas`+`.utoc` triplets) into `End/Content/Paks/~mods/`
(no loader/ReShade). 2 of 7 deferred.

| Mod | Variant | |
|---|---|---|
| [74 Most Combative Team](https://www.nexusmods.com/finalfantasy7rebirth/mods/74) | single | ✅ |
| [157 100% Steal/Drop](https://www.nexusmods.com/finalfantasy7rebirth/mods/157) | single | ✅ |
| [61 8 Materia+Skill Slots](https://www.nexusmods.com/finalfantasy7rebirth/mods/61) | MAX LV weapons+armors | ✅ |
| [140 Fast ATB](https://www.nexusmods.com/finalfantasy7rebirth/mods/140) | Never Stop + Limit | ✅ |
| [199 Stagger](https://www.nexusmods.com/finalfantasy7rebirth/mods/199) | Rate x2 | ✅ |

## ✅ GRANDIA HD Remaster — `install_grandia_mods`

Role: `install_grandia_mods` · appid `1034860` (USB library). Loose-file ops on
`content/` (no loader/ReShade).

| Mod | Type | Notes |
|---|---|---|
| [1 Actual HD Textures](https://www.nexusmods.com/grandiahdremaster/mods/1) | HD PNG atlases | overlaid into `content/FIELD/` |
| [2 Texture Picker + Intro Skip](https://www.nexusmods.com/grandiahdremaster/mods/2) | filter/intro toggle (.bat) | reimplemented natively: `dg_grandia_remove_filters` (move filter data → `_backup`, sharp originals) + `dg_grandia_skip_intro` |

## ✅ MGS Δ: Snake Eater — `install_mgsdelta_mods`

Role: `install_mgsdelta_mods` · appid `2417610` (USB library, UE5). Three
mechanisms, all headless.

| Mod | Type | Notes |
|---|---|---|
| [17 Camera Tweaks](https://www.nexusmods.com/metalgearsoliddeltasnakeeater/mods/17) | UE5 pak → `~mods` | `dg_mgsdelta_camera_variant` = `117` Camera FoV (default) / `119` / `118`; `dg_mgsdelta_install_guns_scope` optional |
| [27 MGSDeltaFix](https://www.nexusmods.com/metalgearsoliddeltasnakeeater/mods/27) | ASI (`dsound.dll`) → Binaries/Win64 | needs launch option `WINEDLLOVERRIDES="dsound=n,b" %command%` |
| [14 Ultimate Engine Tweaks](https://www.nexusmods.com/metalgearsoliddeltasnakeeater/mods/14) | `Engine.ini` → Proton prefix (read-only) | needs the prefix (launch game once first); No-VRR default |

## ✅ MGS3 (Master Collection) — `install_mgs3mc_mods`

Role: `install_mgs3mc_mods` · appid `2131650` (USB library). MGSHDFix + Community
Bugfix extract into the game root; MGSHDFix loads via a `wininet/winhttp` proxy.

| Mod | Type | Notes |
|---|---|---|
| [139 MGSHDFix](https://www.nexusmods.com/metalgearsolid3mc/mods/139) | ASI resolution/widescreen fix | launch option `WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%`; set in-game res/upscaling to Default |
| [189 Community Bugfix (Base)](https://www.nexusmods.com/metalgearsolid3mc/mods/189) | loose CTXR texture fixes | requires 139 |
| [26 NG+ saves](https://www.nexusmods.com/metalgearsolid3mc/mods/26) | savegames | ✅ placed into `<game>/mgs3_savedata_win/<steamid>/` as NG+ slots **6–A** (your save is slot 1, untouched); dir backed up as `<steamid>.dg-save-backup`. |

> **⚠️ MGS3 MC — two Proton gotchas (both handled):**
> 1. **Boot / MGSHDFix settings.** MGSHDFix 4.x won't run without a valid
>    `MGSHDFix.settings` and can't auto-generate one (its Config Tool must run
>    once). The role now **self-heals** this — `scripts/regen-mgshdfix-settings.sh`
>    runs the Config Tool offscreen to (re)generate a valid settings file,
>    idempotently, after every install. (Both roles' `.asi` come from Nexus at
>    4.0.2 while `metal_gear_master_collection` installs 3.1.0 — the regen makes
>    the settings match whatever `.asi` is on disk, so the version drift can't
>    re-break it.)
> 2. **Cutscene audio.** The `movie/*.sdt` cutscenes are MP4 (H.264 + **AAC**).
>    Proton 11.0's built-in Media Foundation decodes the video but not AAC, so
>    cutscenes play silent. **Fix: run MGS3 under GE-Proton** (bundles the AAC
>    codec) — set in `config/config.vdf` `CompatToolMapping` → `2131650` →
>    `GE-Proton11-1` (Steam must be closed; backup `config.vdf.dg-backup-mgs3ge`).
>    This is a per-game **Proton override**, the same idea as a launch-command
>    dependency — re-apply it after a Steam config reset.

## ✅ MGS2 (Master Collection) — `install_mgs2mc_mods`

Role: `install_mgs2mc_mods` · appid `2131640` (USB library). Same MGSHDFix
ecosystem; all headless drops. Load order 49 → 52 → 19/122 → 110.

| Mod | Type | Notes |
|---|---|---|
| [49 MGSHDFix](https://www.nexusmods.com/metalgearsolid2mc/mods/49) | ASI fix | launch option `WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%` |
| [52 Community Bugfix (Base)](https://www.nexusmods.com/metalgearsolid2mc/mods/52) | CTXR textures/fixes | needs 49; recommends Better Audio Mod (off-set) |
| [19 KojiPro Posters](https://www.nexusmods.com/metalgearsolid2mc/mods/19) | HD posters | after 52 |
| [122 UI Textures](https://www.nexusmods.com/metalgearsolid2mc/mods/122) | UI upscale | 2× variant |
| [110 Stillman Skippable](https://www.nexusmods.com/metalgearsolid2mc/mods/110) | `.gcx` → `assets/gcx/eu/_bp` | EU path; incompatible with JP language pack |
| [10 Snake Hair Fix](https://www.nexusmods.com/metalgearsolid2mc/mods/10) | — | ⛔ omitted (redundant — 52 bundles it) |
| [392 Gameplay Enhancement](https://www.nexusmods.com/finalfantasy7rebirth/mods/392) | — | ⏸️ deferred (12 sub-items to curate; conflicts with 61) |
| [3 Ultimate Engine Tweaks](https://www.nexusmods.com/finalfantasy7rebirth/mods/3) | FFVIIHook + Engine.ini | ✅ now installed via `install_ff7rebirth_engine`: FFVIIHook (`xinput1_3.dll`) → `End/Binaries/Win64`, the **No-VRR** Engine.ini → the prefix's `AppData/Local/End/Saved/Config/Windows/`, launch option `WINEDLLOVERRIDES="xinput1_3=n,b" %command%`. Update FFVIIHook after game patches; re-run if the game regenerates Engine.ini. |

## ✅ MGS1 (Master Collection) — `install_mgs1mc_mods`

Role: `install_mgs1mc_mods` · appid `2131630` (USB library). MGS1 in the MC runs
on Konami's **M2ENGAGE** emulator, so its base loader is **MGSM2Fix** (nuggslet),
**not** MGSHDFix. The release drops `d3d11.dll` + `dinput8.dll` proxies +
`MGSM2Fix32/64.asi` + `MGSM2Fix.ini` into the game root; edit `MGSM2Fix.ini` to
tune widescreen/resolution/FMV.

| Mod | Type | Notes |
|---|---|---|
| [5 MGSM2Fix](https://www.nexusmods.com/metalgearsolidmc/mods/5) | ASI loader/fix | launch option `WINEDLLOVERRIDES="dinput8=n,b;d3d11=n,b" %command%` (dinput8+d3d11, **not** wininet/winhttp) |
| [3 HD RetroArch CRT Shader](https://www.nexusmods.com/metalgearsolidmc/mods/3) | — | ⛔ dropped — ReShade-tagged; pipeline needs RetroArch Windowcast + Windows PowerToys + NVIDIA Profile Inspector + interactive GUI setup, PC-only |

## ✅ Red Dead Redemption — `install_rdr_mods`

Role: `install_rdr_mods` · appid `2668510` (USB library). The 2023 PC port keeps
its `.rpf` archives **loose** under `<game>/game/`, so mods that ship a complete
replacement archive are clean drop-ins — the role backs up each original as
`<name>.rpf.dg-orig` (revert restores it). Only 2 of 11 qualify; the rest need
**MagicRDR** (GUI archive injection), an ASI/script loader, or are save data.

| Mod | Type | Notes |
|---|---|---|
| [20 Fast Launch](https://www.nexusmods.com/reddeadredemption/mods/20) | full `.rpf` swap | replaces `game/tune_d11generic.rpf` (skips boot logos) |
| [89 RDR2 Camera](https://www.nexusmods.com/reddeadredemption/mods/89) | full `.rpf` swap | replaces `game/camera.rpf` (RDR2-style camera; MAIN file, not the "closer" variant) |
| [21 RDR Reimagined](https://www.nexusmods.com/reddeadredemption/mods/21) | — | ⛔ dropped — ReShade preset (`reshade-shaders/*.fx`) |
| [525 RDR2 Minimap](https://www.nexusmods.com/reddeadredemption/mods/525) | — | ⏸️ deferred — readme requires **MagicRDR** to inject into `mapres.rpf` + `fonts.rpf` |
| [66 SMIC Textures](https://www.nexusmods.com/reddeadredemption/mods/66) | — | ⏸️ deferred — loose `.wtd`, needs MagicRDR injection into a parent `.rpf` |
| [303 Fast Horse](https://www.nexusmods.com/reddeadredemption/mods/303) | — | ⏸️ deferred — `hrssimtune.xml`, needs MagicRDR injection (pick the "Fast horse" MAIN vs Faster/Fastest variants) |
| [140 Unlimited Deadeye](https://www.nexusmods.com/reddeadredemption/mods/140) | — | ⏸️ deferred — `playertune.xml`, needs MagicRDR injection |
| [719 RDRFix](https://www.nexusmods.com/reddeadredemption/mods/719) | ASI (via `install_rdr_asi`) | ✅ now installed — Ultimate ASI Loader (`dinput8.dll`) + `RDRFix.asi`/`.ini` next to `RDR.exe`; launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%`. v1.3 (intro skip, FPS-cap removal, ultrawide bars, physics-timestep fix, post-fx toggles). Edit `RDRFix.ini`. The more complete of the "similar" fixes (supersedes FusionFix). |

> **⚠️ RDR "running install script" hang (Proton) — fixed by `install_rdr_asi`.**
> RDR's Steam install script (`installscript_sdk.vdf`) silently installs Social Club
> + the **Rockstar Games Launcher**, each gated by a registry *HasRunKey*. The RGL
> silent installer **deadlocks under Proton** (0% CPU forever), so its HasRunKey is
> never written and Steam re-runs the hung installer every launch → the game never
> starts. Fix: write `HKLM\Software\Wow6432Node\Rockstar Games\Steam\Launcher`
> `"101082970"=dword:1` into the prefix's `system.reg` so Steam skips the
> (already-installed) RGL. `install_rdr_asi` now does this idempotently (var
> `dg_rdr_asi_fix_rgl_hang`, backup `system.reg.dg-rdr-backup`) and self-heals if a
> game session rewrites the registry. **Same hang applies to other Rockstar titles
> under Proton (GTA V, RDR2)** — the same HasRunKey trick unblocks them.
| [475 Basic Trainer](https://www.nexusmods.com/reddeadredemption/mods/475) | — | ⏸️ deferred — `.red` script, needs a mod-menu/script loader |
| [114 Starter Save](https://www.nexusmods.com/reddeadredemption/mods/114) · [515 100% Saves](https://www.nexusmods.com/reddeadredemption/mods/515) | — | ⏸️ manual — user save data (repo Safety: never overwrite saves) |

## ✅ Resident Evil 4 (2023 Remake) — `install_re4r_mods`

Role: `install_re4r_mods` · appid `2050650` (USB library). RE Engine loads loose
`<game>/natives/` files and numbered `re_chunk_000.pak.patch_NNN.pak` archives
over the base paks, so **Fluffy Mod Manager** packages install headlessly — no
Fluffy GUI. The role copies a `natives/` tree in, or a `.pak` to a free high slot
(`pak_slot` 900+), tracking each in a `.dg-re4r-<id>.manifest` for clean revert.
This same natives/pak mechanism is reused for RE2/RE3/Village/Requiem.

| Mod | Type | Notes |
|---|---|---|
| [117 Stack Size Changes](https://www.nexusmods.com/residentevil42023/mods/117) | patch `.pak` | v1.10; variant **"Stack Size (All)- 0999"** → `patch_900.pak` (999 stacks, no herb change) |
| [3429 Infinite Ammo](https://www.nexusmods.com/residentevil42023/mods/3429) | `natives/` overlay | v1.5; 5 loose `natives/STM/...` files |

## ✅ Resident Evil 2 (2019) — `install_re2_mods`

Role: `install_re2_mods` · appid `883710` (**box** Steam library — hardcoded, not
USB). Same RE Engine Fluffy natives/pak handler as RE4R.

| Mod | Type | Notes |
|---|---|---|
| [1627 Infinite Ammo](https://www.nexusmods.com/residentevil22019/mods/1627) | `natives/` overlay | v1.1 (2024); `natives/stm/...` — RT-build compatible |
| [182 Weapon & Ammo Overhaul](https://www.nexusmods.com/residentevil22019/mods/182) · [205 Full Pack Ammo](https://www.nexusmods.com/residentevil22019/mods/205) | — | ⏭️ skipped — 2019-era, use the legacy `natives/x64/` layout + old `.scn.19` scene files that the current **ray-tracing build ignores** (it reads `natives/stm/`). Revisit only on the `raytracing_off` classic branch; 182 also needs a variant pick (WAO full-pack vs less-ammo vs keyitem). |

## ✅ Resident Evil 3 (2020) — `install_re3_mods`

Role: `install_re3_mods` · appid `952060` (**box** Steam library). Same RE Engine
Fluffy handler.

| Mod | Type | Notes |
|---|---|---|
| [990 Infinite Ammo](https://www.nexusmods.com/residentevil32020/mods/990) | `natives/` overlay | pinned the **`1.0-RT`** file (3405) → `natives/stm/` for the ray-tracing build (the non-RT file 3407 targets the classic branch) |

## ✅ Resident Evil Requiem (RE9) — `install_rerequiem_mods`

Role: `install_rerequiem_mods` · appid `3764200` (USB library). Same RE Engine
Fluffy handler.

| Mod | Type | Notes |
|---|---|---|
| [14 Stack Size Changes](https://www.nexusmods.com/residentevilrequiem/mods/14) | `natives/` overlay | v1.4; variant **"Stack Size (All)- 00999"** → `natives/STM/...` (999 stacks) |
| [25 Inf Ammo & HP](https://www.nexusmods.com/residentevilrequiem/mods/25) · [100 Infinite CP](https://www.nexusmods.com/residentevilrequiem/mods/100) | REFramework Lua | ✅ now installed via `install_reframework` (loader `dinput8.dll` + `reframework/autorun/*.lua`; mod 25 bundles infinite HP/ammo + aim-assist + auto-parry). Launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%`. |

## ✅ Resident Evil Village — `install_revillage_mods`

Role: `install_revillage_mods` · appid `1196590` (**box** Steam library). Same RE
Engine Fluffy handler.

| Mod | Type | Notes |
|---|---|---|
| [299 Reworked Weapons Mod](https://www.nexusmods.com/residentevilvillage/mods/299) | `natives/` overlay | v1.01; `natives/stm/...` weapon spec data (ships a harmless `.bak`, tracked in the manifest) |
| [457 Higher Resolution Enemies](https://www.nexusmods.com/residentevilvillage/mods/457) | `natives/` overlay | v1.0.0; ~1.5 GB, 237 `natives/stm/character/...` textures |
| [651 Infinite Ammo](https://www.nexusmods.com/residentevilvillage/mods/651) | REFramework Lua | ✅ now installed via `install_reframework` (`reframework/autorun/Infinite Ammo.lua` + loader `dinput8.dll`); launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%` |
| [184 Newgame Plus - WCX Gun Max Upgrade](https://www.nexusmods.com/residentevilvillage/mods/184) | — | ⏸️ manual — `data00*.bin` **save files** (repo Safety: never overwrite saves) |

## ✅ Resident Evil 0 (HD Remaster) — `install_re0_mods`

Role: `install_re0_mods` · appid `339340` (**box** Steam library). RE0 HD runs on
**MT Framework**, which loads loose files from `<game>/nativePC/` over the `.arc`
archives — so the mod installs by copying its `nativePC/` tree in (manifest-tracked).

| Mod | Type | Notes |
|---|---|---|
| [39 Item Box](https://www.nexusmods.com/residentevil0biohazard0hdremaster/mods/39) | `nativePC/` overlay | v0.5.2; adds a shared item box (8 `nativePC/arc/message/msg_*_box.arc` files) |
| [58 re0ct](https://www.nexusmods.com/residentevil0biohazard0hdremaster/mods/58) | — | ⏸️ manual — **Cheat Engine table** (`re0hd_v14.CT`); needs the Cheat Engine GUI under Proton |

## ✅ RoboCop: Rogue City — `install_robocop_mods`

Role: `install_robocop_mods` · appid `1681430` (USB library). UE5 game — loads
loose `.pak`/`.ucas`/`.utoc` triplets from `Game/Content/Paks/~mods/`, so these
install headlessly by dropping the triplet in (manifest-tracked).

| Mod | Type | Notes |
|---|---|---|
| [1 No-Intro / Splash Fix](https://www.nexusmods.com/robocoproguecity/mods/1) | `~mods` pak | v0.3; skips startup logos |
| [43 Old Man](https://www.nexusmods.com/robocoproguecity/mods/43) · [44 Casey Wong](https://www.nexusmods.com/robocoproguecity/mods/44) · [47 Sgt Reed](https://www.nexusmods.com/robocoproguecity/mods/47) · [50 Anne Lewis](https://www.nexusmods.com/robocoproguecity/mods/50) | `~mods` pak triplet | movie-accurate voice packs (`_P.pak` + `.ucas` + `.utoc`) |
| [7 Performance & Lighting](https://www.nexusmods.com/robocoproguecity/mods/7) | — | ⏸️ deferred — `Engine.ini`/`GameUserSettings.ini`/`Scalability.ini` config overlay; prefix-dependent and clobbers the user's own graphics settings |
| [2 Ultra Plus](https://www.nexusmods.com/robocoproguecity/mods/2) | UE4SS (self-contained) | ✅ now installed via `install_ue4ss` — the **Steam** file (206) bundles a full UE4SS install; its `Game/` tree (dwmapi.dll + `ue4ss/UE4SS.dll` + `UltraPlusExtensions` + companion pak) drops into the game root. Launch option `WINEDLLOVERRIDES="dwmapi=n,b" %command%` |
| [49 New Game Plus](https://www.nexusmods.com/robocoproguecity/mods/49) | — | ⏸️ manual — `.sav` **save files** (repo Safety: never overwrite saves) |

## ✅ Sekiro: Shadows Die Twice — `install_sekiro_mods`

Role: `install_sekiro_mods` · appid `814380` (USB library). No anti-cheat
(single-player), so a bundled `dinput8.dll` hook works with a Proton override.

| Mod | Type | Notes |
|---|---|---|
| [1058 Weapon Wheel](https://www.nexusmods.com/sekiro/mods/1058) | bundled `dinput8.dll` | v1.2.1; drops `dinput8.dll` + `WeaponWheelResources/` into the game root; launch option `WINEDLLOVERRIDES="dinput8=n,b" %command%` |
| [418 Sekiro The Easy](https://www.nexusmods.com/sekiro/mods/418) | Sekiro Mod Engine | ✅ now installed via `install_sekiro_modengine`. ModEngine2 doesn't support Sekiro, so this uses **Sekiro Mod Engine** (katalash, `dinput8.dll` + `modengine.ini`, mods from `<game>/mods/`). It coexists with the Weapon Wheel by **dinput8 chainloading**: ModEngine becomes `dinput8.dll`, the Weapon Wheel is renamed `weaponwheel.dll` and set as `chainDInput8DLLPath`. Revert this role **before** `install_sekiro_mods`. |

## ✅ Streets of Rage 4 — existing `install_sor4_reignited`

Mod [133 REIGNITED](https://www.nexusmods.com/streetsofrage4/mods/133) was already
covered before this project by the `install_sor4_reignited` role (tag
`sor4_reignited`), which replaces SOR4's encrypted `data/bigfile` (vanilla backed
up). It is pinned to **v1.0.0** (from the author's GitLab). Nexus is now at
**v2.0.0** — not auto-bumped: the mod is built against a specific game patch, so
updating the `bigfile` must match the installed SOR4 version and can't be verified
headlessly. Bump `dg_sor4_reignited_version` + the bigfile sha256 deliberately.

## ✅ Tokyo Xtreme Racer — `install_txr_mods`

Role: `install_txr_mods` · appid `2634950` (USB library). UE5 — loads loose paks
from `<game>/TokyoXtremeRacer/Content/Paks/~mods/` (doubled dir: Steam installdir
+ inner UE project). (The source list repeats mod 87, so 3 unique mods.)

| Mod | Type | Notes |
|---|---|---|
| [83 No Wanderer Requirements](https://www.nexusmods.com/tokyoxtremeracer/mods/83) | `~mods` pak triplet | v1.2; the **NoWandererRequirements** file (per the user's note) — removes rival-challenge conditions, no Wanderer-framework dependency |
| [87 Ultradynamic TXR](https://www.nexusmods.com/tokyoxtremeracer/mods/87) | UE4SS (core + overlay) | ✅ now installed via `install_ue4ss` — UE4SS core (v3.0.1) into `TokyoXtremeRacer/Binaries/Win64` + the mod's `Mods/` (TXR_DayNightCycle, TXR_AdditionalSettings) overlaid. Launch option `WINEDLLOVERRIDES="dwmapi=n,b" %command%` |
| [5 All Perks + Money](https://www.nexusmods.com/tokyoxtremeracer/mods/5) | — | ⏸️ manual — `UserData_00.sav` **save file** (repo Safety: never overwrite saves) |

## ✅ UNCHARTED: Legacy of Thieves — `install_uncharted_mods`

Role: `install_uncharted_mods` · appid `1659420` (USB library). Plain
file-replacement mods whose archives carry the correct game-relative paths; the
role rsyncs them in and backs up any pre-existing file to `<file>.dg-orig`
(manifest-tracked).

| Mod | Type | Notes |
|---|---|---|
| [137 DLSS 4 (v310.7)](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/137) | DLL swap | replaces game-root `nvngx_dlss.dll` with the newer DLSS runtime |
| [11 PS Video Removed](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/11) | `.psarc` replace | swaps the two `Uncharted4_data/build/pc/{uncharted4,thelostlegacy}/rad1.psarc` (~1.6 GB) to drop the Sony intro; originals backed up |
| [107 RenoDX](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/107) | — | ⛔ dropped — a **ReShade addon** (`.addon64`); ReShade excluded per project rule |
| [2 27GB Reducer](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/2) | — | ⏭️ skipped — overwrites foreign-language voice `.psarc` with 6-byte empty stubs (destroys audio data); against repo Safety |
| [22 Save File](https://www.nexusmods.com/unchartedlegacyofthievescollection/mods/22) | — | ⏸️ manual — user save data |

## ✅ The Witcher 3: Wild Hunt (Next-Gen) — `install_witcher3_mods`

Role: `install_witcher3_mods` · appid `292030` (**box** library; game is Next-Gen,
`bin/x64_dx12`). W3 loads mods natively from `<game>/mods/mod<Name>/`, so these
drop in headlessly (no loader). Manifest-tracked (whole mod folders).

| Mod | Notes |
|---|---|
| [943 Map Quest Objectives](https://www.nexusmods.com/witcher3/mods/943) · [3 Over 9000 Weight](https://www.nexusmods.com/witcher3/mods/3) · [324 Fast Travel Anywhere](https://www.nexusmods.com/witcher3/mods/324) · [820 Always Full Exp](https://www.nexusmods.com/witcher3/mods/820) · [342 Indestructible Items](https://www.nexusmods.com/witcher3/mods/342) · [315 AutoLoot](https://www.nexusmods.com/witcher3/mods/315) · [352 No Fall Damage](https://www.nexusmods.com/witcher3/mods/352) | script/gameplay `mod*/` folders |
| [657 Super Turbo Lighting (NGE)](https://www.nexusmods.com/witcher3/mods/657) · [1024 High Quality Faces](https://www.nexusmods.com/witcher3/mods/1024) | visual `mod*/` folders (NGE = Next-Gen build) |
| [38 Increased Creature Loot](https://www.nexusmods.com/witcher3/mods/38) | FOMOD — installed the **`2_ICL`** variant (`modICL`) |
| [3580 HD Monsters Reworked](https://www.nexusmods.com/witcher3/mods/3580) | ✅ installed the **v5.0 Next-Gen** edition (~7 GB): `modHDMonstersReworked5` (Part 1) + `modHDMonstersReworked5_Exp` (Part 2, DLC monsters) + `modHDMR5_LOD` (LOD optimization). Monster textures only — no conflict with the other mods. Extracts on NAS scratch, not `/tmp`. |
| [1021 HD Reworked Project](https://www.nexusmods.com/witcher3/mods/1021) | ⏭️ skipped — **OldGen-only** (the whole page tops out at the OldGen "Ultimate" v12, ~9.5 GB; there is no Next-Gen version, and CDPR folded HD Reworked textures into the official Next-Gen update). Wrong edition for this Next-Gen game. |

Note: script mods that touch shared scripts (AutoLoot, Weight) may need **Script
Merger** if they conflict in-game; installed as-is.

## ✅ WRC 7 — `install_wrc7_mods`

Role: `install_wrc7_mods` · appid `621830` (box library). One mod, the ~6 GB
**EVOlution MOD 4.0** — a total physics/damage/particles/sound/FFB overhaul that
ships a mirror of the game tree and **overwrites the game's data-chunk PKGs**
(`WIN32/PKG/CHUNK_*.PKG`, 139 files). The 6 GB `.rar` extracts on the NAS scratch
(not `/tmp`); files verified by size against the archive.

| Mod | Notes |
|---|---|
| [1 EVOlution MOD](https://www.nexusmods.com/wrc7/mods/1) | total overhaul; overwrites core data PKGs. **Revert = Steam → WRC 7 → Properties → Installed Files → Verify integrity** (re-downloads the originals), then `-e dg_wrc7_revert=true` to drop the manifest. |

## ⚠️ WRC 5 — flagged, not installed

Mod [3 "dlcunlock"](https://www.nexusmods.com/wrc5/mods/3) is **not a content mod**:
it ships a modified/emulated `steam_api.dll` + `steam_api.ini` + a 378 MB
`missingfiles.7z` to **unlock DLC without owning it**. That trips the crack-marker
legitimacy check (the exact `steam_api.dll` DRM-emulator pattern the skill inspects
for), so it was **not installed** — no role, no download applied. If you actually
own the WRC 5 DLCs and want them enabled, that needs a legitimate route, not a
Steam API emulator. Flagged for your decision.

