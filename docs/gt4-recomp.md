# Gran Turismo 4 Recompiled

Optional [moesuito/gt4-staticrecomp](https://github.com/moesuito/gt4-staticrecomp)
**v1.3.0-rc6** portable build, its standalone `game/gt4.exe` run in the `gaming`
box with Wine. Install from `ansible/` with `ansible-playbook
install-gt4-recomp.yml`; the `gt4_recomp` tag also runs it from `site.yml`.
The role downloads the pinned portable ZIP and GSdx package (reusing a staged
copy in `PC/releases` when it is already there), extracts into
`dg_gt4r_130_release`, stages the prepared executable built once from the owned
ISO with upstream `gt4l-disc`, seeds the memory card, and installs
`gaming-gt4-recomp.desktop`. Saves live in the port's own card under
`dg_gt4r_130_release/data/memcards/gt4.ps2`.

## Disc compatibility and Spec II

The selected `dg_gt4r_iso` is USA retail SCUS-97328. Its entire ISO has
SHA256 `e4d22e964729739e89099d42828a55b75cd0e1ff702ea85a3a5d793733dc1981`.
Its `SYSTEM.CNF` says 1.01, so it differs from upstream's pinned full v2.00
image; the `CORE.GT4` and boot executable **do** match upstream's pinned game
code. The role checks the whole local image, and the helper verifies the core
and the reconstructed executable against upstream pins. The final executable
hash is `10f82e2231a51404b95682ed3ea81171100a1af2fefdeed3391943016c7c935c`.

The separate EmuDeck image is SCUS-97436 (Spec II). v1.2.3's disc setup
explicitly rejects that serial; its [Spec II study](https://github.com/moesuito/gt4-staticrecomp/blob/v1.2.3/docs/SPEC2-STUDY.md)
describes a separate target. Do not feed that image or the Spec II xdelta to
this release. Continue using Spec II in PCSX2; the retail recomp can coexist.

## Display, frame rate and controller

The desktop launcher uses the **PCSX2 GSdx renderer process**
(`GT4_RENDERER=pcsx2`, `game/gs/gt4-gs.exe`) with
`[EmuCore/GS] upscale_multiplier = 6` (`dg_gt4r_upscale_multiplier`, written
to `data/config/gt4-gs.ini`): 6 × the PS2's 640×448 = **native 3840-wide
rendering**, plus GSdx's Automatic deinterlacing for the 480i menus. It
selects the 4K landscape monitor (`dg_gt4r_monitor`), 3840×2160 output, GT4's
progressive 480p and widescreen modes, and FIFO present mode. The game engine
is fixed at 60 Hz; the 60 FPS cap is a target, not a measured gameplay
benchmark. The port does not expose an Ultra graphics preset.

The alternative compiled-in renderer (`GT4_RENDERER=donor`) is **capped at
native PS2 resolution** ("scale=1") and does not deinterlace the menus — at
4K it reads as a soft, flickering picture, which is why GSdx is the default
here. Verified 2026-10-28: `renderer PCSX2 GS Vulkan x6`, both the host and
the GS child window at 3840×2160 on DP-1.

Native SDL3 pad input is selected (`GT4_INPUT=sdl`). The Wine prefix routes
controllers through WineBus SDL with controller mapping enabled; the game's
default bindings cover steering, throttle, brake and menu navigation. Input
enumeration and a full race with a connected pad should be checked in-game.
The `8BitDo Ultimate 2` receiver was present during setup, but no gamepad was
enumerated in the short smoke run, so button presses remain unverified.

## HD textures

The port loads **PCSX2 community texture packs without renaming** ("Load
custom textures" is on by default). The same NAS packs that the PCSX2 setup
links under `SCUS-97328`/`SCUS-97436` (see [gt4-spec-ii.md](gt4-spec-ii.md))
are symlinked into the port's `data/Textures/`:

| Pack | Source | Size |
|---|---|---|
| HD HUD & UI (Silentwarior112) | `Gran Turismo 4 Remaster/Gran Turismo 4 HD HUD & UI Texture pack by Silentwarior112/replacements` | 2.3 GB |
| HD HUD update 2.1 | `Gran Turismo 4 Remaster/update 2.1/replacements` | 137 MB |
| Blocky haze fix v2 | `Gran Turismo 4 Remaster/HD HUD & U.I. blocky haze fix v2/text files jap kor usa pal shared` | small |

Per-texture hashes are version-agnostic (work under both vanilla and Spec II
ELFs — and now the recomp's reconstructed executable, which matches upstream's
pinned game code).

## Cheats, money, easy mode

GT4Recomp has **no cheat, mod or money hook** — prizes and prices are compiled
into the recompiled game code, and no pnach system exists. The only moddable
surfaces are the HD texture packs above and the GSdx renderer settings. For
money/easy mode the working route is **save editing** with
[Nenkai/GT4SaveEditor](https://github.com/Nenkai/GT4SaveEditor) (Windows GUI,
.NET 9; edits credits, garage, event progress, used-car dealership): extract
the `BASCUS-97328GAMEDATA` save from this install's `data/memcards/gt4.ps2`
with [mymc](https://github.com/ps2homebrew/mymc-plus), edit, re-import —
while the game is not running. Not wired into the role (skipped on request,
2026-10-28); back up the card before editing.

## GT4Recomp v1.3.0-rc6 — direct launch (the GUI cannot run here)

**The upstream launcher GUI does not work under Wine.** It is a Tauri app that
needs the Microsoft Edge **WebView2** runtime; without it the program shows
*"GT4Recomp could not start its window: Microsoft Edge WebView2 is missing"*
and exits before drawing anything (the launcher log says
`ERROR WebView2 is missing: the native message is shown before any window`).
WebView2 under Wine is a dead end: the Microsoft installer stalls mid-install
and the Fixed-Version cab links expire.

So the role stages everything the GUI would have set up and starts the
**standalone `game/gt4.exe`** instead:

| The GUI would… | The role does |
|---|---|
| prepare the ELF from your disc | copies the pinned `dg_gt4r_elf` to `data/games/gt4/prepared/SCUS_973.28` |
| download the GSdx renderer | unpacks the pinned 1.2.1 archive into `game/gs/gt4-gs.exe` |
| manage the textures folder | symlinks the PCSX2 HD packs into `data/Textures/` |

Launcher `bin/gt4-recomp` (Walker entry **Gran Turismo 4 · Recompiled**): 4K
fullscreen, fifo present, donor renderer, 480p + widescreen forced,
`--memcard` for the port's own save card, and
`--disc "Z:/…/Gran Turismo 4.iso"` (Wine accepts forward-slash `Z:` paths).

### `--fullscreen` is mandatory in the standalone path

The standalone `gt4.exe` only creates its Win32 window when
`--fullscreen` is on the command line. `GT4_FULLSCREEN=1` alone is not
enough: without the flag the host window is never created, the audio thread
never starts, and the game boots into the void — it runs, waits at its first
prompt, and the desktop shows nothing. With the flag the log gains

```
[window] fullscreen start (GT4_FULLSCREEN)
[window] monitor \\.\DISPLAY2 (3840x2160 at 2160,0), output size 3840x2160, client 3840x2160
[window] real guest GPU output through native Vulkan
[audio] Windows PCM stereo16 48000 Hz, paced: 16 x 256 frames, ...
```

and the picture appears. Verified 2026-10-27: fullscreen 3840×2160 on the
Odyssey G8, Vulkan device = RTX 5090, retail disc mounted (146 files,
2,594,960 sectors), IOP modules loaded, memory card seen in slot 1, audio
stream live (`application.name = "Gran Turismo 4"`).

`GT4_MONITOR` must reach Wine with **two** backslashes
(`\\.\DISPLAY2`), so the launcher passes it through `env '…'` instead of
inside the quoted `sh -c` string — one level of shell escaping eats it
otherwise and the port refuses the value.

### Memory card

The standalone build has no default card path, so a fresh install stops at
"No memory card (PS2) inserted into MEMORY CARD slot 1" and cannot save.
The role seeds `data/memcards/gt4.ps2` **once** from the empty PCSX2 card
(`Mcd002.ps2`) and passes it with `--memcard`; after that the port owns the
file. Deleting it just re-seeds on the next playbook run.

### Placement (host Hyprland rule)

The port asks for 3840×2160 on `\\.\DISPLAY2`, but Hyprland hands a new
fullscreen window to whichever monitor is focused, which here is the
portrait screen — the 16:9 picture ends up squashed into a narrow strip on
the left. `~/.config/hypr/gaming.conf` pins it (see
[hyprland-gaming.md](hyprland-gaming.md)):

```ini
windowrule = monitor DP-1, match:class ^(gt4\.exe)$
windowrule = fullscreen on, match:class ^(gt4\.exe)$
```

**Spec II is not wired yet.** The standalone path runs retail only: Spec II
needs `data/games/spec2/prepared/SCUS_974.36` (an ELF derived from the Spec II
image — that preparation step is GUI-only in v1.3.0) plus the shipped
`gt4-spec2.exe`. Revisit when upstream adds a CLI preparation path or the GUI
runs under Wine.

## GT4Recomp 1.2.3 (retired)

The v1.2.3 release and its desktop entry were removed on 2026-10-27: no saves
existed and v1.3.0 supersedes it.

## Release tracking note

The sweep compares against **stable** releases, so it reports `v1.2.5` as a
candidate while the pin tracks `1.3.0-rc6` (a release candidate). The rc is
newer than 1.2.5 and is what is installed — the CANDIDATE line is expected,
not a missing update.

## Maintenance

The release archives stay in `dg_gt4r_cache` because the role uses them on
rebuilds. Scratch Cargo output is removed after executable preparation. The
dedicated Wine prefix and session directory contain settings/saves and should
be preserved. Change the version and hashes together when upgrading.
