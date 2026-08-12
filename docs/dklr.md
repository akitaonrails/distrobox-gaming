# Donkey Kong Land Remake (DKLR) — `install_dklr`

kasquez's free fangame remake of the GameBoy *Donkey Kong Land* in the SNES
*Donkey Kong Country* style. Opt-in role; installed 2026-08-08.

- **Engine:** Windows **Unity (IL2CPP)** → runs under **Wine + DXVK**.
- **Native resolution:** 256×224 pixel art (Alt+Enter toggles fullscreen in the
  raw build). The launcher **integer-scales** it to the panel with gamescope for
  crisp pixels — no blur.
- **Source:** staged on the NAS at `dg_dklr_source_dir`
  (`ROMS_FINAL/PC/DKLR`); the role copies it to a writable local install
  (`{{ dg_box_home }}/Games/dklr`) so autosaves work.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-dklr.yml           # or: site.yml --tags dklr
# refresh the host menu entry:
scripts/install-host-launchers.sh
# remove it (launcher + prefix + local copy; NAS source untouched):
ansible-playbook install-dklr.yml -e dg_dklr_revert=true
```

Launcher: `{{ dg_box_home }}/bin/dklr`. It pins the RTX (`VK_ICD_FILENAMES`
=nvidia — a Unity/DXVK title black-screens on the AMD iGPU otherwise, like Sega
Rally Revo), focuses DP-1, and wraps the game in gamescope.

## Controls (pad → keyboard bridge)

The game is **keyboard-only** (no native controller support in any version —
the README bundles Windows JoyToKey for exactly this; confirmed by research
2026-08-11). Instead the launcher runs an **evsieve** bridge that grabs the pad
and emits the game's keys — real controller play, no JoyToKey. The game's key
map (from its README) is D-pad→arrows, SNES A→S, B→X, X→A, Y→Z, L→Q, R→W,
Start→Return, Select→Backspace; **jump = `x`** (SNES B), **roll = `z`** (SNES Y).

Current 8BitDo mapping (jump on B, roll on A, per user preference):

Note the game's jump key is **`x`** (SNES B) and roll is **`z`** (SNES Y) — and
on this 8BitDo the physical labels sit at surprising evdev codes (verified with
evtest, do NOT assume Nintendo positions): **A=`btn:south`, B=`btn:east`,
X=`btn:north`, Y=`btn:west`**.

| 8BitDo | evdev code | Emits key | In-game |
|---|---|---|---|
| D-pad | `abs:hat0x/hat0y` (±1) | Arrow keys | move |
| **B** | `btn:east` | **x** | **jump** |
| **A** | `btn:south` | **z** | **roll** |
| **Y** | `btn:west` | z | roll |
| **X** | `btn:north` | a | (SNES X, unused) |
| L / R | `btn:tl` / `btn:tr` | q / w | L / R |
| Start | `btn:start` | Return | Start |
| Select | `btn:select` | Backspace | Select / swap Kong |

Keyboard also works directly. To remap, edit
`roles/install_dklr/templates/dklr.sh.j2`.

### ⚠️ evsieve gotcha — hat/axis → key needs explicit press/release

Buttons map fine with a bare `--map btn:south key:s` (a `btn:` event already
carries value 1/0 = press/release, which evsieve copies to the key). **An
`abs:`/hat axis does NOT** — `--map abs:hat0x:-1 key:left` copies the abs value
(`-1`) onto the key, and a key event with value −1 is not a valid press, so the
d-pad silently does nothing. Map hats with explicit press/release instead
(the same idiom CMR1 uses for its analog stick):

```
--copy abs:hat0x:-1 key:left:1     # press
--copy abs:hat0x:0  key:left:0     # release (0 releases BOTH left+right, so
--copy abs:hat0x:1  key:right:1    #   use --copy, not --map, for the 0 case)
--copy abs:hat0x:0  key:right:0
--block abs:hat0x                  # drop the raw hat -> keyboard-only output
```

### ⚠️ evsieve grabs the pad exclusively — it MUST be reaped on exit

Because the bridge runs `evsieve --input … grab`, the controller is held
exclusively and re-emitted as a keyboard for as long as evsieve lives. If it
leaks (the launcher is SIGKILLed or the box-side script is orphaned when you
close the window), the pad keeps emitting keys into **ES-DE, Steam, everything**
— it looks like "my controller stopped working." The launcher guards this three
ways: (1) a `pkill -x evsieve` at startup clears any stale grab, (2) `cleanup()`
kills evsieve on EXIT/HUP/INT/TERM, and (3) a `setsid` **watchdog** in its own
session releases the grab the moment the launcher PID disappears — covering
SIGKILL, which traps cannot. If you ever see a hijacked pad, `distrobox enter
gaming -- pkill -x evsieve` frees it immediately.

The 8BitDo Ultimate 2 (xpad) d-pad IS on `ABS_HAT0X/HAT0Y`. To verify codes,
`evtest /dev/input/event23` (install evtest first) — but first kill any orphan
`winedevice.exe`/`evsieve` holding the pad, or the capture reads empty. Steam
and Brave open the pad **non-exclusively** and do NOT block evsieve's grab.

## Presentation notes

gamescope runs `-w 256 -h 224 -W 3840 -H 2160 -S integer -f` — integer scaling
centres a crisp pixel image with a border. For a fill-the-screen look instead,
change `-S integer` to `-S fit` in the launcher (slightly softer). Output size
is `dg_dklr_output_width`/`_height`.
