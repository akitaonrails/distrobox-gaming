# Distrobox Gaming Container — Replication Prompts

Historical archive: these prompts document the original interactive setup and
contain stale details. Use `README.md` and the numbered scripts as the current
source of truth for rebuilds.

Step-by-step prompts to replicate the gaming distrobox setup from scratch.
Each prompt is self-contained and can be pasted into a new Claude Code session.
Full reference: `arch-distrobox.md` in this same directory.

---

## Phase 1: Container creation (host side)

### Prompt 1 — Host prep + container create

```
Install game-devices-udev from AUR on the host (preserves controller udev rules
when host Steam is removed later). Then create a distrobox gaming container with:
- name: gaming
- image: archlinux:latest
- --nvidia for GPU passthrough
- separate home at /mnt/data/distrobox/gaming
- bind mount /mnt/data/steam (rw) for the Steam library
- bind mount /mnt/terachad/Emulators (ro) for ROMs and BIOS files

Commands:
  yay -S game-devices-udev
  sudo udevadm control --reload && sudo udevadm trigger
  mkdir -p /mnt/data/distrobox/gaming
  distrobox create --name gaming --image archlinux:latest --nvidia \
    --home /mnt/data/distrobox/gaming \
    --volume /mnt/data/steam:/mnt/data/steam \
    --volume /mnt/terachad/Emulators:/mnt/terachad/Emulators:ro
  distrobox enter gaming
```

---

## Phase 2: Container bootstrap (fixes for archlinux:latest quirks)

### Prompt 2 — Fix sudo, multilib, nvidia-utils

```
The distrobox gaming container is created. I need you to fix three known issues
with archlinux:latest in distrobox, IN THIS ORDER. Use "docker exec -u root gaming"
for operations that need container root.

1. PASSWORDLESS SUDO: /etc/sudoers.d/sudoers ships with bad permissions (0644)
   and %wheel ALL=(ALL:ALL) ALL without NOPASSWD. Create
   /etc/sudoers.d/zz-distrobox-gaming-nopasswd with NOPASSWD rule (zz- prefix so
   it loads AFTER the wheel rule alphabetically). Fix sudoers perms to 0440.
   Verify with: distrobox enter gaming -- sudo -n whoami

2. MULTILIB: The image has NO [multilib] section in pacman.conf (not even
   commented). Also has a stray [options] on the last line. Delete the trailing
   [options] and append [multilib] with Include = /etc/pacman.d/mirrorlist.
   Then pacman -Syu.

3. NVIDIA-UTILS DUMMY: --nvidia bind-mounts host nvidia libs read-only into the
   container. Any pacman install that depends on nvidia-utils will fail with
   file conflicts. Build a local dummy PKGBUILD that provides=(nvidia-utils=VERSION
   vulkan-driver opengl-driver nvidia-libgl) and conflicts=(nvidia-libgl nvidia-utils).
   Get the version from: nvidia-smi --query-gpu=driver_version --format=csv,noheader
   on the host. Also install yay-bin as the AUR helper.

See arch-distrobox.md §1 "First-run setup" for exact commands.
```

---

## Phase 3: Steam + gaming base

### Prompt 3 — Install Steam and gaming stack

```
Inside the distrobox gaming container, install the base gaming stack from extras:
  steam lutris gamescope mangohud protontricks mesa-utils vulkan-tools \
  pipewire-pulse

Note: pipewire-pulse is CRITICAL. Without it, PulseAudio-based audio
(used by Flycast, RPCS3, and many games via SDL2) is silent. The
container shares the host's PipeWire socket but needs pipewire-pulse
to bridge PulseAudio clients to it. Without audio sync, emulators
like Flycast also lose frame timing and run at uncapped speed.

Then export Steam to the host launcher:
  distrobox-export --app steam

Also create /etc/profile.d/gaming-wayland.sh with these env vars:
  QT_QPA_PLATFORM="wayland;xcb"
  QT_WAYLAND_DISABLE_WINDOWDECORATION=0
  GDK_BACKEND="wayland,x11"
  MOZ_ENABLE_WAYLAND=1
  ELECTRON_OZONE_PLATFORM_HINT=auto
  _JAVA_AWT_WM_NONREPARENTING=1
  QT_QPA_PLATFORMTHEME=qt6ct
  QT_STYLE_OVERRIDE=kvantum
  GTK_THEME=Tokyonight-Dark
  ICON_THEME=Papirus-Dark

Do NOT set SDL_VIDEODRIVER (breaks SDL2 games).
```

