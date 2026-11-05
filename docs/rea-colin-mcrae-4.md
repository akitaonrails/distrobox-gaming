# Colin McRae Rally 04 (2004) — REA launcher

[akitaonrails/rea-colin-mcrae-4](https://github.com/akitaonrails/rea-colin-mcrae-4)
replaces the old pc-racing Colin McRae Rally 04 install on this box
(2026-11-02). Like the other REA launchers
([rea-colin-mcrae-3](rea-colin-mcrae-3.md), [rea-outrun-2006](rea-outrun-2006.md),
[rea-sega-rally-revo](rea-sega-rally-revo.md)), the release is a
**self-contained Linux AppImage** — its own Wine 11.20 (WoW64, so the 32-bit
game needs no multilib), DXVK and dgVoodoo — with a pad-navigable settings
window and gamescope for true fullscreen. It works on a **private runtime copy**
and never touches the owned install.

```sh
cd ansible && ansible-playbook install-rea-colin-mcrae-4.yml
```

| | |
|---|---|
| Release | `v0.4.2`, `CMR4Launcher-v0.4.2-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/Colin-McRae-Rally-04` (`cmr4.exe` sha256 `7dca9f4c…`, the **original un-patched** build) |
| AppImage | `tools/rea-colin-mcrae-4/` |
| Prefix + private runtime | `~/.local/share/cmr4-launcher/` (launcher's own default; `CMR4_PREFIX` can override) |
| Launcher | `bin/rea-colin-mcrae-4` → AppImage (`cmr4-play`): settings window, then play |
| Entry | Walker **Colin McRae Rally 04 (REA)** |

v0.4.2 gives the Windows executable version metadata and changes the private
`cmr4.exe` to import `rea_close_hook.dll` when the game starts. The launcher
no longer installs that hook into a running process. Upstream reports the
Alt+F4/window-close behavior is preserved; no new graphics, pacing or pad
setting is required for our profile. The role stages the verified AppImage on
the NAS and keeps a local executable copy.

## What the launcher handles

The entire widescreen/monitor/gamepad stack the old pc-racing slug assembled by
hand is now **built into the launcher**, which is why the slug was retired:

- **Correct widescreen** — CMR04 is a 4:3 engine, and the only right way to
  widescreen it is the AuToMaNiAk005 "16:9 Low" patch *with a 4:3 render
  stretched to 16:9*. The launcher applies that patch to its private `cmr4.exe`,
  renders 4:3 (2880×2160 for a 4K screen) and has **dgVoodoo** (D3D8/9 → D3D11)
  stretch the frame to 16:9, so cars and scenery keep their proportions with the
  wider view. Rendering 16:9 directly (the naïve fix) makes cars 25% too narrow.
  The HUD is on the game's fixed 640×480 grid and stays slightly wide.
- **The right monitor** — it sends the game to the largest **landscape** monitor,
  so a portrait primary (this box's DP-2) no longer gets a squashed strip.
- **Alt+F4 / window close** — CMR04 ignores close requests; a small hook
  (`cmr4close.dll`) ends the game on Alt+F4 or Super+W.
- **A gamepad that drives out of the box** — Xidi presents the pad as a normal
  gamepad (stick steers, RT/LT are analogue pedals, no keyboard emulation), and
  for a profile whose controls were never set up the launcher selects the
  connected pad with analogue pedals in the game's `OPTIONS` (the same trick the
  CMR3 launcher uses), so a new player drives without opening Options.
  Hand-configured profiles are left alone. **Note:** picking the controller in
  the game's own Options → Controllers menu can *freeze* the game under Wine —
  the choice is saved before the freeze, so restart and it is in effect; the
  launcher's auto-setup avoids needing to.

## Graphics

`launcher.cfg` is seeded maxed out: `resolution 3840x2160` (4:3 render at
2880×2160, dgVoodoo stretch to 4K 16:9 — from v0.3.1 the 16:9 resolution is
what selects the widescreen view; the separate `widescreen` toggle was removed
upstream and is no longer seeded), `controller on`.
`fps_limit off` and `vsync off` are the tuned choices — dgVoodoo on the RTX runs
this 2004 game far above 60.

## Saves

CMR04 writes its saves and settings as **loose files beside the exe** —
`OPTIONS` (profiles + controller setup), `CHAMPIONSHIP_SLOT_*` (career) and
`BESTTIMES_GHOSTS` — which here means inside the launcher's private runtime copy
(`AppData/Local/CMR4Launcher/CMR4`). The launcher treats those names as
persistent and never overwrites them from the source once they exist. The owned
source carries a copy so a from-scratch build seeds them; `dg_save_sets` backs
up those files (not the ~1 GB game copy) plus the launcher's `launcher.cfg`.

## The owned source

The clean source at `ROMS_FINAL/PC/games/Colin-McRae-Rally-04` is the stock game
only — `cmr4.exe`, `Data/fonts/shaders`, the `Math*.dll` libraries, the DSOAL
audio (`dsound.dll`/`dsoal-aldrv.dll`/`alsoft.ini`) and the loose save files. It
was staged from the previous pc-racing install with that install's injected Xidi
(`dinput8.dll`, `Xidi.ini`, `.dg-xidi` marker), dgVoodoo (`D3D9.dll`,
`dgVoodoo.conf`, `dgVoodooCpl.exe`), the `CMR4_16x9-Low.exe` patcher tool and the
Inno `unins000.*` stripped out, **and `cmr4.exe` un-patched back to the
original** (the pc-racing 16:9 Low byte patch reversed): the launcher supplies
its own dgVoodoo/Xidi and applies the aspect patch to its private copy, so the
source stays a clean, un-patched game folder. The launcher patches `cmr4.exe` by
byte signature and is idempotent (it would accept an already-patched exe too);
the role sha256-verifies the un-patched source exe.

## CLI

```sh
rea-colin-mcrae-4                 # settings window (pad-navigable), then play
rea-colin-mcrae-4 --play          # saved settings, no window
rea-colin-mcrae-4 stop|status     # manage a run
```

`rea-colin-mcrae-4` re-enters the `gaming` box and runs the AppImage's
`cmr4-play`. The launcher exe inside also takes `--check`, `--setup`,
`--no-window`, `--settings` and the per-setting flags in the README; `--game` is
remembered in `launcher.cfg`, which the role seeds with the NAS source as a
Windows path (`Z:\…`, Wine maps `Z:` to `/`).

## History

The retired path is documented in `docs/pc-racing.md` (and the removed
`colin-mcrae-rally-04` slug in `group_vars/all/pc_racing.yml`): the Magipack Inno
repack installed to `G:\colin-mcrae-rally-04`, the AuToMaNiAk005 16:9 Low byte
patch applied to `cmr4.exe` in place, dgVoodoo forced to 3840×2160 (text
replacements in `dgVoodoo.conf`), registry `Width`/`Height` 3840×2160, gamescope
3840×2160, winetricks DXVK, and a Xidi `CMR04Gamepad` keyboard-emulation mapper.
None of that is needed any more; the NAS keeps the repack installer archive for a
from-scratch rebuild of the owned source.
