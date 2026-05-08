# Cheat Engine on the gaming distrobox

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

## Caveats

- **Trainer .exes** (FLiNG / FearLessRevolution / CheatHappens
  standalones) are designed for Windows CE attaching to Windows
  processes. Native Linux CE doesn't run them directly. If you need
  one of those instead of a `.CT`, fall back to the older
  protontricks-based pattern: `protontricks-launch --appid <id>
  /path/to/Trainer.exe` to launch the trainer in the same compatdata
  prefix as the game. The `protontricks` package was previously
  installed by this role; you can reinstall it manually with
  `yay -S --needed protontricks` if needed.
- **Address randomisation** — modern games use ASLR. Saved `.CT`
  tables with hardcoded addresses won't survive game restarts; use
  AOB (array-of-bytes) scans or pointer scans instead. CE skill
  issue, not Linux issue.
- **Anti-tamper layers (Denuvo, Arxan, VMProtect)** make scanning
  slow and pointer paths unstable. CE still works; expect more
  pointer maintenance per game patch.
