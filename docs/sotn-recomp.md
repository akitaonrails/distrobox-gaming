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
Verified on the RTX at **v0.5.1b** (`[Gpu] … NVIDIA GeForce RTX 5090`, backend
`Gl45`) — the disc loads and the engine reaches its main game overlay
(`[Dispatcher] loaded overlay: main`). v0.5.x also bundles a Vulkan backend
(`Silk.NET.Vulkan.*`); the launcher still uses the OpenGL/GLX path that renders
on the RTX. Requires the .NET 10 runtime (box has `Microsoft.NETCore.App 10.0.11`).

## The disc

The recomp needs these exact files in `<install>/disc/` (names per the upstream
README, rewritten 2026-09-27 — the `"(USA)"` in the bin names is REQUIRED):

```
Castlevania - Symphony of the Night (USA) (Track 1).bin   (MODE2/2352 data)
Castlevania - Symphony of the Night (USA) (Track 2).bin   (CD audio)
Castlevania - Symphony of the Night (USA).cue             (with INDEX lines)
```

The role **symlinks** the EmuDeck rip (`roms/psx/Castlevania Symphony of the
Night (US)/`) in VERBATIM — filenames and cue content already match the spec
byte-for-byte. Override `dg_sotn_recomp_disc_src_dir` if your layout differs.
A CHD also works upstream (ours is
`ROMS_FINAL/psx/Castlevania - Symphony of the Night (USA).chd`).

**Root cause of the 2026-08 crash park (issue #9):** the old role staged bin
names WITHOUT `"(USA)"` and its self-written cue referenced those names — the
RecompOne `CueBinImage` parser only registers tracks on `INDEX 01` lines and
emits exactly our `read outside data track` + `packs=0` when the disc layout
doesn't line up, killing the game ~2s after start. **Fixed 2026-10-03** by
staging the README-verbatim set: boot-verified — GL 4.5 context on the RTX
5090, disc reads OK, and the game reaches its interactive first-run legal
screen instead of crashing (4 deterministic `read outside data track` probe
warnings at startup are benign — same LBAs every boot). Note: the legal
screen's "I understand" button needs a real mouse click (ImGui modal; wtype
keyboard injection doesn't press it).

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

> **2026-11-10 release check:** v1.1.2p is available, but the PS1 disc is no
> longer under `dg_sotn_recomp_disc_src_dir` (the library holds Castlevania
> Chronicles, not Symphony of the Night), so the role cannot re-run and the pin
> stays at v0.5.1b. Restore the redump split bin/cue, then bump and rerun.
