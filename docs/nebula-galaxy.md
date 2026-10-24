# Super Mario Galaxy via Nebula

Updated 2026-10-23 to v1.0.1. The unattended setup recompiled all 788 generated units, `current.json` reports `1.0.1` with `1.0.0` retained as the previous version, and the playbook removed its temporary 3.2 GB game extraction. Gameplay remains unverified after this update; the earlier Wine NAND preflight issue may still apply.

The optional `install_nebula` role installs [Nebula](https://github.com/keepvaibin/nebula) v1.0.1 beside Dolphin. Nebula recompiles the owned USA Wii disc (RMGE01, revision 0) into native Windows modules. The current release is Windows-only, so this experimental installation uses the gaming distrobox's Wine and an isolated prefix. It does not change the original disc image or Dolphin configuration.

The local image under `dg_emudeck_root/roms_heavy/wii/` is an NKit-compressed ISO. Nebula cannot read its game partition directly, so the role downloads the pinned NKit CLI, extracts the files to temporary local storage, then runs Nebula's unattended setup under the distrobox's Wine with four compiler jobs. Setup verifies the supported game executable before building. The temporary extraction is removed after the install attempt. The original image, verified setup download, NKit CLI and installed prefix remain available for a rebuild or update. Setup can return an error after successfully installing because Wine does not implement the .NET call for creating Windows Start-menu shortcuts; the role checks the compiled DLLs, content and installed version before accepting that outcome.

From `ansible/`, run `ansible-playbook install-nebula.yml` or `ansible-playbook site.yml --tags nebula`. Override `dg_nebula_game_image` or `dg_nebula_compile_jobs` in `host_vars/localhost.yml` if needed. The launcher appears as **Super Mario Galaxy · Nebula** and saves inside Nebula's dedicated Wine prefix. The role skips the expensive compilation when its pinned version is already installed.

Nebula's [release requirements](https://github.com/keepvaibin/nebula/releases/tag/v1.0.1) are for Windows and Direct3D 12. On this host, the Wine launcher opens Nebula's settings but the game runtime currently stops during native NAND initialization with `ISFS result -102`. Proton did not get as far as the settings window. Nebula is installed for future compatibility testing but is **not playable here yet**. Dolphin remains the working route for Super Mario Galaxy.

Rechecked 2026-10-22: `current.json` reports v1.0.0, all three compiled
RMGE01 DLLs, `Nebula.exe`, `game.pak`, and the launcher are present. The
focused Ansible playbook completed with `changed=0`; its download and compile
steps were skipped. This confirms the install inventory, not a new gameplay
test.
