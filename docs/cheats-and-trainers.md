# Cheats and trainers on the gaming distrobox

Single-player cheats / trainers via **native Linux** Cheat Engine 7.6.6,
attached to Steam Proton or Wine processes via standard ptrace.

WeMod isn't covered here — its Wine compatibility is title-by-title
flaky and it phones home through Wine on launch. CE through native
Linux ptrace covers everything WeMod does and more, including loading
community cheat tables (`.CT` files) from FearLess Revolution.

PINCE (the older Linux-native CE-equivalent) is intentionally **not**
installed. Native CE 7.6.6 covers the same ground with the actual
Cheat Engine UI and `.CT` table format.

## Online / anti-cheat warning

Do not attach Cheat Engine to any game running:

- VAC (most Valve multiplayer titles, CS, TF2, Dota, etc.)
- EAC (Easy Anti-Cheat — Apex, Fortnite, etc.)
- BattlEye (Rainbow Six Siege, etc.)
- Any other server-side anti-cheat

Anti-cheat fingerprints CE's loader and bans regardless of host OS.
This setup is for offline campaigns and single-player experiences only.

## Install

1. Download `CheatEngineLinux766-4.zip` (or whichever `dg_cheatengine_linux_*`
   version is current in `ansible/group_vars/all/cheatengine.yml`) from
   <https://www.cheatengine.org/downloads.php>.
2. Drop it at `dg_cheatengine_linux_zip` (defaults to
   `<dg_pc_racing_source_root>/CheatEngine/CheatEngineLinux766-4.zip`).
3. From `ansible/`:
   ```sh
   ansible-playbook install-cheatengine.yml
   ```
4. The role unzips the archive to `tools/cheat-engine/CheatEngineLinux766-4/`
   and drops a `cheat-engine` wrapper at `bin/`. Idempotent re-runs.

We don't auto-download — cheatengine.org's URL pattern shifts between
releases, so the role fails-fast with a download pointer if the zip
isn't staged.

## ptrace_scope (one-time host setup)

Arch's default `kernel.yama.ptrace_scope=1` blocks CE from attaching
to processes outside its own shell tree (i.e. anything launched from
Steam). Pick one:

- **Persistent (recommended)** — drop a sysctl file:
  ```sh
  echo 'kernel.yama.ptrace_scope = 0' | sudo tee /etc/sysctl.d/99-ptrace.conf
  sudo sysctl --system
  ```
- **One-shot per session**:
  ```sh
  sudo sysctl kernel.yama.ptrace_scope=0
  ```
- **Per-binary capability** (more surgical):
  ```sh
  sudo setcap cap_sys_ptrace=eip ~/tools/cheat-engine/CheatEngineLinux766-4/cheatengine-x86_64
  ```

Reverse with `kernel.yama.ptrace_scope=1` when you're done if you
care about the security posture.

The wrapper detects a non-zero `ptrace_scope` and prints these hints
on launch.

## Usage

Three modes:

```sh
cheat-engine                           # native Linux CE
cheat-engine --proton <appid>          # Windows CE inside a Steam game's Proton prefix
cheat-engine --proton-install <appid>  # one-time: install Windows CE into that prefix
```

### Native mode (default — try this first)

```sh
cheat-engine
```

CE opens. Click the **computer icon** (top-left) → **Process List**.
All running processes appear including Wine ones. Pick the game's
`.exe` (e.g. `Spider-Man.exe`), attach, then **File → Open** a `.CT`.

Native CE attaches via ptrace, which works on any Linux process —
Wine processes count. Most cheat tables that use AOB-scan-only
addressing work cleanly here.

### Proton-prefix mode (when native CE isn't enough)

Some cheat tables (notably FearLess Revolution tables for AAA Insomniac
ports like Spider-Man Remastered) do **PE module symbol enumeration**
in their activation scripts — `going to wait for all symbols loaded
because of $process` followed by `TMemScan` aborting. Native Linux CE
can't fully resolve PE symbols in a Wine process; Windows CE running
inside the same Wine prefix as the game can.

One-time install per game (Steam must have launched the game at least
once so its compatdata prefix exists):

