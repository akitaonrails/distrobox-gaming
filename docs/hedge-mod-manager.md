# Hedge Mod Manager

Hedge Mod Manager 8 is installed inside the `gaming` distrobox as a native
.NET/Avalonia Linux build. This avoids host Flatpak installation and keeps the
manager in the same filesystem view as Steam, Proton prefixes, and the Sonic
game libraries.

Run from `ansible/`:

```sh
ansible-playbook install-hedgemodmanager.yml
```

The role installs `dotnet-sdk` inside the box, downloads the pinned HMM source
release, publishes `Source/HedgeModManager.UI` for `linux-x64`, and writes this
stable launcher:

```text
{{ dg_box_home }}/bin/hedge-mod-manager
```

Launch it from the host with:

```sh
distrobox-enter -n gaming -- "{{ dg_box_home }}/bin/hedge-mod-manager"
```

HMM detects Steam by reading `~/.local/share/Steam/steamapps/libraryfolders.vdf`
inside the box. If your Sonic games live on an external Steam library, make
sure that library is visible inside the distrobox and recorded by Steam.

Supported installed targets in this setup are Sonic Frontiers, Sonic Origins,
and SONIC X SHADOW GENERATIONS. Sonic Superstars, Mania, CD, Adventure DX, and
Adventure 2 are not Hedge Mod Manager targets.

If a supported game is missing from HMM, launch it once from Steam first so
Proton creates `steamapps/compatdata/<appid>/pfx`.
