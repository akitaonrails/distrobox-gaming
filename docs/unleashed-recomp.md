# Unleashed Recompiled

Unleashed Recompiled is a native Linux Flatpak port of the Xbox 360 version of
Sonic Unleashed. It is not a Wine/Xenia setup. The upstream app includes its
own installer and validation flow, so Ansible installs the Flatpak and stages
stable paths for the game dump/title update instead of trying to bypass the
GUI importer.

Run from `ansible/`:

```sh
ansible-playbook install-unleashed-recomp.yml
```

The role:

- installs Flatpak and portal packages inside the `gaming` distrobox
- adds the Flathub user remote for Flatpak runtime resolution
- downloads the latest upstream `UnleashedRecomp-Flatpak.zip`
- installs the contained `.flatpak` bundle as the distrobox user
- writes the launcher wrapper to `{{ dg_unleashed_recomp_bin }}`
- searches the expected Xbox 360 NAS paths for Sonic Unleashed ISO/raw files and `TU_19KA20I*`
- extracts a detected ISO to the managed source directory when raw files are not already available
- extracts a detected title-update ZIP and stages the raw `TU_19KA20I*` file
- stages detected Sonic Unleashed DLC packages as symlinks under `dlc-files`
- links detected/provided sources under `{{ dg_unleashed_recomp_sources_dir }}`
- renders a host desktop entry; the host installer only exports it when the
  launcher wrapper exists inside the box

Launch it with:

```sh
distrobox-enter -n gaming -- "{{ dg_unleashed_recomp_bin }}"
```

To add or refresh the host menu entry:

```sh
scripts/install-host-launchers.sh
```

When the installer asks for files, use:

```text
{{ dg_unleashed_recomp_sources_dir }}/game-source
{{ dg_unleashed_recomp_sources_dir }}/title-update
{{ dg_unleashed_recomp_sources_dir }}/dlc-files
```

The default search roots are `{{ dg_rom_heavy_root }}/xbox360`,
`{{ dg_rom_heavy_root }}/xbox360-updates`, `{{ dg_roms_final_root }}/xbox360`,
and `{{ dg_roms_final_root }}/xbox360-updates`. The role can detect a Sonic
Unleashed ISO, raw `default.xex` dump, title update, title-update ZIP, and DLC
directory from those roots. Detected files are staged under the managed source
directory.
Upstream requires Xbox 360 US/EU game data and a title update, and JP is
unsupported.

If you add the dump later, either place it under one of the configured search
roots or override:

```yaml
dg_unleashed_recomp_game_source: /path/to/xbox360/sonic-unleashed
dg_unleashed_recomp_iso_source: /path/to/Sonic Unleashed.iso
dg_unleashed_recomp_title_update_source: /path/to/TU_19KA20I...
dg_unleashed_recomp_title_update_zip_source: /path/to/Sonic Unleashed TU.zip
dg_unleashed_recomp_dlc_source: /path/to/Sonic Unleashed DLC
```
