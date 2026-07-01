# SpaghettiKart

SpaghettiKart is the native Linux Mario Kart 64 PC port used by this repo. It
follows the AlfaExploit route with HarbourMasters' Alfredo Alfa release, but the
role pre-generates the ROM-derived `mk64.o2r` asset so the desktop launcher does
not open a first-run ROM chooser.

Run or refresh it with:

```sh
cd ansible
ansible-playbook install-spaghettikart.yml
```

The executable comes from the pinned release ZIP:

```text
SpaghettiKart 0.9.9.1 / Alfredo Alfa 0.9.9.1
https://github.com/HarbourMasters/SpaghettiKart/releases/download/0.9.9.1/Spaghettify-Alfredo-Alfa-1-Linux-Old.zip
SHA256 fbdff87766f409067e8663032319f59d64e8d43bd872a3c47bb7218199d965b7
```

The ROM-derived asset is generated from pinned source commit
`6f5e8d514efb60856ccd01a6669e67d0eb9c6858` via CMake's `ExtractAssets` target.
This avoids relying on the Linux AppImage's interactive file chooser. The role
initializes only the source submodules needed for extraction:

```text
torch          5773373b3620e4a6bc6c92fdc4690d66741c086d
libultraship   5e33d3e7cd0396f847923cd6c471eaf324e90351
```

The local source ROM is `dg_spaghettikart_rom_source`, currently:

```text
{{ dg_rom_mid_root }}/n64/Mario Kart 64 (USA).n64
```

The role converts `.n64` / `.v64` byte-swapped input to canonical `.z64` order
and verifies the supported US SHA1 before extraction:

```text
579c48e211ae952530ffc8738709f078d5dd215e
```

Installed layout:

```text
{{ dg_box_home }}/tools/spaghettikart/current/spaghetti.appimage
{{ dg_box_home }}/tools/spaghettikart/current/mk64.o2r
{{ dg_box_home }}/tools/spaghettikart/current/mods/mk64-reloaded-v2026.04.03-sk-hd.o2r
{{ dg_box_home }}/tools/spaghettikart/current/config.yml
{{ dg_box_home }}/tools/spaghettikart/current/gamecontrollerdb.txt
{{ dg_box_home }}/bin/spaghettikart
```

The role also installs MK64 Reloaded for SpaghettiKart as a checksum-pinned HD
`.o2r` mod:

```text
mk64-reloaded-v2026.04.03-sk-hd.o2r
SHA256 98d852481dbbd1ca378b79ca2146486848118879da9aa4612769eaaee6dba685
```

The desktop launcher is `gaming-spaghettikart.desktop` and sets `Path=` to the
install directory so `mk64.o2r`, config, and mods resolve consistently.
