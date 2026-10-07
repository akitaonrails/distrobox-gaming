# Rebuild Runbook

Use this when recreating the gaming distrobox from scratch.

## Using Ansible (recommended)

1. Install prerequisites:

   ```sh
   pip install ansible-core
   ansible-galaxy collection install community.general
   ```

2. Configure paths for your machine (optional — defaults match the current NAS layout):

   ```sh
   cd ansible
   cp host_vars/localhost.yml.example host_vars/localhost.yml
   $EDITOR host_vars/localhost.yml
   ```

3. Backup existing box (if rebuilding an existing setup):

   ```sh
   ansible-playbook backup.yml
   ```

4. Full setup from scratch:

   ```sh
   ansible-playbook site.yml
   ```

5. Optional: install Xenia Manager:

   ```sh
   ansible-playbook install-xenia.yml
   ```

6. Refresh Hedge Mod Manager only, if needed:

   ```sh
   ansible-playbook install-hedgemodmanager.yml
   ```

7. If something goes wrong, restore from backup:

   ```sh
   ansible-playbook restore.yml
   ```

### Running individual phases

```sh
ansible-playbook site.yml --tags check       # validate host paths and UID/GID
ansible-playbook site.yml --tags create      # create the distrobox
ansible-playbook site.yml --tags bootstrap   # install packages
ansible-playbook site.yml --tags shadps4     # install/update shadPS4
ansible-playbook site.yml --tags hedgemodmanager # install/update Hedge Mod Manager
ansible-playbook site.yml --tags pc_racing   # optional Windows PC racing setup
ansible-playbook site.yml --tags m2emulator  # optional Sega Model 2 Emulator (Wine)
ansible-playbook install-model1.yml          # optional Sega Model 1 (Wanszai + MAME)
ansible-playbook install-sega-rally.yml      # optional Sega Rally HD (Wanszai, Model 2)
ansible-playbook site.yml --tags sonic_p06   # optional Sonic Project '06 setup
ansible-playbook site.yml --tags configure   # apply configs, desktop entries, ES-DE
ansible-playbook site.yml --tags verify      # post-setup assertions
```

`configure` renders desktop entries only. Run `scripts/install-host-launchers.sh`
from the repository root on the host to install or refresh Walker menu entries.

### NexusMods mod-set roles (per-game, opt-in)

The `install_<game>_mods` roles, the shared loaders (`install_reframework`,
`install_ue4ss`, `install_sekiro_modengine`, `install_rdr_asi`,
`install_ff7rebirth_engine`), and the GUI-tool staging (`install_modtools`) are
all `never`-tagged opt-ins — run each via its `ansible-playbook install-<name>.yml`
or `site.yml --tags <name>`. **`docs/nexusmods.md` is the authoritative inventory**
(what each installs, per-game status, deferred/GUI-tool items, save-mod placement,
and the Proton gotchas + their fixes: the Rockstar-Launcher install-script hang,
MGS3 GE-Proton cutscene audio, MGSHDFix settings self-heal). Downloaded loaders/
tools are preserved under `ROMS_FINAL/PC/NexusMods/_loaders/` and reused on
rebuild (no re-download). Their per-game Nexus mods are under
`ROMS_FINAL/PC/NexusMods/<game>/`.

### Resetting configs without rebuilding

```sh
ansible-playbook reset-configs.yml                 # reset all configs
ansible-playbook reset-configs.yml --tags esde     # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs   # reset only emulator INIs
```

All playbooks are idempotent — re-run any phase safely.

### Optional Sega Model 1

Place legally obtained MAME-format archives in
`{{ dg_emudeck_root }}/roms_rare/model1/`, then run
`ansible-playbook install-model1.yml`. The role downloads a pinned frontend
artifact but never downloads, extracts, or modifies ROM archives. Use
`model1-launch status`, then `configure-vr` for Wanszai controller binding;
`vf` and `swa` route to native MAME. See `docs/sega-arcade.md` for routing and
limitations.

