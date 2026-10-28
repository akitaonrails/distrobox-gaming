# Forza on Xbox One via Azimuth

The optional `install_azimuth` role installs [Azimuth](https://almost-there-games.itch.io/azimuth) v1.0.2 and [Extra Options](https://github.com/RokkuDayo/ForzaHorizon2_ExtraOptions/releases/tag/Azimuth_v1.0.0) v0.3.2 (the "Azimuth v1.0.2 compatibility" build) through Proton. Azimuth 1.0 is a **multi-title wrapper**: one install, one prefix and one `azimuth.ini` serve **Forza Horizon 2 (1.0.0.64), FH2 Presents Fast & Furious, Forza Horizon 3 (1.0.125.0), Forza Motorsport 5 (1.0.0.20) and Forza Motorsport 6 (1.0.0.44)** — each from its own dump in `ROMS_FINAL/xboxone`.

**Azimuth 1.0 (2026-10-27)** rebuilt the wrapper: a new controller/mouse
launcher that **finds games and content packages automatically** (it scans the
folder beside it and any folder you point it to — our games live in
`ROMS_FINAL/xboxone`), per-game settings (your 0.9.x settings are copied to
every added game once), up to **40% faster**, real-time pacing at every frame
rate (the frame-pacing setting is gone), TV-level picture output, per-game
volume, photo Gallery, save backups, and **three more games: Forza Motorsport
5, Forza Motorsport 6 and Forza Horizon 3** (each needs its own dump; loyalty
rewards read FM5/FH2 saves). First start after upgrading re-translates shaders
once. The EO 0.3.x mod-loader layout (winmm.dll + `mods/` plugins) replaced
the old tls shim, which the role removes. Azimuth is an experimental Windows wrapper; its author reports Linux support through Proton. The role validates `era.vbi`, `Mount/AppxManifest.xml`, `Mount/`, and `EmbeddedXvd/` before installing the wrapper. It does not modify the game files.

Place the verified `azimuth-windows-<version>.zip` in `PC/releases/` and the pinned Extra Options / radio / ForzaInfinity archives in `PC/mods/`, with SHA-256 checks matching `group_vars/all/azimuth.yml`, and keep the Xbox One dumps under `ROMS_FINAL/xboxone`. From `ansible/`, run `ansible-playbook install-azimuth.yml` or `ansible-playbook site.yml --tags azimuth`. Override `dg_azimuth_proton` in `host_vars/localhost.yml` if needed. The wrapper keeps its Proton prefix beside itself in `dg_azimuth_compatdata` and uses the NVIDIA Vulkan driver.

## Launchers

| Walker entry | Runs | What it does |
|---|---|---|
| **Azimuth · Forza** | `bin/azimuth` | the hub: game picker, per-game settings, photo gallery, save backups |
| **Forza Horizon 2 / 3, Motorsport 5 / 6 · Xbox One** | `bin/azimuth-<fh2\|fh3\|fm5\|fm6>` | boots that game through `azimuth.exe --game=<dump> --skip-launcher` |
| **Forza Horizon 2 · Infinity Online** | `bin/azimuth-fh2-infinity` | the isolated online client (own prefix, own save) |

The per-game entries exist only for dumps present in `ROMS_FINAL/xboxone`
(`dg_azimuth_games`); a dump added later gets its shortcut on the next run,
and a removed dump's entry disappears. **First-run note (1.0.2):** until a
title has been added once inside the hub, `--game` does not resolve and
Azimuth falls back to opening the hub — point the hub's folder picker at
`ROMS_FINAL/xboxone` once and accept everything it offers (done here on
2026-10-28: FH2, FH3, FM5 and FM6 are all registered). All five Forza titles
share the one prefix and `data/azimuth.ini`.

Extra Options is version-locked to Azimuth 1.0.2 (tag Azimuth_v1.0.0). It adds controller shortcuts for autodrive (D-pad Down), lights (right stick), hazards (D-pad Up), and indicators (hold D-pad Left/Right). Its `FH2_ExtraOptions.ini` and `Gamerpic.png` are installed only if absent, so later role runs preserve customization. The installer also preserves Azimuth's existing settings, Proton prefix, saves, and game files; it removes only temporary extraction staging.

The display baseline (2160p, Ultra, 60 FPS) is applied once per machine
(unversioned marker `.dg-display-baseline-applied`); 1.0's own migration then
keeps settings per game. VSync remains under Azimuth's existing setting;
this avoids using its fixed-tick mode at 60 FPS. A marker preserves later
user changes. The 0.9.10 first launch migrated saves into a per-title folder
and made its own backup under `data/saves-backup-*`; keep that backup until
gameplay and saves have been checked. The install, executable and controller
bindings are present, but in-game FPS and input have not yet been measured.

The same optional playbook installs [FH2 Streaming Radio](https://github.com/RussFactorShow/FH2-Streaming-Radio/releases/tag/v0.1.5) v0.1.5 in the regular Azimuth folder. The Proton launcher selects the native `winmm.dll` for Extra Options and `D3DCompiler_47.dll` for radio; the archive's default configuration uses Horizon XS. Spotify Connect needs Premium and a device on the same network. Local MP3, FLAC, OGG, WAV, or M4A files in `spotify-radio/MUSIC/` work without Spotify. The playbook preserves `spotify-radio/config.ini`, `MUSIC/`, and the mod's login/cache on subsequent runs. The controller shortcut LB+X skips tracks. Radio playback and Spotify discovery still need an in-game check.

[ForzaInfinity](https://github.com/anarqz/ForzaInfinity-POC/releases/tag/v0.4.5) v0.4.5 is installed as a separate `Forza Horizon 2 · Infinity Online` launcher. The online hook includes an Extra Options v0.2.74 fork, while the regular launcher keeps the newer v0.2.98. The online install starts from a clean Azimuth archive, copies the current 4K display settings and a one-time copy of the offline save, and points to the public `https://infinity.anarqz.dev` server. The original offline save and Proton prefix remain independent. The online copy does not include the radio mod. ForzaInfinity may update its own hook when the server requires a newer version; the pinned archive remains the rebuild source. The game's Settings → INFINITY menu is where you create a profile; choose NOOB to bring progress over or HARDCORE to start a new career. No online profile has been created or gameplay verified here. The separate online save can diverge from the offline save afterward, so do not treat them as synchronized.

The fan guide's Azimuth 0.9.7 Storm Island and Fast & Furious launchers replace older wrapper/game binaries and are unnecessary for Azimuth 0.9.10. Both DLCs still require the user's own package dumps (`StormIsland_1.0.0.36_neutral__8wekyb3d8bbwe` and `Spire_1.0.0.6_x64__8wekyb3d8bbwe`); neither is present in the current `ROMS_FINAL` library. The guide's immersive camera section has no downloadable mod source, so no camera assets were installed. Extra Options already supplies intro skip and camera/FOV features. The online launcher uses Azimuth's native gamepad input; ForzaInfinity documents that Proton currently reads only the first connected controller. Physical input has not been tested.
