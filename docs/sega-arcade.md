# Sega Arcade Systems (Model 2, Model 3, NAOMI 1/2)

> **Pre-configured NVRAM (Free Play / casual).** Arcade difficulty,
> lives, time, continues and Free Play are **not** config-file settings
> — each game stores them in binary NVRAM written from its own
> Test/Service menu (no global toggle, and the menus can't be driven
> headlessly). Instead the roles seed the standard **pre-configured
> NVRAM packs** from the NAS (Model 2 `NVDATA/*.DAT`, Supermodel
> `NVRAM/*.nv`, NAOMI `*.zip.nvmem/.eeprom`), which are the
> Free-Play + calibrated + English distributions. This gives unlimited
> credits/continues (the core of "easy") for ~44 Model 2, ~37 Model 3
> and ~97 NAOMI games. Seeding is **one-time** (guarded by a
> `.dg-*-seeded` marker so in-game changes you make later are never
> clobbered) and **non-destructive** (any existing NVRAM is moved to a
> sibling `*.pre-easymode/` backup dir first). Exact per-game
> difficulty/lives/time beyond what the packs set can't be verified
> from the binary NVRAM — if a specific game needs tuning, set it in
> that game's Test menu (Model 2/3: Test button; NAOMI: Service→Test),
> then copy the resulting NVRAM file back into the pack source so it
> stays reproducible.


The four Sega arcade ROM sets live under `{{ dg_emudeck_root }}/roms_rare/`
(`model2/`, `model3/`, `naomi/`, `naomi2/`) and each shows up as its own
system in ES-DE. Three different emulators cover them:

| System  | Emulator                | Install path                    |
|---------|-------------------------|---------------------------------|
| Model 3 | Supermodel (native)     | AUR `supermodel` package        |
| Model 2 | Model 2 Emulator (wine) | see its section below           |
| NAOMI 1/2 | Flycast (native)      | AUR `flycast-git` (already in)  |

## Sega Model 3 — Supermodel