---

## Phase 4: Emulators — repo packages

### Prompt 4 — Install extras-repo emulators

```
Inside the distrobox gaming container, install all emulators available from
the Arch extra repo:

  retroarch libretro-core-info
  libretro-bsnes libretro-mesen libretro-mgba libretro-dolphin
  libretro-beetle-psx-hw libretro-beetle-pce
  libretro-genesis-plus-gx libretro-snes9x libretro-picodrive
  libretro-mame libretro-flycast libretro-ppsspp
  libretro-desmume libretro-melonds libretro-mupen64plus-next
  ppsspp dolphin-emu mgba-qt mednafen mame scummvm desmume mupen64plus

Note: libretro-beetle-saturn does NOT exist in repos. Skip it.
```

---

## Phase 5: Emulators — AUR packages

### Prompt 5 — Swap zlib and install AUR emulators

```
Inside the distrobox gaming container:

1. First swap zlib for zlib-ng-compat (required by some -bin packages).
   pacman --noconfirm defaults the destructive "Remove zlib?" to No, so pipe yes:
     yes y | sudo pacman -S zlib-ng-compat

2. Then install AUR emulators. Package selection priority: -bin > stable > -git.

   yay -S --needed --noconfirm --answerclean All --answerdiff None \
     eden-bin rpcs3-bin pcsx2-latest-bin duckstation-qt-bin \
     cemu-bin xemu-bin vita3k-bin shadps4-bin \
     flycast azahar emulationstation-de supermodel

IMPORTANT package traps to avoid:
- duckstation or duckstation-gpl: pulls broken clang19 dep chain. Use duckstation-qt-bin.
- pcsx2-git: works but recompiles every update. Use pcsx2-latest-bin (has _autoupdate).
- pcsx2 (no suffix): pinned at old v2.6.3 stable. Way behind master.

Note: rpcs3-bin pulls llvm19 from AUR as a build dep. First install takes
~15 min for the LLVM compile. Subsequent installs are cached.
```

---

## Phase 6: BIOS wiring

### Prompt 6 — Symlink BIOS files from EmuDeck

```
The EmuDeck BIOS collection at /mnt/terachad/Emulators/EmuDeck/Emulation/bios/
has most BIOSes needed. Since /mnt/terachad is mounted read-only in the container,
use symlinks for read-only BIOS files and COPY for anything the emulator writes to.

Wire these (see arch-distrobox.md "BIOS wiring" section for exact commands):

SYMLINKS (read-only OK):
- xemu: mcpx_1.0.bin + Complex_4627.bin → ~/.config/xemu/
- Flycast: dc/dc_boot.bin, dc_flash.bin, naomi_boot.bin, awbios.zip → ~/.config/flycast/data/
- Mednafen: sega_101.bin, mpr-17933.bin, saturn_bios.bin, scph5500-5502.bios → ~/.mednafen/firmware/
- mGBA: BIOSGBA.ROM → ~/.config/mgba/gba_bios.bin (then patch config: useBios=1, skipBios=0)
- DeSmuME: biosnds7.bin, biosnds9.bin, dsfirmware.bin → ~/.config/desmume/ (then patch config: Use Ext BIOS=1)
- Dolphin: GC/{USA,EUR}/IPL.bin → ~/.config/dolphin-emu/GC/ + dolphin-emu/Sys/ dir

COPY (emulator writes to it):
- xemu HDD: "Xbox HDD Image with Original Dashboard/xbox_hdd.qcow2" → ~/.local/share/xemu/xbox_hdd.qcow2

Then update xemu.toml [sys.files] with the bootrom_path, flashrom_path, hdd_path.

NOT NEEDED (already configured via config SearchDirectory/system_directory):
- DuckStation, PCSX2, RetroArch cores — they point at the bios root already.

Switch keys (Eden): copy prod.keys and title.keys from
/mnt/terachad/Emulators/EmuDeck/Switch/Prodkeys.NET_v21-0-0/ to
~/.local/share/eden/keys/
```

