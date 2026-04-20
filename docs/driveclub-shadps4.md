# Driveclub on shadPS4

Driveclub (CUSA00003) is the primary shadPS4 target in this setup. The
current working install is **v1.28**, boots + plays + controller works,
all DLC-accessible content unlocked, night scenes rendering correctly.
Deep-dive investigation notes live in a separate fork doc — see
`~/Projects/shadPS4/docs/driveclub-v128-investigation.md` for the
phase-by-phase engineering log that produced this setup, including
dead ends, misdiagnoses, and the local fork patches shipped.

This doc is the **operational runbook** for reproducing the setup on the
gaming distrobox. Keep in sync with the investigation doc when anything
material changes.

## Corrections to earlier versions of this doc

- **"DriveClubFS 1.1.0 crashes at file 12/8018" did not reproduce** on the
  properly-staged v1.28 tree. 8018/8018 files extracted cleanly (~47 GB,
  exit 0). The earlier failure was either a transient issue or a
  badly-staged input. No fork patch for DriveClubFS is needed.
- **v1.28 is now the working base**, not v1.00. Earlier guidance "v1.00
  only because DriveClubFS can't handle v1.28" is wrong.
- The **60 FPS patch is disabled** — not because its offsets don't match
  v1.00, but because shadPS4 doesn't scale the game's internal fixed
  timestep. Patched to 60 fps the game renders smoothly but the
  simulation runs at half real-time ("slow-motion smooth playback").
  Disabled → 30 fps at correct wall-clock speed, matches stock PS4 base.
- The **dim daytime image** is Driveclub's own design intent (PS4
  firmware 4.0's display-calibration pipeline doesn't exist on our side),
  not an emulator bug. The investigation doc's Phase 2 + Phase 5 walk
  through the tonemap/exposure/ACES/auto-exposure attempts, all rolled
  back. The in-game brightness slider IS wired (fires
  `sceVideoOutAdjustColor` → `pp_settings.gamma`) and gives the user
  real control.

## Working install — v1.28

### Game tree

```
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/
├── CUSA00003/                            # live: v1.28 eboot + unpacked loose files (~47 GB)
├── CUSA00003.v100-working-backup/        # one-command rollback to v1.00 if v1.28 regresses
├── CUSA00003-v128-test/                  # DriveClubFS input staging (re-runnable if loose tree needs regen)
└── Driveclub.v1.28.PATCH.REPACK.PS4-GCMR.pkg
```

### Install / update recipe (from the investigation doc, summarized)

```sh
cd /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4

# 1. Extract v1.28 PKG to staging. Cumulative patch → eboot, game.ndx,
#    ~41 high-index .dat files, sce_module/, sce_companion_httpd/,
#    partial sce_sys/about/. **Notably missing**: param.sfo, disc_info.dat,
#    keystone — cumulative patches rely on base-install metadata.
/mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg extract \
    -i /mnt/terachad/.../Driveclub.v1.28.PATCH.REPACK.PS4-GCMR.pkg \
    -o /mnt/terachad/.../CUSA00003-v128-test

# 2. Symlink v1.00's low-numbered .dat files into the v1.28 staging dir
#    so DriveClubFS sees the full set (v1.28 index references both).
cd CUSA00003-v128-test
for f in ../CUSA00003.v100-working-backup/game*.dat; do
  ln -s "$f" "$(basename "$f")"
done

# 3. DriveClubFS unpack (v1.28 index = 8018 files, ~47 GB loose).
dotnet ~/Projects/DriveClubFS/DriveClubFS/bin/Release/net10.0/DriveClubFS.dll \
    unpack-all \
    -i /mnt/terachad/.../CUSA00003-v128-test \
    -o /mnt/terachad/.../CUSA00003-v128-test-out \
    --skip-verifying-checksum

# 4. Swap into place; keep v1.00 as backup.
cd /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4
mv CUSA00003 CUSA00003.v100-working-backup
mkdir CUSA00003
mv CUSA00003-v128-test-out/* CUSA00003/
rmdir CUSA00003-v128-test-out

# 5. Copy v1.28 metadata on top (loose files win for content).
cd CUSA00003-v128-test
for f in eboot.bin game.ndx *.prx *.plt; do
  [ -e "$f" ] && cp -a "$f" ../CUSA00003/
done
for d in sce_sys sce_module sce_companion_httpd; do
  [ -d "$d" ] && cp -a "$d" ../CUSA00003/
done

# 6. CRITICAL: restore base metadata from v1.00 backup (see gotcha below).
cd ../CUSA00003/sce_sys
for f in param.sfo disc_info.dat keystone; do
  [ ! -f "$f" ] && cp -a "../../CUSA00003.v100-working-backup/sce_sys/$f" .
done

# 7. Do NOT re-enable Driveclub.xml for the 60 fps patch (see below).
```

