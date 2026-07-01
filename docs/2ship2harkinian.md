# 2Ship2Harkinian

This installs the official HarbourMasters 2Ship2Harkinian prebuilt Linux release
ZIP, rather than building from source or using AUR packages.

## Pins

- Release: `4.0.2` / `Keiichi Charlie`
- Repository: <https://github.com/HarbourMasters/2ship2harkinian.git>
- Tag commit: `acfd617302ebb74e63f26f0049b53400a644c8e8`
- Asset: `2Ship-Keiichi-Charlie-Linux.zip`
- Asset SHA256: `c97fc9440f5584f350c911ec7385778394aa62f651c6613cee0b74c0141932cb`

## Install

Run from `ansible/`:

```sh
ansible-playbook install-2ship2harkinian.yml
```

The role is also available from the full site playbook as an opt-in tag. The tag
uses a leading word instead of starting with a digit:

```sh
ansible-playbook site.yml --tags two_ship2harkinian
```

## ROM and hash notes

The default ROM source is:

```text
{{ dg_rom_mid_root }}/n64/Legend of Zelda, The - Majora's Mask (USA).n64
```

The role accepts standard N64 byte orders, converts the local `.n64` source to a
canonical big-endian z64 copy, and verifies the Majora's Mask USA SHA1 before
launching:

```text
d6133ace5afaa0882cf214cf88daba39e266c078
```

## Installed layout

- Cache: `{{ dg_two_ship2harkinian_cache_dir }}`
- Install directory: `{{ dg_two_ship2harkinian_install_dir }}`
- AppImage: `{{ dg_two_ship2harkinian_install_dir }}/{{ dg_two_ship2harkinian_appimage_name }}`
- Verified ROM copy: `{{ dg_two_ship2harkinian_install_dir }}/{{ dg_two_ship2harkinian_rom_name }}`
- Wrapper: `{{ dg_two_ship2harkinian_bin }}`
