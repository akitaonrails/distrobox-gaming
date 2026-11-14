# Initial D arcade series — REA launcher

[akitaonrails/rea-teknoparrot-initial-d-series](https://github.com/akitaonrails/rea-teknoparrot-initial-d-series)
is one hub for the Initial D arcade games, from **Arcade Stage Ver. 1** (2002)
to **THE ARCADE Season 5** (2025). It does not use TeknoParrot: the NAOMI 2
games run in Flycast, Initial D 4/5 through a locally built lindbergh-loader,
and 6–8 / Zero / THE ARCADE through windowsarcadeloader and its GE-Proton.
Your dumps are only read.

```sh
cd ansible && ansible-playbook install-rea-initiald.yml   # or site.yml --tags rea_initiald
```

| | |
|---|---|
| Release | `v0.1.0` Linux tarball (602 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Install | `tools/rea-initiald/InitialDLauncher-0.1.0-linux-x86_64/` (hub, components, patches, scripts) |
| Data | `~/.local/share/rea-initiald/` — `launcher.cfg`, `settings/<game>.cfg`, `runtimes/<game>` saves, WAL prefix |
| Launcher | `bin/initiald`; entry **Initial D · Arcade Series** |

## Libraries and BIOS

`launcher.cfg` points at the NAS dumps:

```
library = /mnt/terachad/Emulators/EmuDeck/roms_rare/TeknoParrot
library = /mnt/terachad/Emulators/EmuDeck/roms_rare/naomi2
naomi2_bios = /mnt/terachad/Emulators/EmuDeck/roms_unstable/naomi/naomi2.zip
```

The `TeknoParrot` folder supplies ID4, ID5, ID6, ID7, ID8, Zero, Season 3 and
Season 5; the `naomi2` folder supplies Ver. 1, 2 and 3. The NAOMI 2 BIOS is the
`naomi2.zip` set Flycast needs.

The NAS also has `Emulation/bios/sys246` (the PS2-based System 246 BIOS) and
`Emulation/bios/chihiro` (the Xbox-based Chihiro BIOS). **Neither is used by
this launcher**: no Initial D title runs on System 246 or Chihiro. The series
uses NAOMI 2, Lindbergh, RingEdge, Nu and ALLS. Those BIOS folders are left
alone rather than being presented as if the hub consumed them.

## Components

The package brings windowsarcadeloader, its GE-Proton runtime, winetricks and
the Windows Flycast; Flycast for the NAOMI 2 games comes from the box
(`flycast-git`). Lindbergh-loader cannot be shipped (CC BY-NC-SA), so the role
builds the pinned source once on the host with Docker and installs it into
`components/lindbergh/`. That avoids needing Docker inside the gaming box; a
first Play on a machine without that prebuild would try to build it through
`docker`/`podman` itself.

Required in the box: `gamescope`, `bubblewrap`, `flycast-git`, `cabextract`,
a Vulkan driver and 32-bit OpenGL. The role installs the first four.

## Settings and controls

Each game starts fullscreen through gamescope at **3840×2160** with FSR 1
sharpening (the launcher's defaults), and its own render size is native unless
changed in the per-game page. Pads and wheels are read once by the hub: left
stick steers, RT/LT accelerate/brake, RB/LB shift, Y view, Start/A start, X
card, Back coin; wheel force feedback is played back for the Windows-built
games. Logs, saves and settings stay under the data folder; the game dumps are
mounted read-only around each title.

## Verified here

- `initiald-launcher --list`: **all eleven games identified as ready** — Ver.
  1/2/3 from `naomi2`, and ID4/5/6/7/8/Zero/Season 3/Season 5 from the
  TeknoParrot folder.
- lindbergh-loader built from the pinned source into
  `components/lindbergh/lindbergh.so`, so ID4/5 no longer depend on a container
  runtime inside the box.
- The hub opens fullscreen at 3840×2160 (window class `rea-initiald`).
- A bounded `--play id1 --headless --seconds 20` run booted Flycast from the
  NAS dumps, read the **NAOMI 2 BIOS** at `naomi2.zip`, reported
  `NAOMI GAME ID [INITIAL D]` and initialised its EEPROM before the timer
  stopped it.
- A race was not driven interactively during this install. The launcher's own
  release notes record all eleven games played on Linux; wheel/force feedback
  and speaker sound remain unverified here.

## Updating

Bump `dg_initiald_version`, the asset name and SHA256 in
`group_vars/all/rea_initiald.yml`, then re-run. `launcher.cfg`, per-game
settings and `runtimes/` saves are kept. Revert with
`-e dg_initiald_revert=true`; the dumps and BIOS are never modified.