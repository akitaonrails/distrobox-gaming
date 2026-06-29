# Hedge Mod Manager

Hedge Mod Manager 8 is installed inside the `gaming` distrobox as a native
.NET/Avalonia Linux build. This avoids host Flatpak installation and keeps the
manager in the same filesystem view as Steam, Proton prefixes, and the Sonic
game libraries.

Run from `ansible/`:

```sh
ansible-playbook install-hedgemodmanager.yml
```

The role installs `dotnet-sdk` inside the box, downloads the pinned official HMM
Linux x64 release tarball, writes an in-box launcher, and installs a host helper
similar to `dg-fling`:

```text
{{ dg_box_home }}/bin/hedge-mod-manager
~/.local/bin/dg-hmm
```

Launch it from the host with:

```sh
dg-hmm                 # menu of installed supported Sonic games
dg-hmm list            # installed supported games
dg-hmm all             # every HMM-supported Sonic Steam target in this role
dg-hmm frontiers       # preselect Sonic Frontiers, then open HMM
dg-hmm origins         # preselect Sonic Origins, then open HMM
dg-hmm sxsg            # preselect Shadow Generations, then open HMM
```

`dg-hmm <key>` finds the Steam app manifest, resolves the executable path, writes
HMM's shared `ProgramConfig.json` `LastSelectedPath`, then starts the single HMM
instance. If HMM is already open, close and reopen it if the selected game does
not switch immediately; HMM does not expose an official game-selection CLI.

HMM detects Steam by reading `~/.local/share/Steam/steamapps/libraryfolders.vdf`
inside the box. If your Sonic games live on an external Steam library, make
sure that library is visible inside the distrobox and recorded by Steam.

Supported Sonic Steam targets are Sonic Generations, Sonic Lost World, Sonic
Forces, Sonic Colors Ultimate, Sonic Origins, Sonic Frontiers, and Shadow
Generations from Sonic X Shadow Generations. Sonic Superstars, Mania, CD,
Adventure DX, Adventure 2, and Team Sonic Racing are not current Hedge Mod
Manager targets.

If a supported game is missing from HMM, launch it once from Steam first so
Proton creates `steamapps/compatdata/<appid>/pfx`.
