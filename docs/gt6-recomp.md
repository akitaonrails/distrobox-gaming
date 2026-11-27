# Gran Turismo 6 (Recomp) — Project Grand Tourer Advanced

[PrimeTimerer/Project-Grand-Tourer-Advanced](https://github.com/PrimeTimerer/Project-Grand-Tourer-Advanced)
is a static recompilation (`ps3recomp` + Direct3D 12) of **Gran Turismo 6**
(PlayStation 3, European disc **BCES01893**, update **1.22**). Upstream ships a
Windows x64 D3D12 build; on this box it runs from the host through
**GE-Proton11-1** (VKD3D-Proton).

## Install

```sh
cd ansible && ansible-playbook install-gt6-recomp.yml
```

| Item | Path / Value |
| --- | --- |
| Release | `v20261125-2055` (`GT6_PC_20261125-2055.zip`, SHA256-pinned in `ansible/group_vars/all/gt6_recomp.yml`, staged in `ROMS_FINAL/PC/releases/`) |
| Owned disc | `ROMS_FINAL/ps3/Gran.Turismo.6.PS3-DUPLEX` (EU `BCES01893`, `GT.VOL` 15.4 GB verified, symlinked read-only as `game/dev_bdvd`) |
| Updates | Official PKGs `01.02`–`01.22` from `EmuDeck/roms_heavy/ps3-DLC/BCES01893/` plus `01.01` staged in `ROMS_FINAL/PC/releases/gt6-updates/`, extracted into `game/dev_hdd0/game/BCES01893` |
| Decrypted binaries | `game/EMAIN.ELF` (`d65b7e9c…`) and FW 4.93 `game/firmware/libsre.prx` + `libsre_image.bin` (`088bd136…`) prepared via the box's RPCS3 and verified against upstream SHA-256s |
| Install root | `{{ dg_box_home }}/tools/gt6-recomp/` (`releases/<ver>/`, `current/`, shared `game/`, `scratch/`, `logs/`, `GT6Menu.settings.json`) |
| Saves | `game/dev_hdd0/home/00000001/savedata/` + `GT6Menu.settings.json` — backed up by `backup-saves` under `gt6-recomp` |
| Launcher | `{{ dg_box_home }}/bin/gt6-recomp` (host-side GE-Proton11-1) |
| Desktop entry | **Gran Turismo 6 (Recomp)** (`gt6-recomp.desktop`) |

## Graphics & Performance

- `GT6Menu.settings.json` is seeded once (`force: false`, so in-game **F2** menu
  edits survive reruns) with `"MenuFullHd": true` and `"ScreenRealRes": 3`
  (**3840×2160** native 4K internal rendering).
- The launcher exports all upstream `PLAY_GT6.bat` GPU/audio/PDI acceleration
  flags (`GT6_AA=gpu`, `LD_GPU_AA=1`, `GT6_MOVIE_POST=gpu`, `LD_VTX_SLAB=1`,
  `LD_GPU_VERTEX_PULL=1`, `LD_PSO_PREWARM=1`, `GT6_AUDIO_AVX512=1`,
  `GT6_NATIVE_PDI_IRQ=1`, `GT6_NATIVE_PDI_LEAVES=1`, etc.) and pins the NVIDIA
  Vulkan ICD for VKD3D-Proton.
- Press **F2** in-game for the settings overlay (resolution, looser chase camera,
  LAN mode, trainer/unlocks).

## Gamepad Policy

Native SDL2 gamepad support (`SDL2.dll` bundled in the release) with
`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1` works out of the box with the 8BitDo
Ultimate 2.
