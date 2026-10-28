# Super Mario All-Stars Recompiled (`install_smas_recomp`)

[TanookiStudios/SuperMarioAllStarsRecomp](https://github.com/TanookiStudios/SuperMarioAllStarsRecomp)
is a native PC port (static recompilation) of the SNES **Super Mario All-Stars**,
built on TanookiStudios' "retcomm" recompilation framework. It renders through
**OpenGL** with a bundled **SDL3**; no emulator, no Wine. Upstream ships an
**official native Linux build** (`SuperMarioAllStars-Linux.tar.gz`), so this is a
prebuilt-release role (no source build) — the DK64 / Road Rash / F-Zero / VF
pattern.

## Install

```sh
cd ansible
ansible-playbook install-smas-recomp.yml       # or: site.yml --tags smas_recomp
scripts/install-host-launchers.sh              # refresh the host menu entry
```

Launcher `bin/smas`; host/Walker entry **"Super Mario All-Stars · Recompiled"**;
`ogm` id `smas`. Revert with `-e dg_smas_revert=true` (removes the launcher +
install dir; your ROM on the NAS is untouched — note that removes the `config.ini`
/ `keybinds.ini` + `*.srm` battery saves + `*.sav` save states under the gamedir,
which the `backup_saves` role captures).

## ROM — you must supply the 25th-Anniversary dump

The recomp **hard-requires the 2010 25th-Anniversary USA ROM**:

```
sha256  411c7036750fbc79d60b84602414dbe713074de8204d3c4a5ad762679c103c61
size    2,097,152 bytes (2 MiB)
```

The plain 1993 cartridge ("Super Mario All-Stars (USA)") is a **different dump
and is rejected** — the launcher gates on the sha256 above. The role verifies the
staged ROM against that hash before doing anything.

The 25th-Anniversary ROM is **not a cartridge dump**. It exists only as the SNES
Virtual Console title inside the 2010 *Super Mario All-Stars: Limited Edition* Wii
disc, and it is a **modified** ROM: Nintendo replaced every embedded BRR audio
sample with a pointer into a separate PCM sample pack, so the ROM on its own is
silent / won't boot a plain emulator. The internal SNES checksum is left stale
(`A63D`), which is expected — the recomp ignores it and keys on the sha256.

It is staged on the NAS at:

```
{{ dg_rom_mid_root }}/snes/Super Mario All-Stars (USA) (25th Anniversary).sfc
```

(`dg_smas_rom`). Override `dg_smas_rom` / `dg_smas_rom_sha256` in
`host_vars/localhost.yml` if yours lives elsewhere.

### Recovering the ROM from the Wii disc

If the staged ROM is lost (e.g. a from-scratch NAS remount), recreate the exact
`411c7036…` bytes from the user's own *Super Mario All-Stars: Limited Edition*
Wii disc (Redump USA, Game ID `SVME01`). The naive LZH8 decode that circulates
(sha256 `15d9a11e…`, also what TanookiStudios ship as their CI `test-rom.sfc`
placeholder) is **wrong** — it is the ROM *before* the audio samples are
restored, and the recomp rejects it. The correct pipeline is **decode + restore
audio**, which is exactly what [`vcromclaim`](https://github.com/Plombo/vcromclaim)
does for SNES VC titles (hcs's LZH8 decoder + Bryan Cain's BRR sample restore):

1. Extract the disc's filesystem (RVZ/ISO) with `nodtool` (AUR `nodtool-bin`):
   ```sh
   nodtool extract "Super Mario All-Stars (USA).rvz" smas-extract/
   ```
   The two inputs are `files/content5/LZH8SVME.rom` (the LZH8-compressed modified
   ROM) and `files/content5/LZH8SVME.pcm` (the LZH8-compressed PCM sample pack).

2. Run the recovery helper, which decompresses both with hcs's LZH8 decoder and
   re-injects the BRR audio at each `PCMF` marker:
   ```sh
   python3 scripts/recover-smas-25th-rom.py \
     smas-extract/files/content5/LZH8SVME.rom \
     smas-extract/files/content5/LZH8SVME.pcm \
     "Super Mario All-Stars (USA) (25th Anniversary).sfc"
   # -> sha256 411c7036…  MATCH
   ```
   (The helper is a self-contained Python 3 port of `vcromclaim`'s `lzh8.py` +
   `snesrestore.py` + `brrencode3.py`, since upstream is Python 2.)

3. Copy the verified `.sfc` to the NAS path above.

## Graphics

`config.ini` is the host's settings file. Under `[Graphics]`, `Fullscreen = 1`
is desktop fullscreen (0 windowed, 2 exclusive mode change) and the role keeps
it there; `WindowSize = Auto` follows the 4K display, and `[KeyMap] Fullscreen =
Alt+Return` stays the toggle. Note the two `Fullscreen` keys are different
settings in different sections.

## How it works

- Downloads the pinned `SuperMarioAllStars-Linux.tar.gz` (sha256 in
  `group_vars/all/smas_recomp.yml`) to `cache/smas-recomp/` and unpacks the
  `SuperMarioAllStars-Linux/` folder into `tools/smas-recomp/`. The binary is an
  x86-64 ELF; the role asserts `ldd` is clean inside the box.
- Extraction is version-gated on `.dg-installed-ref` and extracts **over the
  top**, so a version bump never wipes your `*.srm` / `*.sav` saves (they are not
  in the tarball). The role also deletes the upstream CI leftovers shipped in the
  tarball (`test-rom.sfc` — the wrong `15d9a11e` decode — plus its `rom.cfg` and
  the stray run logs).
- The launcher passes the ROM as **argv[1]**, which boots straight into the game
  (a bare ROM arg skips the launcher GUI; `--launcher` would force it). It focuses
  **DP-1** (Hyprland Lua IPC) and pins the **nvidia GLX** vendor
  (`__NV_PRIME_RENDER_OFFLOAD` + `__GLX_VENDOR_LIBRARY_NAME=nvidia`) so the GL
  context runs on the RTX, not the AMD iGPU. 8BitDo works out of the box via the
  bundled SDL3 (it auto-detects the controller from `assets/gamecontrollerdb.txt`).
- The recomp anchors its config + saves to its own **exe dir**
  (`config.ini`, `keybinds.ini`, `*.srm` battery saves, `*.sav` save states) —
  there is no separate save subdir, so `backup_saves` captures the whole gamedir
  (`smas-recomp` set in `group_vars/all/backups.yml`).

In-game: the menu is **Esc** (keyboard) or the **Guide/Home** button (or
Select + left-stick click) on a controller. Save states, fullscreen, settings and
mods live there and in `config.ini` next to the binary.

## Updating

Bump `dg_smas_release_tag` / `dg_smas_asset_name` / `dg_smas_asset_sha256` (from
the [releases](https://github.com/TanookiStudios/SuperMarioAllStarsRecomp/releases))
and re-run. The version gate re-extracts over the top; your saves survive.
