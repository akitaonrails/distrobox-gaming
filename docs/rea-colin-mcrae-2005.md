# Colin McRae Rally 2005 (2004) — REA launcher

[akitaonrails/rea-colin-mcrae-2005](https://github.com/akitaonrails/rea-colin-mcrae-2005)
**unparks** Colin McRae Rally 2005 on this box (2026-11-02). The game was a
documented "Wine dead-end" (issue #4): it crashed at `0x41DA27` before the first
menu, and the GOG installer hangs under Wine. The release is a **self-contained
Linux AppImage** — its own Wine (WoW64, so the 32-bit game needs no multilib),
DXVK and a `cmr2005-play` wrapper — that works on a **private runtime copy** and
never changes the owned source.

```sh
cd ansible && ansible-playbook install-rea-colin-mcrae-2005.yml
```

| | |
|---|---|
| Release | `v0.2.2`, `CMR2005Launcher-v0.2.2-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/Colin-McRae-Rally-2005_Win_EN-FR-DE-IT-ES_DRM-Free` — the **GOG v1.1 offline installer** (`setup_colin2005.exe` sha256 `690a5e3f…` + `setup_colin2005-{1,2}.bin`). Retail DVD (StarForce) is **not** supported. |
| AppImage | `tools/rea-colin-mcrae-2005/` |
| Prefix + private runtime | `~/.local/share/cmr2005-launcher/prefix` (the launcher's own default; `CMR2005_PREFIX` can override) |
| Launcher | `bin/rea-colin-mcrae-2005` → AppImage: settings window, then play |
| Entry | Walker **Colin McRae Rally 2005 (REA)** |

v0.2.2 adds Windows executable metadata and changes the private game copy to
load `rea_close_hook.dll` itself, avoiding a live-process hook. Upstream says
closing the window or using the game's Exit still quits, while Alt+F4 works
when the mouse moves because the game captures the keyboard. The existing
4K, graphics and pad profile stays appropriate. The verified AppImage is
staged on the NAS before being copied to its local executable path.

## What the launcher handles

Everything the earlier dead-end attempts needed by hand — and never solved — is
built in:

- **The "Wine dead-end" fix.** The game loads its fonts through registry values
  its installer writes (`HKLM\SOFTWARE\CODEMASTERS\Colin McRae Rally 2005`:
  `INSTALL_PATH`, `SAVEGAME_PATH`, `WIDTH`/`HEIGHT`); without them it crashes at
  `0x41DA27`. The launcher writes them on **every** start (HKLM 32-bit view, or
  the per-user VirtualStore without admin rights), pointing at its private copy.
- **Installs from GOG's files without running the installer.** The GOG setup
  hangs under Wine, so the first start unpacks the game (~3.6 GB) with **bundled
  innoextract 1.9** instead. Unknown installers and missing/wrong-sized `.bin`
  parts are refused with a reason. Later starts are quick. The private copy
  **links** the big data files, so it costs little extra space.
- **4K widescreen via DXVK.** DXVK 3.1.1's `d3d9.dll` took a stage from ~20 fps
  to over 1000; `dxvk.conf` carries the frame-rate cap and VSync. We seed
  `resolution 3840x2160` (16:9 → the game's `WIDESCREENDISPLAY` view at native
  4K), `vsync on`, `fps_limit off` — the "Graphics: Always Max Out" ceiling for
  a 2004 game on the RTX. The three built-in **looks** are Original, Widescreen
  (largest 16:9 that fits) and Steam Deck (1280×720/60).
- **Window-close quits** (the SDK close hook, `PC_CMR5`): the window's close
  button, the compositor's close (Super+W / a desktop's Alt+F4). The game
  itself ignores those keys, so this is the way to quit.
- **Portrait-safe.** Under Wine outside gamescope with a portrait main monitor
  the game runs in a Wine virtual desktop sized to the landscape monitor (it
  stops with "Adapter has no modes" otherwise). On this box gamescope + DP-1
  (landscape 4K) is the normal path.

## Gamepad

The launcher adds nothing for the pad — **the game reads it itself**. Set the
8BitDo up once in the game's own **Options → Controllers**: choose the pad,
then the buttons and the steering/pedal axes. Upstream confirms a gamepad set
up this way played a full stage on Linux. (There is no `controller` key in
`launcher.cfg`; the game owns the mapping.)

## Settings and saves

`launcher.cfg` lives in the prefix at
`…/AppData/Local/CMR2005Launcher/launcher.cfg`; the role seeds `game`,
`resolution`, `fps_limit` and `vsync` once (`force: false`) and only keeps the
`game =` path in sync afterward. Keys: `game`, `look`, `resolution`,
`fps_limit`, `vsync`, `runtime` (each also a `--flag`). Change the resolution in
the launcher, not the game — it is rewritten on every start from the look
(pick the **Original** look to keep an in-game resolution instead).

Saves get their own folder, outside the game and the private copy, at
`…/AppData/Local/CMR2005Launcher/saves/`; any saves already in a `cmr5.exe`
install's `SG` folder are copied there once. `dg_save_sets` mirrors that folder
plus `launcher.cfg` (not the ~3.6 GB unpacked game, which rebuilds from the GOG
source).

## CLI

```sh
rea-colin-mcrae-2005            # settings window, then play
rea-colin-mcrae-2005 --play     # saved settings, no window
rea-colin-mcrae-2005 stop       # end the game and its prefix session
rea-colin-mcrae-2005 status     # running or idle
```

## History

The retired path is in `docs/pc-racing.md` and issue #4: every combination of
Wine/Proton build, prefix arch and GOG-vs-installed layout crashed at
`0x41DA27`, and the workaround was "use the PS2 version via PCSX2". The role
removes the ten dead-end experiment prefixes
(`wineprefixes/pc-racing/colin-mcrae-rally-2005-*`) on install; they held no
saves (the game never ran). The owned GOG source on the NAS is untouched.
