# DriveClub widescreen / high-res on shadPS4 (`install_driveclub_shader_patch`)

DriveClub (PS4, title `CUSA00003`) runs on shadPS4. Its memory patches for
widescreen and higher internal resolution exist in the community patch set, but
the game's **de-interleave post-process compute shader hardcodes the 960×540
half-resolution buffer** (SPIR-V constants `960` and `540`). With a resolution
patch on but that shader unchanged, the frame renders interleaved/garbled — the
**"[DEPTH BUG]"** the patch names warn about.

The community **shader autopatcher** (mediafire *"Driveclub shader autopatcher
v1.0.1"*, by illusion / kalaposfos / u/Charlie_Muggins) rewrites that one dumped
shader to query the real render-target size (`OpImageQuerySize`) instead of the
constants, so the resolution/widescreen patches render correctly.

## What this role sets up (persistent)

- **Expanded patch XML.** `seed_configs/files/shadPS4/Driveclub.xml` is updated to
  the v1.0.1 set (40 patches: 60 FPS, 2560×1080 / 3840×1080 / 32:9 / 4K / 8K
  internal+output, memory-for-NK, FOV fix, …). It deploys to
  `~/.local/share/shadPS4/patches/CUSA00003.xml`, so they appear in shadPS4's
  **Cheats/Patches** panel — all default-off; enable the one you want.
- **`patch_shaders: true`** in the per-game config
  (`seed_configs/templates/CUSA00003.json.j2` → `custom_configs/CUSA00003.json`).
  shadPS4 then loads the fixed shader from `<shader>/patch/`.
- **The patcher + `bin/driveclub-shader-patch` wrapper**, so generating the fix is
  one command.

```sh
cd ansible
ansible-playbook install-driveclub-shader-patch.yml   # or: site.yml --tags driveclub
```

## Generating the shader fix (one-time, local)

The shader dump is produced by shadPS4's recompiler for your exact GPU/driver/
build, so it can't be pre-baked — you run DriveClub once:

```sh
# ~/bin is not on the box PATH, so call the wrapper by path:
distrobox-enter -n gaming -- ~/bin/driveclub-shader-patch dump   # clears old dumps,
                                                                 # arms dumping, launches DriveClub
# In the shadPS4 window: (one-time) Settings > Experimental > turn OFF "Enable
# Shader Cache". Let DriveClub reach the MAIN MENU, then quit the game.
distrobox-enter -n gaming -- ~/bin/driveclub-shader-patch        # patches the dump -> <shader>/patch/,
                                                                 # re-arms patch_shaders, disables dumping
```

Then in shadPS4's **Cheats/Patches** for DriveClub, enable one resolution/
widescreen patch (e.g. *Resolution patch (3840×1080)* + *Memory for up to 4K* +
*FOV fix for wide resolutions*) and play. The wrapper derives everything from
`group_vars/all/driveclub.yml`.

## How it works

- The wrapper's `dump` mode clears `<shader>/dumps/`, sets `dump_shaders=true` /
  `patch_shaders=false` in `CUSA00003.json`, and launches the game via
  `bin/shadps4-launch` (which auto-applies `patches/CUSA00003.xml`).
- The `patch` mode runs the vendored `driveclub_shader_autopatcher.py`, which
  scans the `.spv` dumps, uniquely identifies the de-interleave pass (960/540
  constants, 8×8 local size, image-fetch→image-write, no existing size query),
  injects the size query + rewrites the two `OpUGreaterThan` bounds checks, and
  writes the single patched module to `<shader>/patch/`. It then re-arms
  `patch_shaders=true` / `dump_shaders=false`.
- If the dump has none/many candidates (wrong game version, or dumped before the
  shader ran) the patcher refuses rather than guessing.

Revert the tooling with `-e dg_driveclub_revert=true` (leaves the XML, the
patched shader and the config in place).
