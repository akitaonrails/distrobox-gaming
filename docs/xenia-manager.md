# Xenia Manager in the Gaming Box

This repo treats Xbox 360 support as an optional Wine-managed toolchain.

## Installation

```sh
cd ansible
ansible-playbook install-xenia.yml
```

What the playbook does:

- enables `[multilib]` inside the distrobox if needed
- installs `wine` and `winetricks`
- creates the prefix at `$DG_XENIA_PREFIX`
- installs the Windows runtimes Xenia Manager requires:
  - `.NET 10 Desktop Runtime`
  - `Visual C++ Redistributable`
- downloads the latest Xenia Manager ZIP release
- extracts it into `$DG_XENIA_MANAGER_RELEASES_DIR`
- points `$DG_XENIA_MANAGER_CURRENT` at the active release
- writes the stable launcher wrapper to `$DG_XENIA_MANAGER_BIN`
- renders the desktop entry and symlinks it to the host

The manager and the Canary builds it downloads stay in the same prefix. That
is the cleanest maintenance model on Linux because Xenia Manager expects a
Windows-style environment and already owns Canary download/update logic.

## Post-install setup

1. Launch `Xenia Manager (on gaming)` from the host menu.
2. Go to `Manage`.
3. Install `Xenia Canary`.
4. Point the library scanner at `Z:\mnt\...` or the `G:` drive link if
   `$DG_XENIA_GAME_DIR` exists.
