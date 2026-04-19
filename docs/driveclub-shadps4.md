# Driveclub shadPS4

Driveclub is configured as the only first-class shadPS4 target in this setup.

Current defaults:

```sh
DG_SHADPS4_TITLE_ID=CUSA00003
DG_PS4_ROM_ROOT=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4
DG_SHADPS4_GAME_DIR=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003
DG_PS4_FIRMWARE_MODULES=/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4-firmware/11.00_sys_modules
```

The canonical layout is a clean PS4 root containing the extracted game
directory only:

```text
$DG_PS4_ROM_ROOT/
  CUSA00003/
    eboot.bin
    ...
```

Do not treat raw `.pkg` files or Windows extraction tools in `$DG_PS4_ROM_ROOT`
as part of the normal runtime layout. The expected patch target is Driveclub
v1.28.

Runtime files:

- `$DG_BOX_HOME/.local/share/shadPS4/custom_configs/CUSA00003.toml`
- `$DG_BOX_HOME/.config/shadPS4/custom_configs/CUSA00003.toml`
- `$DG_BOX_HOME/.local/share/shadPS4/patches/Driveclub.xml`
- `$DG_BOX_HOME/.local/share/shadPS4/sys_modules/`
- `$DG_SHADPS4_QTLAUNCHER_ROOT/current/AppRun`
- `$DG_BOX_HOME/.local/share/shadPS4QtLauncher/versions/$DG_SHADPS4_CHANNEL/Shadps4-sdl.AppImage`

`./bin/dg shadps4` now handles the Linux end-user install path:

- downloads the pinned QtLauncher AppImage release
- extracts it under `$DG_SHADPS4_QTLAUNCHER_ROOT/releases/`
- points `$DG_SHADPS4_QTLAUNCHER_ROOT/current` at the extracted launcher
- downloads the current official shadPS4 AppImage for `$DG_SHADPS4_CHANNEL`
- writes `versions.json` and `cache.version` for QtLauncher
- refreshes the wrapper scripts, desktop launchers, and ES-DE PS4 entry

Known-good shadPS4 guidance collected from the current setup:

- use game version 1.28
- use the official `60 FPS with deltatime` patch (the alternative `60 FPS
  with fixed tickrate` patch is shipped but disabled; swap only if
  deltatime causes physics/sim glitches on your build)
- enable `readbacks`, disable `readbackLinearImages`, keep
  `readbacksMode = 0` (full)
- keep `copyGPUBuffers = false` and `directMemoryAccess = false` —
  both are experimental on current shadPS4 and cause crashes/regressions
  with Driveclub
- keep `patchShaders = true`
- window/internal size 1920×1920 @ `FullscreenMode = "Windowed"` + `Fullscreen = true`
  (workaround for shadPS4 issue #3945 — the conventional
  `FullscreenMode = "Borderless"` breaks with Immediate/No-VSync mode)
- **`vblankFrequency = 60`** — shadPS4 now enforces a 60 Hz minimum
  (PRs `be692ad` / `9520c11`). The old "halve vblank for deltatime"
  trick (`vblankFrequency = 30`) is obsolete; the Qt Launcher's
  **Vblank Divider** (Settings → Graphics → set to 2) is the
  replacement UI knob if you want the deltatime halving behavior.
  Most April 2026 community reports just leave divider at 1 (default).
- symlink PS4 11.00 sys_modules instead of copying them

