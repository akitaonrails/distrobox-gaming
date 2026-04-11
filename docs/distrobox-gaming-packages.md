# Package Management Lessons — Distrobox + NVIDIA + Emulators (2026-04)

What we learned about package sources, selection priorities, and gotchas
when building a gaming distrobox container on Arch with an NVIDIA GPU.

---

## Package selection priority

Order of preference when multiple sources exist for the same emulator:

1. **Pacman extras** — first choice. Native Arch packages, auto-update with `pacman -Syu`, smallest footprint, best integration. Used for: retroarch, dolphin-emu, ppsspp, mgba-qt, mednafen, mame, scummvm, desmume, mupen64plus, and all `libretro-*` cores.

2. **AUR `-bin` packages** — preferred for things not in extras. These wrap upstream AppImages or pre-compiled binaries into pacman packages. No compile time, auto-update via `yay -Syu`, AppImage tracks upstream releases. Used for: eden-bin, rpcs3-bin, pcsx2-latest-bin, duckstation-qt-bin, cemu-bin, xemu-bin, vita3k-bin, shadps4-bin.

3. **AUR stable source** (no suffix) — fallback when no `-bin` exists. Source build from a stable release tag. Recompiles on every update but the build is usually deterministic and fast. Used for: flycast, azahar, emulationstation-de, supermodel.

4. **AUR `-git`** — last resort. Tracks `HEAD` of the upstream repo. Recompiles every update, build can break on unstable commits. Only use when no other option exists or when `-bin` is significantly outdated and the upstream doesn't do stable releases.

5. **Flatpak** — see "Flatpak findings" section below. NOT viable inside distrobox.

---

## NVIDIA in distrobox — the dummy package trick

### The problem

Distrobox `--nvidia` bind-mounts the host's NVIDIA userspace libraries (`/usr/lib/libnvidia-*.so`, `/usr/lib/libGLX_nvidia.so*`, Vulkan ICD jsons, etc.) into the container **read-only**. These files physically exist at the same paths where `nvidia-utils` would install them.

When pacman tries to install any package that depends on `nvidia-utils` (which includes `steam`, `lib32-mesa`, `vulkan-tools`, and transitively half the gaming stack), it sees the bind-mounted files as "file conflicts" and aborts:
```
nvidia-utils: /usr/lib/libnvidia-glcore.so.595.58.03 exists in filesystem
```

### Workaround 1: --assume-installed (per-command, not sticky)

```bash
sudo pacman -S --assume-installed nvidia-utils=595.58.03-1 <packages>
```

This tells pacman "pretend nvidia-utils is installed at this version" for dependency resolution. Works for direct `pacman -S` calls but is NOT sticky — you must pass it every single time. And it **does NOT work for yay/makepkg** because makepkg calls pacman internally and there's no way to propagate `--assume-installed` through yay's `--mflags` (that option passes flags to makepkg, not pacman).

### Workaround 2: Dummy local package (permanent fix)

Build a tiny PKGBUILD that `provides=(nvidia-utils=$VERSION vulkan-driver opengl-driver nvidia-libgl)` and `conflicts=(nvidia-libgl nvidia-utils)`. Install it with `pacman -U`. After this, pacman's dependency resolver sees nvidia-utils as satisfied everywhere — including inside makepkg, which means yay works normally.

```bash
# PKGBUILD for nvidia-utils-dummy
pkgname=nvidia-utils-dummy
pkgver=595.58.03  # must match host nvidia driver version
provides=("nvidia-utils=$pkgver" "vulkan-driver" "opengl-driver" "nvidia-libgl")
conflicts=("nvidia-libgl" "nvidia-utils")
package() { :; }
```

To find the version: `nvidia-smi --query-gpu=driver_version --format=csv,noheader` on the host, then append `-1` for the pkgrel.