---

## Phase 7: ES-DE symlink farm

### Prompt 7 — Map EmuDeck multi-root layout to ES-DE

```
ES-DE expects all ROMs under a single ~/ES-DE/roms/ directory, but EmuDeck
spreads ROMs across roms/, roms_heavy/, roms_mid/, roms_rare/. Create a symlink
farm at /mnt/data/distrobox/gaming/ES-DE/roms/ that maps each system to its
actual EmuDeck location. See arch-distrobox.md "ES-DE symlink farm" for the
full list of ~39 system symlinks covering: nes, gb, gbc, gba, genesis, psx,
mame, gc, wii, wiiu, switch, ps2, ps3, n3ds (→3ds), dreamcast, n64, nds, psp,
naomi, psvita, 3do, model2, model3, xbox, xbox360, ps4, etc.

Note the ES-DE naming quirk: ES-DE uses "n3ds" (not "3ds") for the path.
Create BOTH symlinks: n3ds AND 3ds pointing at the same target.
Map megacd → segacd for ES-DE compatibility.
```

---

## Phase 8: Emulator configs (tuned for RTX 5090 + 1440p 120Hz)

### Prompt 8 — Write tuned configs + visual quality + widescreen

```
Write pre-staged config files for all installed emulators, tuned for:
- RTX 5090 (Vulkan everywhere)
- 1440p 120Hz monitor
- 16x anisotropic filtering
- Maximum internal resolution the 5090 can handle per system
- Widescreen enabled (projection hack, not stretch) per-system
- PS1 PGXP polygon correction (full suite minus dangerous options)
- PS2 upscaling fixes (all safe UserHacks)
- Shader stutter elimination (Dolphin ubershaders, RetroArch runahead)

Config locations are under /mnt/data/distrobox/gaming/.config/<emulator>/.
ROM paths point at the EmuDeck structure on /mnt/terachad/Emulators/EmuDeck/.
BIOS paths point at EmuDeck/Emulation/bios/ (or the symlinked locations).

VISUAL QUALITY TUNING — apply these specific overrides:

DuckStation (PS1):
  PGXPDepthBuffer=true, PGXPPreserveProjFP=true, WidescreenHack=true
  Keep OFF: PGXPVertexCache (artifacts ~30% games), PGXPCPU (slow+buggy)

PCSX2 (PS2):
  EnableWideScreenPatches=true, EnableNoInterlacingPatches=true
  UserHacks_HalfPixelOffset=1, UserHacks_RoundSprite=2
  UserHacks_AlignSpriteX=true, UserHacks_MergePPSprite=true
  UserHacks_TextureInsideRT=1, accurate_blending_unit=2, TriFilter=2
  Controller hotkey: add [Hotkeys] ShutdownVM = SDL-0/Start & SDL-0/Back
  and set [UI] ConfirmShutdown=false so Select+Start exits cleanly.

Flycast (Dreamcast) — CRITICAL FORMAT NOTE:
  Flycast uses rend.KEY = VALUE prefixed keys inside the [config] section.
  Do NOT create a separate [rend] section — Flycast ignores it and creates
  its own defaults in [config], overwriting your tuned values silently.
  Also: Flycast regenerates the entire config on first launch with defaults.
  Strategy: let Flycast launch once, then patch the [config] section keys:
    aica.DSPEnabled=yes (AUDIO — without this there is NO SOUND)
    pvr.rend=4 (Vulkan — default is 0/OpenGL)
    rend.Resolution=2880
    rend.AnisotropicFiltering=16
    rend.WideScreen=yes
    rend.TextureUpscale2=4
    rend.TextureFiltering=1
    rend.RenderToTextureBuffer=yes
    rend.EmulateFramebuffer=no

  Keep Full Framebuffer Emulation OFF globally. It is a compatibility fallback
  for specific games that directly access VRAM, but Flycast's own UI warns it
  is incompatible with upscaling and widescreen, and libretro documents it as
  forcing internal resolution to 640x480. If a game needs it, enable it per-game.

  To prevent Flycast from rewriting emu.cfg back to low-quality defaults, create
  ~/bin/flycast-hires and use its absolute path in desktop entries + ES-DE
  because distrobox-enter does not load the interactive shell PATH:
    flycast -config config:pvr.rend=4 -config config:rend.Resolution=2880 \
      -config config:rend.EmulateFramebuffer=no -config config:rend.WideScreen=yes \
      -config config:rend.DupeFrames=yes -config config:rend.DelayFrameSwapping=no \
      -config config:pvr.AutoSkipFrame=0 "$@"

  Frame pacing note: on 120Hz+ monitors, enable rend.DupeFrames=yes. Keep
  rend.DelayFrameSwapping=no unless a game has flickering/video glitches, because
  it can make motion feel more latent. Keep pvr.AutoSkipFrame=0 when diagnosing
  "FPS is correct but motion feels sluggish."

Dolphin (GC/Wii):
  wideScreenHack=True, ShaderCompilationMode=2 (hybrid ubershaders)
  WaitForShadersBeforeStarting=True, DisableCopyFilter=True
  If an 8BitDo Ultimate 2 is the main pad, replace the default
  XInput2/keyboard placeholder config with SDL-based bindings:
    GCPadNew.ini:
      Device = SDL/0/8BitDo Ultimate 2
      A/B/X/Y = Button A/Button B/Button X/Button Y
      Z = Shoulder R
      Start = Start
      left stick = Main Stick
      right stick = C-Stick
      Trigger L/Trigger R = L/R (+ analog)
      d-pad = Pad N/S/W/E
    WiimoteNew.ini default:
      Device = SDL/0/8BitDo Ultimate 2
      A = Button A
      B = Trigger R
      1/2 = Button X/Button Y
      -/+ = Back/Start
      Home = Guide
      d-pad = Pad N/S/W/E
      IR = right stick
      Extension = Nunchuk
      Nunchuk stick = left stick
      Nunchuk C/Z = Shoulder L/Trigger L
      Wii shake = Thumb R
      Nunchuk shake = Thumb L
  Also create reusable profiles under:
    ~/.config/dolphin-emu/Profiles/GCPad/8BitDo Ultimate 2 SDL.ini
    ~/.config/dolphin-emu/Profiles/Wiimote/8BitDo Ultimate 2 Nunchuk.ini
    ~/.config/dolphin-emu/Profiles/Wiimote/8BitDo Ultimate 2 Classic.ini
  Use the Classic profile for Wii games that support Classic Controller and do
  not need pointer-style input.

PPSSPP: SplineBezierQuality=4, TexHardwareScaling=True
Eden: resolution_setup=3 (2x=1440p), enable_compute_pipelines=true
  theme=default, theme\default=true (DO NOT use Eden's UI theme picker —
  eden-bin 0.1.1 crashes with std::out_of_range when selecting any theme.
  The bug: theme string lookup returns -1, used as vector index → crash.
  Kvantum dark theme from the container env already styles the window.)
  Also: create ~/bin/eden wrapper that unsets QT_STYLE_OVERRIDE before
  launching the AppImage, and use that wrapper in the desktop entry +
  ES-DE custom_systems.xml. Without this, Kvantum conflicts with Eden's
  internal stylesheet system.
Azahar: texture_filter=2
RetroArch: run_ahead_enabled=true (1 frame input lag reduction)

IMPORTANT CONFIG GOTCHAS:
- vita3k-bin ships a DEFAULT config.yml at install time. Don't overwrite —
  use targeted edits (resolution-multiplier: 1→4, anisotropic-filtering: 1→16)
- RPCS3 rejects pre-written YAML. Delete any pre-staged config, run rpcs3
  once headlessly to generate defaults, then apply targeted edits.
- Flycast regenerates emu.cfg with ALL defaults on first launch. Your
  pre-staged config gets overwritten. Let it launch once, close it, then
  patch the specific keys in the [config] section. The key names use
  "rend." prefix (e.g., rend.Resolution, rend.AnisotropicFiltering).
- Eden's theme picker is broken in eden-bin 0.1.1. Never use it.
  Set theme=default in qt-config.ini manually.

Also create ~/ES-DE/custom_systems/es_systems.xml that overrides the default
emulator for: PSX→DuckStation, PS2→PCSX2, DC→Flycast, GC/Wii→Dolphin,
PSP→PPSSPP, Switch→Eden, Naomi→Flycast, and adds PS4/Xbox/Model3 as new
systems. RetroArch stays default for retro platforms (NES, SNES, GB, etc.).

See arch-distrobox.md per-emulator tuning section for all details.
```

