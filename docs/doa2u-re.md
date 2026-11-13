# Dead or Alive 2 Ultimate — DOA2U PC Port (Moonalesca fork)

[Moonalesca/doa2u-re](https://github.com/Moonalesca/doa2u-re) is a fork of
[NoRain211/doa2u-re](https://github.com/NoRain211/doa2u-re): a static
recompilation of the Xbox *Dead or Alive 2 Ultimate* executable with a
hand-written runtime. On Linux it renders through **SDL_GPU (Vulkan)** with
shaderc-compiled shaders, SDL3 audio and controllers — no Wine.

The fork adds a **dynamic KO replay** (three of the game's own replay cameras,
the last at 85% speed), **DOA4 hit voices** (when you import your own DOA4
`snd.afs`), combo damage and life-bar changes, a two-page PC Settings screen,
and fixes for audio queueing, safari-stage reflections, window focus and AMD
exits. It is built on upstream 0.3.2 Alpha.

Upstream publishes a Windows-only bundle for this fork, so the role builds the
**Linux runner from the pinned tag** and its pinned lifter submodule. Managed
by `install_doa2u_re` / `install-doa2u-re.yml`; runs in the gaming distrobox.

## Game data and the in-place build

The release ships no runner and no game data: the game is built from your own
disc, once (~15–25 min in the box):

- ISO: `roms_heavy/xbox/Dead or Alive 2 Ultimate (USA, Japan) (En,Ja).iso` —
  the DOA Ultimate **Disc 2**. The lifter selects the executable by SHA-256 and
  **refuses other regions, versions and Disc 1**.
- `build_game.sh` reuses an `imported-disc` extraction from an earlier release
  when one exists (~4.1 GB), otherwise extracts the ISO into
  `private/imported-disc`. It then lifts the program to C (capstone 5.0.7 venv
  + the pinned `tools/xboxrecomp` submodule), verifies the manifest hash and
  builds the runtime and runner. Marker: `private/.dg-built`.
- The build chain is installed in the box: cmake, ninja, clang, Python, SDL3,
  git and shaderc. `extract-xiso` is already present; the build has a pinned
  download fallback.

Saves and the disc cache live in `private/play-disc` (Xbox UDATA/TDATA storage
inside it). The role adopts the newest `play-disc` from the previous release
when the new install has none, and prunes older release trees (each carries
4–5 GB) only after the new build marker exists. `play-disc` is in backups as
`doa2u-re`.

## Baseline

`private/launcher.json` (seeded once, later launcher changes win): **2160p**,
the game's own **16:9 widescreen**, **MSAA 8** (the SDL_GPU/Linux ceiling;
higher falls back), **SMAA**, all unlocks, stereo, intro movies kept, and
**KO Replay = dynamic**. **Hit voices are off**: they need your own DOA4
`snd.afs` and `ffmpeg` to import, which is not done here.

The game's frame pacing is its own Xbox flip-on-refresh at 60 fps. Launcher:
`bin/doa2u-re` → `run_game.sh`; the upstream `launcher.sh` window also works
for interactive changes. Controls: any SDL3 gamepad; keyboard player 1
(arrows=D-pad, Enter=Start, Z/X=A/B, A/S=X/Y, Q/W=White/Black, E/R=triggers).

## Status — bring-up alpha

Working on this install: the native runner builds, launches, loads the disc
from `private/play-disc`, writes its session log and renders through Vulkan.
Upstream lists boot, menus, character select, Story/Watch/attract, all story
endings, audio with HRTF/5.1, movies and 16:9 up to 4K as working. The Xbox
Live menus still stop the game (no online service). The fork's KO replay and
combo HUD build on Linux; hit voices, the Jukebox/mod loader and online play
were not exercised here.

## Updating

Bump `dg_doa2u_version` and `dg_doa2u_commit` (and the lifter revision) in
`group_vars/all/doa2u_re.yml`, then re-run. The ISO extraction and the
`play-disc` saves are reused, and older releases are pruned. Revert by removing
the install and launcher; the ISO is never modified.