Check `pacman -Q lib32-nvidia-utils` — on some images it installs successfully (the file conflict is 64-bit only). If it's missing, build a second dummy for `lib32-nvidia-utils-dummy` with the same pattern.

---

## Flatpak findings

### Flatpak inside distrobox: DOES NOT WORK

Tested April 2026. Flatpak's `bwrap` (bubblewrap) sandbox does not nest cleanly inside Docker's mount namespaces:

```
Failed to open runtime files: Bad address
Could not connect: No such file or directory
```

The freedesktop/nvidia **runtimes** download and install fine. Actual **application** installs fail at the bwrap-deploy step. This is a known interaction between flatpak and rootless container engines, not specific to distrobox.

The broken distrobox→host `flatpak` symlink at `/usr/bin/flatpak` (created by distrobox for host delegation) also blocks installing a real flatpak inside the container — must be removed first with `docker exec -u root gaming rm /usr/bin/flatpak`.

### Flatpak on the host: works perfectly

If you want Flathub apps for gaming, install flatpak on the **host** (not in distrobox):
```bash
sudo pacman -S flatpak xdg-desktop-portal-hyprland
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub <app-id>
flatpak override --user --filesystem=/mnt/terachad/Emulators:ro <app-id>
```

This adds exactly ONE package to host pacman (`flatpak`). The actual gaming flatpaks live in `~/.local/share/flatpak/` or `/var/lib/flatpak/`, completely outside pacman. Host setup wasn't taken in our case because AUR `-bin` packages covered everything.

### Flatpak vs AUR version comparison (as of April 2026)

| Emulator | Flathub version | AUR -bin version | Winner |
|----------|----------------|-----------------|--------|
| PCSX2 | v2.6.3 (very stale — summer 2024) | 2.7.245 via pcsx2-latest-bin | AUR by ~250 commits |
| RPCS3 | 0.0.40-19146 | 0.0.40.19180 via rpcs3-bin | Comparable, AUR slightly newer |
| Azahar | 2124.3 | 2125.0.1 | Comparable, AUR slightly newer |
| Flycast | v2.6 | 2.6 | Same |
| DuckStation | NOT on Flathub | 0.1.r10975 via duckstation-qt-bin | AUR only |
| Eden | NOT on Flathub | 0.1.1 via eden-bin | AUR only |
| ES-DE | NOT on Flathub | 3.4.0 | AUR only |

**Takeaway:** Flathub emulator versions lag behind AUR for several key emulators. PCSX2 on Flathub is especially stale (slow stable release channel). Unless you specifically need the sandboxing flatpak provides, AUR `-bin` is better.

---

## Specific package gotchas

### duckstation — metapackage trap

`duckstation` (AUR) is now a **metapackage** redirecting to `duckstation-gpl`. The GPL fork bumped its build dependency to `clang19`, which in turn pulls `compiler-rt19` + `lld19` from AUR. The `compiler-rt19` package **fails to build** against current GCC due to a `-Werror` + `-Wformat=` warning in `sanitizer_stack_store.cpp`.

**Fix:** Use `duckstation-qt-bin` instead. Pre-compiled AppImage, no clang19 needed.

### pcsx2 — three confusing packages

| Package | Version | What it is |
|---------|---------|-----------|
| `pcsx2` | v2.6.3 | Old stable release from 2024. Way behind master. |
| `pcsx2-git` | 2.7.245+ | Tracks git HEAD. Compiles from source (~10 min). Most current code. |
| `pcsx2-latest-bin` | 2.7.245 | AppImage wrapper. **Has `_autoupdate=true`** in PKGBUILD, so yay rebumps the version to current master at build time even though the static `pkgver` field says `2.7.133`. Best of both worlds: latest code, no compile. |

**Use `pcsx2-latest-bin`.** It's the same upstream master as `-git` but as an AppImage.

### rpcs3-bin — llvm19 dep on first install

