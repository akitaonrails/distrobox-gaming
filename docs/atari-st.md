# Atari ST (Hatari / RetroArch)

Atari ST uses the existing `hatari` libretro core and the ES-DE `atarist`
system. This targets the Linux x86_64 gaming distrobox, not native macOS.
The dedicated playbook requires an existing box with RetroArch and ES-DE.

## Assets and paths

Supply your own ST-compatible TOS image and disk images. No BIOS or games
are downloaded. Override paths in `ansible/host_vars/localhost.yml`:

```yaml
dg_atari_st_enabled: true
dg_atari_st_rom_dir: "{{ dg_rom_root }}/atarist"
dg_atari_st_tos_source: "{{ dg_bios_root }}/tos.img"
```

Create the ROM directory and put your disk images there before installation.
The catalog accepts `.st`, `.msa`, `.stx`, `.dim`, `.ipf`, `.zip` and uppercase
variants. ZIP contents must be supported disk images. IPF support depends on
the installed core build. M3U and 7z are deliberately not advertised without
validation against this core.

The official Libretro documentation lists TOS 1.00, 1.02, 1.04 and 2.06 for
plain ST mode. Use an appropriate image for the intended machine; a nonempty
file check cannot establish BIOS compatibility.

## Install and mandatory validation

From `ansible/`, on the Linux host:

```sh
ansible-galaxy collection install -r collections/requirements.yml
ansible-playbook --syntax-check install-atari-st.yml
ansible-playbook --syntax-check verify-atari-st.yml
ansible-playbook install-atari-st.yml
ansible-playbook verify-atari-st.yml
```

The install configures TOS, installs only the Hatari core through the existing
`retroarch_extras` role, refreshes the complete managed ES-DE catalog (with a
backup), and runs mandatory prerequisite checks. It does not bootstrap a box,
install RetroArch/ES-DE, populate ROMs, or scrape artwork. Existing cores are
not updated automatically; the shared installer uses the current buildbot
nightly only when the core is absent.

A missing/empty BIOS, core, profile or catalog, a missing ROM directory, or
missing RetroArch causes validation to fail. Checks run inside the box for
asset visibility. Validation is not proof that a game boots or that the core
binary is compatible. Do not report the system as gameplay-tested until the
smoke test below passes.

The ST-only RetroArch append configuration lives at
`dg_atari_st_retroarch_config`. It sets `system_directory` to
`dg_atari_st_system_dir`, containing a `tos.img` symlink and `hatari.cfg`.
This avoids depending on the user's global BIOS directory. Only the TOS path
in `hatari.cfg` is managed; other Hatari settings are preserved, with backups.
The TOS symlink is forced, so a re-run replaces a stale link or a file
dropped there by hand — the source at `dg_atari_st_tos_source` is never
touched.

To reapply configuration after installation:

```sh
ansible-playbook reset-configs.yml --tags configs,esde
ansible-playbook verify-atari-st.yml
```

Keep `dg_atari_st_enabled: true` in host overrides for this reset workflow.
Running the focused installer again also reapplies the profile. Never use
`--check` as a substitute for the mandatory installation verification.

## Mandatory game smoke test on Linux

1. Launch a known-working ST disk from ES-DE and verify boot, picture and audio.
2. Verify joystick movement/fire in a joystick game. The core uses RetroPad.
3. Check the Hatari menu (default RetroPad Y), mouse mode (Select), and keyboard
   overlay. Physical controller labels may differ from RetroPad labels.
4. In a multi-disk game, use Hatari's Floppy menu to insert the next disk without
   resetting the running machine. Do not assume RetroArch M3U/disk control.
5. Exit to ES-DE and launch again. Confirm the TOS path and user settings persist.
6. Rerun installation and verification; investigate unexpected changes. Record
   game, TOS version, core build, controller, outcomes and any exceptions.

Some games need different RAM, machine or TOS settings, configurable in Hatari.
Do not assume RetroArch save states/rewind work; test required persistence in
Hatari itself with the chosen game. Do not use original writable game media
for write/save experiments without a backup.

## Validation record

Local macOS checks cover syntax, configuration generation and idempotence in
an isolated fixture. Linux core loading, actual TOS compatibility, gameplay,
audio, controllers and disk swaps remain pending until run on the target.
No user ROM or BIOS is included in the fixture.

## Source

[Official Libretro Hatari documentation](https://docs.libretro.com/library/hatari/)
for extensions, BIOS, configuration and controls. Consulted 2026-09-05.
