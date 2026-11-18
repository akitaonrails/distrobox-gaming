# Daytona USA 2 Power Edition — Web

[Johann Ruiz's **Daytona USA 2 Power Edition — Web**](https://github.com/johannruiz/daytona-usa-2-web)
is a static recompilation of the Sega Model 3 arcade racer (1998) compiled to
**WebAssembly** with a **WebGPU** renderer. It is a static site: no installer,
no emulator front end, no Windows layer — the cabinet runs in the browser.

There is no native or desktop build upstream, so this repo ships it as a
**local web-app wrapper**: the pinned site is served from this machine on
`127.0.0.1` and opened in a Chromium app window, with the owned ROM preloaded
and the window already fullscreen on the main display.

```sh
cd ansible && ansible-playbook install-daytona2-web.yml   # or site.yml --tags daytona2_web
```

| | |
|---|---|
| Upstream | `0.9.7` at commit `1adde5b4` (Apache-2.0; keep `NOTICE`/credits: "Daytona USA 2 Power Edition Recomp by Johann Ruiz") |
| Archive | codeload tarball, SHA256-pinned, staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/daytona2-web/` (site + `roms/dayto2pe.zip` symlink) |
| Profile | `.local/share/daytona2-web/profile` (cabinet NVRAM/EEPROM) |
| ROM | `ROMS_FINAL/arcade/model3/dayto2pe.zip` — your own **non-merged** MAME set |
| Launcher | `bin/daytona2-web`; entry **Daytona USA 2 · Power Edition (Web)** |
| Runtime | host Chromium (WebGPU + WASM JSPI, Chrome/Edge 137+); no box, no Wine |

## Requirements

- A Chromium-155-or-newer browser with **WebGPU** and **WebAssembly JSPI**.
  The page refuses to start without them (`This browser has no WebGPU`).
- The **`dayto2pe`** MAME set as one complete ZIP. The page hashes it chip by
  chip before running and names the missing/wrong chip if the dump is off.
- A reasonably fast CPU: the emulation runs at 60 fields per second.

## What the wrapper does

- Serves the site with `python3 -m http.server` bound to `127.0.0.1:8791`
  (the port is pinned in `dg_daytona2_web_port` because the browser's
  IndexedDB — where the cabinet keeps its NVRAM backup — is keyed by origin).
- Symlinks your ROM to `tools/daytona2-web/roms/dayto2pe.zip`; nothing is
  copied and no game data enters the repo or the browser profile.
- Starts the cabinet with `?rom=1`, which imports the served ZIP through the
  same chip-checking path as a manual pick, so no file dialog appears.
- Runs `<browser> --app=… --start-fullscreen` and stops the local server when
  the window closes. The desktop entry points at the launcher directly.

### Browser flags, and why

```
--ozone-platform=x11 --enable-features=Vulkan --use-angle=vulkan --ignore-gpu-blocklist
--disable-component-update
```

`--disable-component-update` keeps Chromium from downloading its own
Widevine/TTS/crash-reporting components into the game profile; the cabinet
needs none of them.

Chromium's **Wayland** backend on this NVIDIA host refuses Vulkan
(`--ozone-platform=wayland is not compatible with Vulkan`) and the page's
WebGPU device is lost right after the first frame — a white cabinet at ~2 fps.
Running the window through Xwayland with **Vulkan compositing** keeps the
compositor and Dawn on one Vulkan instance, and the game holds 60 fps at
2560×1440 fullscreen.

`--enable-unsafe-webgpu` is deliberately **not** used: WebGPU is enabled by
default in current Chromium, and that flag only adds Chrome's "unsupported
command-line flag" banner across the top of the screen.

## Graphics: already at the ceiling

The site's own maximum is also its default, so the role seeds nothing:

| Setting | Value |
|---|---|
| Display | **Enhanced** — widescreen at the window's resolution (2560×1440 here) with the original HUD |
| Render scale | **100%** — full window resolution; 50%/75% exist only for slower GPUs |
| Draw distance | **2** (max; the mobile default is 1) |

Change any of them in **Settings → Graphics**; the choice is stored in the
browser profile and survives updates. The arcade's own **TEST** menu (`F2`)
and **SERVICE** button (`F3`) are available for cabinet options.

## Controls

| Action | Keyboard | Gamepad (8BitDo Ultimate 2) |
|---|---|---|
| Steer | ← → | left stick |
| Accelerate / brake | ↑ ↓ | RT / LT |
| Gears 1–4 | `1` `2` `3` `4` | B A X Y |
| Shift down / up | `Q` / `W` | LB / RB |
| Insert coin / start | `5` / `Enter` | Back / Start |
| Camera views | `A` `S` `D` `F` | d-pad |
| Menu / pause | `Esc` | — |
| TEST / SERVICE | `F2` / `F3` | — |

The pad is read through the browser's Gamepad API (native SDL/XInput pads
appear as standard gamepads); rumble is on by default and can be switched off
in Settings. Every input can be remapped, and racing wheels have their own
calibration page under **Settings → Experimental**.

## Saves

The cabinet writes its SRAM/EEPROM backup into this origin's IndexedDB, in the
browser profile at `.local/share/daytona2-web/profile`. The `daytona2-web` set
in `dg_save_sets` covers `profile/Default/IndexedDB` (cabinet NVRAM) and
`profile/Default/Local Storage` (display, volume and control settings) — not
the rest of the profile, which is Chromium's own component cache. A revert
keeps both; deleting the profile is a factory reset.

## Verified here

- The pinned site loads, `dayto2pe.zip` is fetched from the local server and
  verified chip by chip (`ROM verified.`), and the cabinet reaches its attract
  mode, car selection and a race at **60.0 FPS / 60.0 Hz** fullscreen.
- No console errors (no WebGPU device loss) with the launcher's flags, and no
  unsupported-flag banner.
- A first launch immediately after the browser profile was created can lose
  its WebGPU device while the GPU pipeline cache is cold (white picture, HUD
  pinned at ~2 fps). Closing the window and starting again works; the cache
  lives in the profile afterwards. If it happens twice in a row the browser or
  driver, not this install, is the place to look.

## Multiplayer

The page offers linked races over WebRTC (PeerJS only for discovery). Single
player is fully offline; nothing about the ROM or your profile leaves the
machine.

## Updating

Bump `dg_daytona2_web_version`, `dg_daytona2_web_commit` and the tarball
`dg_daytona2_web_asset_sha256` in `group_vars/all/daytona2_web.yml` and re-run
the playbook; the role re-unpacks when `.dg-version` changes and re-applies the
`?rom=1` loader. Revert with `-e dg_daytona2_web_revert=true`; the ROM, the
browser profile and the NVRAM backup are kept.