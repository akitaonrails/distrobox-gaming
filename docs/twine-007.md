# 007: The World Is Not Enough · Recompiled

The optional `install_twine` role installs
[I Could Have Given You The World](https://github.com/riseio/TWIPE_00Sheven),
the native Linux recompilation of the N64 game, from the pinned
`ICHGYTW_0.1.96` AppImage. Run `ansible-playbook install-twine.yml` from
`ansible/`, or `ansible-playbook site.yml --tags twine`. The launch entry is
**007: The World Is Not Enough · Recompiled**.

The tested ROM is `dg_twine_rom_source` in `dg_rom_mid_root/n64/`, the USA
revision 0 dump in byte-swapped order (`.n64`, SHA-256
`87942bce2b6aff1c7091673282bbdaa7cc3d5ead6e7f1e5f3ce507fa779aabeb`).
The role leaves it intact and writes `dg_twine_rom_z64` in the install
directory. The normalized SHA-256 is
`72e3e7b4ff1615bc17336d3d10e18aa9342898db063ace68922a47f5e46c48b1`,
the value required by the port's source. Set `dg_twine_rom_source` in
`host_vars/localhost.yml` if the owned dump moves.

The runtime is stored in `dg_twine_install_dir`, with the pinned download
kept in `dg_twine_cache_dir` for rebuilds. On first launch, upstream compiles
native game code locally from the ROM. Its adjacent `data/` directory holds
the generated code, settings and saves; keep that directory during updates.
The port supports widescreen, high-refresh interpolated output and native
gamepads with twin-stick controls. The role seeds `graphics.json` once with
fullscreen Vulkan output, expanded widescreen, 4× MSAA and the display's
refresh rate; on this machine the fullscreen display mode targets 3840×2160.
`Display` tracks the monitor refresh rather than forcing an uncapped game
clock. These are configured targets, not measured gameplay results. Later
in-game graphics changes are preserved. The launcher selects the NVIDIA
Vulkan ICD. The upstream [README](https://github.com/riseio/TWIPE_00Sheven#readme)
lists the complete controller layout. Rumble on Steam Deck is listed as
upcoming upstream; desktop-pad rumble should be checked in game. A launch
check reached the menu at 3840×2160. The runtime detected the connected
8BitDo Ultimate 2 controller and switched its prompts to A/B; a later run
kept the fullscreen/Vulkan/4× MSAA settings. The log showed a 240 Hz display
target and about 204 presentation frames per second at one menu sample;
this is not a gameplay benchmark. Buttons, sticks and rumble still need a
hands-on play session.
