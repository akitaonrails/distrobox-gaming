# Installing on macOS

This guide covers the first phase of macOS support. The commands are meant to
be run on the target Mac; reading this document installs nothing.

## What gets installed

| Application | Role | Homebrew package |
|---|---|---|
| ES-DE | Frontend for browsing the library and launching games | `es-de` |
| Dolphin | GameCube and Wii | `dolphin` |
| PCSX2 | PlayStation 2 | `pcsx2` |
| PPSSPP | PSP | `ppsspp-emulator` |
| RetroArch | Atari, NES, SNES, Master System, Mega Drive, GBA, Game Boy/Color, C64 | `retroarch-metal` |

Plus the two tools that do the installing and configuring:

- **Homebrew** — prerequisite for the current installer. Install it from
  [brew.sh](https://brew.sh) if it is not already present.
- **Ansible** — applies the project's configuration; it is in the `Brewfile`.
  It is neither an emulator nor a frontend.

RetroArch needs libretro cores, which are not Homebrew packages. The installer
fetches them separately; see [Retro collections](#retro-collections) below.

[Brewfile](Brewfile) is the list the installer actually uses. Applications are
expected in `/Applications`. Homebrew may pull additional dependencies, and
versions follow their packages — this is not a version-locked environment.

Windows games, Wine, Proton, CrossOver and Windows-only tooling are
deliberately out of scope. No ROMs, BIOS or firmware are supplied.

## 1. Check the environment

From the repository root:

```sh
command -v brew
brew bundle check --verbose --file=macos/Brewfile
```

Neither command installs anything. If a dependency is missing or outdated, the
check exits non-zero and names it.

## 2. Install the applications

The full installer covers Ansible plus the four applications:

```sh
./macos/install-apps.sh
```

The equivalent individual commands are:

```sh
brew install ansible
brew install --cask es-de
brew install --cask dolphin
brew install --cask pcsx2
brew install --cask ppsspp-emulator
brew install --cask retroarch-metal
python3 macos/scripts/install-cores.py
```

Use whichever suits you — the full installer always considers every Brewfile
entry. Installing only some applications does not drop the other systems from
the generated configuration: an entry whose emulator is absent simply cannot
launch anything.

### Inspecting and extending the list

```sh
./macos/install-apps.sh --list
./macos/install-apps.sh --check
```

To add an application, append `cask "package-name"` to
[macos/Brewfile](Brewfile); for a CLI tool use `brew "package-name"`. Then run
the installer again — the script itself needs no edit. Note that adding an
emulator to the Brewfile installs the application only; wiring a new console
into ES-DE also means configuring its system in the Ansible playbook.

The script runs from any directory, installs or updates what is declared, and
verifies the result. If Homebrew fails it returns an error and can be rerun
once the cause is fixed. It never removes packages that are not on the list.
`./macos/bootstrap.sh install` remains available as a shortcut to the same
installer.

## 3. Configure your library paths

Create the local override only if it does not exist yet:

```sh
if [ ! -f macos/ansible/host_vars/localhost.yml ]; then
  cp macos/ansible/host_vars/localhost.yml.example macos/ansible/host_vars/localhost.yml
fi
```

Edit it with the absolute paths to your library:

```yaml
dg_macos_rom_root: /Volumes/Games/roms
```

For a split library use `dg_macos_rom_paths`, as shown in the example file. The
default is `~/Games/roms` with `gc`, `wii`, `ps2` and `psp` subdirectories. The
retro collections use the same mapping under the keys listed in
[Retro collections](#retro-collections).
External volumes must be mounted. Missing directories are reported, never
created — a disconnected `/Volumes/...` mount must not silently become a local
library.

## 4. Review and apply

Close ES-DE before applying:

```sh
./macos/bootstrap.sh check
./macos/bootstrap.sh configure
```

`check` previews without writing; `configure` writes. The generated file is
`~/ES-DE/custom_systems/es_systems.xml`, or elsewhere if you customised
`dg_macos_esde_home`. **The generated file owns the complete custom-system
list** and the previous version is backed up first, so review the diff if you
already had custom systems. ES-DE's built-in systems stay available.

## 5. First launch

1. Open Dolphin, PCSX2 and PPSSPP once and finish their first-run setup.
2. In PCSX2, select your own PS2 BIOS.
3. Configure your controller in each emulator. For Wii, pick the input profile
   that suits the game and the controller you are using.
4. Open ES-DE with `open -a ES-DE` and launch one game per configured system.
5. Check video, audio, controller input, clean exit, and saving/loading.

This phase automates installation and ES-DE integration. BIOS, controllers and
graphics settings are still configured inside each emulator, and the automated
tests are no substitute for testing with real games.

## Retro collections

The installer also covers **RetroArch Metal** plus the macOS cores Stella,
Nestopia, Snes9x, Genesis Plus GX, mGBA, Gambatte and VICE x64sc. Cores are
downloaded from the official Libretro buildbot for the Mac's architecture,
verified with `lipo`, and kept in
`~/Library/Application Support/distrobox-gaming/cores`. Each new download
records its URL and SHA-256 alongside the core. That hash is an integrity
record of what was fetched, not a vendor signature, and the buildbot URL is a
rolling `latest` build — this is not a pinned, reproducible core set. Cores
already present are never overwritten or auto-updated.

To reinstall only the cores, without touching the applications:

```sh
python3 macos/scripts/install-cores.py
python3 macos/scripts/install-cores.py --check
```

Map the collections with `dg_macos_rom_paths` in your local override. The new
keys are `atari2600`, `atari2600homebrew`, `nes`, `snes`, `mastersystem`,
`megadrive`, `gba`, `gbc` and `c64`. The two Atari collections stay separate so
each keeps its own files and metadata. Bundled Atari ZIP archives are not
listed as games — those archives are expected to be extracted already, and
listing both would show every game twice.

The playbook imports each collection's `gamelist.xml` into the ES-DE folder,
rewriting paths to absolute form and symlinking any cover art it finds. Source
ROMs and metadata are never modified. Entries whose game file is missing are
dropped, and a previous imported gamelist is backed up first. The import is
skipped in `check` mode; the preview still covers every other setting.

`ES-DE/retroarch-macos.cfg` applies Vulkan video (through MoltenVK) and
controller autodetection to launches from this integration only. **F8 + Escape**
exits the emulator. Specific controller mapping depends on the device; set it
in RetroArch if needed. On the C64, some games expect the keyboard or the other
joystick port — that is per-title, not a configuration error.

GBA `.bin` files are accepted alongside `.gba`. Older homebrew may use different
headers: the extension alone does not prove compatibility.

### Known display issues

`pause_nonactive = "false"` keeps RetroArch rendering while ES-DE hands over
focus. Without it, launching can sit on a black screen. The trade-off is that
switching applications no longer pauses the game automatically — pause manually
before leaving the window.

The experimental Metal driver showed a symptom where the image only advanced
while the mouse moved. The default is therefore `video_driver = "vulkan"`,
following the [official guidance](https://docs.libretro.com/guides/install-macos/).
The same RetroArch Metal application ships Vulkan, so no reinstall is needed.

### Validation status

Installation of RetroArch and the seven ARM64 cores is verified, along with the
Brewfile and per-core architecture checks. The Ansible integration test passes
and a second apply reports `changed=0`.

Gameplay was confirmed on this baseline for two systems: a NES ROM under
Nestopia and an Atari 2600 ROM under Stella both loaded and rendered through
Vulkan/MoltenVK on Apple Silicon. Audio, controller input, save/load and the
remaining systems are still unverified, and end-to-end testing with your own
games remains necessary.

See [README.md](README.md) for architecture, scope boundaries and how the
automation is tested.
