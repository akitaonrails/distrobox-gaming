# Cheat Engine on the gaming distrobox

Single-player cheats / trainers via Cheat Engine, wired to attach into
Steam Proton compatdata prefixes (and to non-Steam Wine prefixes for
the PC racing games).

WeMod isn't covered here. Its Wine compatibility is title-by-title
flaky and it phones home through Wine's network stack on launch, which
breaks on enough games that maintaining it isn't worth it. CE through
Proton covers everything WeMod does and a lot more — including the
ability to load community cheat tables (`.CT` files) from FearLess
Revolution and similar.

PINCE (the Linux-native Cheat-Engine-equivalent) is intentionally
**not** installed. It would only matter for native-Linux Steam games
that don't run through Wine, and CE's scanner already attaches to
those just as well via ptrace.

## Online / anti-cheat warning

Do not attach Cheat Engine to any game running:

- VAC (most Valve multiplayer titles, CS, TF2, Dota, etc.)
- EAC (Easy Anti-Cheat — Apex, Fortnite, etc.)
- BattlEye (Rainbow Six Siege, etc.)
- Any other server-side anti-cheat

Anti-cheat fingerprints CE's loader and bans regardless of host OS.
This setup is for offline campaigns and single-player experiences only.

## Install

The CE Windows installer (Inno Setup) is the supported path. The
native Linux build at 7.6.6 exists but isn't cleanly packaged on Arch
yet — drop in once a clean AUR / upstream tarball appears.

1. Download `CheatEngine{{ version }}.exe` from
   <https://www.cheatengine.org/downloads.php>
   (defaults assume 7.6 — bump `dg_cheatengine_version` in
   `ansible/group_vars/all/cheatengine.yml` for newer releases).
2. Drop the installer at:
   `{{ dg_pc_racing_source_root }}/CheatEngine/CheatEngine7.6.exe`
   (`dg_cheatengine_installer`).
3. Run the focused playbook from `ansible/`:
   ```sh
   ansible-playbook install-cheatengine.yml
   ```
4. The role:
   - installs `protontricks` inside the box (AUR) for Steam compatdata
     prefix discovery;
   - extracts the Inno Setup installer with `innoextract` (already in
     the PC racing package list) to
     `{{ dg_box_home }}/tools/cheat-engine/app/`;
   - drops a `cheat-engine` wrapper at `{{ dg_box_home }}/bin/`.

The installer drop, version variable, and wrapper path all follow
`dg_*` variables — no hardcoded user paths. If you renamed the
installer to a non-default name, override
`dg_cheatengine_installer` in `host_vars/localhost.yml` instead of
editing the role.

## Usage

The wrapper has three modes. All three launch the same `Cheat Engine.exe`
binary; what changes is the **Wine prefix it attaches to**, which
determines which game processes CE can ptrace.

### Steam Proton games

```sh
cheat-engine --steam <appid>
```

Uses `protontricks-launch` to launch CE inside the game's
`compatdata/<appid>/pfx` with the same Proton version Steam picked,
including the Steam Linux Runtime container if applicable. CE then
sees the game's wine processes when you click the computer icon.

To find the appid, either:

```sh
cheat-engine --list-steam       # protontricks --list, prints appid + name
```

or look it up on Steam (right-click game → Properties → URL or App ID).

### Non-Steam Wine games

```sh
cheat-engine --prefix /path/to/wineprefix
```

For the PC racing entries (CMR04, OutRun, etc.) the prefix root is
`{{ dg_pc_racing_prefix_root }}/<game-slug>` per `pc_racing.yml`.

### Standalone (no game target)

```sh
cheat-engine
```

Runs CE in `{{ dg_cheatengine_prefix }}` — useful for browsing the UI,
testing CE itself, or working with `.CT` tables disconnected from any
running game.

## Caveats

- **Trainer .exes** (FLiNG, FearLessRevolution, CheatHappens) follow
  the same pattern: `protontricks-launch --appid <id> /path/to/Trainer.exe`.
  No CE needed. The wrapper here is CE-specific; if you end up running
  trainers regularly, generalising the wrapper to take an arbitrary
  `.exe` is a small change.
- **Cross-prefix attachment doesn't work.** If CE is launched in
  prefix A, it cannot see processes in prefix B even though they're
  all real Linux processes — Wine's process table is per-prefix.
  Always match the target game's prefix.
- **Address randomisation:** modern games use ASLR. Saved `.CT` tables
  with hardcoded addresses won't survive game restarts; use AOB
  (array-of-bytes) scans or pointer scans instead. This is a CE skill
  issue, not a Linux issue.
- **Some games' anti-tamper layers (Denuvo, Arxan, VMProtect)** make
  scanning slow and pointer paths unstable. CE still works, just
  expect more pointer maintenance per patch.
