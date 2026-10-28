# F-ZERO GX — F-ZERO GLINUX

[Mabec-games/F-ZERO-GLINUX](https://github.com/Mabec-games/F-ZERO-GLINUX)
wraps a Dolphin-derived runtime (**ModernGekko**) in a controller-friendly
launcher with resolution presets, AA, HD-texture/graphics mods and online play.
It is a native Linux build — no Wine, but it renders through the box's Vulkan
stack, so it runs inside the `gaming` distrobox.

```sh
cd ansible && ansible-playbook install-fzero-glinux.yml
```

| | |
|---|---|
| Release | `v0.9`, `F-ZERO-GLINUX-0.9-glibc2.35-x86_64.AppImage` (pinned + sha256) |
| AppImage | `tools/fzero-glinux/0.9/` (unpacked with `--appimage-extract`, no FUSE needed) |
| Game data | `~/.local/share/fzero-glinux/games/GFZE01/` (1.4 GB, extracted once) |
| Settings | `~/.local/share/fzero-glinux/config.ini` |
| Launcher | `bin/fzero-glinux` (`--launcher` opens the GUI), entry **F-ZERO GX · GLINUX** |

## Disc

Upstream asks for **F-ZERO GX USA (GFZE01)** as ISO or RVZ, and this build
checks **only the 6-byte disc id** — no hash, no revision gate. The library has
no plain GX image: `gc/F-Zero AX (Patch)/F-Zero AX (Patched).iso` is GX with
the AX arcade mode unlocked, and its header still reports
`F-ZERO GX (US Version)` / `GFZE01`, so it extracts and boots (as AX content).

Extraction is the launcher's own headless import — the one non-GUI entry point:

```sh
GLINUX_USER_DIR=<user dir> squashfs-root/AppRun --extract "<iso|rvz>"
```

It is idempotent ("Using existing extraction" re-verifies the extracted files'
hashes), which is what the role's `creates:` guard relies on.

## Widescreen: yes, natively

Two things have to line up, and the role sets both:

1. `config.ini` → `[Video] aspect_ratio = 16:9` (allowed values:
   `preserve`, `16:9`, `4:3`). This is the render aspect; no widescreen hack is
   involved.
2. The game's **own Screen Mode = 16:9**, saved on the memory card. Upstream
   ships a memory patch for that — `$Default Native 16:9 Widescreen on New
   Save` (`0x8027DC0C:dword:0x38600001:0x4BFE3AED`) — in
   `Sys/GameSettings/GFZE01.ini`, but the launcher writes a **user-side**
   `GameSettings/GFZE01.ini` containing only its unlock cheats, and the user
   copy shadows the system one. The role re-adds the `[OnFrame]` /
   `[OnFrame_Enabled]` block there (idempotent, marker-delimited), so new saves
   start in 16:9.

An existing save that was created at 4:3 keeps its aspect until it is changed
in the game (**Options → Screen Mode**), which is a card-side setting the role
does not rewrite.

## Graphics

The `config.ini` `[Video]` block the role keeps:

| Key | Value | Why |
|---|---|---|
| `resolution` | `2560x1440` | **Vulkan + this build**: the 3840×2160 preset exits immediately and silently (rc 0, no window) both windowed and fullscreen; 1440p holds 59.9 FPS on the 5090. 4K would need gamescope around a 1440p render — untested |
| `aspect_ratio` | `16:9` | native widescreen, see above |
| `anti_aliasing` | `msaa4` | upstream offers `off`/`fxaa`/`msaa4`; 4x MSAA is the sharpest option and free here |
| `anisotropy` | `16` | from the default 1 |
| `backend` | `Vulkan` | the box's NVIDIA ICD |
| `fullscreen` | `true` | borderless fullscreen on the 4K display |
| `vsync` | `true` (default) | the runtime's own pacing; the title reports ~59.9 FPS |

The GUI launcher's own presets are 480p / 800p / 720p / 1080p / 1440p / 4K —
the role writes the equivalent keys directly instead of clicking them.

## Controller

The runtime reads GameCube pad bindings from `Config/GCPadNew.ini`, and this
build leaves that file **empty**, which reads as "no pad at all" — the reason
pad input did nothing in a fresh profile. A profile now exists for the
reference pad:

```
[GCPad1]
Device = SDL/0/8BitDo Ultimate 2 Wireless Controller
Buttons/A|B|X|Y = the face buttons, Z = Shoulder R | Shoulder L | Back,
Start
Main Stick / C-Stick = Left/Right X±, Y± (deadzone 5.00)
Triggers L/R + L-Analog/R-Analog (deadzone 5.00, threshold 85.00)
D-Pad, Rumble/Motor
```

`config.ini` also ends up with `[Input] controller1=SDL/0/8BitDo Ultimate 2
Wireless Controller`. If the pad is renamed or a different controller is used,
regenerate from **CONTROLLER → Generate GameCube controller profile** in the GUI
launcher (`fzero-glinux --launcher`); the role only seeds the file when it is
missing or empty, so a generated profile is never overwritten.

In-game pad input has **not** been exercised yet (the runtime boots and the
profile is in place); treat the bindings as configured-but-unverified.

## Notes

- `--allow-interpreter` is mandatory: this release ships no static-recomp
  module, so the runtime refuses to boot without it (README's "JIT" wording
  notwithstanding). `--headless` is broken in 0.9 (ImGui assert), so a smoke
  test needs a real display.
- Saves live in `~/.local/share/fzero-glinux/GC/USA/Card A/` — never wipe that
  on upgrade.
- The GUI launcher is a settings tool here: `bin/fzero-glinux --launcher`.
