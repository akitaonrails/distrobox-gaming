# Metroid Prime Hunters Recomp (`install_mph_recomp`)

[mstan/MetroidPrimeHuntersRecomp](https://github.com/mstan/MetroidPrimeHuntersRecomp) —
a native **recompilation** of the Nintendo DS *Metroid Prime Hunters* (built on
`ndsrecomp`), running as a real executable instead of emulating the hardware.
Opt-in role; installed 2026-08-14.

- **Form:** prebuilt **Linux AppImage** (`v0.3.0-alpha`, ~22 MB) — no build, no
  deps beyond `libfuse2` (already on the box). Renderer is **OpenGL 4.3
  compute**; input is **native SDL** (gamepad works out of the box).
- **Ships no game data.** It boots BIOS-less using the built-in **FreeBIOS +
  generated firmware**, so no DS BIOS/firmware dump is needed.

## Required ROM (strict)

The runner validates the ROM and accepts **only USA rev-0**:

- **`Metroid Prime - Hunters (USA).nds`** — game code **`AMHE`**, 64 MiB,
  **SHA-256 `7d0a98ff98e1b7c985d1f3d89b01730af1b2115061a4dfea847612d217a8b855`**.
- **Rejected:** `(USA) (Rev 1)` (`bcd9c2d4…`) and the Pt-Br fan translation
  (`044dfe47…`) — both are `AMHE` but modified/revised, so they fail the check.

The ROM stays on the NAS (`dg_mph_rom`) and is passed to the runner with
`--rom`; it is never copied.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-mph-recomp.yml     # or: site.yml --tags mph_recomp
scripts/install-host-launchers.sh           # refresh the host menu entry
ansible-playbook install-mph-recomp.yml -e dg_mph_revert=true   # remove
```

Launcher: `{{ dg_box_home }}/bin/mph-recomp`. It pins the RTX 5090
(PRIME/GLX-nvidia, the renderer is OpenGL), focuses DP-1, then runs the
AppImage with the ROM and the default flags. Extra args win, so
`mph-recomp --supersampling 4` overrides for a one-off.

## Boot + gamepad

- **Boot flags:** `--freebios --generated-firmware --boot direct`. Note
  `--freebios` **requires** `--boot direct` — the runner refuses otherwise.
- **Gamepad:** native SDL. The key flag is **`--mph-prime-controls on`**, which
  maps the DS stylus-aim onto the **right stick** — that's what makes this
  stylus-aim FPS actually playable on a controller. The 8BitDo is auto-detected;
  remap bindings in the AppImage's launcher (Mods page), or via the runner's
  `--mph-pad-bind-<action>` / `--mph-pad-aim-sensitivity` flags.
- **Presentation:** defaults to `--adaptive-widescreen both --supersampling 3
  --antialiasing 4` — effectively free on the RTX 5090 for a DS-resolution game.
  Tune in `group_vars/all/mph_recomp.yml` (`dg_mph_flags`).

## Updating

The AppImage is a manual download (not auto-updated). Bump `dg_mph_version` +
`dg_mph_asset_sha256` in `group_vars/all/mph_recomp.yml` and re-run — the
checksum-gated `get_url` pulls the new build.
