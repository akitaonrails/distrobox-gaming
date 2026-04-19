# Project Gotham Racing on Xenia Canary

PGR3 and PGR4 both run on Xenia Canary. PGR2 and PGR1 are Original Xbox
titles — use xemu for those, not Xenia. Xenia Canary has no OG Xbox
backwards-compat layer.

## Library layout

| Game | Title ID | Location | Emulator |
|---|---|---|---|
| Project Gotham Racing | — | `roms_heavy/xbox/Project Gotham Racing (USA).iso` | xemu |
| Project Gotham Racing 2 | — | `roms_heavy/xbox/Project Gotham Racing 2 (USA, Japan).iso` | xemu |
| **Project Gotham Racing 3** | `4D5307D1` | `roms_heavy/xbox360/Project Gotham Racing 3 (USA)...iso` | Xenia Canary |
| **Project Gotham Racing 4** | `4D5307F9` | `roms_heavy/xbox360/Project Gotham Racing 4 [RF].iso` | Xenia Canary |

## PGR3 — Playable

- **Title update:** `Project Gotham Racing 3 (USA) (v5)` on archive.org's
  `microsoft_xbox360_title-updates` collection. Install via
  **Xenia Manager → Manage → Install Content** (see `docs/xbox360-title-updates.md`).
- **Per-game settings** (community-optimized via `xenia-manager/optimized-settings`):
  - `framerate_limit = 0` + `vsync = false` — uncaps frame rate

No other per-game tweaks required.

## PGR4 — Playable with caveats

- **Title update:** `Project Gotham Racing 4 (World) (v2)` on archive.org.
  Install via XM.
- **Per-game settings** required to fix the game rendering dark (critical):
  - **On D3D12 (Windows):** `render_target_path_d3d12 = "rov"` (Rasterizer-Ordered Views)
  - **On Vulkan (Linux — our setup):** `render_target_path_vulkan = "fsi"`
    (Fragment Shader Interlock, Vulkan's equivalent of D3D12 ROV).
    Same mechanism used for FM4's magenta paint dither fix in this repo.
- **Framerate unlock** (optional): `framerate_limit = 0`, `vsync = false`
- **Known residual bugs** (no config fix — upstream Xenia limitations):
  - XMA-decoded menu audio degrades to garbage on NVIDIA setups
    ([xenia-canary #161](https://github.com/xenia-canary/xenia-canary/issues/161)).
  - Occasional crash when creating a profile in-game.
  - Broken brightness/gamma in menu UI. In-race rendering is clean with
    the `fsi` path enabled.

### Applying the Vulkan fsi path in Xenia Manager

After registering PGR4 and installing the TU:

1. In Xenia Manager, right-click PGR4 → **Configure** (or edit the
   per-game config toml directly at
   `Emulators/Xenia Canary/config/Project Gotham Racing 4.config.toml`).
2. Set under `[GPU]`:
   ```toml
   render_target_path_vulkan = "fsi"
   framerate_limit = 0
   vsync = false
   ```
3. Save. Launch from Xenia Manager (not directly from Xenia) — this repo's
   memory notes that Xenia Manager's per-game toml is the authoritative
   source; launching from Xenia itself will clobber the root toml but not
   the per-game one.

## References

- [Xenia Manager optimized settings — PGR3](https://github.com/xenia-manager/optimized-settings/blob/main/settings/4D5307D1.toml)
- [Xenia Manager optimized settings — PGR4](https://github.com/xenia-manager/optimized-settings/blob/main/settings/4D5307F9.toml)
- [xenia-canary issue #161 — PGR4 audio/brightness](https://github.com/xenia-canary/xenia-canary/issues/161)
- [xenia-project game-compatibility #180 — PGR4 status](https://github.com/xenia-project/game-compatibility/issues/180)
- [archive.org TU collection](https://archive.org/details/microsoft_xbox360_title-updates)
