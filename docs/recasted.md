# Ratchet & Clank (PS4) — ReCasted

[AndyALRLabs/ReCasted](https://gitlab.com/AndyALRLabs/ReCasted) is not an
emulator: it is a small **HLE compatibility layer and native x86-64 loader** for
*Ratchet & Clank (PS4)*. It maps the Orbis system calls and the Liverpool GNM
graphics pipeline onto POSIX and Vulkan 1.3 and runs the game binary as a host
process — no full-system emulation, no Wine.

```sh
cd ansible && ansible-playbook install-recasted.yml    # or: site.yml --tags recasted
```

| | |
|---|---|
| Release | `v0.4.0` Linux x86_64 tarball (30 MB, SHA256-pinned, staged in `ROMS_FINAL/PC/ports/recasted/v0.4.0/`) |
| Install | `tools/recasted/v0.4.0/recasted-linux-x86_64/`, with `tools/recasted/current` pointing at it |
| Game | USA **CUSA01047** (base PKG + v1.07 patch) extracted to `Games/ratchet-clank-cusa01047/` (25 GB, local NVMe for streaming) |
| Launcher | `bin/recasted` — boots the game; `--launcher` opens the GUI; entry **Ratchet & Clank · ReCasted (PS4)** |
| Save data | `user/` in the install dir (emulated PS4 user/cache/save data), mirrored as `recasted` |

## The game dump

ReCasted contains no game data. Upstream's targets are **CUSA01073 v1.09 (EU,
"fully playable")** and **CUSA01047 v1.09 (USA, "supported")**. This library has
the USA release at v1.07, which boots:

```sh
# Base PKG (25 GB) -> local staging, then the v1.07 patch over it.
distrobox-enter -n gaming -- \
  tools/ShadPKG/build-cli/shadpkg extract \
  "ROMS_FINAL/ps4/Ratchet and Clank/Ratchet.and.Clank.PS4-CUSA01047/….pkg" \
  /mnt/data/distrobox/gaming/tmp/rac-base
distrobox-enter -n gaming -- \
  tools/ShadPKG/build-cli/shadpkg extract \
  "ROMS_FINAL/ps4/Ratchet and Clank/Ratchet.and.Clank.v1.07.PATCH…/….pkg" \
  /mnt/data/distrobox/gaming/tmp/rac-patch
rsync -a tmp/rac-patch/ tmp/rac-base/ && mv tmp/rac-base Games/ratchet-clank-cusa01047
```

Two quirks that mattered:

- `shadpkg` extracts the game files but **never writes `sce_sys/param.sfo`**, so
  ReCasted sees the dump as `UNKNOWN`. The role writes one with
  `scripts/recasted_param_sfo.py` (`TITLE_ID=CUSA01047`, `APP_VER=01.07`) when
  it is missing; the launcher also reads it for the title/version.
- The bundled `patches.bin` is cut for the **CUSA01073 v1.09** image. Applied to
  this v1.07 dump it corrupts the code (`rcgpu_handle_fault`, guest fault at
  `0x184a9ec`). The launcher therefore boots with `RC_NO_PATCHES=1`.

## Presentation

`bin/recasted` focuses DP-1 and runs the game under gamescope
(`-W 3840 -H 2160 -r 60 -f`) with `RC_NEO_MODE=1` and `RC_RES=1440p`: the PS4 Pro
Neo path renders at 1440p and reconstructs toward 4K with IGTI. Logs confirm
`video ok 3840x2160`, `sceKernelIsNeoMode -> 1` and the Vulkan presenter ready.
The GUI (`--launcher`) still has the original presets, display and settings
tabs; its 1080p/60 and Neo presets write the same switches, but any preset that
re-enables the v1.09 patches will crash this dump.

## Status here

The game boots to the title screen fullscreen at 4K with Neo mode on, from the
USA v1.07 dump. **Not verified:** gameplay past the title screen, controller
mapping, the 60 FPS target and level streaming — those need a play session.
Upstream's "fully playable" claim is for the EU CUSA01073 v1.09 dump; if a v1.09
USA patch turns up, the launcher can drop `RC_NO_PATCHES=1` (the synthesized
param.sfo stays harmless either way).

## Notes

- The loader is game-specific: it will not run other PS4 titles (use shadPS4 for
  those).
- Upstream is a GitLab project (no GitHub Releases API), so ogm tracks the
  project page for update badges; bumps are pinned by SHA256 in `dg_recasted_*`.
- The extracted dump is derived from the owned PKG and is not backed up; only
  the loader's `user/` data is.
