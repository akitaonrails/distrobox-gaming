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

## Safety

Do not run cleanup commands against ROM, BIOS, save, firmware, or game-data
directories from these playbooks or scripts.
