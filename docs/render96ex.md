# Render96ex

Render96ex is the preferred native Linux Super Mario 64 PC port in this repo. It
replaces the earlier SM64 Plus automation because it supports the Render96 model
and high-resolution texture workflow from AlfaExploit.

Run or refresh it with:

```sh
cd ansible
ansible-playbook install-render96ex.yml
```

The role builds the `alpha` branch of `https://github.com/Render96/Render96ex`
from the pinned `dg_render96ex_git_ref` in
`ansible/group_vars/all/render96ex.yml`.

The local N64 source is `dg_render96ex_rom_source`, currently the USA ROM under
`{{ dg_rom_mid_root }}/n64`. That ROM is in byte-swapped `.n64` order, so the
role converts it to `baserom.us.z64` and verifies the canonical US SHA1:

```text
9bef1128717f958171a4afac3ed78ee2bb4e86ce
```

After building, the role installs:

- Render96 DynOS model pack v3.25 into `dynos/packs/`, checksum-pinned with
  SHA256 `22eea6dafcc0a87659d60513eb6a6b0f4ea0acbc6645a6b1b445de9e5812e6df`.
- Render96 HD texture pack tag `1.2.1` into `res/gfx/`.

The newer Render96 HD Texture Pack `1.3` release is aimed at the CoopDX
`textures/` layout, so this role keeps the known-good Render96ex `res/gfx/`
texture source until the Render96ex workflow changes.

Render96ex is built with `TEXTURE_FIX=1`, which is needed for the Render96
model and texture workflow.

Installed layout:

```text
{{ dg_box_home }}/tools/render96ex/current/sm64.us.f3dex2e
{{ dg_box_home }}/tools/render96ex/current/res/
{{ dg_box_home }}/tools/render96ex/current/dynos/packs/
{{ dg_box_home }}/bin/render96ex
```

`install-render96ex.yml` also runs `desktop_apps`, rendering and installing the
host application launcher `gaming-render96ex.desktop`.

The DynOS model pack may still need to be enabled once in-game via Pause → DynOS
/ Model Packs, depending on Render96ex's current defaults.
