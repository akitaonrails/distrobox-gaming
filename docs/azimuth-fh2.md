# Forza Horizon 2 via Azimuth

The optional `install_azimuth` role installs [Azimuth](https://almost-there-games.itch.io/azimuth) v1.0.2 and [Extra Options](https://github.com/RokkuDayo/ForzaHorizon2_ExtraOptions/releases/tag/Azimuth_v1.0.0) v0.3.2 (the "Azimuth v1.0.2 compatibility" build) through Proton for the Xbox One Forza Horizon 2 release v1.0.0.64.

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

Place the verified `azimuth-windows-0.9.10.zip` and `FH2_Extra_Options_0.2.98-release.zip` under `dg_roms_final_root/PC/`, with SHA-256 checks matching `group_vars/all/azimuth.yml`, and unpack the Xbox One game under `dg_azimuth_game_dir`. From `ansible/`, run `ansible-playbook install-azimuth.yml` or `ansible-playbook site.yml --tags azimuth`. Override `dg_azimuth_game_dir` and `dg_azimuth_proton` in `host_vars/localhost.yml` if needed. The launcher keeps its Proton prefix beside the wrapper in `dg_azimuth_compatdata` and uses the NVIDIA Vulkan driver. On first launch, select `dg_azimuth_game_dir` in Azimuth's folder picker if it is not already configured.

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
