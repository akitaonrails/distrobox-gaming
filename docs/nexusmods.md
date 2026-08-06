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
| Alex Kidd in Miracle World DX | alexkiddinmiracleworlddx | `1333470` | 1 | ⏳ |
| Ace Combat 7 | acecombat7skiesunknown | `502500` | 1 | ⏳ |
| Batman: Arkham Knight | batmanarkhamknight | `208650` | 2 | ⏳ |
| Batman: Arkham City GOTY | batmanarkhamcity | `200260` | 3 | ⏳ |
| Batman: Arkham Asylum GOTY | batmanarkhamasylum | `35140` | 2 | ⏳ |
| Black Myth: Wukong | blackmythwukong | `2358720` | 1 | ⏳ |
| Bloodstained: RotN | bloodstainedritualofthenight | `692850` | 7 | ⏳ |
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
| Resident Evil 4 (2005) | residentevil4 | `254700` | 1 | ⏳ (see also install_re4_hd) |
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
