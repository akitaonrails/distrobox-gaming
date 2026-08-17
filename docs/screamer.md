# Screamer + Screamer 2 (GOG DOS) — `install_screamer`

The GOG releases of **Screamer** (1995) and **Screamer 2** (1996) — MS-DOS arcade
racers — run under **dosbox-staging** in the box (no Wine). `innoextract` pulls
the DOS files out of the GOG installers; a self-contained dosbox-staging binary
(pinned v0.82.2, SHA-256-checked) runs them. Opt-in; installed 2026-08-17.
Screamer 1 **smoke-verified booting**.

Sources are the GOG installers in `ROMS_FINAL/PC/Screamer/`
(`setup_screamer_1.01_gog_v2_*.exe`, `setup_screamer2_2.0.0.1.exe`). The separate
`patch_screamer_1.0_to_1.01_*.exe` is **not needed** — the installer is already
1.01 (v2).

## Install / play

```sh
cd ansible
ansible-playbook install-screamer.yml        # or: site.yml --tags screamer
```

Each game gets a desktop entry (**Screamer**, **Screamer 2**) and a launcher with
three modes:

```sh
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-launch        # play (VGA)
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-launch setup  # configure controls
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-launch svga   # SVGA (may crash)
```

The launcher generates a clean dosbox-staging config (absolute mount paths) with
GOG's tuned settings and pins the RTX (GLX) + DP-1.

## Gamepad

dosbox-staging recognises a modern pad as an SDL *GameController* and does **not**
auto-wire it to the emulated game-port joystick, so Screamer sees nothing by
default — and Screamer has no joystick menu in SETUP. The fix is a
**dosbox-staging mapperfile** that binds the pad to the arrow keys the game uses
(the "map the gamepad to keyboard" route). It's captured once and committed, so
it's reproducible and **shared by both games** (`dg_screamer_mapperfile`, one
`screamer.map` for Screamer + Screamer 2).

Committed binding (`roles/install_screamer/files/screamer.map`) for the 8BitDo:
left stick + d-pad → steer (←/→), A / right-trigger → accelerate (↑), B /
left-trigger → brake (↓), Start → Enter, Select → Esc. The launcher also keeps
`joysticktype = 2axis` + `timed = false` (the only type Screamer's DOS code
understands), and the mapper's `jaxis_*` entries are bound too, so the emulated
analog joystick works for anything that reads it.

To re-bind: launch a game, **Ctrl+F1** opens the mapper — click an emulated key,
**Add**, press the pad input, then **Save**. Re-commit `screamer.map` afterwards.

`SETUP.EXE` (`<launcher> setup`) remains for sound/graphics tweaks.

## Screamer Rally (CD-rip, needs a one-time install)

Screamer Rally (1997) isn't a GOG installer — it's a DOS **CD image** rip
(`Screamer-Rally_DOS_EN_ISO-Version.zip`, a CloneCD `.img` the role converts to a
plain ISO). It installs to a virtual HDD and then plays with the CD mounted, so
the bundled Windows NoCD patcher isn't needed (the CD is always mounted).

```sh
# 1. one-time interactive DOS install (a text menu appears):
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-rally-launch install
#    → Source drive: D    Destination drive: C    Directory: \SR (default)
#    → it then runs SETUP for controls; finish and it drops to DOS/exits.
# 2. play:
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-rally-launch       # VGA
distrobox-enter -n gaming -- {{ box_home }}/bin/screamer-rally-launch setup # controls
```

The launcher mounts the HDD as C: and the ISO as D: for every mode. `play_exe`
defaults to `C:\SR\STARTL.EXE`; if the installer nests the exe differently, fix
`play_exe` for the `screamer-rally` entry in `group_vars/all/screamer.yml`. The
committed pad mapperfile applies here too (arrow-key steering).

## Known quirks (baked into the launchers)

- **SVGA mode hard-crashes** on every platform (PCGamingWiki) → the default
  **play** mode uses VGA (`STARTL.EXE`). `svga` mode (`STARTH.EXE`) is there if
  you want to try it.
- **`SETUP.EXE` crashes at high cycles** → the `setup` mode runs it at
  ~20000 `cpu_cycles_protected` (Screamer is a DOS4GW protected-mode game, so
  the *protected* cycle count is the one that matters). Play mode uses 60000
  (Screamer 1) / 75000 (Screamer 2).
- Screamer 2 also ships a **3Dfx/Glide** mode (`S2_3DFX.EXE` + bundled nGlide) —
  not wired up here (Glide needs a wrapper); the DOS VGA path is the baseline.

Tuning lives in `group_vars/all/screamer.yml` (per-game cycles, machine, cputype,
exe). Reused GOG's values: `machine=svga_s3`, `cputype=pentium_mmx`, `sbtype=sb16`.