```sh
cheat-engine --proton-install 1817070   # Spider-Man Remastered
```

An Inno Setup wizard pops up; click through Next/Install/Finish. CE
lands at `<prefix>/drive_c/Program Files/Cheat Engine/Cheat Engine.exe`
inside that game's prefix. Repeat per game that needs Windows CE.

Then to launch:

```sh
cheat-engine --proton 1817070
```

protontricks-launch fires Wine in the game's exact Proton prefix; CE
sees the game as a same-prefix Windows process with full module table,
and `.CT` activations work normally.

### Overrides

- `DG_CHEATENGINE_DIR` — native CE install location (default
  `~/tools/cheat-engine/CheatEngineLinux766-4`)
- `DG_CHEATENGINE_PROTON_REL` — relative path to `Cheat Engine.exe`
  inside a Proton prefix (default
  `drive_c/Program Files/Cheat Engine/Cheat Engine.exe`)
- `DG_CHEATENGINE_WIN_INSTALLER` — Windows CE installer source for
  `--proton-install` (default
  `<dg_pc_racing_source_root>/CheatEngine/CheatEngine76.exe`)

## Workflow with Spider-Man Remastered (worked example)

1. Launch Marvel's Spider-Man Remastered from Steam, reach a save.
2. From a separate terminal: `cheat-engine`
3. CE → computer icon → pick `Spider-Man.exe` from the process list.
4. Load a `.CT`: search FearLess Revolution for the current Spider-Man
   Remastered table (community-maintained, AOB-scanned addresses so
   it survives most game patches).
5. Tick the cheat checkboxes — they activate immediately.

Same shape works for any Steam Proton single-player title.

## Emulator cheat databases

The distrobox has two cheat flows:

- **Eden Cheats Manager** is installed by the main playbook. Run the full
  playbook or the focused tag:
  ```sh
  cd ansible
  ansible-playbook site.yml --tags eden_cheats_manager,desktop
  ```
  The role downloads the pinned AppImage, extracts it under
  `{{ dg_box_home }}/tools/eden-cheats-manager/`, installs the stable wrapper
  `{{ dg_box_home }}/bin/eden-cheats-manager`, and renders the host launcher
  `gaming-eden-cheats-manager.desktop`.
- **Azahar, PCSX2, DuckStation, and RPCS3 community databases** are synced
  from local clones with `scripts/sync-emulator-cheats.py`. The script is
  intentionally conservative: it only copies files that match local emulator
  caches or ROM names, and it skips ambiguous 3DS title matches.

Example after cloning the upstream cheat repositories somewhere outside the
repo checkout:

```sh
scripts/sync-emulator-cheats.py \
  --box-home "$DG_BOX_HOME" \
  --n3ds-root "$DG_N3DS_ROOT" \
  --ctrpf "$DG_CTRPF_CHEATS_REPO" \
  --pcsx2 "$DG_PCSX2_CHEATS_REPO" \
  --duckstation "$DG_DUCKSTATION_CHTDB_REPO" \
  --rpcs3-artemis "$DG_RPCS3_ARTEMIS_REPO" \
  --report /tmp/emulator-cheat-sync-report.json
```

Use `--dry-run` first when changing source repos or library roots.

Installed destinations:

| Emulator | Destination | Filename rule |
| --- | --- | --- |
| Azahar | `{{ dg_box_home }}/.local/share/azahar-emu/cheats/` | `16_UPPERCASE_HEX_TITLEID.txt` |
| PCSX2 Qt | `{{ dg_box_home }}/.config/PCSX2/cheats/` | `<SERIAL>_<CRC>.pnach`; CRC-only aliases are kept for compatibility |
| DuckStation | `{{ dg_box_home }}/.config/duckstation/cheats/` | `<SERIAL>.cht` |
| RPCS3 | `{{ dg_box_home }}/.config/rpcs3/patches/` | `<TITLE_ID>_patch.yml` |

RPCS3 loads the installed patch YAML files, but cheats still need to be enabled
in RPCS3's Patch Manager. DuckStation is configured in this repo under
`{{ dg_box_home }}/.config/duckstation`; if a future DuckStation build opens
`{{ dg_box_home }}/.local/share/duckstation` from **Tools → Open Data
Directory**, mirror the generated `cheats/` files there or update the wrapper
environment before expecting auto-load to work.

