# Metroid Prime 4: Beyond Recompiled

[linuxopt/mp4-recomp](https://github.com/linuxopt/mp4-recomp) is MZ Labs'
**SwitchRecomp** static recompilation of *Metroid Prime 4: Beyond*. It is an
ahead-of-time recompiler: it turns the owned Switch title into native x86-64 C,
compiles it here with a bundled GCC into a `_code.so`, and runs it under a
native SDL runtime. There is no Switch emulator in the loop. The recompiler and
runtime ship in an AppImage; the game code itself is built on this machine from
your own dump. Our opt-in role `install_mp4_recomp` pins the AppImage, extracts
its recompiler, verifies the owned base + update, builds the game once, seeds
maxed graphics defaults, and publishes the menu entry.

## Owned game data (base **and** the RS15 update are required)

The recompiler enforces a title-version gate: the **base-only** dump
(`E860CBED`) is **refused**. You must supply the base XCI *and* the **v1.1.0
update (RS15, title version 131072)**. The role takes:

- `dg_mp4_base_xci` — `roms_heavy/switch/Metroid_Prime_4_Beyond_NSW-HR/hr-bgw5a.xci`
  (sha256 `1f86f467…`), the base cart dump.
- `dg_mp4_update_rar` — `ROMS_FINAL/switch/Metroid_Prime_4_Beyond_Update_v1.1.0_NSW-HR/hr-bgw5av131072.rar`,
  the multipart RAR holding the update `hr-bgw5av131072.nsp` (sha256
  `6646db80…`). The role extracts the NSP from the RAR when absent.
- `dg_mp4_keys` — your Switch decryption keys at
  `~/.local/share/eden/keys/prod.keys`.

The base and update checksums are verified **only when a build is needed** (the
check is gated behind `…_data/setup.ok`), so a normal run never re-hashes the
32 GB base. On another machine, override these paths and their checksums in host
vars.

## Install and rebuild

```sh
cd ansible
ansible-playbook install-mp4-recomp.yml
```

The first run **builds the game from your dump** with the bundled recompiler:

```
python3 <recompiler>/beyond_setup.py --out <game> --name "Metroid Prime 4 Beyond" \
    --base <xci> --update <nsp> --keys prod.keys --jobs 24
```

This recompiles ~250 translation units and links the native `_code.so` — expect
a long, CPU-heavy one-off run. Everything built lands under
`~/.local/share/MetroidPrime4Recomp/` (`Metroid Prime 4 Beyond` runtime binary,
`Metroid Prime 4 Beyond_code.so`, `Metroid Prime 4 Beyond_data/{romfs,exefs,
setup.ok,save}`, `Metroid Prime 4 Beyond_build/`). The role runs the build only
while `…_data/setup.ok` is absent; afterwards it is idempotent. `beyond_setup.py`
reports failures through an `@@E` line while still exiting 0, so the role greps
for `@@E` and for `setup.ok` to decide success.

The save backup registers the title's `…_data/save` directory and the settings
`.ini`; the recompiler output (`_code.so`, `_build/`, `_data/romfs`+`exefs`) is
reproducible from the dump and excluded.

## Graphics and input

`Metroid Prime 4 Beyond.ini` is seeded only when absent (the runtime rewrites it,
so later in-game choices win) at this box's ceiling: internal 3D resolution
**x2.4** (supersamples far above the 4K panel), the **FSR** upscaler, **16×**
anisotropic filtering, and the port's anti-aliasing on. `fast_forward` lets the
stick fast-forward; `ps4` button glyphs suit the 8BitDo. The recomp exposes no
*output*-resolution setting — it runs at its own fullscreen video mode on DP-1
with that heavy internal supersampling as the quality ceiling it offers.

This AppImage build has **no native Vulkan renderer** (`renderer=vulkan_native`
falls back to OpenGL), so it runs **OpenGL/GLX on the NVIDIA dGPU** via PRIME
offload. The launcher therefore runs it **native on NVIDIA XWayland and does not
wrap it in gamescope**: on this box gamescope grabs the AMD iGPU for SDL+GL
NVIDIA apps and flickers (the same reason Supermodel runs native). The launcher
focuses DP-1 over Hyprland's Lua IPC, pins the NVIDIA GLX vendor, and exports
`SWR_RECOMPILER` so the runtime can find the recompiler dir extracted from the
AppImage.

Gamepad: the runtime reads SDL game controllers with
`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS` on; an 8BitDo in XInput mode is picked up
and bound in the in-game controller settings.

## Updating the recomp

Bump `dg_mp4_release_tag` and `dg_mp4_appimage_sha256` to a newer
[release](https://github.com/linuxopt/mp4-recomp/releases) and re-run the
playbook. The AppImage re-extracts on a version change (tracked by
`.dg-installed-ref`); the already-built game is left in place unless you delete
`setup.ok` (or the `_data` tree) to force a rebuild.
