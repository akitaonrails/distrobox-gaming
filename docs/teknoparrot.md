# TeknoParrot arcade (Windows UI under Wine)

Arcade games via **TeknoParrot** running the stable Windows `TeknoParrotUI`
(1.0.0.2064, .NET Framework) under Wine in a dedicated prefix. Managed by
`install_teknoparrot` / `install-teknoparrot.yml`. Games launch from ES-DE
(system `teknoparrot`) via `bin/teknoparrot-launch <GameId>`.

## Why not the experimental native-Linux build

The teknogods **net8 Linux** build (`TeknoParrotUI-net8`, 2.0.0.127) is **broken**:
its zip ships **no .NET runtime, no Avalonia UI framework, and no game loaders**,
and its `ParrotPatcher` (which is supposed to download the loaders) doesn't work
on Linux. You can hand-graft the runtime + Avalonia (from NuGet) to get the UI to
*open*, but with no loaders **zero games launch**. So we use the Windows build
under Wine, whose loaders we fetch directly from GitHub. Revisit the native build
when teknogods ships a complete Linux release.

## The working recipe (what the role automates)

- **Prefix:** dedicated 64-bit Wine prefix at `wineprefixes/teknoparrot`.
- **winetricks:** `dotnet462` + `vcrun2010` (for the UI) and `d3dcompiler_47` +
  `d3dcompiler_43` + `dxvk` (for the D3D games).
- **Registry tweaks:**
  - `HKCU\Software\Wine\X11 Driver` `UseEGL=N` — force GLX on the RTX; wine 11's
    EGL backend picks the iGPU/llvmpipe and the UI renders **black** without it.
  - `LogPixels=192` (Control Panel\Desktop) — 2× DPI so the UI is readable on 4K.
  - **Explorer virtual desktop `1920x1080`** — the games do exclusive-fullscreen
    and grab the 4K multi-monitor span (garbage `3804x2085` resolution → crash);
    a prefix-wide virtual desktop confines them to a real window.
  - `teknoparrot://` URL protocol → `TeknoParrotUi.exe "%1"` — `--profile` launches
    go through this scheme; without it you get *"No open command associated with
    file type 'teknoparrot'"*.
- **UI package:** `TeknoParrotUi.zip` (145M, stable). Bundles GameProfiles +
  Metadata but **not** the loaders.
- **Loaders** (fetched from teknogods GitHub, extracted into EmulatorType-named
  subdirs of the install): `OpenParrotWin32` / `OpenParrotx64` (teknogods/OpenParrot),
  `TeknoParrot` (core, includes `BudgieLoader.exe`), `ElfLdr2`, `N2`
  (teknogods/TeknoParrot release assets). These are what the broken Linux build
  could never obtain.
- **Launch:** `wine TeknoParrotUi.exe --profile=<GameId>`, on DP-1, with the
  nvidia Vulkan/GLX pin.

## Game configuration (profile generation)

`files/tp_generate_profiles.py` matches each descriptively-named folder in
`roms_rare/TeknoParrot/` (e.g. `Ikaruga (2013) [Taito NESiCAxLive] [TP]`) to a
TeknoParrot **GameId** via the shipped `Metadata/*.json` (`game_name` + `platform`),
then writes `UserProfiles/<GameId>.xml` with `<GamePath>` = the game exe as a Wine
`Z:` path, and a `<GameId>.tp` stub + `gamelist.xml` for ES-DE.

**Console-backed games are excluded and archived.** EmulatorTypes `pcsx2x6`,
`cxbxr`, `RPCS3`, `Dolphin` (PS2 / Xbox-Chihiro / PS3 / GameCube-Triforce) are
**not** installed — those consoles have dedicated emulators on this box. The
generator moves such folders to `ROMS_FINAL/teknoparrot/`.

**~31 games auto-configure cleanly.** The rest are skipped and need one-by-one
attention:
- **empty `ExecutableName`** in the GameProfile (many BlazBlue / fighting titles) —
  the exe isn't declared, so add the game manually in the UI (Add Game → browse to
  the exe), or set `<GamePath>` in `UserProfiles/<GameId>.xml` by hand.
- **name mismatch / region variant** (Initial D `ID4Exp` vs `ID4Jap`, etc.) or a
  title TeknoParrot doesn't have a profile for.

## Per-game playability is ongoing

TeknoParrot-on-Wine is a **per-game** endeavour — roughly half of any collection
works, each needing individual tuning (DXVK vs dgVoodoo, windowed/resolution,
specific dlls, controller mapping). Confirmed here: the pipeline launches games
(`game.exe` via the loader, DXVK renders) at the correct 1920×1080. Some games run,
some crash (e.g. Battle Gear 4 requests a D3D9 format DXVK can't map). Tune games
individually; annotate and skip ones that resist.

## Controller

TeknoParrot has per-game **CONTROLLER SETUP** (in the UI). The 8BitDo (XInput mode
via the dongle) is seen by TeknoParrot's SDL/XInput layer; map buttons per game in
the UI. See [[feedback_always_gamepad]].

## Commands

```sh
cd ansible
ansible-playbook install-teknoparrot.yml          # full install + configure
# then, in the box, open the UI to tune games / map controllers:
/mnt/data/distrobox/gaming/bin/teknoparrot-launch  # (no arg) opens the UI
/mnt/data/distrobox/gaming/bin/teknoparrot-launch Ikaruga   # launch one game
```
