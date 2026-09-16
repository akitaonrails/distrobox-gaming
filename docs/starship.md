# Starship

This installs the official HarbourMasters Starship prebuilt Linux release ZIP,
rather than building from source or using AUR packages.

## Pins

- Release/tag: `v2.0.0` / `Starship - Barnard Alfa`
- Repository: <https://github.com/HarbourMasters/Starship.git>
- Tag commit: `cb19785b51698185a688e17ba1a34c7889195bdb`
- Asset: `Starship-Barnard-Alfa-Linux.zip`
- Asset SHA256: `85dd03d3ad8abd881aa3aa2b49ded336627b44b8ac8333e3c41b5bf7c4336289`

## Install

Run from `ansible/`:

```sh
ansible-playbook install-starship.yml
```

The role is also available from the full site playbook as an opt-in tag:

```sh
ansible-playbook site.yml --tags starship
```

## ROM and hash notes

The default ROM source is:

```text
{{ dg_rom_mid_root }}/n64/Star Fox 64 (USA) (Rev A).n64
```

Override `dg_starship_rom_source` if your ROM set uses a different supported
Star Fox 64 / Lylat Wars filename, region, or revision.

The role accepts standard N64 byte orders, converts the local `.n64` source to a
canonical big-endian z64 copy, and verifies the Star Fox 64 USA Rev A SHA1
before launching:

```text
09f0d105f476b00efa5303a3ebc42e60a7753b7a
```

## Installed layout

- Cache: `{{ dg_starship_cache_dir }}`
- Install directory: `{{ dg_starship_install_dir }}`
- AppImage: `{{ dg_starship_install_dir }}/{{ dg_starship_appimage_name }}`
- Verified ROM copy: `{{ dg_starship_install_dir }}/{{ dg_starship_rom_name }}`
- Wrapper: `{{ dg_starship_bin }}`

## Optional HD packs

Starship loads `.o2r` mods from `{{ dg_starship_install_dir }}/mods/` (the
launcher `cd`s into the install directory, so the relative `mods/` path is
found). The role installs LR2EB ("Lylat Reloaded 2: Electric Boogaloo" by
MaddiAddi, <https://gamebanana.com/wips/90597>) when
`dg_starship_lr2eb_enabled` is true. It is the only Starship-native visual
overhaul: hi-poly Star Fox Zero / 64 3D models for the Arwing, Landmaster,
Blue Marine, and Great Fox, plus HD textures, HUD, and explosion animations.

The archive is staged on the NAS at
`{{ dg_roms_final_root }}/PC/starship/` so rebuilds never re-download it. To
bump to a newer preview, update `dg_starship_lr2eb_file_id`,
`dg_starship_lr2eb_asset_name`, `dg_starship_lr2eb_asset_md5`, and
`dg_starship_lr2eb_version` in `group_vars/all/starship.yml`.

Caveats (LR2EB is a WIP preview):

- Known visual issues: Venom 1 title mispositioned and skybox tiling, visible
  seams in planet renders, map-screen planet shading offset, credits text
  point-filtered, credits sunset skybox misaligned.
- If the game crashes at the title screen, restart once or twice — a known
  Starship custom-asset loading quirk, not fixable mod-side.
- The beta boost gauge toggle requires Starship 2.0 "Barnard" or later (our
  pin qualifies).
- Not toggleable per-texture; HD vehicle models can be reverted by removing
  the HD-model `.o2r` files from `mods/`.

Emulator-format texture packs (UnaidedCoder's, Razius's HD, the original Lylat
Reloaded for GLideN64/PJ64) cannot be loaded by Starship; they only work in
N64 emulators. DirectX 11 / Helix Mod fixes are Windows-only and do not apply
to the native Linux AppImage.
