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
monitor mode.

### Arcade Classics Anniversary Collection (1018000) — `WINEDLLOVERRIDES="sensapi=n,b" DXVK_FRAME_RATE=60 %command%`

Besides the refresh-rate cap, this one **crashes on launch under every Proton**
(null-deref creating the WIC imaging factory from a worker thread with no COM
MTA in the process). The `sensapi=n,b` override loads the MTA-keepalive proxy
DLL deployed by `install_mta_shim` — see `docs/mta-shim.md`.

### The other M2-engine collections — same option

Every other installed Konami/M2 (and Taito/M2) collection shares that layer and
gets the same `DXVK_FRAME_RATE=60 %command%` (all D3D9/D3D11 → DXVK, verified
from the exe imports): **Contra Anniversary** (1018020), **Arcade Classics
Anniversary** (1018000), **Castlevania Advance** (1552550), **Castlevania
Dominus** (2369900), **GRADIUS origin** (2897590), **Darius Cozmic Collection
Arcade** (1638330 — its appmanifest says installed but the install dir is missing
from the STEAM drive; the option is pre-set and applies once it's reinstalled).

### Surveyed and NOT capped (report if they run fast)

Other installed retro/collection titles use their own engines with an internal
60 FPS lock, so no cap was added: Capcom Fighting Collection 1/2, Mega Man
(X) Legacy Collections, Street Fighter 30th Anniversary, TMNT Cowabunga, Sonic
Origins, MGS Master Collection (has its own fixes role), Dark Souls Remastered,
DMC5, NFS HP Remastered / Most Wanted, Halo MCC. Worth an eye: **Ninja Gaiden
Master Collection** (Σ/Σ2/3RE) and **Sonic Adventure DX / SA2** have community
reports of speed scaling with FPS above 60 — if either feels fast, add the same
entry to the map.
