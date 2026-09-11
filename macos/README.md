# macOS console emulation

Native macOS companion to the Linux setup. The first baseline installs ES-DE,
Dolphin (GameCube/Wii), PCSX2 (PS2), and PPSSPP (PSP), then generates ES-DE
launch commands and configurable library paths. Apple Silicon is the initial
target; Intel has not been validated. An application's macOS build may use
Rosetta: native macOS does not necessarily mean native ARM64.

## Intentional scope boundary

**Windows PC games are permanently outside this macOS implementation's scope.**
This includes Wine, Proton, CrossOver, Windows Steam games, Windows installers,
Windows mod managers/trainers, and Windows-only fan games or recompilations.
They are not a future migration phase. The existing Linux features remain in
place. A console game is eligible when its emulator has a usable macOS build;
this exclusion is about Windows software, not console manufacturers.

Other console emulators and macOS-compatible native ports can be added later.
PS1, PS3, Dreamcast, Switch, PS4 and Xbox are not configured by this
first baseline. Their absence is not a claim that macOS support is impossible.

## Retro collections

RetroArch Metal now covers Atari 2600 (two separate collections), NES, SNES,
Master System, Mega Drive, GBA, Game Boy/Color and Commodore 64. The installer
also installs architecture-matched cores; existing cores are retained.
See [Retro collections](INSTALL.md#retro-collections) for library mapping,
metadata import, hotkeys and limitations.

## Install and configure

For the application list and step-by-step instructions, see
[Installing on macOS](INSTALL.md).

Install [Homebrew](https://brew.sh) first. From the repository root:

```sh
./macos/install-apps.sh
cp macos/ansible/host_vars/localhost.yml.example macos/ansible/host_vars/localhost.yml
# Edit localhost.yml with your absolute ROM paths.
./macos/bootstrap.sh check
./macos/bootstrap.sh configure
open -a ES-DE
```

`install` invokes Homebrew Bundle to install Ansible and the four applications.
It can update existing packages to satisfy the Brewfile. Versions follow
Homebrew; this is not a version-locked environment. `configure` never installs
software. `check` previews configuration without writing it; it still gathers
facts and inspects paths. Missing applications and libraries are reported.
No Distrobox or Linux runtime is used.

Ansible can also be installed separately to use `check` or `configure` without
installing applications. No additional Ansible collections are required.

The default library is `~/Games/roms/{gc,wii,ps2,psp}`. An existing split NAS or
external-drive library can be mapped per system with `dg_macos_rom_paths`.
Paths with spaces and XML special characters are supported. Missing library
directories are only reported, not created: a disconnected `/Volumes/...`
mount must not silently become a local library. Enable
`dg_macos_create_rom_dirs: true` explicitly for new local directories.

ES-DE configuration is written to `~/ES-DE/custom_systems/es_systems.xml`.
Change `dg_macos_esde_home` if ES-DE uses another home directory. Existing custom
systems XML is backed up by Ansible before replacement. **The generated file
owns the complete custom-system list**, so review the diff if you already have
custom systems. ES-DE's built-in systems remain available. Close ES-DE while
applying configuration, then restart it.

The four entries use ES-DE's macOS emulator discovery and upstream standalone
launch arguments. No Linux wrappers, GPU environment variables or `.so` cores
are copied. Applications are expected in `/Applications`, as installed by the
Brewfile. An existing ES-DE alternative-emulator selection may need to be reset
to the corresponding standalone emulator in its UI.

## First launch and validation

1. Open each emulator once and complete its first-run setup. macOS may require
   normal first-open confirmation; this project does not disable Gatekeeper.
2. In PCSX2, select your own PS2 BIOS. This baseline does not supply or configure
   BIOS files, firmware, game downloads or keys.
3. Add your existing games at the configured paths. If ES-DE requests an initial
   ROM directory, use your library root; the custom entries use explicit paths.
4. Launch one game per system from ES-DE. Check video, audio, controller input,
   clean exit, saving and loading. Wii input requires a suitable controller profile.
5. Run `configure` again; an unchanged configuration should report `changed=0`.

Graphics settings, controller profiles, saves, BIOS directories, texture packs
and cheats remain emulator-managed in this phase. Linux NVIDIA/4K/controller
presets are not copied. End-to-end gameplay requires user-owned games and BIOS
and has not yet been validated by the automated tests.

## Verification

On macOS with Ansible on PATH:

```sh
bash -n macos/bootstrap.sh
python3 macos/tests/verify.py
brew bundle check --file=macos/Brewfile
```

The integration test runs real Ansible in temporary directories. It checks
preview behavior, XML escaping, per-host overrides, configuration backups,
missing-volume handling, repeat-run idempotence and opt-in directory creation.
It never installs or launches emulators or changes your actual ES-DE settings.
`brew bundle check` reports missing dependencies; it does not install them.

Run it with the Ansible you actually intend to use. It passes on ansible-core
2.15 and 2.21, and the spread matters: a registered result's `invocation` key
disappeared in 2.19, so a playbook that reads it works on the older one and
fails on whatever `brew install ansible` gives you today. The playbook resolves
paths from loop items for that reason.

## Architecture and next steps

Keep platform installation, commands and configuration under `macos/`. Reuse
existing Python utilities only after checking their dependencies and filesystem
assumptions. Extract shared data when a second actual use warrants it; do not
import the Linux playbook or its optional Windows roles.

Next steps are real-game validation of these four systems, macOS controller and
BIOS configuration, then additional console emulators and reusable asset tools.
A GitHub fork may host this work while tracking upstream; a separate macOS-only
codebase is unnecessary for this architecture.

## Sources

- [ES-DE macOS system definitions](https://gitlab.com/es-de/emulationstation-de/-/blob/master/resources/systems/macos/es_systems.xml)
- [ES-DE downloads and guide](https://www.es-de.org/)
- Homebrew casks: [ES-DE](https://formulae.brew.sh/cask/es-de),
  [Dolphin](https://formulae.brew.sh/cask/dolphin),
  [PCSX2](https://formulae.brew.sh/cask/pcsx2),
  [PPSSPP](https://formulae.brew.sh/cask/ppsspp-emulator).

Package availability and launch definitions were checked on 2026-09-05.
