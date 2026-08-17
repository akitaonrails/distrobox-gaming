# Ridge Racer Collection — Wanszai PC wrapper (`install_ridge_racer`)

[Wanszai *Ridge Racer Collection*](https://github.com/wanszai/Ridge-Racer-Collection)
— a **Namco System 22** frontend (Ridge Racer, Ridge Racer 2, Rave Racer) run
under Wine in the box. Same family as the Wanszai Sega Rally / Virtua Racing
wrappers (`install_sega_rally`, `install_model1`): a pinned GitHub release
extracted immutably and rsynced into a work dir that preserves generated state,
with the owned MAME ROMs linked in. Opt-in; installed 2026-08-17. **Verified
booting** — DXVK renders D3D11 on the RTX 5090 at 4K, ROM set accepted.

- **Form:** native Win64 `RRC.exe` (no .NET), renders through **D3D11 → DXVK**.
  Up to 4K, wheels + FFB, free online multiplayer, cross-play with the Xbox
  builds. Ships **no ROMs**.
- The GitHub repo is info-only in the browser; the actual build is the
  `RidgeRacerCollectionPC_1.1.0.zip` **release asset** (there are X360 / XSX
  variants too). We saw an empty release once — that was a GitHub 503, not a
  missing build.

## ROMs (BYO, MAME 0.150)

RRC's own help text wants these exact zips in its `roms/` folder next to the exe.
They're consolidated in the Wanszai source archive
(`dg_ridge_racer_rom_source_dir` = `ROMS_FINAL/PC/wanszai/ridge-racer/roms/`) and
the role symlinks them into the work dir:

| File | Notes |
| --- | --- |
| `ridgerac.zip`, `ridgeracb.zip` | Ridge Racer (`ridgeracb` is needed for the split set) |
| `ridgera2.zip` | Ridge Racer 2 |
| `raverace.zip` | Rave Racer — the World romset (README: World-only for now; staged from `raveracw.zip`) |
| `namcoc71.zip`, `namcoc74.zip` | C71/C74 MCU BIOS as MAME device zips — **built** from the `c71.bin`/`c74.bin` that live inside the game sets |

Box MAME (0.288) may flag these as incomplete vs post-0.150 BIOS splits; that's
expected — the sets are correct for the wrapper's 0.150 core (same situation as
Sega Rally `srallyc` / Model 1 `vr`).

## Install / run

```sh
cd ansible
ansible-playbook install-ridge-racer.yml       # or: site.yml --tags ridge_racer
distrobox-enter -n gaming -- {{ box_home }}/bin/ridge-racer-launch status   # ROM/prefix/pad check
```

Launch via the **Ridge Racer Collection** desktop entry (or
`bin/ridge-racer-launch`). The launcher pins the RTX Vulkan ICD (D3D11→DXVK must
not hit the AMD iGPU), applies the shared SDL pad policy, and adds a
**Select+Start** exit chord via `evsieve` (same as Sega Rally). Prefix:
`wineprefixes/ridge-racer-wanszai` (win64, GLX pin, vcrun2022 + dxvk). First boot
runs a ROM check — if a set is flagged, fix it in the archive `roms/` and relink.

## Xbox 360 version

The X360 build (`default.xex`) is separate, at
`EmuDeck/roms_heavy/xbox360/RidgeRacerCollection/` (Xenia). Cross-play works
between the PC and console builds.