`rpcs3-bin` is an AppImage wrapper (fast to install) but it depends on `llvm19` (runtime lib). LLVM19 is NOT in the Arch extras repo (extras has LLVM 22), so yay builds it from AUR source. **First install** takes ~15 minutes for the LLVM compile. Subsequent installs use the cached package.

This also pulls `compiler-rt19` → `clang19` → `lld19` as build deps. These can fail if yay doesn't serialize the dependency chain correctly (race condition in parallel builds). **If they fail, just re-run yay** — llvm19 is now installed, so the deps resolve on retry.

### zlib-ng-compat swap

Several AUR `-bin` packages (vita3k-bin, shadps4-bin) depend on `zlib-ng-compat`, a drop-in faster replacement for `zlib`. pacman's `--noconfirm` defaults the destructive "Remove zlib?" prompt to **No**, causing the install to fail silently.

**Fix:** Pre-swap manually:
```bash
yes y | sudo pacman -S zlib-ng-compat
```

### vita3k-bin — ships default config

Unlike most emulators, `vita3k-bin` writes a default `~/.config/Vita3K/config.yml` at package install time (not first launch). If you pre-write a tuned config before installing the package, the package install overwrites it.

**Pattern:** Install first, then apply targeted edits to the default config.

### RPCS3 — rejects pre-written YAML

RPCS3's `config.yml` has version-specific key names and structure. If you pre-stage a YAML config that doesn't match RPCS3's expected format exactly, it errors with `Failed to apply global config` and silently ignores it.

**Pattern:** Delete any pre-staged config, run RPCS3 once (headless or GUI) to generate fresh defaults, then apply targeted edits to specific keys (Resolution Scale, Anisotropic Filter, VSync, etc.).

### distrobox-export --app name matching

`distrobox-export --app <name>` greps for `<name>` inside the `Exec=` and `Name=` lines of desktop files in `/usr/share/applications/`. It does **NOT** match against the `.desktop` filename.

| Works | Fails |
|-------|-------|
| `--app retroarch` | `--app com.libretro.RetroArch` |
| `--app duckstation-qt` | `--app org.duckstation.DuckStation` |
| `--app mgba-qt` | `--app io.mgba.mGBA` |

Always use the **binary name** or the human-readable **display name**.

### eden.desktop — SPDX comment bug

`eden.desktop` ships with SPDX license comments before the `[Desktop Entry]` section. This confuses `distrobox-export`'s parser, producing a garbage 20-byte file named `gaming-eden` (no `.desktop` extension). Must write the eden desktop file manually on the host.

---

## archlinux:latest container image quirks

Things that differ from a standard Arch install and break common setup guides:

1. **No `[multilib]` section** in `/etc/pacman.conf` — not even commented out. Must be appended manually.
2. **Stray `[options]` at end of pacman.conf** — empty section that absorbs anything appended after it. Delete it before appending `[multilib]`.
3. **Passwordless sudo not configured** — despite distrobox's init running. The shipped `/etc/sudoers.d/sudoers` has wrong permissions (0644 instead of 0440) so sudo silently ignores it, AND the `%wheel` rule has no NOPASSWD. Fix: create `/etc/sudoers.d/zz-*` (zz prefix loads last = wins).
4. **No `flatpak` binary** — distrobox creates a symlink `/usr/bin/flatpak → /usr/bin/distrobox-host-exec` for host delegation. If the host has no flatpak, this is a broken symlink that also blocks installing flatpak inside the container (file conflict on `/usr/bin/flatpak`).
5. **Docker is the container manager** (not podman) on this host. Direct container-root ops use `docker exec -u root gaming <cmd>`.

---

## What's NOT available anywhere

