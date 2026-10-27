# Shadow of the Colossus — native PC port (SOTC-PC)

[AjncSystem/ShadowOfTheColossus-PC](https://github.com/AjncSystem/ShadowOfTheColossus-PC)
`v0.60.6-C3` is a native Windows port of the **PS4 Bluepoint remake** of
Shadow of the Colossus: the game's own x86-64 code runs on the CPU, the PS4
GPU is translated to Vulkan (bloodborne_pc-style loader + shadPS4 video
core). Windows x64 exe → GE-Proton. Managed by `install_sotc_pc` /
`install-sotc-pc.yml`. Upstream status: **the game can be finished start to
end** (v0.60.3), high quality textures, PS4 Pro mode, 60 FPS.

## Game data (from the library's PRELUDE FPKGs)

`ROMS_FINAL/ps4/sotc-kyty/` — the merged **EU 1.01** dump:

- Base: `Shadow.of.the.Colossus.iNTERNAL.PS4-PRELUDE.pkg` (13.5 GB, CUSA08809
  EU, APP_VER 01.00, `\x7FCNT` retail PKG) — extracted with the box's
  **shadPKG** (`~/tools/ShadPKG/build-cli/shadpkg extract`).
- Update: `Shadow.of.the.Colossus.iNTERNAL.UPDATE.v1.01.PS4-PRELUDE.pkg`
  (16.8 MB, APP_VER 01.01, **data-only**: replaces `cachedfiles.psarc` +
  discmap — no eboot, matching the port's note that EU 1.01 and US 1.00 ship
  the same executable).
- **Case-conflict gotcha**: the base extracts `cachedFiles.psarc`, the update
  `cachedfiles.psarc` — on case-sensitive Linux both landed side by side (one
  auto-renamed "(case conflict)"). Fixed by copying the update's 1.01 psarc
  over the base-cased filename and deleting the duplicate, so whichever case
  the engine opens it gets 1.01 data (md5 `32e6b115…`).
- The four PRELUDE DLC rars (Ancient Bow / Cloak of Fate / Life Sword /
  Spotted Steed) unpack to 1 MB PKGs that shadPKG extracts empty — cosmetic
  DLC, not installed; revisit with shadPS4's own installer if wanted.

## ⚠️ Sound is missing on this box

The port needs **two decrypted firmware modules from your own PS4**:
`libSceNgs2.sprx` + `libSceUlt.sprx` (`/system/common/lib/`, via GoldHEN FTP).
Neither is on this box (no shadPS4 `user/sys_modules` either) — **the game
runs silent until they are copied** to `<app>/data/sys_modules/` or
`SOTC_SYS_MODULES` in `sotc.ini` points at a folder containing them. This is
a Sony-firmware redistribution boundary the project will not cross; the files
must come from your console.

## Baseline and run

Walker entry: **Shadow of the Colossus · PC Port**; launcher
`bin/sotc-pc` → `SotC.exe` via GE-Proton (Vulkan, nvidia ICD). `sotc.ini`
points at the game folder and sets **`SOTC_MODES=fps60`** (the PS4 Pro
Performance mode; 60 FPS through the game's own timing). In-game menu on
**F1** (FPS/upscaler/textures/sharpening/volume, apply at once); **F7**
30↔60↔unlimited, **F8** frame generation, **F11** fullscreen. First launch
builds shaders (~2 min load, pop-in on new areas). Textures: High is the
stable default (Maximum can crash in wide views).

Not yet launched on this box — first boot is the verification step (plus the
sound-module copy above).
