# Mickey & Donald Collection

The optional `install_mickey_donald` role installs
[Mickey & Donald Collection](https://github.com/Darhkfox/MickeyAndDonaldCollection)
v1.1, a Windows port of **Castle of Illusion**, **QuackShot**, and **World of
Illusion**. The pinned ZIP is cached under `dg_mdc_cache_dir`; the executable
and its settings live in `dg_mdc_game_dir` with a dedicated Wine prefix.
Run `ansible-playbook install-mickey-donald.yml` from `ansible/`, or use
`ansible-playbook site.yml --tags mickey_donald`.

The port accepts only these original Genesis revisions. The role validates
SHA-256 before linking them into its `roms/` directory; it does not modify or
copy the source ROMs.

| Game | Source default | CRC32 required |
| --- | --- | --- |
| Castle of Illusion | `dg_rom_root/genesis/Castle of Illusion Starring Mickey Mouse (USA, Europe).md` | `BA4E9FD0` |
| QuackShot | `dg_roms_final_root/genesis/Quack Shot Starring Donald Duck.gen` | `88C8DD94` (Rev 0) |
| World of Illusion | `dg_rom_root/genesis/World of Illusion Starring Mickey Mouse and Donald Duck (USA, Korea) (En).md` | `921EBD1C` |

The EmuDeck QuackShot file is Rev 1 and has a different CRC, so it cannot be
used by this port. Override `dg_mdc_roms` in `host_vars/localhost.yml` if
moving or replacing any source; keep the checksums accurate.

The initial `settings.ini` selects fullscreen on the 4K desktop, the games'
true 16:9 view, VSync, a bilinear filter, a re-anchored HUD, and an
FPS counter. These games emulate the Genesis at their normal 60 FPS; faster
settings are fast-forward controls, not a higher gameplay frame-rate target.
Black-frame insertion remains off because it requires a suitable 120/180/240
Hz display and dims the image. Ansible seeds settings only when absent, so
in-game changes, achievements, saves, and states persist across reinstall.

The game's native XInput/DirectInput controller support is kept. The Wine
prefix uses SDL-backed WineBus, `Map Controllers=1`, automatic first/second
pad assignment, and left-stick-as-D-pad; the default A/B/C mappings and
hotkeys remain. The port offers two-player World of Illusion. Physical
controller input and gameplay still need hands-on verification.