---

## Phase 9: Theming

### Prompt 9 — Dark theme for container GUI apps

```
Install dark theming inside the distrobox gaming container:

Packages (extras):
  kvantum kvantum-qt5 qt5ct qt6ct breeze papirus-icon-theme

Packages (AUR):
  kvantum-theme-catppuccin-git tokyonight-gtk-theme-git

Config files to write:
- ~/.config/Kvantum/kvantum.kvconfig → theme=catppuccin-mocha-blue
- ~/.config/gtk-3.0/settings.ini → gtk-theme-name=Tokyonight-Dark, Papirus-Dark icons
- ~/.config/gtk-4.0/settings.ini → same as gtk-3.0
- ~/.config/qt5ct/qt5ct.conf → style=kvantum, icon_theme=Papirus-Dark
- ~/.config/qt6ct/qt6ct.conf → same as qt5ct

Env vars are already in /etc/profile.d/gaming-wayland.sh from Phase 3.
```

---

## Phase 10: Desktop exports + Hyprland monitor pinning

### Prompt 10 — Export all emulators to host launcher

```
Export all emulators from the distrobox gaming container to the host launcher.

IMPORTANT: distrobox-export --app matches on Exec=/Name= content inside
.desktop files, NOT on the filename. Pass the BINARY NAME, not the reverse-DNS
desktop file basename. Example: use "retroarch" not "com.libretro.RetroArch".

Working export loop:
  for app in retroarch dolphin-emu PPSSPPQt mgba-qt mame scummvm desmume \
             pcsx2 eden rpcs3 duckstation-qt flycast azahar es-de \
             mupen64plus cemu xemu vita3k supermodel shadps4; do
      distrobox-export --app "$app"
  done

EDEN BUG: eden.desktop has SPDX comments before [Desktop Entry] which breaks
distrobox-export's parser. Write the eden desktop file manually at
~/.local/share/applications/gaming-eden.desktop with
Exec=/usr/bin/distrobox-enter -n gaming -- /usr/bin/eden %F

Then add a Hyprland windowrule to pin all emulator windows to the gaming
monitor (HDMI-A-2 = Asus VG32V). Append to ~/.config/hypr/looknfeel.conf:

  windowrule = monitor HDMI-A-2, match:class (?i)^(rpcs3|pcsx2|pcsx2-qt|dolphin-emu|duckstation-qt|cemu|xemu|flycast|azahar|eden|vita3k|shadps4|supermodel|mupen64plus|ppssppqt|desmume|mgba|retroarch|org\.azahar_emu\.azahar|org\.duckstation\.duckstation|com\.libretro\.retroarch)$

Then: hyprctl reload
```

