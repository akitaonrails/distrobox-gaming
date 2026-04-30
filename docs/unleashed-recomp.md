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
- writes the launcher wrapper to `/mnt/data/distrobox/gaming/bin/unleashed-recomp`
- searches the expected Xbox 360 NAS paths for Sonic Unleashed ISO/raw files and `TU_19KA20I*`
- extracts a detected ISO to the managed source directory when raw files are not already available
- extracts a detected title-update ZIP and stages the raw `TU_19KA20I*` file
- stages detected Sonic Unleashed DLC packages as symlinks under `dlc-files`
- links detected/provided sources under `/mnt/data/distrobox/gaming/tools/unleashed-recomp/sources/`
- renders a host desktop entry; the host installer only exports it when the
  launcher wrapper exists inside the box

Launch it with:

```sh
distrobox-enter -n gaming -- /mnt/data/distrobox/gaming/bin/unleashed-recomp
```

To add or refresh the host menu entry:

```sh
scripts/install-host-launchers.sh
```

When the installer asks for files, use:

```text
/mnt/data/distrobox/gaming/tools/unleashed-recomp/sources/game-source
/mnt/data/distrobox/gaming/tools/unleashed-recomp/sources/title-update
/mnt/data/distrobox/gaming/tools/unleashed-recomp/sources/dlc-files
```

Current NAS check: the Xbox 360 ISO exists at
`/mnt/terachad/Emulators/ROMS_FINAL/xbox360/Sonic Unleashed (USA) (En,Ja,Fr,De,Es,It).iso`.
The role extracts it to `game-files` under the managed source directory.
The matching title update ZIP was matched as `Sonic Unleashed (Europe) (v2).zip`
and is extracted to `title-update-files` under the managed source directory.
The DLC directory is mapped from
`/mnt/terachad/Emulators/ROMS_FINAL/xbox360/Sonic Unleashed DLC`; the role
stages the six Adventure Pack package files as symlinks in `dlc-files`.
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
