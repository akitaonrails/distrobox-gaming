# Castlevania: Rondo of Blood — RondoRecomp

[gminustwo/RondoRecomp](https://github.com/gminustwo/RondoRecomp) is a static
recompilation of **Castlevania: Rondo of Blood** (PC Engine Super CD-ROM²) into
a native program. Upstream ships an official Linux AppImage; its Setup reads
your own disc, recompiles the game code to C and builds `rondo` with the
bundled Zig compiler. No game data is included.

```sh
cd ansible && ansible-playbook install-rondo-recomp.yml   # or site.yml --tags rondo_recomp
```

| | |
|---|---|
| Release | `v1.2` — `RondoRecomp-1.2-x86_64.AppImage` (83.9 MB, SHA256-pinned), staged in `ROMS_FINAL/PC/releases/` |
| Build/home | `tools/rondo-recomp/install` (`RONDO_HOME`) — `game/en`, `game/ja`, `build/`, `rondo` |
| Portable profile | `tools/rondo-recomp/user` — `settings.ini`, BRAM saves and save states |
| Discs | `ROMS_FINAL/tg16_cd/Akumajou Dracula X - Chi no Rondo (Japan).chd` and `Castlevania - Rondo of Blood (Japan) (Translated).chd` (both SHA256-pinned) |
| Launcher | `bin/rondo-recomp`; entry **Castlevania: Rondo of Blood · Recomp** |

## How it works

The AppImage is a read-only image carrying Setup, the SDK and Zig. Setup runs
from the box with `RONDO_HOME` pointing at the install folder, so the extracted
discs (`game/en`, `game/ja`) and the built `rondo` stay outside the image. Both
CHDs were imported: the Japanese original and the English fan translation, so
the game's **Language** option switches between them. The first disc triggers
the recompilation; the second is imported alongside it and the runner is
rebuilt.

A portable `user` folder next to the AppImage selects portable mode: options,
BRAM saves and save states live there instead of `~/.local/share`, which keeps
them stable across AppImage updates and inside the backup set.

The AppImage runs with `APPIMAGE_EXTRACT_AND_RUN=1` (the gaming box has no
FUSE), and the launcher enters the box itself.

## Baseline

`user/settings.ini` is seeded once with **fullscreen at the display's own
resolution**, 4:3 (the game's own picture), Fit, sharp filtering, blurred
sides on a wide screen, VSync, rewind, the start screen, and the Super
Castlevania IV moves (**8-way whip/doves** and limp whip). Cheats, Maria and
RetroAchievements start off; `check_updates=0` because the role manages the
pin. The in-game **F1 / Back** menu rewrites the file; later changes survive.

The original PC Engine game is 4:3, so on this 16:9 monitor the role uses the
game's 4:3 presentation with the picture's sides filled by the blurred
backdrop, rather than stretching. 4K output means the fullscreen window at the
display's resolution.

## Verified here

- Both discs imported and identified: Japanese original (fingerprint
  `DB4D9415EC501573`) and English translation, installed as `game/ja` and
  `game/en`.
- Recompilation and `zig cc` build completed: `install/rondo` plus
  `build/version.txt` (`1.2`).
- Bounded launch: fullscreen at **3840×2160**, the in-game video menu renders
  at 4K, and the window title reports the disc fingerprint. Gameplay, rewind,
  save states, RetroAchievements and controller input were not exercised.

## Updating

Bump `dg_rondo_version`, `dg_rondo_tag` and the AppImage SHA in
`group_vars/all/rondo_recomp.yml`, then re-run. The role replaces the AppImage
and runs `--setup-cli --rebuild` when `build/version.txt` no longer matches;
the extracted discs, `settings.ini`, saves and states stay in place. Revert
with `-e dg_rondo_revert=true`; the CHDs are untouched.