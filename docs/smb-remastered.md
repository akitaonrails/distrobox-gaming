# Super Mario Bros. Remastered — `install_smb_remastered`

JHDev2006's **Godot 4.6** remake of Super Mario Bros. — includes SMB1, Lost
Levels, SMB Special and All Night Nippon, plus a full level editor and custom
level / resource-pack system. Upstream:
[JHDev2006/Super-Mario-Bros.-Remastered-Public](https://github.com/JHDev2006/Super-Mario-Bros.-Remastered-Public).
Opt-in role; installed 2026-08-11.

- **Distribution:** a prebuilt **native Linux** Godot export (`SMB1R.x86_64` +
  `.pck`, self-contained). Pinned to `dg_smb_remastered_version` (`1.1-rc4`),
  fetched from the GitHub release by sha256. **No Wine.**
- **You must provide** an original **SMB1 NES ROM** — none of the original
  assets ship with the game (they're generated from the ROM). This box has one
  in `nes/`; the role extracts the `.nes` into the game folder.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-smb-remastered.yml       # or: site.yml --tags smb_remastered
scripts/install-host-launchers.sh                 # refresh the host menu entry
ansible-playbook install-smb-remastered.yml -e dg_smb_remastered_revert=true
```

Launcher: `{{ dg_box_home }}/bin/smb-remastered` (menu: **"Super Mario Bros.
Remastered"**). It focuses DP-1, pins the RTX, and runs the game.

## ROM auto-import (no file picker)

The game runs in **portable mode** (`portable.txt`, so config/saves live beside
the executable). On first launch its `find_local_rom()` scans the executable's
own folder for a `*.nes`, and copies the first match to `config/baserom.nes`,
generating the SMB1 assets. The role stages the `.nes` from
`dg_smb_remastered_rom_zip` into the install dir, so the import is fully
automatic — no drag-and-drop or file dialog. Saves for all four campaigns land
in `config/saves/`.

## Rendering + controller

- **Rendering:** Godot picks the **OpenGL Compatibility** renderer here and runs
  on the RTX 5090. The launcher pins GLX/PRIME (and the NVIDIA Vulkan ICD, in
  case a driver update flips it to the Vulkan backend) so it never lands on the
  AMD iGPU.
- **Fullscreen:** the role seeds `config/settings.cfg` with video `mode=3`
  (→ `WINDOW_MODE_EXCLUSIVE_FULLSCREEN` on Linux) once, so it comes up
  fullscreen; `settings.cfg` is otherwise left to the game (in-game changes,
  including audio volume and controls, are preserved). ALT+ENTER also toggles
  fullscreen.
- **Controller (always supported):** native Godot gamepad input — the 8BitDo
  works out of the box.
- **Volume:** unlike CannonBall, this one has in-game volume (Settings → Audio,
  master/music/sfx).

## Notes

- Bump `dg_smb_remastered_version` + `_asset_sha256` for a new release;
  re-extract preserves `config/` (settings, imported ROM, saves).
- The SMB1 ROM on the NAS is only read, never modified.
