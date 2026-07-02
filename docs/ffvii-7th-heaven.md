# Final Fantasy VII classic with MateriaForge / 7th Heaven

Use MateriaForge for the Linux route. 7th Heaven itself is still the Windows mod
manager; MateriaForge downloads and configures it for Proton/Linux and replaces
the deprecated 7thDeck workflow.

Status: MateriaForge `0.4.1` successfully installed 7th Heaven for the current
Steam app ID `3837340`, and the `7th Heaven Mod Manager (on gaming)` desktop
launcher was confirmed to open the manager after the wrapper was fixed to launch
from the 7th Heaven install directory.

Launching FFVII from 7th Heaven initially produced a black game window. The
FFNx log showed `renderer_backend = 0` auto-selecting D3D12 and then crashing in
DXGI/NVAPI under Proton. The local FFNx config was backed up to
`FFNx.toml.bak-renderer-auto-20260702` and changed to `renderer_backend = 5`
to force Vulkan. The Ansible role reapplies this override whenever an installed
`ff7/workingdir/FFNx.toml` is present.

## Supported Steam app IDs

- `3837340` — current FFVII classic / 2026 Steam app. This is preferred by the
  wrapper when both apps are installed.
- `39140` — legacy 2013 Steam app.

## Install prep tooling

```sh
cd ansible
ansible-playbook install-7th-heaven.yml
```

This installs MateriaForge and wrappers only. It does not silently edit Steam
configuration or mutate Proton prefixes. The playbook also renders the desktop
entry after the wrapper is installed.

Launch FFVII once from Steam first so Steam creates the Proton prefix for the
app, then run:

```sh
dg-7th-heaven install
```

MateriaForge is interactive. On the first configuration prompt, click **Save**;
do not click **Reset Defaults** unless you intentionally want to discard the
detected settings.

When MateriaForge asks where to install 7th Heaven, use the default destination
shown by `dg-7th-heaven install` for best wrapper and desktop integration. If you
choose a different destination, set `DG_7TH_HEAVEN_INSTALL_ROOT` to that path
before using `dg-7th-heaven launch`, `launch-game`, `path`, or `status`.

The Ansible prep role is read-only toward Steam config and Proton prefixes, but
the interactive MateriaForge installer can patch the selected game, Proton
prefix, desktop entries, and Steam config after you approve its prompts.

## Wrapper commands

```sh
dg-7th-heaven              # launch MateriaForge GUI
dg-7th-heaven install      # preflight status, then MateriaForge GUI
dg-7th-heaven status       # Steam app, Proton prefix, and launcher state
dg-7th-heaven list         # detected supported FFVII Steam apps
dg-7th-heaven path         # preferred installed 7th Heaven launcher path
dg-7th-heaven launch       # launch installed 7th Heaven, preferring 2026
dg-7th-heaven launch-game  # pass /launch /quit to 7th Heaven
```

Inside the box, the same commands are available as `7th-heaven`.

The desktop menu has two entries after `install-7th-heaven.yml` or
`site.yml --tags desktop` renders launchers:

- `7th Heaven Mod Manager (on gaming)` opens the 7th Heaven manager.
- `Final Fantasy VII - 7th Heaven (on gaming)` launches FFVII through 7th
  Heaven with `/launch /quit`.

## Troubleshooting notes

MateriaForge and its generated 7th Heaven launcher must not inherit arbitrary
host or repo working directories. If Proton/Pressure Vessel logs show a failure
like `bwrap: Can't chdir to /run/host/...`, ensure the distrobox-gaming wrapper
is current: it changes into the MateriaForge release directory before install
and into the 7th Heaven install directory before `launch` or `launch-game`.

### Black window on launch (32-bit NVIDIA userspace)

If launching FFVII through 7th Heaven opens a black window while vanilla
FFVII from Steam works, check `ff7/workingdir/FFNx.log` for:

```
BGFX Init error: vkCreateInstance failed -9: VK_ERROR_INCOMPATIBLE_DRIVER.
BGFX Init error: Unable to create DXGI factory.
```

Root cause: vanilla Steam launches `FFVII.exe` (64-bit), but 7th Heaven
launches the classic `ff7_en.exe` (32-bit) with FFNx injected. distrobox
`--nvidia` bind-mounts the host's **64-bit** NVIDIA driver files over the
box's `/usr/lib32` at every container start (the host has no lib32 NVIDIA
userspace). pressure-vessel classifies those impostors by their actual ELF
class, so its i386 override set ends up with no NVIDIA Vulkan driver at
all — every FFNx backend (D3D12, D3D11, Vulkan, OpenGL) needs 32-bit GPU
userspace, so all fail identically.

Fix: `bootstrap_packages/tasks/repair-lib32-nvidia.yml` unmounts the
impostor binds and symlinks the extracted `lib32-nvidia-utils` libraries
(the `dg_nvidia_lib32_*` workaround) into `/usr/lib32`. The binds come
back on every container restart, so re-run after restarting the box:

```sh
ansible-playbook reset-configs.yml --tags gpu
```

Note: `renderer_backend = 5` (Vulkan) in `FFNx.toml` is still the right
renderer — even with working 32-bit Vulkan, the auto backend picks D3D12
whose 32-bit vkd3d path crashes in `bgfx::Dxgi::init`. 7th Heaven
re-applies its GameDriver copy of `FFNx.toml` (in
`7thWorkshop/GameDriver/`) over `ff7/workingdir/FFNx.toml` on every
launch, so renderer changes must be made in 7th Heaven's Settings > Game
Driver (or in both files), not just the workingdir copy.

Stale pressure-vessel runtime copies can mask the repair after fixing
`/usr/lib32` — clear them with:

```sh
rm -rf "<STEAM library>/steamapps/common/SteamLinuxRuntime_sniper/var/tmp-"*
```

## Caveats

- The playbook only prepares MateriaForge/wrappers. 7th Heaven installation and
  game configuration remain interactive in MateriaForge.
- The desktop entries launch installed 7th Heaven wrappers. They will not open
  MateriaForge itself if you have not completed the interactive install yet; use
  `dg-7th-heaven install` first.
- If `status` shows `prefix=missing`, launch Final Fantasy VII once from Steam.
- If no launcher is found, complete the MateriaForge flow before using
  `launch` or the desktop entry.
