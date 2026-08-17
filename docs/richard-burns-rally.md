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
   is hundreds of GB).
2. **Source folder** → `Z:\mnt\terachad\Emulators\ROMS_FINAL\PC\Richard Burns Rally\rsf_installer_files`
3. **RSF destination** → `G:\richard-burns-rally` (maps to the pc-racing install
   root; keep it out of Program Files / Users).

Then first launch:

```sh
/mnt/data/distrobox/gaming/bin/richard-burns-rally
```

- Log into the RSF launcher (free rallysimfans.hu account); it downloads cars.
- In the launcher → **Screen & Graphics** → **Graphics mode = Vulkan (1.2)**.
- Controllers: wheels/pads come through native `dinput8`; the pc-racing
  gamepad allow-list already admits the 8BitDo + Xbox pads.

> The launcher path in the entry (`rsf_launcher/RSF_Launcher.exe`) follows the
> community layout; confirm it after install and fix `launch_exe` in
> `group_vars/all/pc_racing.yml` if RSF lays out the folder differently.
