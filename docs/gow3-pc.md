# God of War III Remastered PC port

The Linux AppImage is pinned to [windows-v2.7.0](https://github.com/FelipePrado0/gow3_pc/releases/tag/windows-v2.7.0) (`spartanport-x86_64.AppImage`, SHA256-verified). Existing launcher settings and game files are preserved by the update.

The optional `install_gow3_pc` role installs [FelipePrado0/gow3_pc](https://github.com/FelipePrado0/gow3_pc)'s experimental Linux AppImage alongside shadPS4. It uses the existing PS4 game folder directly and does not copy or alter the dump. The tested local dump is CUSA01623, app version 01.00; upstream lists 01.00 and 01.02 as tested. The upstream Linux instructions specifically mention 01.02, so verify gameplay on this machine before assuming the 01.00 build is fully supported.

From `ansible/`, run `ansible-playbook install-gow3-pc.yml` or `ansible-playbook site.yml --tags gow3_pc`. Override `dg_gow3_pc_game_dir` in `host_vars/localhost.yml` when the game root differs; it must contain `eboot.bin`, `sce_module/` and `sce_sys/`. The launcher passes this path through `GOW3_GAME_DIR` for first-run setup. Select the same game folder in the graphical launcher if it already has a saved setting. The port writes saves, settings and shader cache under `~/.local/share/gow3` and launcher preferences under `~/.config/gow3-launcher` inside the box.

The port's own settings live in `~/.local/share/gow3/gow3.ini` (its in-game menu
is Insert / R3+L2). The role keeps `display_mode=fullscreen` and
`output_res=3840x2160`; the render resolution is separately maxed at `4K` with
the FSR4 upscaler and a 120 FPS engine cap, and everything else in the file is
left to the player.

The release is pinned by SHA-256 in `group_vars/all/gow3_pc.yml`. Update the tag, asset hash and installed ref together when upgrading. On first install, the role seeds the game folder and disables the experimental Vulkan pipeline binary cache because the tested NVIDIA driver crashes while initializing it. Existing launcher settings are preserved. The existing PS4 installation and separate patch PKG are not touched by this role.

On 2026-10-13, release 2.1.8 accepted the 01.00 dump and reached the in-game brightness setup screen on the NVIDIA RTX 5090. With the pipeline binary cache enabled it instead crashed during Vulkan initialization. Gameplay beyond the setup screen remains untested.