| System/Feature | Status |
|---------------|--------|
| `libretro-beetle-saturn` | Not in extras. Use mednafen standalone or beetle-saturn-git from AUR. |
| `libretro-fbneo` | Not in extras. Use libretro-fbneo-git from AUR. |
| `libretro-stella`, `libretro-bluemsx`, `libretro-handy`, `libretro-prosystem`, `libretro-o2em`, `libretro-mednafen-{ngp,pcfx,saturn}`, `libretro-virtualjaguar`, `libretro-vecx` | None in extras. Use mednafen standalone for covered systems, or AUR -git builds. |
| `melonds` standalone | Not in extras. Only AUR git builds. Use `libretro-melonds` (extras, via RetroArch) or `desmume` standalone (extras). |
| Sega Model 2 emulator | No native Linux emulator at all. Use MAME's partial Model 2 driver, or run the Windows "Sega Model 2 Emulator" via Wine/Lutris. |
| PS4 emulation | Keep `shadps4-bin` installed as a fallback/icon source, but Driveclub now launches through `/mnt/data/distrobox/gaming/bin/shadps4-current`, a wrapper that targets the QtLauncher-managed Pre-release build. |

Driveclub-specific shadPS4 notes:

- Local Driveclub runtime content is now expected as an extracted
  `CUSA00003/` directory under
  `/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4`, with `eboot.bin` inside it.
- shadPS4 runtime state is under
  `/mnt/data/distrobox/gaming/.local/share/shadPS4/`, and the setup mirrors
  `CUSA00003.toml` into `/mnt/data/distrobox/gaming/.config/shadPS4/custom_configs/`
  because current Linux builds do not consistently agree on the game-config path.
- PS4 11.00 firmware modules live in
  `/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4-firmware/11.00_sys_modules`.
  They are symlinked into shadPS4's `sys_modules` directory to avoid duplicating
  ~1.5 GB of firmware files.
- Game-specific config: `custom_configs/CUSA00003.toml`.
- Patch file: `patches/Driveclub.xml`, with the official `60 FPS with deltatime`
  v1.28 patch enabled.
- ES-DE PS4 launcher is Driveclub-specific and points at the extracted game
  boot file:
  `/mnt/data/distrobox/gaming/bin/shadps4-current -g %ROM% -p /mnt/data/distrobox/gaming/.local/share/shadPS4/patches/Driveclub.xml -f true`.
- Current upstream/forum guidance for Linux mainline/nightly is: Driveclub needs
  readbacks enabled, readback linear images disabled, v1.28, 1920x1080 window and
  internal size, and the 60fps deltatime patch. Expect shader/cache warm-up and
  occasional crashes; this title is still experimental.
- Keep the PS4 root clean. Do not leave raw `.pkg` files or Windows extraction
  tools mixed beside the extracted game directory. This shadPS4 build launches
  an installed/dumped game directory or `eboot.bin`.

PS4 PKG tooling notes:

- Working tool: `ShadPKG`, kept under
  `/mnt/data/distrobox/gaming/tools/ShadPKG`.
- Working CLI binary:
  `/mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg`.
- Local Linux build worked with `BUILD_GUI=OFF` plus a small local
  `Findcapstone.cmake` helper for Arch.
- `ShadPKG` successfully handled both:
  - `blz-dc.pkg`
  - `Driveclub.v1.28.PATCH.REPACK.PS4-GCMR.pkg`
- `sfo-info`, `pfs-info`, and full `extract` succeeded on both PKGs.
- Comparing extracted base+patch contents against the live
  `/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA00003` tree showed no
  missing files from the package view; the live tree only has extra metadata
  files and Synology `@eaDir` artifacts.
- That makes a plain "bad extraction" explanation unlikely for the current
  Driveclub black-screen hang.
| Xbox 360 emulation | `xenia-canary-git` exists on AUR but Linux support is experimental. Many games don't boot. |
| 3DS AES keys | NOT in EmuDeck or any package. Must come from a real 3DS hardware dump. |
| Tokyo Night Kvantum theme | Does not exist. Closest Qt match is Catppuccin Mocha (blue accent). Tokyo Night GTK theme exists (`tokyonight-gtk-theme-git`). |
