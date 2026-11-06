# UltraTears — Tears of the Kingdom (native static recompilation)

[UltraTears](https://github.com/kuraeow/ultratears) is an MZ-Labs-style **static
recompilation** of *The Legend of Zelda: Tears of the Kingdom* (Switch, **1.4.3**):
the owned title is turned into native C, compiled on this machine into a Linux
game, and played by a native **SDL3 + Vulkan** runtime. No Switch emulator is
involved. Opt-in role `install_ultratears` (data in
`group_vars/all/ultratears.yml`).

- **Role:** `install_ultratears` — `ansible-playbook install-ultratears.yml`
  (or `site.yml --tags ultratears`).
- **Upstream:** `kuraeow/ultratears`, Linux `UltraTears.AppImage`, pinned by
  version + sha256.
- **Needs:** a pre-extracted **1.4.3** `exefs/`+`romfs/` dump (see below). The
  box needs kernel 6.7+, glibc 2.34+, Vulkan 1.3 + `VK_EXT_shader_object`.
- **Install size:** ~28 GB built game on the NVMe box home
  (`tools/ultratears`); the 16 GB dump stays on the NAS, read once at build.

## Producing the dump (one-time prerequisite)

UltraTears **refuses encrypted packages** (`.xci`/`.nsp`/`.nca`) and reads no
keys — it only accepts the ExeFS + RomFS of 1.4.3 as **plain files**. You
produce that dump once from your own copies with
[`scripts/totk-dump-extractor`](../scripts/totk-dump-extractor/README.md):

```sh
cd scripts/totk-dump-extractor
dotnet run -c Release -- \
  "<base>.xci" "<update-1.4.3>.nsp" \
  "$HOME/.local/share/eden/keys/prod.keys" "$HOME/.switch/title.keys" \
  "<dg_ut_dump_dir>"     # .../roms_heavy/switch/UltraTears-TOTK-1.4.3-dump
```

Merging the base RomFS with the 1.4.3 **BKTR** update patch is something only
the full **.NET LibHac** does — `hactool` (even git master) reports
`Invalid BKTR layout` on 1.4.3, and the Rust ports don't implement BKTR. The
tool pulls **LibHac 0.19.0 from NuGet**, independent of the DMCA'd GitHub
mirrors. See that README for the `title.keys` (encrypted-titlekey) detail. The
result (`exefs/` 5 files, `romfs/` ~304,243 files / 16 GiB) is staged on the NAS
and consumed like a ROM; `setup.py --check-dump` confirms it is TOTK 1.4.3
cryptographically, so the role pins no checksum on the 19 GB tree.

This mirrors `scripts/recover-smas-25th-rom.py`: the role verifies and builds
from the artifact, the script reproduces the artifact if it is lost.

## How the role builds it

The AppImage is a **builder package** — `tools/setup.py` builds the game **in
place** in the package root. The role lays the package down in
`tools/ultratears`, then (only while `linux/ultratears` is absent, or after an
AppImage version bump) runs the bundled builder headlessly:

```sh
deps/python/bin/python3.14 tools/setup.py --dump <dump>   # ULTRS_SKIP_GPU_CHECK=1
```

Nine steps — check → romfs → lift → compile → shaders → **graphics** → textures
→ finish — take ~15–40 min (32 threads). The **graphics** step compiles all
~28,667 shaders for this box's GPU (verified: *NVIDIA GeForce RTX 5090*) ahead
of time, headless, so first launch has no shader-compile wait. `setup.py` is
resumable/idempotent and rebuilds only what a later version changes; re-running
the role after a bump refreshes the builder files (rsync without `--delete`,
preserving `data/` and `userdata/`) and rebuilds the changed steps only.

`ultratears.cfg` is just a path manifest (`exefs`/`romfs`/`shaderpack`/
`compiled`/`textures`/`saves=userdata`/`fonts`); there are **no graphics knobs**
in it — the quality ceiling is set at the window/compositor (below).

## Graphics — native Wayland 4K/60 (important)

The game boots **fullscreen on its own**; the launcher only focuses `DP-1`
first so it lands on the main 4K panel. The quality ceiling for this NVN→Vulkan
recomp is **native 4K output + the game's built-in 60 FPS** — it exposes no
PC-style internal-resolution multiplier (it renders at the title's native layer
resolution).

**The one non-obvious setting: `SDL_VIDEODRIVER=wayland`.** The bundled SDL3
otherwise picks x11 (XWayland), where the Vulkan swapchain present **throttles
to ~2–14 FPS** on this fractional-scale (1.5) 4K panel. Native Wayland presents
the Vulkan WSI directly and locks a clean **60 FPS at true 3840×2160**
(scale-aware). The launcher sets it, plus the nvidia Vulkan ICD pin (not the
AMD/Intel iGPU). Verified: title screen + in-game at 4K/60 on `DP-1`.

## Gamepad

8BitDo works natively through the bundled **SDL3** (Switch button layout: A is
the right button), like the other SDL recomps on this box. The launcher sets
`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`. Keyboard also works (WASD move, arrows
camera, J=A, K/Space=B, I=X, U=Y, Q/E=L/R, Alt/Shift=ZL/ZR, Enter=+, Tab/Esc=−,
TFGH=d-pad, F11/Alt+Enter fullscreen).

## Saves & backups

Saves live in `tools/ultratears/userdata` (`account.uid`, `save/<hash>`),
registered as the `ultratears` set in `dg_save_sets` — backed up by
`~/.local/bin/backup-saves` on the host, restored by
`~/.local/bin/restore-saves` / `restore-saves.yml`. The
game is rebuilt from the NAS dump on a from-scratch rebuild; only `userdata`
carries real state.

## Revert

```sh
ansible-playbook install-ultratears.yml -e dg_ut_revert=true
```

Removes the launcher, the install tree and the desktop entry. **The saves under
`userdata` go with it** — run `~/.local/bin/backup-saves` first. The NAS dump is
untouched.

## Gotchas

- The launcher is single-instance (`/run/user/1026/ultratears-launcher.lock`).
  A second launch pops a zenity "already running" dialog and exits; that stray
  dialog, if focused, steals focus from the game and the compositor throttles
  the unfocused window. Launch once.
- The launcher's process `comm` truncates to **`ultratears-laun`** (15-char
  kernel limit), so `pkill -x ultratears-launcher` never matches it — use
  `pkill -x ultratears-laun` or the full path. The in-place game binary is
  `ultratears` (`pkill -x ultratears`).
