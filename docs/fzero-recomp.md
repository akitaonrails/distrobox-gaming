# F-Zero SNES Recompiled (`install_fzero_recomp`)

[mstan/FZeroSNESRecomp](https://github.com/mstan/FZeroSNESRecomp) is a native PC
build of the SNES **F-Zero**, a static recompilation on the shared `snesrecomp`
engine and `recomp-ui` launcher (the same family as the DKC recomps). It adds
widescreen (16:9 / 21:9 / 32:9 / Fit), high-refresh presentation (60–360 FPS),
display shaders (CRT Soft, LCD Grid, Sharp, Warm Composite, or your own GLSL),
a 12-slot save-state browser with thumbnails, rewind, and the optional
**BS F-Zero Deluxe** Satellaview content. Runs on the RTX — no emulator.

Unlike the DKC trilogy, upstream ships an **official native Linux AppImage**, so
this is a prebuilt-release role (no source build). You supply your own
**F-Zero (USA)** dump.

## Install

```sh
cd ansible
ansible-playbook install-fzero-recomp.yml    # or: site.yml --tags fzero_recomp
scripts/install-host-launchers.sh            # refresh the host menu entry
```

Launcher `bin/fzero`; host/Walker entry **"F-Zero · Recompiled"**; `ogm` id
`fzero`. Revert with `-e dg_fzero_revert=true` (removes the launcher + install
dir; your ROM is untouched — note that removes `saves/` under the install dir,
which the `backup_saves` role captures).

## How it works

- Downloads the pinned `FZeroSNESRecomp-linux-1.6.1-x86_64.AppImage` (sha256 in
  `group_vars/all/fzero_recomp.yml`) to `tools/fzero-snes-recomp/`.
- The role verifies your ROM is the expected F-Zero (USA) revision (headerless
  sha256 `bf16c3c8…`, sha1 `d3efd32b…`), matching the host's own check, and
  fails early with a clear message otherwise. It strips a 512-byte copier header
  first, so a headered `.smc` of that revision also passes.
- The launcher runs the AppImage with the **ROM as its first argument**:
  `resolve_rom()` takes `argv[1]` and returns before the launcher window is ever
  created, so the game boots straight in — **the GUI ROM picker never appears**.
  DP-1 focus + nvidia GLX offload are set in the wrapper. 8BitDo works via SDL.
- The wrapper `cd`s into the install dir so `config.ini`, `rom.cfg` and `saves/`
  (SRAM + save states) land there and stay stable/backed up.

In-game: **Settings > Display** for aspect + shader, **Mods** for widescreen /
presentation FPS / BS Deluxe. **F7** (or Select+R) opens the save-state browser,
**F8** (or Select+L) opens rewind (off by default; enable + set depth/interval
in the launcher's Settings). Stock and BS Deluxe keep separate state files
(`saves/fzero<N>.sav` vs `saves/bs-deluxe/…`).

## ROM

F-Zero (USA), No-Intro, 512 KiB headerless LoROM. The curated
`ROMS_FINAL/snes/F-ZERO.smc` copy already matches the recomp's baked-in sha256
exactly and is used as-is; override `dg_fzero_rom` if yours lives elsewhere (any
dump of that revision, `.sfc` or headered `.smc`, works).

## Updating

Bump `dg_fzero_release_tag` / `dg_fzero_asset_name` / `dg_fzero_asset_sha256`
(from the [releases](https://github.com/mstan/FZeroSNESRecomp/releases); take the
sha256 from the asset's `.sha256` sidecar) and re-run.
