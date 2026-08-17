# Richard Burns Rally + RallySimFans (RSF)

RBR through the **RallySimFans (RSF)** platform — the big community mod (NGP
physics, hundreds of cars/stages, HUD, VR). Managed as a `install_pc_racing`
game entry (`slug: richard-burns-rally`); Wine, DX9→DXVK/Vulkan. Opt-in.

Unlike the other racing games this one is **not a clean offline install**: RSF
is an online platform. The bulk content installs from local files, but the RSF
launcher needs a **free rallysimfans.hu account + internet** on first run (it
downloads cars on demand), and it cannot coexist with other RBR mods in the same
prefix.

## Sources (consolidated)

Everything lives under `ROMS_FINAL/PC/Richard Burns Rally/`:

- `Rallysimfans_Installer.exe` — the RSF GUI installer app (md5 `975135861905cdf662c9ece9218b9dcc`).
- `rsf_installer_files/` — the RSF torrent payload the installer consumes
  (`rbr_install.7z.001–010` base, `Cars.7z`, 485 `Maps*_v4.7z` stage packs, the
  launcher, NGP, HUD, VR, audio…).
- `Richard-Burns-Rally_Win_EN_Installer/` — a standalone retail RBR (kept as a
  fallback; not used by the RSF path).

## What the role provisions (reproducible)

`ansible-playbook site.yml --tags pc_racing -e '{"dg_pc_racing_selected_slugs":["richard-burns-rally"]}'`

- Wine prefix at `wineprefixes/pc-racing/richard-burns-rally` (win64), GLX pin
  (`UseEGL=N`), G: → the pc-racing install root.
- winetricks **d3dx9 + vcrun2022 + dxvk**; DLL override **`dinput8=n,b`**.
- `game_env`: **`VK_ICD_FILENAMES`** pinned to the NVIDIA ICD (DXVK must not land
  on the AMD iGPU = black screen) and **`SDL_VIDEODRIVER=x11`** (Wayland).
- **Native, no gamescope** — DXVK/Vulkan under gamescope routes to the iGPU on
  this box (same trap as Sega Rally Revo / Supermodel).
- Install + launch wrappers in `bin/`, host desktop entry.

## The interactive install (run from your session)

The RSF installer is a native-Win32 **GUI wizard** with no silent flags, and it
needs your display — run it from your own session, not headless:

```sh
/mnt/data/distrobox/gaming/bin/install-richard-burns-rally   # or via `! ` in this session
```

In the wizard:

1. Language + install type (**Full**, or **Minimal** then add stages later — Full
   is ~97 GB installed, and RSF pulls more on first launch).
2. **Source folder** → `Z:\mnt\terachad\Emulators\ROMS_FINAL\PC\Richard Burns Rally\rsf_installer_files`
3. **Destination** → accept the default **`C:\Richard Burns Rally`**. RSF hardcodes
   that path into the registry + inis, so don't relocate it — `installed_path` in
   the entry points there. `C:` is the prefix's `drive_c` on the local NVMe
   (`/mnt/data`), the right place for a sim.

**Expected mid-install crash (harmless):** around 1% the RSF installer launches
Microsoft's `dxwebsetup`, which page-faults under Wine (`page fault on execute
… 0x00000000` in `dxwsetup`). We already installed `d3dx9` into the prefix, so
this DirectX step is redundant — **dismiss the Wine crash window and the RSF
install continues** to completion.

Then first launch (from your session):

```sh
distrobox-enter -n gaming -- /mnt/data/distrobox/gaming/bin/richard-burns-rally
```

- Log into the RSF launcher (free rallysimfans.hu account); it downloads cars.
- In the launcher → **Screen & Graphics** → **Graphics mode = Vulkan (1.2)**.
- Controllers: wheels/pads come through native `dinput8`; the pc-racing
  gamepad allow-list already admits the 8BitDo + Xbox pads.

### The RSF launcher is .NET 10 WPF — needs fonts (baked in)

The launcher is a **.NET 10 WPF** app (AdonisUI). Two gotchas, both fixed in the
entry so a rebuild handles them:

- **.NET 10 runtime**: installed into the prefix by the RSF installer itself
  (`Program Files/dotnet`, `Microsoft.WindowsDesktop.App 10.0.5`). Don't try to
  substitute an older .NET — the app is hard-targeted to `net10.0` and refuses
  to run on anything else. It's *not* a wine-mono/.NET-Framework app.
- **Fonts**: with no Windows fonts in the prefix, WPF hard-crashes
  (`Environment.FailFast` in `TypefaceMap.MapUnresolvedCharacters`) while laying
  out a TextBox — the app initializes fully (`debug.log` "Completed reading all
  configuration options") then dies **before the window appears**. Fixed with
  winetricks **`corefonts` + `tahoma`** and a **`Segoe UI → Arial`**
  FontSubstitutes registry entry (WPF's default UI font is Segoe UI, which is
  absent under Wine). After that the launcher window maps and runs on the RTX
  via DXVK.

Launcher path confirmed after install:
`C:\Richard Burns Rally\rsf_launcher\RSF_Launcher.exe` (`launch_exe` +
`installed_path` in the entry point there).

## Stopping it cleanly

The RSF launcher **relaunches itself after the game exits** (launch game →
RichardBurnsRally.exe `DirectX9` window → quit → launcher returns). So a plain
window-close (Hyprland `Super+W`) on the game or launcher can appear to *hang*,
and killing the wineserver alone just lets the launcher respawn. Kill the
**wrapper parent first**, then the prefix's wineserver:

```sh
# 1. stop the launch wrapper so nothing respawns
pkill -f '/bin/richard-burns-rally'
# 2. take down the prefix's Wine session (launcher + game + services.exe)
distrobox-enter -n gaming -- \
  env WINEPREFIX=/mnt/data/distrobox/gaming/wineprefixes/pc-racing/richard-burns-rally \
  wineserver -k
```

Note: `wineserver -k` doesn't always take down the prefix's `services.exe` /
`winedevice.exe`; if a dead `Richard Burns Rally - DirectX9` window frame
lingers (an orphaned XWayland surface held by a leftover wine process or an
unreaped zombie), kill those PIDs directly — verify each with
`grep WINEPREFIX /proc/<pid>/environ` first — or just restart the box.
