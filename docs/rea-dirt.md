# Colin McRae: DiRT (2007) — REA launcher

[akitaonrails/rea-dirt](https://github.com/akitaonrails/rea-dirt) replaces the
old pc-racing DiRT install on this box (2026-11-01). The release is a
**self-contained Linux AppImage** — Wine 11.20 (WoW64 build, so the 32-bit game
needs no multilib), DXVK and a `dirt-play` wrapper — that works on a **private
runtime copy** and leaves the owned install untouched.

```sh
cd ansible && ansible-playbook install-rea-dirt.yml
```

| | |
|---|---|
| Release | `v0.3.2`, `DiRTLauncher-v0.3.2-x86_64.AppImage` (SHA256 pinned; archived in `ROMS_FINAL/PC/releases/`) |
| Owned source | `ROMS_FINAL/PC/games/DiRT-2007` (official v1.22 + LAA `DiRT.exe`, sha256 `e4b66bd3…`; the vanilla v1.22 `e10268f8…` is equally accepted) |
| AppImage | `tools/rea-dirt/` |
| Prefix + private runtime | `~/.local/share/dirt-launcher/` (launcher's own default; `DIRT_PREFIX` can override) |
| Launcher | `bin/rea-dirt` → AppImage: settings window, then play |
| Entry | Walker **Colin McRae: DiRT (REA)** |

v0.3.2 adds Windows executable metadata and shared SDK v0.4.3 to reduce
antivirus false positives. It introduces no new graphics, frame pacing, or
controller setting; the role keeps the existing 4K profile and stages the
verified AppImage on the NAS before installing its local executable copy.

## What the launcher handles

Everything the old install needed by hand is now built in, which is why the
pc-racing slug was retired rather than kept alongside:

- **v1.22 detection by SHA-256**, then a private writable copy
  (`%LOCALAPPDATA%\DiRTLauncher\DiRT` inside the prefix).
- **Large Address Aware** on the runtime exe, and the **corrected 4/8/12-worker
  EGO maps** for modern CPUs — this is the old CMCR-DiRT-MTFix race-load crash
  (EGO v1 worker init on 32 logical CPUs), solved properly: `workers = auto`
  caps at 12 and never references undeclared workers.
- **4K + Ultra + 60 Hz vsync** (`launcher.cfg`: `resolution 3840x2160`,
  `aspect 16:9`, `quality ultra`, `fullscreen true`, `vsync true`,
  `scaler linear` for gamescope). The settings window re-detects the screen
  when resolution/aspect are unset.
- **Native XInput** with analog triggers and force feedback — no Xidi, no
  mapper. Pick DiRT's XInput preset in its Controls menu once.
- **True fullscreen via gamescope** (box-provided); without gamescope it falls
  back to an isolated Wine desktop at the same size.

## Saves

DiRT keeps saves/settings under `Documents/Codemasters/DiRT` inside the
launcher's prefix (the v1.22 build may also cache hardware settings in the
runtime — the launcher configures both). The role migrates the old pc-racing
prefix's `Public/Documents/Codemasters/DiRT` into the new prefix once and then
deletes the retired 11 GB per-game prefix; `dg_save_sets` mirrors
`~/.local/share/dirt-launcher/prefix/.../Documents/Codemasters/DiRT` plus the
launcher's `launcher.cfg`.

## CLI

```sh
rea-dirt                 # settings window (pad-navigable), then play
rea-dirt --play          # saved settings, no window
rea-dirt stop|status     # manage a run
```

The launcher exe itself also takes `--check`, `--setup`, `--game <folder>` etc.
(`--game` is remembered in `launcher.cfg`; the role seeds it with the NAS
source as a Windows path, `Z:\…`).

## History

The retired path is documented in `docs/pc-racing.md`: interactive
InstallShield install of the RELOADED disc, the 1.1 → 1.2 → 1.21 → 1.22 patch
chain, then the MTFix for the race-load crash. None of that is needed any
more; the NAS keeps the source archives (`DiRT-2007-RELOADED_Extracted`, the
patch folder, and an elamigos v1.22 repack) for a from-scratch rebuild of the
owned source.
