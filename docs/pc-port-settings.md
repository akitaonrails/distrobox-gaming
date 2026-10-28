# PC port display and controller baseline

Run `ansible-playbook configure-pc-ports.yml` from `ansible/` after installing
and first launching the optional PC ports. The playbook changes only settings
files that already exist, applies each baseline once, and then leaves later
in-game edits alone. Adjust `dg_pc_port_*` variables in
`group_vars/all/pc_port_settings.yml` or override them in host vars.

The two displays on this machine are 3840×2160; DP-1 runs at 240 Hz. “Auto”
resolution in a fullscreen RT64 port uses the display's size, so an explicit
3840×2160 value is unnecessary for those ports. Higher presentation rates do
not override a game's simulation clock.

> This playbook covers the ports below only. Ports whose role owns the
> setting seed it directly instead — Sonic 2 (2013) at 9× integer scale,
> DKC2/DKC3 at 16:9 fullscreen, Super Mario All-Stars at desktop fullscreen,
> Project R and God of War III at 4K, F-ZERO GX at 1440p + 4× MSAA, and FM4's
> whole settings baseline; each is documented on its own page.

| Port | External display setting checked | Result |
| --- | --- | --- |
| Fukami | `~/.local/share/Fukami/fukami.ini` | Fullscreen 3840×2160, 6× internal scale, 16× anisotropic, high draw distance; native SDL gamepad and rumble. The game's normal ~60 Hz pacing remains enabled. |
| DekUI | `user/config/qt-config.ini` | 10× internal scale and the detected 8BitDo SDL controller profile. `frame_limit=100` is the emulation-speed percentage, not a 100 FPS target; upstream still lists 60 FPS as planned. VSync remains enabled. |
| Conker Recompiled | RT64 `graphics.json` | Fullscreen, native-resolution Auto, **8× MSAA** (the port offers 2×/4×/8×). SDL controller support remains intact. |
| Road Rash 64 Recompiled | RT64 `graphics.json` | Fullscreen, native-resolution Auto, 4× MSAA, maximum LOD, extended horizon haze, 60 FPS. The port's own menu holds the MSAA choice. |
| Ship of Harkinian | `shipofharkinian.json` | Fullscreen; advanced resolution preset raised from 1440 to 2160 vertical pixels. Existing SDL button and stick mappings are preserved. |
| 2Ship2Harkinian, Starship, SpaghettiKart | Port JSON beside the executable | Fullscreen on the 4K display; their existing input settings are preserved. |
| G-Diffuser | `gdiffuser.cfg.json` | Fullscreen on the 4K display, interpolation matched to display refresh while simulation remains at 60 Hz; the separate 60 Hz frame pacer stays off. Native SDL controller settings are preserved. |
| DKR-R | `~/.config/dkr-port/dkr-port-settings.ini` | Modern presentation, fullscreen, automatic integer scale, widescreen, 4× MSAA, match-display presentation rate, high precision and maximum detail; rumble remains enabled. |
| Unleashed Recompiled | `~/.config/UnleashedRecomp/config.toml` | 3840×2160 fullscreen, 120 FPS, existing 4× MSAA/16× anisotropic and vibration. 120 FPS is a high target while avoiding the port's documented extra stutter sensitivity at higher rates. |
| Sonic 3 A.I.R. | `~/.local/share/Sonic3AIR/settings.json` | Fullscreen; the 60 Hz simulation setting remains intact. Its native gamepad auto-assignment remains available. |
| Star Fox Enhanced | `pregame.cfg` | 120 FPS presentation, heavy AA, enhanced graphics, medium model smoothing. Its existing maximum 4× render scale and native controller rumble remain in place. |
| Dusk | Godot user `config.json` | Fullscreen on the 4K display with a 240 FPS cap; Auto internal resolution, unlimited frame interpolation and existing 4× shadow resolution remain in place. |
| Render96ex | `~/.local/share/sm64ex/sm64config.txt` | Fullscreen at 3840×2160; native controller bindings and the game's 60 FPS mode remain intact. |
| TriAevum | `data/config/TriAevum.json` and `TriAevum.launch.json` | 3840×2160 borderless, 90 Hz interpolation, 4× MSAA. Its 30 Hz simulation stays native and experimental effects stay at known-working values. A scoped launch opened a 4K-sized window; gameplay quality still needs checking. |
| Midnight Club LA | Launcher cvar | 3× internal scale from 1280×720 to 3840×2160; a launch log confirmed the scaled source and active target. The upstream launcher offers higher FPS caps, but the installed standalone build has no verified external FPS-cap setting, and its own performance notes report substantially less than 60 FPS in free roam. Native SDL gamepad remains in place. |

Other installed ports checked: Banjo Tooie is already presented by gamescope at
3840×2160 with controller mapping; DK64, GoldenEye and Pilotwings have
fullscreen/Auto RT64 graphics; Perfect Dark already uses borderless fullscreen
with a safe 144 FPS cap and native dual-analog controls; Sonic 2 (2013) is
fullscreen with its required 60 FPS engine pacing and native controller
mappings; MPH Recomp uses SDL gamepad controls and its launcher supplies 4× AA.
Wind Waker HD Recompiled is fullscreen with native SDL3 input. SotN Recompiled's
external JSON contains disc and gamepad bindings, but no display resolution.
SM64DS PC port is configured for 60 FPS; SM64CoopDX also has a 60 FPS frame
limit with interpolation and VSync enabled. Sonic Galactic exposes VSync but no
verified high-FPS setting in its external config. These were left at their
existing timing settings.
F-Zero SNES Recompiled, Wave Race 64 Recompiled and Beetle Adventure Racing
Recompiled expose the relevant graphics controls through their game or launcher menus;
their external files here do not contain a verified 4K setting. Controller
support remains native or is configured in their launchers.

CannonBall, WipEout PE and Doom II Ray Traced already launch fullscreen at the
display size; the last two use 4K gamescope. Super Mario Bros. Remastered is
seeded fullscreen, while Super Mario World Remastered is fullscreened by the
host. DUDE's `r_mode=20` already selects 3840×2160 in its source mode table.
OpenSC2K's external settings cover imported assets, not display or
controller mapping. Project R's external TOML contains its configured 8BitDo
gamepad profile but no resolution setting. OpenCMR2's external controller data
is binary; its known menu D-pad up/down issue remains, with keyboard arrows as
the fallback. The parked GoW3 and Azimuth ports and Nebula's blocked runtime
are not treated as verified playable installs.

These are configuration checks, not proof that every port sustains its target
frame rate in gameplay. Keep game simulation caps when increasing presentation
rate, and test real controller buttons and sticks in-game after changing pads.
The 2160-pixel Ship preset is listed in [Shipwright's resolution editor](https://github.com/HarbourMasters/Shipwright/blob/develop/soh/soh/SohGui/ResolutionEditor.cpp),
the DKR-R setting meanings are in its [graphics UI](https://github.com/ThatGuyMcd/DKR-R/blob/main/runtime-recomp/src/game/runtime_graphics_ui.inl),
and the 120 FPS caution follows [Unleashed Recompiled's README](https://github.com/hedge-dev/UnleashedRecomp/blob/main/README.md).
G-Diffuser's [source](https://github.com/Zorkats/G-Diffuser/blob/main/port/gdx_menu.cpp)
documents interpolation and its 60 Hz pacer as mutually exclusive; its
[README](https://github.com/Zorkats/G-Diffuser/blob/main/README.md) notes that
interpolation may occasionally slow after screen transitions. DekUI's
[README](https://github.com/tgacquin/mm3d-dekui) lists 60 FPS as planned.
