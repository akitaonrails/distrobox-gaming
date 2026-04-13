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

6. If something goes wrong, restore from backup:

   ```sh
   ansible-playbook restore.yml
   ```

### Running individual phases

```sh
ansible-playbook site.yml --tags check       # validate host paths and UID/GID
ansible-playbook site.yml --tags create      # create the distrobox
ansible-playbook site.yml --tags bootstrap   # install packages
ansible-playbook site.yml --tags shadps4     # install/update shadPS4
ansible-playbook site.yml --tags configure   # apply configs, desktop entries, ES-DE
ansible-playbook site.yml --tags verify      # post-setup assertions
```

### Resetting configs without rebuilding

```sh
ansible-playbook reset-configs.yml                 # reset all configs
ansible-playbook reset-configs.yml --tags esde     # reset only ES-DE
ansible-playbook reset-configs.yml --tags configs   # reset only emulator INIs
```

All playbooks are idempotent — re-run any phase safely.

## Using legacy shell scripts

The `bin/dg` wrapper and `scripts/` directory contain the original shell
implementation. These are retained as reference but the Ansible playbooks
are the primary interface.

```sh
cp config/distrobox-gaming.env.example config/distrobox-gaming.env
$EDITOR config/distrobox-gaming.env
./bin/dg all
```

## Safety

Do not run cleanup commands against ROM, BIOS, save, firmware, or game-data
directories from these playbooks or scripts.
