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