Open upstream bugs to be aware of (no config workaround — just know they
exist):
- [#3315](https://github.com/shadps4-emu/shadPS4/issues/3315) loading-screen hang
- [#3346](https://github.com/shadps4-emu/shadPS4/issues/3346) CUSA00093 GPU driver reset
- [#3407](https://github.com/shadps4-emu/shadPS4/issues/3407) stuttering
- [#3210](https://github.com/shadps4-emu/shadPS4/issues/3210) crash during load
- [#3239](https://github.com/shadps4-emu/shadPS4/issues/3239) Intel iGPU crash
- Day races reportedly cleaner on AMD than NVIDIA as of April 2026

### Desktop entry: one tile, the Manager

There used to be three shadPS4 desktop entries (direct-to-Driveclub with
patch, direct-to-Driveclub without patch, and Qt Launcher GUI). All three
were confusing and the two direct-launch tiles are obsolete now that
shadPS4's Qt Launcher ("shadPS4 Manager") is the preferred entry point —
it lets you pick Driveclub or any other installed title, toggle patches
in its UI, install DLC `.pkg` files, and update the emulator itself.

Current state: **one** desktop entry, `gaming-shadps4-gui.desktop`
rendered as "shadPS4 Manager (on gaming)", which simply launches the
Qt Launcher. From there, right-click Driveclub and choose **Play** to
run the configured per-game toml. The `-g CUSA00003 -p ...` CLI flags
that the old tiles used are still supported by shadPS4 if you need
them, but the Manager route is more flexible and matches upstream's
intended workflow.

ES-DE should point to `$DG_PS4_ROM_ROOT/$DG_SHADPS4_TITLE_ID/eboot.bin`
and run `$DG_SHADPS4_BIN -g $DG_SHADPS4_GAME_ARG -p ...`, while the
system path stays anchored on `$DG_PS4_ROM_ROOT/$DG_SHADPS4_TITLE_ID`
for library discovery.

If Driveclub fails because of sysmodule behavior, the official patch XML also
has a `Run without sysmodules` option upstream. It is not enabled here because
it can remove text and slow boot. Treat it as a fallback after inspecting logs.

## DLC landscape

Driveclub shipped ~32 premium DLC packs + several free patches between
Oct 2014 and late 2016. The **v1.28 patch already includes every free
content drop** — Japan tracks (Jan 2015: Lake Shoji, Nakasendo + 3 more),
the final Oct 2016 update's 15 tracks sourced from Driveclub VR, bike
tracks integrated at the base-game level, and the Mega Fix community
tweaks the user overlaid on top of that (`data/databases/dc.tour`,
`liveryeditor/assets/assets.txt`, `newdata/vehicles.csv`).

Premium DLC that is **not** included in the patch:

| DLC category | Packs | Count | shadPS4 status |
|---|---|---:|---|
| **Tour packs** (unlock events) | Photo-Finish, Elements, Speed, Style, Performance, Unite In Speed, Up & Under, Final Shift | 8 | Boot but share the same readback/texture artifacts as base; races load |
| **Car packs** (monthly Oct 2014 – Jul 2015) | Ignition, Redline, Apex, Horsepower, Torque, Downforce, Turbocharged, Wombat Typhoon (Apr 1 2015 tribute), Finish Line (final pack, Mar 2016) | 9 | Same story — load, playable, not pristine |
| **Livery packs** | Monthly 2-per-month, themes like Motorsports, Stars & Stripes, Heritage, Citrus, etc. | ~80 | Safest category — pure asset overlays; load cleanly |

The **Driveclub Season Pass** bundled all the premium packs for ~€25.
There was never a "Complete Edition" disc release.

### Driveclub Bikes

Standalone PS4 product (**CUSA02010** US / **CUSA02311** EU), **not a DLC**
of CUSA00003. Separate shadPS4 install if you want it; compatibility is
worse than base Driveclub and the current `Driveclub.xml` patch XML does
not target it. `CUSA00064` / `CUSA00066` / `CUSA00879` in the patch XML's
TitleID list are region variants of the base game, not Bikes.

### Getting the DLC pkgs

Driveclub DLCs shipped only as individual PS4 Store packs — no single
"all-in-one" pkg exists. The user's existing base+patch are from scene
release groups; the same groups (GCMR, BlaZe, CPY, DUPLEX) produced DLC
pack repacks. Community mirrors live on archive.org, r/Driveclub, and
the shadPS4 Discord. No canonical download URL to hardcode here — the
user sources these on a case-by-case basis.

### Installing DLC on shadPS4

Qt Launcher → **File → Install .pkg** (supports multi-select). DLCs
land at:

```
$DG_BOX_HOME/.local/share/shadPS4/addcont/CUSA00003/<ENTITLEMENT_LABEL>/
```

Each pack extracts into its own entitlement-label subfolder (e.g.
`DCXTOURXXXXXX005`). The game auto-detects on next launch — no config
file edits needed. Install packs progressively (tours → cars →
liveries) so any shadPS4 crash can be bisected to a specific pack.

## Local PKG Tools

For future PS4 PKG debugging, keep the working `ShadPKG` build here:

```text
/mnt/data/distrobox/gaming/tools/ShadPKG
```

The working CLI binary is:

```text
/mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg
```

What worked:

- `shadpkg sfo-info blz-dc.pkg` correctly reads `CUSA00003`
- `shadpkg pfs-info blz-dc.pkg` and the v1.28 patch both work
- `shadpkg extract blz-dc.pkg ...` succeeds
- `shadpkg extract Driveclub.v1.28.PATCH.REPACK.PS4-GCMR.pkg ...` succeeds

What this proved:

- the base and patch PKGs are readable and extractable on Linux with `ShadPKG`
- the union of extracted base+patch files has nothing missing compared to the
  live `CUSA00003` tree
- the repeated `/app0/audio/fmodstudio/*.bank` open failures in shadPS4 are not
  explained by missing extracted filesystem files from the PKGs
- this points more toward shadPS4 runtime handling of Driveclub's packed data
  layout than a simple bad extraction

Discarded tool:

- `pkg_pfs_tool` was tested first, but it could not decrypt this retail PKG on
  this machine because the needed retail entry-key/passcode material was not
  available locally, so it was removed
