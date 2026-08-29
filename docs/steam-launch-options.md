# Per-game Steam launch options (in-box Steam)

`steam_launch_options` (`site.yml --tags steam_launch_options` /
`steam-launch-options.yml`) applies a data-driven map of **launch options** to
the in-box Steam's `userdata/<id>/config/localconfig.vdf`, via
`scripts/set-steam-launch-options.py`. Add an entry to
`dg_steam_launch_options_by_appid` in `ansible/group_vars/all/steam_launch_options.yml`
and re-run. It is for standalone fixes that need no other install step — game
mod roles keep their own launch options.

**Steam must be closed** when it runs: Steam rewrites `localconfig.vdf` on exit,
so the role detects a running in-box Steam, **warns and skips** the write, and
prints the options to set by hand meanwhile (Properties → Launch Options).

## Entries

### Castlevania Anniversary Collection (1018010) — `DXVK_FRAME_RATE=60 %command%`

Symptom: menus and games run in a **permanent fast-forward** (~4×, impossible
to control) under Proton. Cause: Konami/M2's emulation layer ties its game speed
to the **display refresh rate**, and DP-1 runs at **240 Hz**. `game.exe` is
D3D9 → DXVK under Proton, so DXVK's frame limiter caps presentation at 60 FPS
and the game runs at the intended speed. Do **not** fix this by switching the
monitor mode. (Likely the same for the Contra Anniversary / Arcade Classics
collections — same M2 layer.)
