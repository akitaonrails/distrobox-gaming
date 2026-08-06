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
| Dark Souls Remastered | darksoulsremastered | `570940` | 3 | ⏳ |
| Elden Ring | eldenring | `1245620` | 1 | ⏳ |
| FINAL FANTASY VII REMAKE Intergrade | finalfantasy7remake | `1462040` | 5 | ⏳ |
| FINAL FANTASY VII REBIRTH | finalfantasy7rebirth | `2909400` | 7 | ⏳ |
| Grand Theft Auto V Enhanced | gta5enhanced | `3240220` | 7 | ⏳ |
| GRANDIA HD Remaster | grandiahdremaster | `1034860` | 2 | ⏳ |
| Metal Gear Rising: Revengeance | metalgearrisingrevengeance | `235460` | 4 | ⏳ |
| MGS Δ: Snake Eater | metalgearsoliddeltasnakeeater | `2417610` | 3 | ⏳ |
| MGS3 (Master Collection) | metalgearsolid3mc | `2131650` | 3 | ⏳ |
| MGS2 (Master Collection) | metalgearsolid2mc | `2131640` | 6 | ⏳ |
| MGSV: Ground Zeroes | metalgearsolidvgz | `311340` | 2 | ⏳ |
| MGS1 (Master Collection) | metalgearsolidmc | `2131630` | 2 | ⏳ |
| MGSV: The Phantom Pain | metalgearsolidvtpp | `287700` | 6 | ⏳ |
| Red Dead Redemption | reddeadredemption | `2668510` | 11 | ⏳ |
| Red Dead Redemption 2 | reddeadredemption2 | `1174180` | 13 | ⏳ |
| Resident Evil 4 (2023 Remake) | residentevil42023 | `2050650` | 2 | ⏳ |
| Resident Evil 2 (2019) | residentevil22019 | `883710` | 3 | ⏳ |
| Resident Evil 3 (2020) | residentevil32020 | `952060` | 1 | ⏳ |
| Resident Evil Requiem | residentevilrequiem | `3764200` | 3 | ⏳ |
| Resident Evil Village | residentevilvillage | `1196590` | 4 | ⏳ |
| Resident Evil 4 (2005) | residentevil4 | `254700` | 2 | ✅ re4_tweaks 1.9.1 via install_re4_hd (mod 306 dropped — wrong port) |
| Resident Evil 0 (HD Remaster) | residentevil0biohazard0hdremaster | `339340` | 2 | ⏳ |
| RoboCop: Rogue City | robocoproguecity | `1681430` | 8 | ⏳ |
| Sekiro: Shadows Die Twice | sekiro | `814380` | 2 | ⏳ |
| Marvel's Spider-Man Remastered | marvelsspidermanremastered | `1817070` | 8 | ⏳ |
| Marvel's Spider-Man: Miles Morales | spidermanmilesmorales | `1817190` | 6 | ⏳ |
| Streets of Rage 4 | streetsofrage4 | `985890` | 1 | ⏳ |
| Tokyo Xtreme Racer | tokyoxtremeracer | `2634950` | 4 | ⏳ |
| WRC 5 | wrc5 | `354160` | 1 | ⏳ |
| UNCHARTED: Legacy of Thieves | unchartedlegacyofthievescollection | `1659420` | 5 | ⏳ |
| Yakuza 0 (Director's Cut) | yakuza0 | `2988580` | 10 | ⏳ |

### ⛔ Skipped — not installed in Steam (as of the 2026-08-06 scan)

Re-check if you later install these; they're in `tmp/nexusmods.txt`.

| Game | Nexus domain | Reason |
|---|---|---|
| Resident Evil HD Remaster (RE1) | residentevilbiohazardhdremaster | not found in any Steam library |
| Metal Gear & Metal Gear 2 (MC) | metalgearandmetalgear2mc | not found in any Steam library |
| The Witcher 3 | witcher3 | not found in any Steam library |
| WRC 7 | wrc7 | not found in any Steam library |
| Colin McRae Rally 2 | colinmcraerally2 | not a Steam title (user-noted) — covered by `install_pc_racing` instead |

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