---

## Phase 11: PS3 DLC batch extraction

### Prompt 11 — Extract all PS3 DLC PKGs without RPCS3 GUI

```
RPCS3 blocks --installpkg in both --no-gui and --headless modes ("Cannot
perform installation in no-gui mode!"). But the PS3 PKG format is documented
and the DLCs are unencrypted (type 0x0001). I wrote a Python extractor that
decrypts the file table with the well-known PS3 AES key and extracts files
directly to RPCS3's dev_hdd0/game/ directory.

The extractor script is at /mnt/data/distrobox/gaming/scripts/extract_ps3_dlc.py.
It uses the `cryptography` Python library (already installed on the host).

Run the batch extraction:

  python3 /mnt/data/distrobox/gaming/scripts/extract_ps3_dlc.py \
    "/mnt/terachad/Emulators/EmuDeck/roms_heavy/ps3-DLC" \
    --dest "/mnt/data/distrobox/gaming/.config/rpcs3/dev_hdd0/game"

This extracts all PKGs in one pass. The script:
- Reads PKG headers (magic 0x7F504B47, content type, IV at offset 0x70)
- Decrypts file table with AES-128-CTR using key 2E7B71D7C9C9A14EA3221F188828B8F8
- Extracts each file (PS3LOGO.DAT, PARAM.SFO, ICON0.PNG, USRDIR/...) to
  dev_hdd0/game/<CONTENT_ID>/
- Skips files that already exist (idempotent, safe to re-run)
- Works on any unencrypted PS3 PKG (free DLC, patches, updates)
- Does NOT work on paid/licensed PKGs that require RAP files

Verified: 122 PKGs → 51 content IDs → 27 GB extracted.
RPCS3 auto-detects these on next launch by scanning dev_hdd0/game/.
```