### The `sce_sys/param.sfo` gotcha

v1.28 is a **CUMULATIVE_PATCH** PKG. ShadPKG's extraction gives you
`sce_sys/about/right.sprx` and not much else — base metadata
(param.sfo, disc_info.dat, keystone) is **not re-shipped** because a
real PS4 already has them from the base install.

If you naively overlay v1.28's `sce_sys/` onto the new install, the
result has `about/right.sprx` but no `param.sfo`. shadPS4 loads the
eboot, applies patches if any, boots the game, but the game's internal
"am I running v1.28? what content is unlocked?" checks silently fall
back to "not yet released → download required" because there's no
APP_VER to compare. Symptom: **all premium content locked, asking to
download**, even though the v1.28 eboot is running.

The v1.00 backup's `param.sfo` works as-is — already has `APP_VER = 01.28`
and `VERSION = 01.00` (base VERSION stays at 01.00 forever, APP_VER
reflects whatever patch is installed).

`npbind.dat` is absent in both our v1.00 backup and the v1.28 patch
output. Only needed for premium DLC entitlement verification; free-update
content and base game don't require it.

## shadPS4 configuration (required)

### Global — `~/.local/share/shadPS4/config.json`

```jsonc
{
  "GPU": {
    "readbacks_mode": 0          // full readbacks — issue #3210 documented fix
  },
  "Vulkan": {
    "pipeline_cache_enabled": true,   // <<< manual change — kills first-launch shader compile stalls
    "pipeline_cache_archived": false  // fast load over small disk footprint
  }
}
```

The pipeline cache change is the Phase 1 fix from the investigation doc:
without it every cold launch re-compiles ~864 shaders + ~590 pipelines
and the menus animate at crawl speed on first use. Enabling persists the
cache to disk; second launch onwards replays instantly.

Backup of the pre-change config preserved as
`config.json.bak-before-pipeline-cache` next to the live file.

### Per-game — `~/.local/share/shadPS4/custom_configs/CUSA00003.json`

```json
{
  "General": { "neo_mode": false },
  "GPU": {
    "full_screen": true,
    "full_screen_mode": "Windowed",
    "window_width": 1920,
    "window_height": 1080,
    "internal_screen_width": 1920,
    "internal_screen_height": 1080,
    "patch_shaders": true,
    "readback_linear_images_enabled": false,
    "readbacks_mode": 0,
    "copy_gpu_buffers": false,
    "direct_memory_access_enabled": false,
    "vblank_frequency": 60
  },
  "Vulkan": {
    "gpu_id": 0,
    "vkvalidation_core_enabled": false,
    "vkvalidation_enabled": false,
    "vkvalidation_gpu_enabled": false,
    "vkvalidation_sync_enabled": false
  }
}
```

Delete any stale `.toml` from either `.config/shadPS4/custom_configs/` or
`.local/share/shadPS4/custom_configs/` — shadPS4 migrated to JSON silently,
TOML files are ignored without a deprecation warning.

### Controller wrapper (required for hotplug detection)

shadPS4's SDL init reports `TryOpenSDLControllers: 0` on first run even
with the 8BitDo Ultimate 2 / DualShock already connected. Wrap the
AppImage to force SDL's hidapi backend:

