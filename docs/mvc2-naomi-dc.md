# Marvel vs. Capcom 2 — NAOMI/Dreamcast decompilation port

[gibletto/mvc2-naomi-dc](https://github.com/gibletto/mvc2-naomi-dc) is a
byte-matching decompilation of **Marvel vs. Capcom 2** from both the NAOMI
arcade cartridge and the Dreamcast disc. The same C builds the original
arcade/Dreamcast programs and a PC port; the release here is the 32-bit
Windows port (SDL3, SDL_GPU), played under Wine in the gaming box.

```sh
cd ansible && ansible-playbook install-mvc2-naomi-dc.yml   # or site.yml --tags mvc2
```

| | |
|---|---|
| Release | `0.4.1` Windows zip (7.2 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/mvc2/` — `mvc2.exe`, `mvc2dc.exe`, SDL3, `roms/`, `disc/`, saves |
| Arcade ROM | `ROMS_FINAL/arcade/mame-naomi/mvsc2.zip` (MAME `mvsc2`, export), linked read-only |
| Dreamcast | `ROMS_FINAL/dreamcast/Marvel vs. Capcom 2 (USA)_dup1.chd`, linked read-only |
| Launcher | `bin/mvc2`; entry **Marvel vs. Capcom 2 · NAOMI/Dreamcast** |

## How it runs

The port's first start unpacks the arcade set into
`roms/mvsc2/mvsc2.bin` (136 MB) and, when the Dreamcast version is chosen, the
CHD into `disc/` (210 MB). The source ROMs and disc are only read. Both modes
run at the boards' 59.94 Hz; F9 switches between the arcade and Dreamcast
versions once both are installed.

There is no Linux build: the port is a 32-bit MSYS2 mingw32 program. It uses
**SDL_GPU/Vulkan** under Wine (the launcher exports `SDL_GPU_DRIVER=vulkan`;
Wine's D3D12 path is not needed). The Wine prefix is `wineprefixes/mvc2`.

## Baseline

`mvc2.cfg` is seeded once with **arcade mode**, fullscreen, GPU rendering at
the window's resolution (4K), **4× AA**, sharp sprites and **all characters,
colours and stages unlocked**. The in-game F1 settings and test menu rewrite
the file; later changes survive role reruns.

Controls: arrows/S-A-D-Z-X-C for player 1 (I-J-K-L/R-T-Y-F-G-H for player 2),
5 coin, 1/2 start, F1 controls, F2 test menu, F9 arcade/Dreamcast, F10 scaling,
F11/Alt+Enter fullscreen, Escape quit. Pads: d-pad/stick move, face buttons
punches/kicks, shoulders assists, triggers assist 2, Start/Back.

## Verified here

- The arcade mode boots under Wine and runs fullscreen at **3840×2160**
  (window class `mvc2.exe`) from the linked `mvsc2.zip`; the port logs a few
  unimplemented NAOMI library stubs but reaches the game.
- Role rerun `changed=0`. The Dreamcast mode (F9), a full match, audio and
  physical pad input were not exercised in this install.

## Updating

Bump `dg_mvc2_version`, the asset and SHA256 in
`group_vars/all/mvc2_naomi_dc.yml`, then re-run. The unpacked game data,
`mvc2.cfg` and saves are preserved. Revert with `-e dg_mvc2_revert=true`; the
ROM and disc are untouched.