---

## Phase 12: RPCS3 per-game custom configs

### Prompt 12 — Write per-game optimal settings

```
RPCS3 supports per-game custom configs at:
  ~/.config/rpcs3/custom_configs/<TITLE_ID>_config.yml

These YAML files override specific keys from the global config.yml.
Only list keys that DIFFER from global. Example (MGS4):

  Video:
    Write Color Buffers: true
    Read Color Buffers: true
    Strict Rendering Mode: true
    Multithreaded RSX: false
    Resolution Scale: 100
  Core:
    SPU Loop Detection: true
    Accurate GETLLAR: true

The RPCS3 wiki at wiki.rpcs3.net has per-game recommendations but is behind
Cloudflare JS challenges that block ALL automated access (curl, headless
Chrome, API, WebFetch). The compatibility API at
https://rpcs3.net/compatibility?api=v1&g=<search> DOES work (returns JSON
with title, status, wiki-id) but doesn't include custom config data.

For this setup, write configs based on training knowledge of known-good
per-game settings. The most common override is "Write Color Buffers: true"
which fixes rendering in ~60% of "Ingame" status titles. Other common
overrides: Read Color Buffers, SPU Loop Detection, SPU Block Size: Mega,
Strict Rendering Mode, Resolution Scale (downscale demanding titles to 100%).

Use the RPCS3 API to get each game's TITLE_ID and compatibility status:
  curl -s "https://rpcs3.net/compatibility?api=v1&g=<TITLE_ID>"

Map the user's PS3 game directories to TITLE_IDs by:
1. Parsing PARAM.SFO inside each game directory (strings <PARAM.SFO> | grep -oP '^[A-Z]{4}\d{5}$')
2. Falling back to extracting from directory names (grep -oP '[A-Z]{4}[-]?\d{5}')

Write configs for all "Ingame" status games. "Playable" games use global
config as-is (no override needed unless specific issues are known).
```

