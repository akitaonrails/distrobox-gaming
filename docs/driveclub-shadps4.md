# Driveclub on shadPS4

Driveclub (CUSA00003) is the primary shadPS4 target in this setup. It
**does work** — boots past all init, loads UI, goes ingame — but the path
is non-obvious and every Driveclub-specific walkthrough on the internet
omits at least one step. This doc captures the **exact working recipe**
and the **traps we hit** so we don't re-chase them next session.

## Working configuration (verified Apr 2026)

- shadPS4 **main** branch — commit `90b75ea` or later, stock AppImage from
  the repo CI. Do NOT use the `fontlib` PR #3772 branch; main already has
  font HLE merged (PR #2761, Nov 2025) and is closer to what community
  YouTube / DSOGaming / KitGuru footage uses.
- Game layout: **Driveclub v1.00 only** — original base PKG (e.g. BlaZe
  scene release) extracted via **ShadPKG** then **unpacked via DriveClubFS**
  so every `.ndx`/`.dat` archive becomes loose files on disk. No v1.28
  patch content, no hybrid, no mixed eboot.
- Per-game config at `custom_configs/CUSA00003.json` (JSON, not TOML —
  see gotcha below). Key settings:
  - `"neo_mode": false` (Driveclub has no Pro patch)
  - `"readbacks_mode": 0` (full readbacks — **mandatory**, issue #3210)
  - `"readback_linear_images_enabled": false`
  - `"patch_shaders": true`
  - `"copy_gpu_buffers": false`, `"direct_memory_access_enabled": false`
  - `"vblank_frequency": 60`
  - `"full_screen_mode": "Windowed"`, `"full_screen": true`
  - `"window_width": 1920`, `"window_height": 1080`
  - `"internal_screen_width": 1920`, `"internal_screen_height": 1080`
  - `"gpu_id": 0` (pick the NVIDIA dGPU explicitly — see controller gotcha)
- Global config `config.json` must also set `"readbacks_mode": 0` in the
  `GPU` section (the per-game config layers on top; both coherent).
- `Driveclub.xml` patch XML **disabled** — it targets v1.28 eboot and
  corrupts v1.00 if applied. We rename it to `.disabled-for-v1.0`.
- Controller: shadPS4's SDL needs hidapi hints to detect the 8BitDo
  Ultimate 2 (and likely others). Wrapper script exports
  `SDL_JOYSTICK_HIDAPI=1` plus platform-specific HIDAPI toggles.
  Plug controller in BEFORE launching the Qt Launcher.

Result: Driveclub loads, intros play, menus work, races start,
controller input works for accel/brake/steer.

## Install recipe

### 1. Extract the base PKG to the expected layout

```sh
# Base v1.00 PKG lives e.g. under $DG_PS4_ROM_ROOT/Driveclub.PS4-BlaZe/blz-dc.pkg
distrobox enter gaming -- /mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg extract \
    /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/Driveclub.PS4-BlaZe/blz-dc.pkg \
    /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003
```

This gives you `eboot.bin`, `game.ndx`, a bunch of `gameNNN.dat` (packed
archives), `libfmod.prx`, `libfmodstudio.prx`, `sce_module/`, `sce_sys/`.
But the actual game **assets** (audio banks, UI, cars, tracks) are
packed inside the `.dat` files via Evolution Studios' custom archive
format — shadPS4 does NOT read through that format.

### 2. Unpack `.ndx` / `.dat` with DriveClubFS

Nenkai's DriveClubFS is the only public tool that walks Evolution's
`.ndx` index and decompresses the `gameNNN.dat` archives into named
loose files. Requires .NET 10 SDK (Arch package `dotnet-sdk`).

```sh
cd /mnt/data/distrobox/gaming/tools
git clone https://github.com/Nenkai/DriveClubFS
# Source targets net9.0; we only have net8/net10. Retarget:
sed -i 's|<TargetFramework>net9.0</TargetFramework>|<TargetFramework>net10.0</TargetFramework>|' \
    DriveClubFS/DriveClubFS/DriveClubFS.csproj

distrobox enter gaming -- dotnet build -c Release DriveClubFS/DriveClubFS/DriveClubFS.csproj

distrobox enter gaming -- dotnet \
    /mnt/data/distrobox/gaming/tools/DriveClubFS/DriveClubFS/bin/Release/net10.0/DriveClubFS.dll \
    unpack-all \
    -i "/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003" \
    -o "/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003/extracted" \
    --skip-verifying-checksum
```

Expected: **5343 files, ~25 GB**, including `audio/fmodstudio/masterbank.bank`
which is what the FMOD retry loop was looking for. Then flatten the
`extracted/` dir contents up to the game root:

```sh
cd /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003
mv extracted/* .
rmdir extracted
```

You can delete the `gameNNN.dat` + `game.ndx` files afterward to save
~16 GB — shadPS4 reads only the loose files.

### 3. Per-game JSON config

File: `$DG_BOX_HOME/.local/share/shadPS4/custom_configs/CUSA00003.json`

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

Also delete any stale `CUSA00003.toml` from either `.config/shadPS4/custom_configs/`
or `.local/share/shadPS4/custom_configs/` — shadPS4 main ignores TOML
silently and will never log a complaint.

### 4. Controller wrapper

shadPS4's Qt Launcher calls `Shadps4-sdl.AppImage`; wrap it so SDL
uses hidapi (otherwise `TryOpenSDLControllers: 0 controllers` even
with a working 8BitDo Ultimate 2 or DualShock). In the launcher's
version dir:

```sh
VERDIR=$DG_BOX_HOME/.local/share/shadPS4QtLauncher/versions/main-<date>
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

Then point `~/.local/share/shadPS4QtLauncher/qt_ui.ini`'s
`versionSelected=` at that wrapper path.

Plug the controller in **before** opening Qt Launcher. If it wasn't
detected, unplug, relaunch the Qt Launcher, plug in again — hotplug
works inside a running game.

### 5. Desktop entry

One tile: `gaming-shadps4-gui.desktop` (renders as "shadPS4 Manager (on
gaming)"). Launches the Qt Launcher; user picks Driveclub from its game
list. Old direct-Driveclub tiles were deleted.

## Dead ends — what did NOT work

Logged so we don't repeat them.

| Dead end | Why it doesn't work |
|---|---|
| **v1.28 patch on a v1.00 loose-file tree** | Patch eboot expects v1.28-only content files that DriveClubFS can't extract from the v1.28 patch PKG's `.dat` archives. DriveClubFS (v1.1.0 checked) crashes at file 12/8018 with `EndOfStreamException` on the merged tree. Pure v1.00 or nothing. |
| **`Driveclub.xml` 60fps patch on v1.00 eboot** | The patch's byte offsets target v1.28 eboot. Applied to v1.00 it corrupts live code. Disable the XML (rename to `.disabled-for-v1.0`). The game runs at 30 FPS native without it; accept the tradeoff or source a v1.00-native 60fps patch. |
| **Dropping raw STFS-style file in the content root** | Wrong emulator — that's Xenia. Doesn't apply here. |
| **TOML per-game config** | shadPS4 main migrated to JSON in late 2025 (`emulator_settings.cpp`). TOML files are silently ignored. Always use `.json`. No deprecation warning logged. |
| **fontlib PR #3772 branch fork** | Was a 2-3 hour rabbit hole. Fontlib's sceFont HLE was already merged to main via PR #2761 (Nov 2025). The fork was orthogonal and added config-format complexity. Use main. |
| **Dumping PS4 system fonts from `PS4UPDATE.PUP`** | Retail PUPs are AES-128 encrypted with keys fused into PS4 Secure Boot hardware. No Linux-only decryption exists; every public `pup_decrypt` tool is a PS4 homebrew payload requiring a jailbroken console. Tried `psxhax.com` guide — same requirement. Not feasible. |
| **Rename-substituting Adobe Source Han Sans as PS4 fonts** | Set up 18 files matching `SST-*.otf`, `SSTCC-*.OTF`, `SSTJpPro-*.otf`, `DFHEI5-SONY.ttf`, `SCEPS4Yoongd-*.otf` names. fontlib loaded them but still crashed at `0x29` — turned out font dumps weren't the blocker on main at all. |
| **libtbb HLE / shadPS4 fork search** | 3-hour red-herring. `Returning zero to 0x80cee039d x29` stub calls looked like unresolved libtbb imports. They're harmless — every shadPS4 game sees them. Not the crash cause. |
| **Qt Launcher "Check for Updates"** | Hits unauthenticated GitHub API, rate-limited to 60/hour. Produces a scary-looking "server replied: ..." dialog at launch that has nothing to do with running games. Disable `checkForUpdates` and `checkOnStartup` in `qt_ui.ini`. |
| **vkBasalt chained effects (liftGammaGain + vibrance + CAS)** | On NVIDIA + Vulkan 1.4 (RTX 5090, April 2026), this chain produces a blown-out white image with noise — probably uninitialized intermediate buffer. Single-effect may work; haven't tested. |
| **Hyprland `decoration:screen_shader` empty string** | Setting the keyword to `""` (empty) makes Hyprland try to load `""` as a file path and log "shader path not found" every frame. Must set to the literal `[[EMPTY]]` marker to truly unset. `hyprctl reload` also fixes it. |
| **`gamescope` for SDR brightness/saturation** | gamescope's color options are HDR-focused (`--hdr-itm-enabled`, etc.). No native SDR vibrance knob. |
| **nvidia-settings Digital Vibrance on Wayland** | X11 only. Doesn't exist on Wayland sessions. Hyprland's `screen_shader` is the Wayland-friendly equivalent but has its own pitfalls. |
| **`apply_title_update = false` in FM3's Xenia config cross-contaminating FH2** | Different emulator (Xenia) but same class of bug. Documented in `feedback_xenia_config_flow.md`. |

## Key insight about the FMOD loop

The `/app0/audio/fmodstudio/masterbank.bank failed, file does not exist`
retry loop that stops boot **is about Evolution's packed archive format**,
not about FMOD, not about Fios2, not about libtbb. The .bank file literally
doesn't exist on disk because it's inside a `gameNNN.dat` archive that
shadPS4's VFS can't read.

**The only fix is DriveClubFS**. It's the tool community setups use
(even when their guides don't say so). Every other diagnosis we tried
(shadPS4 Fios2 gap, font HLE, libtbb, etc.) was a misreading of the
same root cause.

## Image looks dark/desaturated — known

Driveclub was tonemapped on PS4 for HDR TV output. shadPS4 outputs SDR
by default; the dynamic range compression makes everything look dim. On
our Wayland/Hyprland setup:

- nvidia-settings Digital Vibrance is not an option (X11-only)
- vkBasalt's chained shaders broke the image on RTX 5090 / Vulkan 1.4
- Hyprland `screen_shader` works but if you pass an empty string to
  unset it later, Hyprland logs "shader path not found" errors every
  frame until `hyprctl reload`

Conclusion: **accept the dim look for now**. This is what the community
footage actually looks like; it's the state of SDR Driveclub emulation
in 2026. Future shadPS4 releases may add a built-in HDR output or
ShadeBoost-style post-process.

## Known upstream bugs (no config fix)

- [shadPS4 #3315](https://github.com/shadps4-emu/shadPS4/issues/3315) loading-screen hang (closed)
- [shadPS4 #3210](https://github.com/shadps4-emu/shadPS4/issues/3210) crash during load — documents `readbacks = true` as the fix
- [shadPS4 #3346](https://github.com/shadps4-emu/shadPS4/issues/3346) CUSA00093 GPU driver reset
- [shadPS4 #3407](https://github.com/shadps4-emu/shadPS4/issues/3407) stuttering
- [shadPS4 #3239](https://github.com/shadps4-emu/shadPS4/issues/3239) Intel iGPU crash
- [shadPS4 #4276](https://github.com/shadps4-emu/shadPS4/pull/4276) Driveclub input regression fix (merged Apr 19 2026)

Day races reportedly cleaner on AMD than NVIDIA. Our setup (RTX 5090)
works but gets some texture dither artifacts on shiny surfaces.

## DLC landscape

Driveclub shipped ~32 premium DLC packs between Oct 2014 and Mar 2016.
`v1.28` patch already includes every free drop (Japan tracks, VR-sourced
tracks from the Oct 2016 final update). Premium DLC NOT included:

| Category | Count | shadPS4 status |
|---|---:|---|
| Tour packs | 8 | Boot but share the same rendering artifacts as base |
| Car packs | 9 | Same |
| Livery packs | ~80 | Safest — asset overlays load cleanly |

Since this repo uses **v1.00 base only** (for DriveClubFS compatibility),
none of the above is currently installed. Installing DLC PKGs onto a
v1.00 install may or may not work — untested. The Qt Launcher's
**File → Install .pkg** (multi-select supported) routes DLCs to
`$DG_BOX_HOME/.local/share/shadPS4/addcont/CUSA00003/<ENTITLEMENT>/`.

### Driveclub Bikes

Standalone product: **CUSA02010** (US) / **CUSA02311** (EU). Not a DLC
of CUSA00003. Separate install if you want it.

## Files and paths quick reference

```
# Game install
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003/
  eboot.bin                       (v1.00, md5 02d68ebe...)
  eboot.bin.v128                  (backup if you ever want to try patched route)
  audio/fmodstudio/masterbank.bank (from DriveClubFS)
  + 5342 other loose files
  + gameNNN.dat / game.ndx        (safe to delete after extraction)

# shadPS4 configs
~/.local/share/shadPS4/config.json                          # global
~/.local/share/shadPS4/custom_configs/CUSA00003.json        # per-game override
~/.local/share/shadPS4/patches/Driveclub.xml.disabled-for-v1.0

# Qt Launcher version
~/.local/share/shadPS4QtLauncher/versions/main-<date>/
  Shadps4-sdl.AppImage            # wrapper with SDL hidapi hints
  Shadps4-sdl.real.AppImage       # actual AppImage from CI
~/.local/share/shadPS4QtLauncher/qt_ui.ini                  # versionSelected, checkForUpdates=false

# Tools
/mnt/data/distrobox/gaming/tools/DriveClubFS/
/mnt/data/distrobox/gaming/tools/ShadPKG/
```

## References

- [DriveClubFS by Nenkai](https://github.com/Nenkai/DriveClubFS)
- [shadPS4 main](https://github.com/shadps4-emu/shadPS4)
- [shadPS4 issue #3210 — Driveclub readbacks fix](https://github.com/shadps4-emu/shadPS4/issues/3210)
- [shadPS4 compat tracker #710 — CUSA00003 Linux status-ingame](https://github.com/shadps4-compatibility/shadps4-game-compatibility/issues/710)
- [shadPS4 PR #4276 — Driveclub input fix](https://github.com/shadps4-emu/shadPS4/pull/4276)
- [Evolution Studios .ndx/.dat format (010 templates)](https://github.com/Nenkai/010GameTemplates/tree/main/Evolution%20Studios/DriveClub)