```sh
VERDIR=$DG_BOX_HOME/.local/share/shadPS4QtLauncher/versions/<build-name>
mv "$VERDIR/Shadps4-sdl.AppImage" "$VERDIR/Shadps4-sdl.real.AppImage"
cat > "$VERDIR/Shadps4-sdl.AppImage" << 'EOF'
#!/usr/bin/env sh
export SDL_JOYSTICK_HIDAPI=1
export SDL_JOYSTICK_HIDAPI_PS4=1
export SDL_JOYSTICK_HIDAPI_PS5=1
export SDL_JOYSTICK_HIDAPI_XBOX=1
export SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1
exec "$(dirname "$0")/Shadps4-sdl.real.AppImage" "$@"
EOF
chmod +x "$VERDIR/Shadps4-sdl.AppImage"
```

Connect the controller before opening Qt Launcher. Hotplug works once
the game is running.

### Qt Launcher polling

Turn off the GitHub API polling at startup — produces a scary-looking
"Error transferring releases" dialog when rate-limited (unauthenticated
API = 60 requests/hour):

```ini
# ~/.local/share/shadPS4QtLauncher/qt_ui.ini
[general_settings]
checkForUpdates=false
checkOnStartup=false
```

## 60 FPS patch — don't enable

`Driveclub.xml` in `~/.local/share/shadPS4/patches/` ships with two 60 FPS
patch blocks. Leave them disabled. The patches rewrite the render rate
but **not** the game's internal fixed-timestep logic rate. On real PS4
Pro, the engine reconciles the mismatch internally; shadPS4 doesn't.

Symptom if enabled: game appears to run smoothly at 60 fps but cars
accelerate in slow-motion, lap times don't advance at real speed. Disable
→ 30 fps at correct wall-clock speed, matches stock PS4 base console.

To disable cleanly:

```sh
mv ~/.local/share/shadPS4/patches/Driveclub.xml \
   ~/.local/share/shadPS4/patches/Driveclub.xml.disabled-for-v1.0
```

The filename suffix is historical — at the time we thought the issue was
v1.00 eboot offset mismatch; it's actually the timestep mismatch and
applies to both v1.00 and v1.28. Rename pattern kept to avoid churn.

Long-term fix options (out of scope): patch the game to also scale the
internal timestep; implement frame interpolation host-side; both are
substantial work that isn't queued.

## Night scenes — known upstream gap

Driveclub's forward+ lighting renders geometry into a 4x MSAA D32Sfloat
depth target then binds that depth aspect as a 1-sample
R32G32B32A32Sfloat sampler2D for SSAO, soft particles, and volumetric
headlights. **shadPS4 upstream nightly has no path for this combination**
in `TextureCache::ResolveDepthOverlap` — the fallback `else` branch
`FreeImage`-s the cached MSAA depth and returns an uninitialised 1-sample
color image. Downstream reads garbage.

**Symptom**: night tracks render near-pure black — HUD visible, no
headlights, no track surface, no AI car lights. Daytime scenes look
"only dim" because ambient+sun still lights the material pass, but
subtle depth-dependent effects are silently broken.