Installed from the AUR as `supermodel` (a maintained release snapshot;
`supermodel-git` is orphaned, and `supermodel-bin` is an **unrelated AI
tool** — don't "upgrade" to it). The package ships two binaries:

- `/usr/bin/supermodel-binary` — the real emulator.
- `/usr/bin/supermodel` — a packaging wrapper that is **unusable from a
  frontend**: it drops its arguments (no ROM ever reaches the binary),
  requires a ROMs dir behind a zenity error, and seeds
  `~/.config/supermodel`, a path this build never reads.

The 0.3a binary resolves everything under **`~/.supermodel/`**
(`Config/Games.xml`, `Config/Supermodel.ini`, `NVRAM/`, `Saves/`).
Our `supermodel-launch` wrapper (deployed by `seed_configs` to
`{{ dg_box_home }}/bin/`) seeds that layout from `/usr/share/supermodel`
on first run, forces SDL onto XWayland (`WAYLAND_DISPLAY=''` — the
native Wayland GL context fails with "OpenGL initialization failed"),
and passes the ROM through. The ES-DE `model3` entry launches it.

Managed render settings (`dg_supermodel_settings` →
`~/.supermodel/Config/Supermodel.ini`, merged into the pre-staged file):
4K exclusive fullscreen (`FullScreen=1`), true widescreen FOV + wide
backgrounds (Model 3 has a real widescreen mode, unlike Model 2), New3D
engine, quad rendering, force feedback.

**Runs under gamescope** (like every other emulator here). Supermodel
only applies its 4K resolution in *exclusive fullscreen*, and that
mode-set fails on scaled XWayland ("Unable to enter fullscreen mode:
Couldn't find any matching video modes"); its windowed/borderless path
ignores the resolution entirely and opens a tiny native-res 496x384
window (which showed as ~330x256 at the 1.5 monitor scale — the "small
window, no game" symptom). gamescope presents a real 3840x2160 mode, so
the wrapper runs `gamescope -W 3840 -H 2160 -f -- supermodel-binary
<rom> -res=3840,2160 -fullscreen`. Supermodel is native (no wine) so
gamescope tears down cleanly when it exits.

Verified 2026-07-13: Daytona USA 2 and Scud Race boot and render
fullscreen at 4K on the RTX 5090 (GL 4.5 core profile) via the ES-DE
command path.

Controls: Supermodel's `JOY1_BUTTONn` is 1-based over the SDL joystick
button list, and on xpad-ordered pads (8BitDo dongle, Xbox) the
defaults land wrong: Start on Guide, Coin on L3, accel/brake on the
d-pad, gears 3/4 colliding with Back/Start. The managed
`dg_supermodel_settings` fix this: Start=Start, Coin=Back,
accel/brake=RT/LT, sequential shift on RB/LB (the 4-way shifter is
keyboard-only to avoid the collision). Verify with
`WAYLAND_DISPLAY= supermodel-binary -print-inputs`. Per-game overrides
go in sections named after the ROM set (e.g. `[ daytona2 ]`).

**Exit chord**: `Select+Start` quits — the `supermodel-launch` wrapper
runs an evsieve bridge (no grab) that injects Escape (Supermodel's
UIExit) on a virtual keyboard when the chord fires on any connected
pad. Note the chord necessarily also sends Coin+Start to the game for
an instant — harmless since you're leaving.

**No per-game config needed (unlike Model 2).** Supermodel is native
SDL with a single global mapping — there is no wine joypad-number split
and no per-game `.input` files, so the class of problem Model 2 had
cannot occur here. The pad's SDL axis layout was verified against the
kernel (`/proc/bus/input/devices` ABS bitmap `3003f` = X, Y, Z, RX, RY,
RZ + HAT0, the standard xpad order), confirming the managed mapping is
hardware-correct: steering = left-stick X, **accel = RT** (`RZAXIS`,
SDL axis 5), **brake = LT** (`ZAXIS`, SDL axis 2). Button numbers are
1-based over SDL's list, so `BUTTON8` = Start, `BUTTON7` = Back (Coin),
`BUTTON6`/`BUTTON5` = RB/LB (shift up/down), `BUTTON1` = A (view). The
pad is detected automatically (it's a clean `js0`); the only thing that
can't be verified without hands-on is per-button in-game feel.

## Sega Model 2 — Model 2 Emulator (Wine)

ElSemi's Windows-only Model 2 Emulator v1.1a, run under Wine by the
opt-in **`install_m2emulator`** role
(`ansible-playbook site.yml --tags m2emulator`; knobs in
`group_vars/all/m2emulator.yml`).

Source is the copy already on the NAS at
`{{ dg_external_games_root }}/M2emulator_1.1a` — the segaretro.org
download page is **captcha-gated**, so if that copy is ever lost, fetch
it manually in a browser from <https://segaretro.org/Model_2_Emulator>.

What the role does:

- Copies the emulator **box-local** to
  `{{ dg_box_home }}/emulators/m2emulator` (`rsync --ignore-existing`)
  because NVDATA (high scores), CFG (per-game inputs) and EMULATOR.INI
  are all mutated next to the exe — the NAS original is never run in
  place.
- Creates a dedicated wine prefix (`wineprefixes/m2emulator`) with
  `d3dx9`, `d3dcompiler_47` (the emulator compiles its `scripts/*.ps`
  pixel shaders at runtime) and `dxvk`.
- Symlinks the ROM dir as `ROMS/` next to the exe — the emulator always
  scans that subdir (README), which sidesteps `[RomDirs]` Windows-path
  backslash escaping entirely (a first attempt via ini_file produced a
  mangled `Z:\mnt\\terachad\...` value; don't reintroduce it).
- Manages EMULATOR.INI: `FullScreenWidth=3840`, `FullScreenHeight=2160`
  (fills the 16:9 output — see aspect note), `AutoFull=1` (safe —
  gamescope hosts the mode), 4x FSAA, bilinear, XInput on.
- Deploys `m2emulator-launch`: reduces ES-DE's `%ROM%` path to the
  romset name (`EMULATOR.EXE` takes names, not paths, and resolves the
  zip via the ROMS dir), runs `emulator_multicpu.exe` (the multicore
  build) under gamescope.

**Aspect ratio — 16:9 stretched (a deliberate compromise).** Model 2
games are 4:3 and the emulator has no true widescreen. A proper 4:3
pillarbox was attempted (emulator renders 2880x2160, gamescope
`-w 2880 -h 2160 -S fit`, plus a Hyprland `opaque` rule) but proved
**unstable with this emulator**: it starts centered with black bars,
then the `AutoFull` fullscreen mode-switch (~1s after launch) drifts
the surface off-centre and re-exposes gamescope's transparent letterbox
— the desktop bleeds through and the edges tear/blink in motion (a
screenshot forces a repaint and misleadingly looks correct; only OBS or
the naked eye shows the real state). Filling the whole 16:9 output
(FullScreenWidth = the gamescope width) sidesteps all of it — no
letterbox, no bleed, no drift. The ~33% horizontal stretch is accepted
as the stable trade-off (verified fine by the user). If a future
gamescope/emulator version fixes the drift, revert to the 4:3 approach
in git history (commit `1ee9d1c`).

The ES-DE `model2` system lists `roms_rare/model2/*.zip` and launches
through the wrapper. Verified 2026-07-13: Daytona USA and Sega Rally
boot and render (16:9) cleanly.

Controllers: the prefix gets the same winebus policy as the pc-racing
prefixes (`DisableHidraw=1`, `DisableInput=1`, `Enable SDL=1`,
`Map Controllers=1`) so Wine presents one clean XInput pad to the
emulator's `XInput=1` mode, and the launcher exports the pc-racing SDL
environment (`SDL_JOYSTICK_HIDAPI=0`, background events, the pad
allow-list). The `+xinput` trace confirms the emulator polls
`XInputGetState` with the 8BitDo on slot 0.

**Controller maps are pre-seeded, not hand-configured.** The stock
`M2emulator_1.1a` ships only `daytona`/`daytonam` `.input` files, and
those are a broken **two-device** setup (analog axes on joypad 1,
buttons/hats on joypad 2 — a wheel-plus-buttonbox arcade rig) that does
nothing with a single pad. The `.input` format is a flat array of
4-byte little-endian entries in the game's control display-order plus
an 8-byte analog-enable footer (keyboard = scancode in byte 0; button =
button# in byte-0 high nybble + joypad# in byte-1 low nybble; hat =
0..3 dir in byte 0; axis = axis id in byte 0, joypad in byte 1,
`00 FF` in bytes 2-3). Rather than hand-write these blind (the
per-game control *order* is undocumented), the role seeds a
**pre-configured single-XInput-pad pack** (41 games, all bindings on
joypad 1) from `dg_m2_cfg_source` into the install `CFG/`, **once**,
guarded by a `.dg-cfg-seeded` marker so later in-GUI remaps persist.

Re-mapping in the GUI: the config dialog captures the mouse (a
double-click registers "Mouse Left" instantly, and mouse motion reads
as an axis). Click a control field **once** then press the pad
button / move the stick — don't move the mouse. Windowed mode is
`AutoFull=0` (temporary) or just run `m2emulator-launch <romset>` from
a terminal.

**Exit chord**: `Select+Start` quits. Note Esc only *leaves
fullscreen* in this emulator (it resizes the window, doesn't quit), so
the chord injects **Alt+F4** (WM_CLOSE) via the evsieve bridge, not
Esc.

**Clean exit under gamescope**: gamescope only exits once its whole
child process tree is empty, but `wine <exe>` returns while wine's
background `winedevice.exe` service keeps running — leaving gamescope
as an empty, unclosable window (had to be killed from btop) and
hanging the launcher's `wait`. The gamescope child therefore runs
`wine …; wineserver -k`, so winedevice is torn down the instant the
emulator quits and gamescope exits on its own.

## ES-DE gamelists: hiding MAME clone sets

ES-DE never reads the Skraper `gamelist.xml` inside the ROM dirs, so
model2/model3 games showed as raw MAME filenames — and with scraper art
attached, every clone set (daytona/daytonam/daytonase/daytonata all
scrape to "Daytona USA") looked like duplicated entries. The
`configure_esde` role now generates
`ES-DE/gamelists/<system>/gamelist.xml` from the Skraper file via
`arcade-clone-gamelist.py`: entries sharing a display name keep the
shortest filename visible (MAME parents are prefixes of their clones)
and hide the rest (`model2`: 7 hidden, `model3`: 13 hidden). Systems
covered are listed in `dg_esde_arcade_clone_systems`; regeneration
happens on every configure run and discards ES-DE-side
favorites/playcounts for those systems (Skraper file is the source of
truth). Hidden clones stay on disk and can be shown again with ES-DE's
"show hidden games" setting.

## Sega NAOMI 1/2 — Flycast

Both systems run in the already-installed Flycast (`flycast-git`),
launched via the existing `flycast-hires` wrapper (4K internal
resolution).

**ROM layout** (MAME-style, both dirs): `<game>.zip` at the top level;
GD-ROM games additionally keep their `gdl-*/gds-*.chd` inside a folder
named after the zip — flycast resolves the CHD from there
automatically. This is why the ES-DE `naomi`/`naomi2` entries list
**zips only**: a wider extension list would surface the bare CHDs as
duplicate entries that can't boot on their own.

**BIOS**: flycast only finds arcade BIOS sets (`naomi.zip`,
`naomi2.zip`, `awbios.zip`) in its data dir or a configured content
path — NOT in the EmuDeck bios tree. `seed_configs` symlinks them from
`{{ dg_bios_root }}/dc/` into `~/.local/share/flycast/`. Without the
links, NAOMI games fail to boot with no visible error from ES-DE.

Verified 2026-07-13: `azumanga.zip` (NAOMI GD-ROM) and `initdexp.zip`
(NAOMI 2 GD-ROM, Initial D Export) both boot — game ID read, EEPROM
initialized, CHD resolved from the per-game folder. The
`naomi2: Cannot open epr-*.ic27` warnings at startup are flycast
probing for BIOS revisions this `naomi2.zip` set doesn't carry before
settling on a working region — harmless.