## Caveats

- **Trainer .exes** (FLiNG / FearLessRevolution / CheatHappens
  standalones) are separate per-game Windows executables. This repo uses
  `steam-trainer` as the reusable wrapper: each game gets a staged trainer
  binary, but the launch flow is shared.

  ```sh
  cd ansible
  ansible-playbook install-steam-trainers.yml
  dg-fling list
  dg-fling streets-of-rage-4
  ```

  The playbook also installs a host-side helper:

  ```sh
  dg-fling              # menu; fzf when available, numbered fallback otherwise
  dg-fling list         # launchable official FLiNG trainers only
  dg-fling keys         # keys and aliases for shell completion
  dg-fling sor4         # direct launch by key or alias
  ```

  Launch the Steam game first, reach gameplay or a menu, then run `dg-fling` and
  pick the matching trainer. Shell completion files are installed for bash and
  zsh under the user's local completion directories.

  Start the Steam game first if the trainer says it cannot find the game
  process. The game must also have been launched once from Steam so its Proton
  compatdata prefix exists.

  The wrapper launches trainers in a Wine virtual desktop by default
  (`trainer_<appid>,1024x768`). This avoids FLiNG WinForms windows colliding
  with fullscreen/game windows under Wine, which can show up as an X11
  `BadWindow` crash. To bypass that mode for troubleshooting:

  ```sh
  DG_STEAM_TRAINER_DESKTOP=none steam-trainer streets-of-rage-4
  ```

  Streets of Rage 4 ships a native Linux build, but the FLiNG trainer is a
  Windows process trainer. Force Proton for it before expecting a prefix:

  ```sh
  cd ansible
  ansible-playbook install-steam-trainers.yml \
    -e dg_steam_trainers_steam_config=$HOME/.local/share/Steam/config/config.vdf
  ```

  If Steam is running, close it first or add
  `-e dg_steam_trainers_stop_steam=true`. After that, launch Streets of Rage 4
  once from Steam so it downloads/boots the Windows build and creates
  `compatdata/985890/pfx`.

  Streets of Rage 4's FLiNG trainer was tested with the game already running;
  it needs the wrapper's virtual desktop mode to keep the trainer window open.
  Avoid forcing `dotnet48` into this Proton/CachyOS prefix: the attempted
  install removed Wine Mono and did not complete. If the trainer stops launching
  with `mscoree.dll` errors, restore the prefix's built-in Wine `mscoree.dll`
  links from the active Proton tool instead of rerunning `dotnet48`.

  That virtual-desktop mode is now the default for every `steam-trainer` /
  `dg-fling` launch. It uses Proton's own `wine` from Steam's configured compat
  tool and runs `explorer /desktop=trainer_<appid>,1024x768 <trainer.exe>`.

  Current staged official FLiNG trainers:

  | Key | Aliases | Steam app ID | Source |
  | --- | --- | ---: | --- |
  | `streets-of-rage-4` | `sor4` | `985890` | Streets of Rage 4, 10 options, `v1.0-v20210715+` |
  | `spider-man-remastered` | `spiderman`, `spider-man` | `1817070` | Marvel's Spider-Man Remastered, 30 options, `v1.812-v2.616+` |
  | `soulcalibur-vi` | `soul-calibur-vi`, `sc6` | `544750` | Soulcalibur VI, 12 options, `v1.0-v2.25+` |
  | `bloodstained-ritual-of-the-night` | `bloodstained` | `692850` | Bloodstained, 15 options, `v1.0-v1.4+` |
  | `black-myth-wukong` | `wukong`, `bmw` | `2358720` | Black Myth Wukong, 44 options, `v1.0-v1.0.20+` |
  | `devil-may-cry-5` | `dmc5` | `601150` | Devil May Cry 5, 25 options, `v1.0-v20201215+` |
  | `final-fantasy-vii-rebirth` | `ff7-rebirth`, `ffvii-rebirth` | `2909400` | Final Fantasy VII Rebirth, 58 options, `v1.0-v1.005+` |
  | `halo-mcc-ce-anniversary` | `halo-ce`, `halo-ce-anniversary` | `976730` | Halo MCC: Halo CE Anniversary, 13 options |
  | `halo-mcc-halo-2-anniversary` | `halo-2`, `halo-2-anniversary` | `976730` | Halo MCC: Halo 2 Anniversary, 13 options |
  | `halo-mcc-halo-3` | `halo-3` | `976730` | Halo MCC: Halo 3, 13 options |
  | `halo-mcc-halo-3-odst` | `halo-3-odst`, `odst` | `976730` | Halo MCC: Halo 3 ODST, 13 options |
  | `halo-mcc-halo-4` | `halo-4` | `976730` | Halo MCC: Halo 4, 14 options |
  | `halo-mcc-reach` | `halo-reach`, `reach` | `976730` | Halo MCC: Reach, 13 options |
  | `mega-man-x-legacy-collection` | `mmx-legacy`, `megaman-x-legacy` | `743890` | Mega Man X Legacy Collection, 4 options |
  | `mega-man-x-legacy-collection-2` | `mmx-legacy-2`, `megaman-x-legacy-2` | `743900` | Mega Man X Legacy Collection 2, 5 options |
  | `red-dead-redemption` | `rdr1` | `2668510` | Red Dead Redemption, 11 options |
  | `red-dead-redemption-2` | `rdr2` | `1174180` | Red Dead Redemption 2, 12 options |
  | `resident-evil-4` | `re4`, `re4-remake` | `2050650` | Resident Evil 4 remake-era trainer, 36 options |
  | `resident-evil-requiem` | `re9`, `requiem` | `3764200` | Resident Evil Requiem, 29 options |
  | `sekiro` | `sekiro-shadows-die-twice` | `814380` | Sekiro, 24 options |
  | `uncharted-legacy-of-thieves` | `uncharted`, `legacy-of-thieves` | `1659420` | Uncharted Legacy of Thieves, 5 options |

  Halo MCC, Red Dead Redemption, and Red Dead Redemption 2 are online-capable;
  use these trainers only in offline/single-player modes. For Halo MCC, launch
  the anti-cheat-disabled/offline mode.

  Requested titles with no verified official FLiNG trainer page/direct download
  are intentionally not added to the launcher: Sonic Generations, Sonic Mania,
  TMNT Shredder's Revenge, TMNT Cowabunga Collection, Batman Arkham Asylum,
  Batman Arkham City, Capcom Fighting Collection 1/2, Castlevania Advance /
  Anniversary / Dominus Collections, Chrono Trigger, Contra Anniversary
  Collection, GTA IV, Legacy of Kain Soul Reaver 1&2 Remastered, Marvel Cosmic
  Invasion, Mega Man Legacy Collection 1/2, Old School Rally, Shinobi: Art of
  Vengeance, SNK vs Capcom SVC Chaos, Sonic Adventure DX/2, Sonic CD, Sonic
  Colors Ultimate, Sonic Frontiers, Sonic Origins, Sonic Superstars, Sonic X
  Shadow Generations, Strider, Ultra Street Fighter IV, and Virtua Fighter 5.
  Batman Arkham Knight, Crash N. Sane Trilogy, Mega Man 11, and Ultimate Marvel
  vs Capcom 3 were seen only in FLiNG's old archive text without a direct
  official download, so they are also not launchable here.

  FLiNG does **not** ship one reusable trainer app. It ships one trainer
  executable per game. The reusable piece in this repo is the `steam-trainer`
  launcher and Ansible data model; add future games to
  `ansible/group_vars/all/steam_trainers.yml` with their Steam app ID, official
  source URL, and SHA-256.

- **Address randomisation** — modern games use ASLR. Saved `.CT`
  tables with hardcoded addresses won't survive game restarts; use
  AOB (array-of-bytes) scans or pointer scans instead. CE skill
  issue, not Linux issue.
- **Anti-tamper layers (Denuvo, Arxan, VMProtect)** make scanning
  slow and pointer paths unstable. CE still works; expect more
  pointer maintenance per game patch.