---

## Phase 13: Switch cheats for Eden

### Prompt 13 — Symlink Atmosphere-format cheat files to Eden's load path

```
Switch cheats are at /mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_cheats/.
Each directory is named "<TITLE_ID> - <Game Name>" and contains a cheats/ subdir
with <build_id>.txt files (Atmosphere cheat format).

Eden reads cheats from: ~/.local/share/eden/load/<TITLE_ID>/cheats/

Symlink each game's cheats/ subdir (not the whole parent — parent has extra
non-cheat files) to Eden's load path:

  python3 -c "
  import os, re
  CHEATS_SRC = '/mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_cheats'
  EDEN_LOAD = os.path.expanduser('~/.local/share/eden/load')
  for entry in sorted(os.listdir(CHEATS_SRC)):
      src = os.path.join(CHEATS_SRC, entry)
      if not os.path.isdir(src): continue
      match = re.match(r'^([0-9A-Fa-f]{16})', entry)
      if not match: continue
      tid = match.group(1).upper()
      cheats = os.path.join(src, 'cheats')
      if not os.path.isdir(cheats): continue
      dest = os.path.join(EDEN_LOAD, tid, 'cheats')
      os.makedirs(os.path.dirname(dest), exist_ok=True)
      if os.path.islink(dest): os.unlink(dest)
      os.symlink(cheats, dest)
      print(f'  {tid} -> {entry[17:][:40]}')
  "

Result: 54 games with cheats linked. Eden picks these up automatically per-game.
To enable cheats in Eden: Emulation → Configure → General → Enable Mods (should
already be on by default in yuzu forks).
```

---

## Phase 14: Switch updates/DLC for Eden

### Prompt 14 — Extract NSP updates to Eden NAND

```
Switch updates and DLC are NSP files at:
  /mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_updates/

Eden has no CLI flag for "Install Files to NAND" (GUI only, like RPCS3).
But NSP is just a PFS0 container (unencrypted) holding NCA files. Eden's NAND
stores NCAs flat at ~/.local/share/eden/nand/user/Contents/registered/.

The extractor script at /mnt/data/distrobox/gaming/scripts/install_switch_updates.py
parses PFS0 headers, extracts .nca + .cnmt.nca + .tik files, and places them
directly in Eden's NAND registered directory.

  python3 ~/scripts/install_switch_updates.py \
    "/mnt/terachad/Emulators/EmuDeck/roms_heavy/switch_updates" \
    --dest "~/.local/share/eden/nand/user/Contents/registered"

This processes all NSP files recursively (updates inside subdirectories too).
Some updates are 1-4 GB each so the full batch takes 15-30 minutes on NFS→NVMe.

Eden auto-detects updates by matching the update NCA's title ID to the base
game (update title IDs are base_id + 0x800 by Switch convention). No manual
game-to-update mapping is needed — Eden reads the CNMT metadata from the NCAs.

The script is idempotent — re-running skips files that already exist with
matching sizes.
```

---

## Phase 15: RetroArch cores + assets (pre-load everything)

### Prompt 15 — Download cores and all assets from buildbot

