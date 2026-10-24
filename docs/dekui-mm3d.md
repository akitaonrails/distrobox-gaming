# Majora's Mask 3D via DekUI

The optional `install_dekui` role installs [DekUI](https://github.com/tgacquin/mm3d-dekui) v1.0.0 alongside Azahar and the N64-based 2Ship2Harkinian. DekUI is a custom Azahar build with a single-screen interface for Majora's Mask 3D. It requires a decrypted USA v1.1 game-card image; the role checks the game's partition against DekUI's supported fingerprint before copying it beside the application. DekUI's setup requires a real adjacent file and creates a real `user/` directory on first launch; the original game image is untouched.

From `ansible/`, run `ansible-playbook install-dekui.yml` or `ansible-playbook site.yml --tags dekui`. Override `dg_dekui_rom` in `host_vars/localhost.yml` for a different source path. The launcher is **Zelda: Majora's Mask 3D · DekUI**. First launch prepares game resources in `dg_dekui_user_dir`; this can take longer than later launches. The role preserves that directory when a new release is extracted. Back it up before an upgrade. Press F1 for DekUI settings and controls.

The Linux release is an AppImage. The launcher uses `APPIMAGE_EXTRACT_AND_RUN=1` so a FUSE mount is not required. DekUI is [still a beta](https://github.com/tgacquin/mm3d-dekui); keep frequent in-game saves.

After the first launch creates its settings file, rerun the install playbook to apply the initial graphics and controller baseline: 10× internal resolution (4K-class output) and the matching 8BitDo SDL gamepad profile. The role applies these once and then preserves changes made in DekUI's settings. If another pad is used, set `dg_dekui_controller_guid` to its SDL GUID and configure that pad's profile before selecting it.
