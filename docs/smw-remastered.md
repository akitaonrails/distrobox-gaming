# Super Mario World Remastered

**Super Mario World Remastered** ([JHDev2006/Super-Mario-World-Remastered-Public](https://github.com/JHDev2006/Super-Mario-World-Remastered-Public))
is JHDev2006's **Godot 4** remake of the SNES *Super Mario World* — the sibling
of our *Super Mario Bros. Remastered* (which is SMB1/NES). Native Linux export,
runs on the RTX (no Wine). Managed by `install_smw_remastered` /
`install-smw-remastered.yml` (`site.yml --tags smw_remastered`).

## Game data (required)

Like SMB Remastered, it ships none of the original assets — it needs an original
**Super Mario World SNES ROM**. Its `rom_checker` looks for a **headerless
`baserom.sfc`** in its Godot **`user://` data dir**
(`~/.local/share/SuperMarioWorldRemastered/` — shown on-screen as "Please place
your SMW ROM into: …"). The role stages the USA SMW `.sfc` there automatically.

> Must be **plain Super Mario World**, *not* All-Stars+SMW or SMA2 (the game
> rejects those). Default source: `EmuDeck/roms/snes/Super Mario World (USA).sfc`
> — override `dg_smw_remastered_rom`.

## Install / run

```sh
cd ansible
ansible-playbook install-smw-remastered.yml
```

Then launch **"Super Mario World Remastered"** from Walker, or
`/mnt/data/distrobox/gaming/bin/smw-remastered`. On first run it verifies +
imports `baserom.sfc` and creates `Saves/Super Mario World/`. Runs native on the
RTX; **8BitDo works** via Godot's controller DB. Opens on DP-1 (the launcher
focuses it via the Hyprland Lua `eval` API; fullscreen via the host `gaming.lua`
rule, which lists `marioworldremastered`).

Version pinned by `dg_smw_remastered_version` + sha256; bump both for updates
(extract is version-gated and preserves the imported ROM data + saves).
Revert: `-e dg_smw_remastered_revert=true` (your ROM on the NAS is untouched).
