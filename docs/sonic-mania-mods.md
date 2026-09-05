# Sonic Mania modding stack · Sonic 2 (2013) + Sonic 2 Mania

`install_sonic_mania_mods` (`install-sonic-mania-mods.yml`,
`site.yml --tags sonic_mania_mods`) sets up three related things:

## 1. Sonic Megamix Mania (Steam Sonic Mania + Mania Mod Loader, Proton)

Megamix (sonicmegamixmania.github.io, v1.1.1 rar on the NAS) is a **DLL-based
mod** (ManiaAPI: AdvancedItemSystem.dll etc.) — Windows-only logic, so it runs
on the **Windows Sonic Mania under Proton** with the
[Mania Mod Loader](https://github.com/sonicretro/mania-mod-loader). The .NET
Mania Mod Manager GUI does **not** run under wine-mono, but the manager's
"Install loader" is trivially replicated headlessly (from its source):
`mods/ManiaModLoader.dll` copied into the game dir as **`d3d9.dll`**, mods
enabled in `mods/ManiaModLoader.ini` (`Mod1=Sonic Megamix Mania v1.1.1`; the
Amy Lock-On folder is staged too — add it as `Mod2=` to enable). Activation
needs the launch option (in `dg_steam_launch_options_by_appid`):

```
WINEDLLOVERRIDES="d3d9=n,b" %command%
```

then **launch Sonic Mania from Steam** (direct proton runs exit via Steam
DRM). Requires the **Encore DLC** (owned). Save data notes ship inside the
Megamix rar (`SAVEDATA (if needed)` + READMEs).

**Switching Megamix ⇄ vanilla:** the loader always loads; which mods are
active is `mods/ManiaModLoader.ini`. Use the Walker entries
**"Sonic Mania — Megamix"** / **"Sonic Mania — Vanilla"** (or
`bin/mania-mode megamix|vanilla`) — they write the ini and launch through
Steam. A DRM quirk to know: a direct `proton run` of the game exits and
spawns a NESTED Steam via `steam://run/…`, leaving a ghost "running" app that
crashes Steam's Stop button — kill any processes whose args carry
`steam://run/584400` if that ever happens.

## 2. Sonic 2 (2013) + the "Sonic 2 Mania" mod (native)

The GameBanana "Sonic 2 Mania" mod (`sonic_2_mania_9e646.zip`) targets
**Sonic 2 (2013)**, not Sonic Mania. The role builds the
[RSDKv4 decompilation](https://github.com/RSDKModding/RSDKv4-Decompilation)
natively in the box, extracts `Data.rsdk` from the user's Android XAPK
(`assets/Data.rsdk.xmf` inside `com.sega.sonic2.runner.apk`), installs the
data-only mod under `mods/` and enables it via `mods/modconfig.ini`
(`[mods]` / `Sonic 2 Mania=y`), and seeds `settings.ini` fullscreen +
DevMenu. Verified: fullscreen DP-1, classic cartridge start screen.
Launcher `bin/sonic2-2013`, Walker "Sonic 2 (2013) + Sonic 2 Mania".

## 3. Native Sonic Mania decompilation (data-only mods)

The [Mania decompilation](https://github.com/RSDKModding/Sonic-Mania-Decompilation)
(RSDKv5U + libGame.so) is also built natively — it symlinks the Steam
install's `Data.rsdk` and loads **data-only** mods from its `mods/` dir.
DLL mods (Megamix) cannot load here; use route 1 for those.
Launcher `bin/sonic-mania-decomp`, Walker "Sonic Mania · Decomp".
