# Metal Gear Solid: Master Collection fixes

This repo installs the current stable community fixes for the Steam Master
Collection games with an opt-in Ansible role. It does not run in the default
rebuild path because it modifies Steam game folders and downloads large mod
archives.

## What the role installs

| Steam game | App ID | Folder | Fixes |
| --- | --- | --- | --- |
| METAL GEAR SOLID - Master Collection Version | `2131630` | `MGS1` | MGSM2Fix 3.6.0 |
| METAL GEAR SOLID: MASTER COLLECTION Vol.1 BONUS CONTENT | `2306740` | `MGS Master Collection Bonus Content` | MGSM2Fix 3.6.0 |
| METAL GEAR & METAL GEAR 2: Solid Snake | `2131680` | `MG and MG2` | MGSHDFix 3.1.0 |
| METAL GEAR SOLID 2: Sons of Liberty - Master Collection Version | `2131640` | `MGS2` | MGSHDFix 3.1.0 + MGS2 Community Bugfix Compilation Base 2.2.0 |
| METAL GEAR SOLID 3: Snake Eater - Master Collection Version | `2131650` | `MGS3` | MGSHDFix 3.1.0 + MGS3 Community Bugfix Compilation Base 1.1.0 |

Optional upscaled texture/audio packs are intentionally not installed by the
role. The base Community Bugfix Compilation packs already replace many files and
are the lowest-risk default.

## Install / reinstall

Set the Steam library root to the directory that contains `steamapps/`. For this
machine it is supplied at runtime or in `host_vars/localhost.yml`; do not bake a
personal mount path into the role.

```sh
cd ansible
ansible-playbook install-metal-gear-master-collection-fixes.yml \
  -e dg_mgs_master_steam_library_root=/path/to/SteamLibrary
```

The role downloads pinned archives into
`{{ dg_box_home }}/cache/metal-gear-master-collection-fixes`, verifies SHA-256,
extracts them into the game folders, and writes marker files under each game's
`.dg-metal-gear-fixes/` directory. Use
`-e dg_mgs_master_force_reinstall=true` to re-extract after Steam verifies or
updates the game files.

## Proton launch options

The DLL overrides are required on Linux/Proton:

```text
MGS1 and Bonus Content: WINEDLLOVERRIDES="dinput8=n,b;d3d11=n,b" %command%
MG/MG2, MGS2, MGS3:    WINEDLLOVERRIDES="wininet,winhttp=n,b" %command%
```

The role can write these into Steam's `localconfig.vdf` when you pass the
account-specific path and Steam is closed:

```sh
ansible-playbook install-metal-gear-master-collection-fixes.yml \
  -e dg_mgs_master_steam_library_root=/path/to/SteamLibrary \
  -e dg_mgs_master_steam_localconfig=$HOME/.local/share/Steam/userdata/<steamid>/config/localconfig.vdf
```

If Steam is running, either close it first or add
`-e dg_mgs_master_stop_steam=true`. The helper creates a one-time backup named
`localconfig.vdf.bak-dg-metal-gear` before changing launch options.

## Post-install game settings

For MGS1, the role keeps MGSM2Fix on desktop-sized borderless output and forces
the internal render height to `2160` in `MGSM2Fix.ini`. The in-game resolution
still needs to be set to a high-resolution mode, such as **High** or **Max**, for
MGSM2Fix's internal override to apply.

For MGS2 and MGS3, the role writes `plugins/MGSHDFix.settings` to use
borderless-windowed 3840x2160 output and 3840x2160 internal render resolution.
Open each game's launcher and set **Internal Resolution** and **Internal
Upscaling** to **Default / Original** so the game's built-in FSR/upscaling does
not fight MGSHDFix. The config tools live under each game's `plugins/` folder:

```text
MGS2/plugins/MGSHDFix Config Tool.exe
MGS3/plugins/MGSHDFix Config Tool.exe
```

Sources:

- <https://github.com/nuggslet/MGSM2Fix/releases>
- <https://github.com/ShizCalev/MGSHDFix/releases>
- <https://github.com/ShizCalev/MGS2-Community-Bugfix-Compilation/releases>
- <https://github.com/ShizCalev/MGS3-Community-Bugfix-Compilation/releases>