## From-scratch rebuild (container destroyed)

If the `gaming` distrobox's Docker container was pruned or otherwise
destroyed but the bind-mounted box home survived, `site.yml` recreates
the container and reinstalls everything into it. Only the container's
packages were lost — configs, ROMs, saves, and anything else under the
bind mount are untouched.

- **Host-sudo prerequisite.** `create_box` is the only role in the
  entire playbook set that runs a host-side `sudo` command — it chowns
  `dg_steam_root` to the box UID/GID before the container exists to do
  it itself. Run `ansible-playbook site.yml --ask-become-pass`, or set
  up a NOPASSWD sudoers entry for that command ahead of time. Every
  other privileged step in this repo is passwordless sudo *inside* the
  box.
- **Container-runtime access (docker group).** distrobox talks to the
  container runtime over its socket; on a Docker host that socket is
  `root:docker 0660`, so the invoking user **must be in the `docker`
  group** (`sudo usermod -aG docker $USER`, then re-login — or `newgrp
  docker` for the current shell). Without it *every* `distrobox-enter`
  fails with "permission denied … docker.sock" and distrobox offers to
  *create a new box* instead of entering the existing one — never accept
  that prompt. `check_host` (`site.yml --tags check`) now asserts this.
  Watch for it after host updates: a `containerd`/`docker` package
  upgrade restarts the runtime (which also restarts the box, wiping its
  tmpfs `/run` — see `docs/box-steam-dbus.md`) and may leave the daemon
  stopped (`sudo systemctl start containerd docker`).
- **Run in the foreground.** Do not launch a full rebuild detached or
  backgrounded (`nohup … &`, a tmux pane you detach from, etc.). Slow
  steps — Wine installers, large archive extraction — have been killed
  mid-task on background runs. Keep a terminal attached until the
  playbook finishes.
- **Opt-in roles need explicit `--tags`.** ~22 roles are gated behind
  the `never` tag plus a named tag, so a plain `ansible-playbook
  site.yml` skips them. Request the ones you actually use:

  ```sh
  ansible-playbook site.yml --tags dlcs,cheats,rpcs3_configs,retroarch,pcsx2_textures,pc_racing,m2emulator,model1,sega_rally,prboom_rt,metal_gear_master_collection,steam_lib32_nvidia,steam_trainers,render96ex,spaghettikart,ship_of_harkinian,two_ship2harkinian,starship,sonic_p06,unleashed_recomp,smm2_levels,seven_heaven
  ```

  Only pass the tags for games/features you have assets staged for.
- **Restore save data (only if the box `$HOME` was lost).** A container
  prune leaves the bind-mounted home — and therefore all saves —
  untouched. But if you re-provisioned onto a *fresh* box home, pull the
  saves back from the NAS backup after `site.yml`:

  ```sh
  ansible-playbook restore-saves.yml
  ```

  It's safe (never overwrites a save already present). See
  [docs/save-backups.md](save-backups.md). Get in the habit of running
  `distrobox enter gaming -- bash -lc '$HOME/bin/backup-saves'` periodically
  so this backup is current.
- **Standalone installer playbooks.** 30 `ansible/install-*.yml`
  playbooks exist outside `site.yml`, one role each, for the
  Windows/Wine games and tools (Xenia Manager, Azahar, Cheat Engine,
  HD textures, Dusk, the Colin McRae Rally titles, OutRun 2006, Sega
  Rally 2/Revo, GT5 Master Mod, the native-port recomps, and more).
  See [docs/external-installers.md](external-installers.md) for the
  full list and what each one fetches, rather than duplicating it
  here.
- **`vita3k-bin` is expected-skipped.** It's commented out of the AUR
  package list — the upstream PKGBUILD currently fails to build
  (dropped `org.vita3k.vita3k.metainfo.xml`). Bootstrap now also
  tolerates any single broken AUR package instead of aborting the
  whole run, so don't treat one AUR failure in the batch as a reason
  to stop and debug.
