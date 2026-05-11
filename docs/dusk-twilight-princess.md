# Dusk — Twilight Princess reimplementation

[Dusk](https://github.com/TwilitRealm/dusk) is an open-source
reverse-engineered reimplementation of *The Legend of Zelda:
Twilight Princess* (GameCube). Runs natively on Linux as a single
AppImage, uses Vulkan (RTX 5090 + NVIDIA proprietary driver works
fine), and supports higher resolutions / framerates than the
original GameCube target. You provide your own legally-dumped disc
image.

This entry is **optional** — not in `site.yml`. Run it explicitly:

```sh
cd /mnt/data/Projects/distrobox-gaming/ansible
ansible-playbook install-dusk.yml
```

## What the playbook does

1. Hits GitHub's latest-release API for `TwilitRealm/dusk`, picks
   the Linux x86_64 AppImage asset.
2. Downloads it to `tools/dusk/Dusk.AppImage` inside the box home.
3. Deploys a `dusk` wrapper at `~/bin/dusk` (the box's `~/bin` is
   on PATH for interactive zsh).
4. Walks the configured ROM search paths
   (`dg_rom_heavy_root/gc`, `dg_roms_final_root/gc` by default) for
   any Twilight Princess disc image (`.iso .gcm .gcz .ciso .rvz`).
5. For raw `.iso`/`.gcm` matches, computes SHA-1 and reports whether
   it matches Dusk's accepted GameCube USA / EUR hashes.
6. For compressed `.rvz`/`.gcz` matches, prints a ready-to-run
   `dolphin-tool convert` command for the conversion to raw ISO.

## Supported game dumps (raw ISO SHA-1)

| Region | SHA-1 |
|---|---|
| GameCube USA (NTSC-U) | `75edd3ddff41f125d1b4ce1a40378f1b565519e7` |
| GameCube EUR (PAL) | `2601822a488eeb86fb89db16ca8f29c2c953e1ca` |

Wii versions of Twilight Princess are **not** supported by Dusk yet.

## Disc image format

Dusk wants **raw GameCube ISO** (`.iso` / `.gcm`). If your dump is in
Dolphin's compressed `.rvz` or `.gcz` container, the playbook prints
the exact `dolphin-tool convert` command to produce a raw ISO
alongside it (no re-dump from disc needed; the conversion is
lossless and the resulting ISO will match the official SHA-1).

Example (the playbook prints the matching one for your specific
discovered file):

```sh
distrobox enter gaming -- dolphin-tool convert \
  -i "/path/to/Twilight Princess (USA).rvz" \
  -o "/path/to/Twilight Princess (USA).iso" \
  -f iso
```

`dolphin-tool` ships with the `dolphin-emu` package which is already
installed in the gaming distrobox.

## Launch

```sh
distrobox enter gaming -- dusk
# or, from an interactive box shell:
distrobox enter gaming
dusk
```

Dusk opens its launcher window. First time:

1. **Select Disc Image** → point at the raw `.iso` you converted
   (or had originally).
2. **Play**.

Dusk caches the choice; subsequent launches skip straight to game.

## Caveats

- The conversion step is one-time per disc image; keep the raw ISO
  beside the original `.rvz` and Dolphin will still pick up the
  `.rvz` for normal GameCube emulation (Dolphin handles both).
- Dusk is active development; the binary's UI / settings layout can
  shift between releases. The role pins to "latest" so re-running
  picks up the newest build.
- Some Steam-Proton-class apps shell out to `open <url>` for
  hyperlinks; if Dusk does so (release-note popups, update checks),
  the `open` shim already deployed by `seed_configs` routes it
  through the host's browser via `org.freedesktop.portal.OpenURI`.
- No anti-cheat to worry about — Dusk is single-player only.
