# SymphonyRecomp (Castlevania: SotN) — `install_sotn_recomp`

BlackLabelHQ's native **recompilation** of Castlevania: Symphony of the Night
(PS1). Opt-in role; installed 2026-08-09. Not a decomp and unrelated to the SOTN
Decomp project — see the upstream repo.

- **Distribution:** a prebuilt, **framework-dependent .NET 10** app (no build
  step). Renders with **OpenGL** (Silk.NET/GLFW); SDL2 + OpenAL are bundled.
- **You must provide** a legally-owned **NTSC-U (SLUS-00067)** PS1 rip as a
  2-track split **bin/cue** in `<install>/disc/`.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-sotn-recomp.yml        # or: site.yml --tags sotn_recomp
scripts/install-host-launchers.sh               # refresh the host menu entry
ansible-playbook install-sotn-recomp.yml -e dg_sotn_recomp_revert=true
```

Launcher: `{{ dg_box_home }}/bin/sotn-recomp` (menu: **"Symphony of the Night
(Recomp)"**). It points the .NET apphost at the system runtime, focuses DP-1,
and **forces the NVIDIA GLX vendor + PRIME offload** — the recomp is OpenGL, and
on this AMD-iGPU + RTX box GLX otherwise defaults to the iGPU/llvmpipe → black.
Verified booting on the RTX (`[Gpu] … NVIDIA GeForce RTX 5090`, backend `Gl45`).

## The disc

The recomp needs these exact files in `<install>/disc/`:

```
Castlevania - Symphony of the Night (Track 1).bin   (MODE2/2352 data)
Castlevania - Symphony of the Night (Track 2).bin   (CD audio)
Castlevania - Symphony of the Night (USA).cue
```

This box has the NTSC-U rip split across two redump tracks whose byte total
equals the CHD exactly (Track 1 in `psx-usa/…`, Track 2 in `psx/…`), so the role
**symlinks** them in (no copy — the ~583 MB stays on the NAS) and writes the cue.
Point `dg_sotn_recomp_track1_src` / `dg_sotn_recomp_track2_src` at your own rip
if the layout differs. A CHD can be split with `chdman extractcd` + a bin
splitter if you only have the compressed image (note: this build's `chdman
--splitbin` errored, so split with `binmerge` instead).

## Disc auto-load

On first launch the app writes `settings.json` with an **empty `CdPath`** and
then sits on its **Disc Setup / Disc Picker** screen (blank grey ImGui panels —
looks stuck). The role pre-seeds `settings.json` with `CdPath` pointed at the
staged cue so it loads the game immediately. If you ever wipe `settings.json`,
either re-run the role or set the disc via the app's Disc Setup panel.

## Notes

- The build self-checks GitHub for updates on launch (`[AutoUpdater]`); dev
  builds don't auto-update. Bump `dg_sotn_recomp_version` + `_asset_sha256` to
  move to a newer release.
- Re-extracting on a version bump preserves the existing `disc/`.