**Fix shape** (`ReinterpretMsDepthAsColor` + fragment shader + wiring in
`ResolveDepthOverlap`) is described in detail in
`~/Projects/shadPS4/docs/driveclub-v128-investigation.md` Phase 4.
Upstream-candidate PR shape — clean, bounded, symmetric with the existing
`ReinterpretColorAsMsDepth` path. Until merged, run a build that carries
the fix locally (e.g. the investigation doc's `gamma-debug` branch)
from a Manager-visible version entry. The distrobox's default stays on
upstream **nightly** — once upstream ships the fix, no local divergence
is needed here.

## Dim image — accepted as-is

Owners tried exhaustively on `gamma-debug`: static gamma lift, static
linear boost, per-channel ACES, luma-preserving ACES, scene-aware
auto-exposure (peak+mean), shadow-lift curves, peak-aware clamping,
mean-aware headroom, hysteresis adaptation. Each fixed one case by
breaking another — menus would blow out when dark scenes got lifted, or
dark scenes stayed dim when menus were tamed.

Root diagnosis after adding `SHADPS4_PP_BYPASS=1`: **Driveclub's raw
output is already correct.** The 5-second "dim pocket" at race start
that triggered the whole investigation is a **game-side cinematic
fade-in VFX**, not something post-process can fix (can't multiply
visibility into a `vec3(0)` reveal).

The final shader in `gamma-debug` branch is **standard sRGB encode +
4×4 Bayer dither**. No exposure multiplier, no tonemap, no auto-exposure,
no bypass flag (nothing to bypass).

The **in-game brightness slider** does work — game calls
`sceVideoOutAdjustColor`, the shader responds. Tops out before matching
an HDR reference, but it's the honest answer.

Lesson kept in the investigation doc: **when "the image looks wrong"
is the bug, the first diagnostic should be a bypass path that shows
raw game output.** If bypass looks right, the emulator post-process is
mangling the signal; keep your hands off the tonemap.

If you want to try display-side color correction, the gotchas we
already hit are captured in the investigation doc's dead-end section —
worth reading before trying vkBasalt or Hyprland `screen_shader` tricks.

## DLC landscape

Driveclub shipped ~32 premium DLC packs between Oct 2014 and Mar 2016.
The v1.28 patch already includes every free drop (Japan tracks, the
Oct 2016 VR-sourced tracks, Bike tracks). Premium DLC NOT included:

| Category | Count | shadPS4 status |
|---|---:|---|
| Tour packs | 8 | Boot but share same rendering artifacts as base |
| Car packs | 9 | Same |
| Livery packs | ~80 | Safest — asset overlays load cleanly |

Install DLC PKGs via Qt Launcher → **File → Install .pkg** (multi-select).
Lands at `~/.local/share/shadPS4/addcont/CUSA00003/<ENTITLEMENT>/`.

### Driveclub Bikes

Standalone product: **CUSA02010** (US) / **CUSA02311** (EU). Not a DLC
of CUSA00003.

## Files / paths quick reference

```
# Game install (v1.28 live)
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003/
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003.v100-working-backup/
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003-v128-test/

# shadPS4 configs
~/.local/share/shadPS4/config.json                    # pipeline_cache_enabled=true
~/.local/share/shadPS4/config.json.bak-before-pipeline-cache
~/.local/share/shadPS4/custom_configs/CUSA00003.json  # per-game
~/.local/share/shadPS4/patches/Driveclub.xml.disabled-for-v1.0
~/.local/share/shadPS4/log/shad_log.txt

# Qt Launcher versions (distrobox default: whichever nightly QtLauncher auto-fetches)
~/.local/share/shadPS4QtLauncher/versions/Pre-release/           # stock upstream nightly (DEFAULT)
~/.local/share/shadPS4QtLauncher/versions/gamma-debug-2026-04-20/ # optional — investigation build w/ MSAA depth fix

# Tools
/mnt/data/distrobox/gaming/tools/DriveClubFS/
/mnt/data/distrobox/gaming/tools/ShadPKG/

# Fork source
~/Projects/shadPS4                         # akitaonrails/shadPS4 (gamma-debug branch)
~/Projects/DriveClubFS                     # akitaonrails/DriveClubFS (stewardship fork)
~/Projects/shadPS4/docs/driveclub-v128-investigation.md   # the engineering log
```

## References

- **`~/Projects/shadPS4/docs/driveclub-v128-investigation.md`** — the
  detailed engineering log: every phase, misdiagnosis, dead end, and fix
  shape. Read this if you're touching anything here.
- [DriveClubFS by Nenkai](https://github.com/Nenkai/DriveClubFS)
- [shadPS4 main](https://github.com/shadps4-emu/shadPS4)
- [shadPS4 issue #3210 — Driveclub readbacks fix](https://github.com/shadps4-emu/shadPS4/issues/3210)
- [shadPS4 compat tracker #710 — CUSA00003 Linux status-ingame](https://github.com/shadps4-compatibility/shadps4-game-compatibility/issues/710)
- [shadPS4 PR #4276 — Driveclub input fix](https://github.com/shadps4-emu/shadPS4/pull/4276)
- [Evolution Studios .ndx/.dat format (010 templates)](https://github.com/Nenkai/010GameTemplates/tree/main/Evolution%20Studios/DriveClub)
