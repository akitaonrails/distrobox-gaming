# Sonic Project '06

Sonic Project '06 is a Windows Unity fan remake, so this repo manages it as an
optional system-Wine install inside the `gaming` distrobox. It is skipped during a
normal `site.yml` rebuild.

Research notes:

- Lutris lists Project '06 as a Windows standalone game installed from a ZIP.
- Linux Gaming Central reports that P-06 works well on Linux/Steam Deck through
  Wine/Proton, but recommends GE-Proton 8-3 because vanilla Proton can show a
  broken/checkered menu background and regular Wine can render menu text badly.
- Wine-GE 8-26 is the last archived standalone Wine-GE runner family and is
  intended for non-Steam games outside Steam/Lutris.
- Local testing rejected Wine-GE 8-26 for this distrobox because prefix
  initialization hangs. System Wine 11 initializes cleanly here.
- Unity video playback requires GStreamer codec plugins; without them, the game
  reaches the intro with subtitles over a black screen and logs
  `WindowsVideoMedia error 0xc00d36bb`.
- WineD3D can leave the loading overlay stuck over gameplay. The role installs
  DXVK 2.7.1 into the prefix with `winetricks dxvk2071`.
- Save/load UI fonts can be incomplete with the default Wine font set. The role
  installs `winetricks corefonts` into the same prefix.
- The Silver Release does not provide Story Episode mode. Use Single Player ->
  Trial Select -> Act Trial to play the available Sonic, Shadow, and Silver
  stages. A greyed-out Story Episodes option is expected.

Sources:

- https://lutris.net/games/project-06/
- https://linuxgamingcentral.org/posts/sonicp-06/
- https://github.com/GloriousEggroll/wine-ge-custom/releases
- https://www.dsogaming.com/news/new-version-released-for-the-sonic-2006-fan-remake-project-06/

Run from `ansible/`:

```sh
ansible-playbook install-sonic-p06.yml
```

The role:

- validates the extracted source at `{{ dg_sonic_p06_source_dir }}`
- installs system Wine, Winetricks, DXVK support, core fonts, and GStreamer
  runtime packages inside the distrobox
- copies the extracted game to `{{ dg_sonic_p06_install_root }}`
- creates a dedicated Wine prefix at `{{ dg_sonic_p06_prefix }}`
- writes `{{ dg_sonic_p06_bin }}`
- renders a host launcher entry

Refresh the host menu after install:

```sh
scripts/install-host-launchers.sh
```

The launcher uses the distrobox's `/usr/bin/wine` directly with esync/fsync
disabled for predictable startup. The prefix components are marked with
`.dg-winetricks-*` files so repeated Ansible runs do not reinstall them. Saves
and Wine state live in the dedicated prefix, not in the source dump.
