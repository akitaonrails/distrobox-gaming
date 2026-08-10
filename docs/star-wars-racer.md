# STAR WARS Episode I: Racer (GOG classic) — `install_pc_racing` + `install_swracer_mods`

The GOG re-release of the 1999 LucasArts podracer, run under Wine in the
`gaming` distrobox. Base game is a data entry in the shared `install_pc_racing`
pipeline (slug `star-wars-racer`); mods are a small opt-in set
(`install_swracer_mods`). Installed 2026-08-09.

## Base game (`install_pc_racing`)

```sh
cd ansible
ansible-playbook site.yml --tags pc_racing -e '{"dg_pc_racing_selected_slugs":["star-wars-racer"]}'
```

- **Source:** the GOG **offline** installer (`setup_star_warstm_episode_i_-_racertm_1.0_hotfix3_(20791).exe`)
  in `ROMS_FINAL/PC/`. NOT the `GOG_Galaxy_*.exe` web-installer stub (that is a
  .NET Galaxy downloader, useless offline). Extracted with `innoextract`
  (`innoextract_root: "."` — this old GOG layout puts `SWEP1RCR.EXE` + `data/`
  at the archive root, not under `app/`).
- **Render path:** 32-bit DirectDraw/D3D7 game. GOG bundles a `ddraw.dll` that
  wraps to **D3D9**; with **DXVK** that becomes D3D9→Vulkan, which gamescope can
  present (unlike CMR1's builtin GL-ddraw path). `WINEDLLOVERRIDES`
  `ddraw,dinput,dsound,wsock32=n,b` loads the bundled natives first (Lutris GOG
  recipe). NVIDIA Vulkan ICD pinned so DXVK stays on the RTX 5090 (dual-GPU box).
- **The "Please reinstall program" trap:** `innoextract` skips the installer's
  **registry** writes, and `SWEP1RCR.EXE` reads the `CD Path` value under
  `HKLM\SOFTWARE\WOW6432Node\LucasArts Entertainment Company LLC\Star Wars: Episode I Racer\v1.0`
  (32-bit → WOW6432Node) to pass its install check. The role seeds `CD Path`,
  `Install Path`, `FullScreen=1`, and `Display Width/Height=1280x960`. Without
  the display values it also defaults to a tiny windowed 640×480 top-left.
  (`CD Path` has **no** trailing backslash — the game finds data via the working
  dir; a trailing `\` only breaks the role's shell quoting.)
- **Display:** it is a 4:3 game. It renders 1280×960 and gamescope `-S stretch`
  distorts that to fill the 16:9 4K panel (user preference: fill the monitor).
  True widescreen would need a swe1r-patcher/mod, not done here.

### Controller (8BitDo Ultimate 2)

Works through Wine's **builtin DirectInput** — no Xidi, and force-feedback is
available. A playable control map is **seeded once** (marker-guarded, so any
in-game rebinds survive) as `data/config/current/current_control.map`:

| Input | Action | | Input | Action |
|---|---|---|---|---|
| Left stick | Steer (X) + pitch (Y) | | **A** | Thrust |
| **RT** | Accelerate (analog, Z+) | | **B** | Brake |
| **LT** | Brake (analog, Z−) | | **X** | Repair *(only when damaged)* |
| **L1 / R1** | Air-brake (Slide) | | **Y** | Boost *(only after the turbo charges)* |
| **Back/Select** | Look back | | **RS-click** | Camera cycle |
| **Start** | ESC / pause *(evsieve bridge)* | | | |

Notes: button numbering is **1-based** (A=`BUTTON=1`, verified). Repair and
Boost are **contextual** — they do nothing until the pod is damaged / the turbo
is charged, which reads as "dead buttons" when idle. SW Racer has one air-brake
("Slide"); holding it while steering tightens the turn. There is no bindable
pause function (ESC is hardcoded), so **Start→ESC is bridged with `evsieve`** at
the input layer (`--copy`, non-grab, same technique as CMR1). Rebind anything in
the game's **Configure Controller** menu; changes persist (the seed never
overwrites an existing map).

## Mods (`install_swracer_mods`)

```sh
cd ansible
ansible-playbook install-swracer-mods.yml          # or: site.yml --tags swracer_mods
ansible-playbook install-swracer-mods.yml -e dg_swracer_mods_revert=true
```

Nexus archives are preserved under `dg_swracer_mods_staging_root`
(`ROMS_FINAL/PC/NexusMods/star-wars-racer/`); a Premium API key auto-downloads,
else stage manually. Originals are backed up under
`<game>/.dg-mod-backups/<mod-id>/` and each mod is marker-guarded + idempotent.

| Mod | Nexus | Status | Notes |
|---|---|---|---|
| **Starfighter's Audio Overhaul** | mod 5 | ✅ installed | Loose-file audio swap: 7 film-sourced pod `.wav`s overwrite `data/wavs/22K/` (22050 Hz — the game's high-quality set; needs audio quality on High, the default). Dependency-free. Untested-on-GOG upstream, works here. |
| **StixsworldHD's HD-4K Experience** | mod 2 | ⛔ excluded | NOT a texture pack — the 2 KB archive is a **ReShade preset** (+ dgVoodoo2). ReShade is avoided under distrobox/Wine (`feedback_avoid_reshade_mods`). Archive preserved on the NAS, not installed. |

To revert the audio to stock: `-e dg_swracer_mods_revert=true` (restores the
backed-up originals).