```
RetroArch's "Online Updater" downloads cores, assets, controller profiles,
cheats, databases, shaders, and overlays. All of these are direct zip
downloads from https://buildbot.libretro.com/ — no GUI needed.

Download 21 additional cores matching the user's ROM systems:
  CORES=(fbneo stella prosystem handy gambatte mednafen_ngp bluemsx fmsx
         o2em opera mednafen_saturn mednafen_wswan mednafen_vb
         mednafen_supergrafx vecx neocd fceumm puae hatari vice_x64 atari800)

  BASEURL="https://buildbot.libretro.com/nightly/linux/x86_64/latest"
  for core in "${CORES[@]}"; do
      curl -sfL "$BASEURL/${core}_libretro.so.zip" -o "/tmp/${core}.zip"
      unzip -qo "/tmp/${core}.zip" -d ~/.config/retroarch/cores/
      rm -f "/tmp/${core}.zip"
  done

Download all assets:
  ASSETS_URL="https://buildbot.libretro.com/assets/frontend"
  for zip in info.zip assets.zip autoconfig.zip cheats.zip \
             database-rdb.zip database-cursors.zip shaders_slang.zip overlays.zip; do
      dest=$(echo $zip | sed 's/.zip//;s/database-rdb/database\/rdb/;s/database-cursors/database\/cursors/;s/shaders_slang/shaders/')
      mkdir -p ~/.config/retroarch/$dest
      curl -sfL "$ASSETS_URL/$zip" -o "/tmp/$zip"
      unzip -qo "/tmp/$zip" -d ~/.config/retroarch/$dest/
      rm -f "/tmp/$zip"
  done

Then update retroarch.cfg paths to point at ~/.config/retroarch/ subdirs
instead of /usr/share/libretro/ system paths.

Total: 36 cores (15 pacman + 21 buildbot), 762 MB of data.
Covers every system in the EmuDeck ROM collection through RetroArch.
```

---

## Phase 16: Update script

### Prompt 16 — Create ~/bin/update-gaming one-shot updater

```
Create ~/bin/update-gaming inside the container. This script updates
everything in one command:

1. pacman -Syu (system + extras packages)
2. yay -Syu (AUR packages — eden-bin, rpcs3-bin, etc.)
3. RetroArch cores — re-downloads each installed core from buildbot nightly,
   replaces if file size differs
4. RetroArch assets — re-downloads all 8 asset zips and overwrites

Options: --dry-run, --skip-aur, --skip-cores, --skip-assets

Add ~/bin to PATH in /etc/profile.d/gaming-wayland.sh so the script is
callable by name from within the container.

Usage:
  distrobox enter gaming -- update-gaming
  distrobox enter gaming -- update-gaming --dry-run

The script is at /mnt/data/distrobox/gaming/bin/update-gaming.
See arch-distrobox.md for the full source.
```

---

## Phase 17: Manual steps (cannot be automated)

These require GUI interaction — do them yourself on first launch:

1. **Steam**: log in, Settings → Storage → Add Drive → `/mnt/data/steam`
2. **RPCS3**: File → Install Firmware → `/mnt/terachad/Emulators/EmuDeck/Emulation/bios/PS3UPDAT.PUP`
   (rpcs3 --headless --installfw FAILS with "Cannot perform installation in headless mode")
3. **Eden**: File → Install Firmware → `/mnt/terachad/Emulators/EmuDeck/Switch/Firmware.21.0.0/`
   (keys already copied in Phase 6)
4. **Vita3K**: File → Install Firmware → `/mnt/terachad/Emulators/EmuDeck/Emulation/bios/psvita/PSVUPDAT.PUP`
5. **Azahar (3DS)**: source AES keys from your own 3DS dump → `~/.local/share/azahar-emu/sysdata/aes_keys.txt`
6. **ES-DE**: first launch wizard → point at `~/ES-DE/roms/` (default)
7. **RPCS3 first game**: expect 10-30 min "LLVM Cache Batch Creation" on first launch per game — NOT stuck, just PPU/SPU precompilation. Subsequent launches use cache.

---

## Phase 18: Host cleanup (AFTER verifying container works)

```
Remove gaming packages from the host pacman db:

  sudo pacman -Rns steam gamescope lib32-nvidia-utils lib32-vulkan-radeon cemu-bin

DO NOT REMOVE (name collisions):
- dolphin — this is the KDE FILE MANAGER, not dolphin-emu
- proton-vpn-* — this is ProtonVPN (the VPN service), not Steam Proton
```
