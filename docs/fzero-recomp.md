# F-Zero Forever (SNES F-Zero recomp)

[RetroPortingToolKit/FZeroSNESRecomp](https://github.com/RetroPortingToolKit/FZeroSNESRecomp)
(the former `mstan/FZeroSNESRecomp`) recompiles the SNES **F-Zero** into a native
PC program on the shared `snesrecomp` engine. The project grew into **F-Zero
Forever**: 85 course versions (CGP, Astra Velocity/Astra Front,
Bower League and MAX packs) alongside the original 15, two-to-four-player local
VS, netplay, HD Mode 7 up to 8×, presentation up to 360 FPS, display shaders, a
save-state browser with thumbnails, offline rewind, and BS F-Zero Deluxe
content.

Upstream ships **Windows x64 bundles only** now. This role builds the Linux
binary from the pinned source (the DKC / DK64 pattern) and stages the release
bundle's platform-independent data. It replaces the old v1.8.3 Linux AppImage.

```sh
cd ansible && ansible-playbook install-fzero-recomp.yml   # or site.yml --tags fzero_recomp
```

| | |
|---|---|
| Source | `v0.20.0-rc.3`, commit `6e2800f7…`, submodules pinned in `group_vars/all/fzero_recomp.yml` |
| Data bundle | `F-Zero-Forever-0.20.0-rc.3-windows-x64-without-msu.zip` (45.8 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Build | `~/.cache/fzero-forever-build/src` + `build` (reused on version bumps) |
| Install | `tools/fzero-snes-recomp/` — native `F-Zero Forever` binary, `assets/`, `mods/packs/` |
| ROM | `ROMS_FINAL/snes/F-ZERO.smc` (F-Zero USA, headerless, sha256 `bf16c3c8…`) |
| Launcher | `bin/fzero`; entry **F-Zero · Forever** |

## How it works

- Verifies the owned ROM (accepts a 512-byte copier header and strips it, like
  the host does).
- Clones the pinned tag with its pinned submodules, copies the ROM as
  `fzero.sfc`, runs `tools/regen.sh` to generate the recompiler, then builds
  `FZeroSNESRecomp` with CMake/SDL3. The build tree is kept so a version bump
  reuses the checkout.
- Unpacks the official bundle for the data that has no platform dependency:
  `mods/packs` with ready course caches, `assets/` (shaders, fonts, vehicle-pack
  sources), docs and licences. Its Windows binaries and DLLs are not used.
- Seeds `config.ini` (`SkipLauncher=1`, fullscreen) and `fzero-video.ini`
  (16:9, **4× HD Mode 7**, 240 FPS presentation, sharp pixels, rewind on). Both
  files are seeded only when absent; the in-game menu rewrites them and later
  changes survive.
- The launcher boots the binary with the ROM as argv[1], focuses DP-1 and uses
  the RTX OpenGL path. No AppImage, no FUSE, no Wine.

## Graphics and controls

The seeded ceiling is 16:9 at **3840×2160** on DP-1, **4× HD Mode 7** with
2-sample edge smoothing, presentation at **240 FPS** (the panel's refresh), sharp
filtering, and rewind at 50 snapshots every 15 frames. Shaders (CRT Soft, LCD
Grid, Sharp, Warm Composite or your own GLSL) are selectable in Settings;
Display Size, Fit and the other aspect modes stay available. The game's
simulation keeps its original timing; presentation FPS only smooths output.

The 8BitDo works through SDL with the same control layout as upstream (stick or
D-pad steer, A/RT accelerate, B/LT brake, shoulder buttons drift/lean, Start
pause, Select settings). Local VS assigns each pad/keyboard in **Controls**.
F7 opens save states, R rewinds, Alt+Enter toggles fullscreen.

## Limitations here

- **BS Deluxe is not in this build.** Its native module needs the external
  Deluxe patch archive and a second recompilation from the resulting cartridge.
  The CGP pack still supplies corrected BS courses.
- **CGP vehicle packs and stock rebalances stay off.** Upstream routes vehicle
  packs through the BS Deluxe preparation path, so a build without the Deluxe
  module refuses to start when they are enabled. The 85 courses, four stock
  machines, local VS and netplay are unaffected. Re-enable them only after
  building with BS Deluxe.
- Netplay reports that this build has no mod support; the bundled course packs
  still load locally. Online play was not exercised here.

## Verified here

The role builds the native binary, stages 237 MB of runtime data and reruns
`changed=0`. A bounded `bin/fzero` launch boots directly to the title screen in
fullscreen at 3840×2160, 16:9, with an `snes-hd` target of 3840×2160. Physical pad input, a full race, local 2–4
player and netplay were not exercised during this update.

## Updating

Bump `dg_fzero_version`, `dg_fzero_commit`, the submodule revisions, and the
data bundle version/hash in `group_vars/all/fzero_recomp.yml`, then re-run. The
role rebuilds only when the build marker or binary is missing; saves and menu
settings are preserved. Revert with `-e dg_fzero_revert=true`.