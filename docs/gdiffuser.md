# G-Diffuser (F-Zero X PC port) — `install_gdiffuser`

Zorkats's native PC port of **F-Zero X (N64)**, including full **64DD Expansion
Kit** support (Course Edit + DD cups). Built on **libultraship** — the same
engine as Ship of Harkinian and Starship — via the inspectredc/fzerox
decompilation. Adds true widescreen, an ImGui enhancement menu (F1), frame
interpolation, texture-pack modding, ghost library and more. Upstream:
[Zorkats/G-Diffuser](https://github.com/Zorkats/G-Diffuser). Opt-in role;
installed 2026-08-11.

- **Distribution:** a prebuilt **native Linux** binary (no Wine). Pinned to
  `dg_gdiffuser_version` (`v1.0.1`), fetched from the GitHub release by sha256.
- **You must provide three files (all required).** G-Diffuser ships no game
  data — it builds its `.o2r` archives from your dumps on first launch.

## Required game files

| Canonical name (beside the exe) | Source on this box | What it is |
|---|---|---|
| `baserom.us.rev0.z64` | `sdcard-bundle-6666/F-Zero X (U) [!].zip` | F-Zero X **US rev0** ROM (big-endian `.z64`; the loader does not byte-swap) |
| `baserom.translated.ek.ndd` | `nes/…` → `n64/EFZE_ENGLISHv02_DISK.zip` (`NUD-EFZE-USA_2.ndd`) | fan-translated 64DD **Expansion Kit disk** (Zoinkity translation, LuigiBlood 64DD port), ~64.9 MB |
| `N64DDIPLROM.n64` | `n64/64DD BIOS/IPL4USA.zip` (the 4 MB US-prototype IPL) | a **64DD IPL / drive ROM** (supplies the drive font). The retail `ipl4rom.n64` is only 1.16 MB — not the full IPL; use the 4 MB one. |

The role stages all three under those canonical names, so the first-boot setup
auto-detects and SHA-validates them (it confirmed our ROM is US rev0) and builds
`fzerox.o2r` + `n64ddipl.o2r` + `fzerox-disk.o2r` **unattended** — no wizard
click. (The IPL SHA differing from the author's reference dump is expected and
explicitly "not an error".)

## Install / run / revert

```sh
cd ansible
ansible-playbook install-gdiffuser.yml            # or: site.yml --tags gdiffuser
scripts/install-host-launchers.sh                 # refresh the host menu entry
ansible-playbook install-gdiffuser.yml -e dg_gdiffuser_revert=true
```

Launcher: `{{ dg_box_home }}/bin/g-diffuser` (menu: **"G-Diffuser - F-Zero X"**).
It focuses DP-1 and pins the RTX. **First launch** does the one-time asset build
(~30-60 s) then boots to the game; later launches boot straight in. Press **F1**
for the enhancement menu.

## Rendering + controller

- **Rendering:** native OpenGL (libultraship Fast3D). The launcher pins
  GLX/PRIME + the NVIDIA Vulkan ICD so it renders on the RTX, not the AMD iGPU.
  No gamescope (native GL, same as Cannonball/Supermodel).
- **Controller (always supported):** native SDL input (incl. DualSense) — the
  8BitDo works out of the box. Menu also opens with Gamepad Back.

## Notes

- All three input dumps stay on the NAS untouched; the role only reads them.
- Bump `dg_gdiffuser_version` + `_asset_sha256` for a new release; re-extract
  (`--strip-components=1`) preserves the staged files, built `.o2r` and saves.
- The loader also accepts `baserom.jp.ek.ndd` (Japanese disk) and
  `64DD_IPL_US_MJR.n64` (US-proto IPL under its own name) if you have those.
