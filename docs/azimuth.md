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

Place the verified `azimuth-windows-<version>.zip` in `PC/releases/` and the pinned Extra Options and radio archives in `PC/mods/`, with SHA-256 checks matching `group_vars/all/azimuth.yml`, and keep the Xbox One dumps under `ROMS_FINAL/xboxone`. From `ansible/`, run `ansible-playbook install-azimuth.yml` or `ansible-playbook site.yml --tags azimuth`. Override `dg_azimuth_proton` in `host_vars/localhost.yml` if needed. The wrapper keeps its Proton prefix beside itself in `dg_azimuth_compatdata` and uses the NVIDIA Vulkan driver.

## Launcher

| Walker entry | Runs | What it does |
|---|---|---|
| **Azimuth · Forza** | `bin/azimuth` | Azimuth's own hub: game picker, per-game settings, photo gallery, save backups and updates |

**One entry on purpose.** The role used to render a shortcut per dump
(`bin/azimuth-<slug>` running `azimuth.exe --game=<dump> --skip-launcher`).
In 1.0.x that combination does not resolve — `--skip-launcher` is not honoured
before the title is registered — so every shortcut just reopened the hub and
added a click. They were removed on 2026-10-28 (`dg_azimuth_legacy_shortcuts`
lists the leftovers the role deletes), and the hub is the single entry point
for all five titles, which share one prefix and one `data/azimuth.ini`.

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

The fan guide's Azimuth 0.9.7 Storm Island and Fast & Furious launchers replace older wrapper/game binaries and are unnecessary for Azimuth 0.9.10. Both DLCs still require the user's own package dumps (`StormIsland_1.0.0.36_neutral__8wekyb3d8bbwe` and `Spire_1.0.0.6_x64__8wekyb3d8bbwe`); neither is present in the current `ROMS_FINAL` library. The guide's immersive camera section has no downloadable mod source, so no camera assets were installed. Extra Options already supplies intro skip and camera/FOV features. Physical input has not been tested.
