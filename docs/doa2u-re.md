# Dead or Alive 2 Ultimate — native PC port (doa2u-re)

[NoRain211/doa2u-re](https://github.com/NoRain211/doa2u-re) `0.1.6-Alpha` is a
static recompilation of the Xbox DOA2U executable with a hand-written runtime.
On Linux it renders through **SDL_GPU (Vulkan)** with shaderc-compiled shaders,
SDL3 audio and controllers — no Wine. Managed by `install_doa2u_re` /
`install-doa2u-re.yml`; runs in the gaming distrobox.

## Game data and the in-place build

The release ZIP ships **no prebuilt runner** — the game is built from your own
disc, once (~15–25 min in the box):

- ISO: `roms_heavy/xbox/Dead or Alive 2 Ultimate (USA, Japan) (En,Ja).iso` —
  the DOA Ultimate **Disc 2** (the DOA2U disc). The lifter selects the
  executable by SHA-256 and **refuses other regions, versions and Disc 1**.
- `build_game.sh` extracts the ISO once into `private/imported-disc`
  (~4.1 GB), lifts the program to C (capstone 5.0.7 venv), verifies it against
  the manifest hash, compiles the runtime + SDL3 (bundled build) and the
  runner. Marker: `private/.dg-built`.
- Box prerequisites were already present: `extract-xiso`, Python 3.12, cmake,
  ninja, clang; the role installs `shaderc` for runtime shader compilation.

Saves and the disc cache live in `private/play-disc`, symlinked to
`~/.local/share/doa2u-re` so they survive version upgrades (also in backups).
Every character and costume starts unlocked.

## Baseline

`private/launcher.json` (seeded once, later launcher changes win): **2160p,
native 16:9 widescreen, MSAA 8** (the SDL_GPU/Linux ceiling; higher counts
fall back), **SMAA on**, stereo, intro movies kept. Frame pacing is the
game's own Xbox flip-on-refresh at 60 fps, including 4K rain stages.
Launcher: `bin/doa2u-re` → `run_game.sh`; the upstream `launcher.sh` window
also works for interactive changes. Controls: any SDL3 gamepad; keyboard
player 1 (arrows=D-pad, Enter=Start, Z/X=A/B, A/S=X/Y, Q/W=White/Black,
E/R=triggers).

## Status — bring-up alpha

Working: boot, menus, character select, Story/Watch/attract on every stage,
all story endings, audio with HRTF/5.1, movies, 16:9 up to 4K. Not yet played
through upstream: most characters' full Story, Versus, Tag, Survival, Time
Attack, Sparring. The **Xbox Live menus stop the game** (no online service).
An unsupported draw stops the game with a message in `private/play-logs`.
Known niggles: single dropped frame on The Burai Zenin peaks, safari stage
heat haze static. Sister projects exist for DOA3 and DOAXBV (also in
`roms_heavy/xbox`).
