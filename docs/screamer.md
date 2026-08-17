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

## Gamepad (the main goal)

Both games configure controls **only in a separate `SETUP.EXE`**, not in-game.

1. `screamer-launch setup` → in the DOS setup, choose **Joystick**.
2. The launcher runs with **`joysticktype = 4axis`**, so a modern pad's analog
   stick + triggers map onto the emulated joystick → analog steering. Buttons map
   to the joystick buttons.
3. **Keyboard-mapping fallback:** if the joystick feels off, open dosbox-staging's
   mapper with **Ctrl+F1** and bind pad buttons/stick to the arrow keys the game
   uses. (This is the "map the gamepad to keyboard" route.)

The 8BitDo/Xbox pads the box already exposes work as SDL controllers under
dosbox-staging.

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
