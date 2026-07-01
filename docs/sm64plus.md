# Super Mario 64 Plus

SM64 Plus is managed by the optional `install_sm64plus` role and focused
playbook:

```sh
cd ansible
ansible-playbook install-sm64plus.yml
```

The role builds the native Linux PC port from
`https://github.com/MorsGames/sm64plus`. The upstream source is pinned by
`dg_sm64plus_git_ref` in `ansible/group_vars/all/sm64plus.yml` so rebuilds are
reproducible.

The local N64 source is `dg_sm64plus_rom_source`, currently the USA ROM under
`{{ dg_rom_mid_root }}/n64`. That ROM is in byte-swapped `.n64` order, so the
role converts it to `baserom.us.z64` and verifies the canonical US SHA1:

```text
9bef1128717f958171a4afac3ed78ee2bb4e86ce
```

Current upstream needs the Linux OpenGL include fix from MorsGames/sm64plus PR
134, otherwise the build fails in `src/pc/gfx/gfx_opengl.c` with missing symbols
such as `GL_RGBA8`, `GL_READ_FRAMEBUFFER`, and `glTexImage2DMultisample`. The
role downloads and applies that patch before running `make`.

Installed layout:

```text
{{ dg_box_home }}/tools/sm64plus/current/sm64.us
{{ dg_box_home }}/tools/sm64plus/current/gfx/
{{ dg_box_home }}/bin/sm64plus
```

The wrapper runs `sm64.us` with the installed `gfx` directory as its first
argument, matching upstream's Linux launcher requirement. `install-sm64plus.yml`
also runs `desktop_apps`, which renders and installs
`gaming-sm64plus.desktop` for the host application menu.
