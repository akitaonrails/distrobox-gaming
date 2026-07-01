# Ship of Harkinian

This installs the official HarbourMasters Shipwright Linux release ZIP for
Ship of Harkinian, rather than building from source or using AUR packages.

## Pins

- Release: `9.2.3` / `Ackbar Delta 9.2.3`
- Repository: <https://github.com/HarbourMasters/Shipwright.git>
- Tag commit: `cb71e22a79bc5d1f688fa881795bbd93094895fc`
- Asset: `SoH-Ackbar-Delta-Linux.zip`
- Asset SHA256: `f81cde8052142d6abbbaaffa70699d6748e4cde3f158be8f268c3aab338ee315`
- HD pack: `oot-reloaded-v11.0.0-soh-o2r-hd.7z`
- HD pack SHA256: `a6a551e880739de7f5313888f6cf4eea2eb9d2f04274697fe8ad524ea3c30161`

## Install

Run from `ansible/`:

```sh
ansible-playbook install-ship-of-harkinian.yml
```

The role is also available from the full site playbook as an opt-in tag:

```sh
ansible-playbook site.yml --tags ship_of_harkinian
```

## ROM and hash notes

The default ROM source is:

```text
{{ dg_rom_mid_root }}/n64/Legend of Zelda, The - Ocarina of Time (USA) (Rev B).n64
```

The role accepts standard N64 byte orders, converts the local `.n64` source to a
canonical big-endian z64 copy, and verifies the Ocarina of Time USA Rev B (v1.2)
SHA1 before launching:

```text
41b3bdc48d98c48529219919015a1af22f5057c2
```

## Installed layout

- Cache: `{{ dg_ship_of_harkinian_cache_dir }}`
- Install directory: `{{ dg_ship_of_harkinian_install_dir }}`
- AppImage: `{{ dg_ship_of_harkinian_install_dir }}/soh.appimage`
- Verified ROM copy: `{{ dg_ship_of_harkinian_install_dir }}/{{ dg_ship_of_harkinian_rom_name }}`
- HD mod: `{{ dg_ship_of_harkinian_install_dir }}/mods/OoT_Reloaded_v11.0.0_HD.o2r`
- Wrapper: `{{ dg_ship_of_harkinian_bin }}`

OoT Reloaded uses alternate assets. Enable **Use Alternate Assets** from the SoH
menu, or press `Tab`, if the HD textures are not visible after launch.