- **AUR source packages break on soname bumps.** After a box
  `pacman -Syu`, AUR packages built from source (`emulationstation-de`,
  its dep `freeimage`, etc.) keep linking the OLD library soname and
  fail with `error while loading shared libraries: lib<old>.so: cannot
  open shared object file` (seen 2026-09-28: openexr 3.4 → 3.5 broke
  ES-DE). Always run `scripts/check-box-sonames.sh` after a box update
  and rebuild what it flags from source with makepkg — `yay -S` just
  reinstalls the cached binary:
  `cd /tmp && git clone https://aur.archlinux.org/<pkg>.git && cd <pkg> && makepkg -srci --noconfirm`
  (rebuild `freeimage` first for ES-DE).
- **Wine bumps can break behavior, not just linkage.** wine 11.18's "fix
  monitor DPI awareness" made DPI-aware apps (Avalonia: Xenia Manager) honor
  the prefix `LogPixels`, and the pinned 192 suddenly rendered the UI at 2x
  with unreachable controls (2026-09-28). `install_xenia` now ENFORCES
  `dg_xenia_wine_dpi: 96` on every run, and `scripts/check-box-sonames.sh`
  audits the value after box updates — if it flags drift, re-run
  `install-xenia.yml` with the manager closed. Details in
  `docs/xenia-manager.md` ("UI sizing on the 4K panel").

## Updating the box

Routine maintenance. `update-gaming` covers pacman + AUR + RetroArch, but the
emulators we moved off AUR onto upstream binaries are **not** in it — they are
managed by their own roles, so update them explicitly:

```sh
# 1. System + AUR + RetroArch cores/assets (inside the box)
distrobox enter gaming -- ~/bin/update-gaming          # add --skip-cores --skip-assets for a quick pkg-only pass

# 2. Catch AUR soname breakage + Xenia Wine-DPI drift (host). Rebuild anything
#    it flags from source with makepkg -srci (NOT yay -S).
scripts/check-box-sonames.sh

# 3. sha256-PINNED emulator AppImages — report-only; update-gaming never touches
#    these. If OUTDATED, bump the pin (asset name + version + sha256 from the
#    GitHub asset digest) in ansible/group_vars/all/<emu>.yml and re-run the role.
scripts/check-emulator-updates.sh                      # rpcs3, xemu
cd ansible && ansible-playbook install-rpcs3.yml       # when rpcs3 is outdated
cd ansible && ansible-playbook install-xemu.yml        # when xemu is outdated

# 4. SELF-UPDATING emulators — their roles always fetch the latest upstream
#    release, so just re-run them (close the shadPS4 GUI / Xenia Manager first).
cd ansible && ansible-playbook refresh-shadps4.yml     # latest shadPS4 Pre-release (+ QtLauncher)
cd ansible && ansible-playbook install-xenia.yml       # latest Xenia Manager
```

Note: `refresh-shadps4.yml` bundles the shadPS4 config seed, whose "is shadPS4
running" guard can false-trip on the refresh's own AppImage probe — the binary
still updates; the guard refuses *before* editing `config.toml`, so nothing is
left half-written. Re-run `reset-configs.yml --tags configs` while idle if you
want the config re-seeded.

Game ports / recomps / mods pinned by release tag are a **separate** per-game
concern (the periodic "ports update sweep"), not part of routine box
maintenance — bump those deliberately, one game at a time.

## Safety

Do not run cleanup commands against ROM, BIOS, save, firmware, or game-data
directories from these playbooks or scripts.

## Atari ST

For an existing gaming box, run `ansible-playbook install-atari-st.yml` from
`ansible/`. This installs Hatari and requires BIOS/configuration validation.
See [Atari ST](atari-st.md) for paths, repeat runs and the mandatory Linux
game smoke test. `ansible-playbook verify-atari-st.yml` reruns prerequisite
checks without installing games or changing configuration.
