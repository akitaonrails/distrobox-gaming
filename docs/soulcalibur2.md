# Soulcalibur II — native Xbox recompilation

[tmcleroy/soulcalibur2-recomp](https://github.com/tmcleroy/soulcalibur2-recomp)
is a **static recompilation** of *Soulcalibur II* (original Xbox): the game's
program is translated ahead of time into C and runs on a native **SDL3 + Vulkan**
runtime — no emulator. It adds training mode, rollback online play, a free
camera, widescreen, higher resolutions and RetroArch shaders, and puts all three
console-exclusive guests on one roster (Spawn from Xbox, Link from GameCube,
Heihachi from PS2). Opt-in role `install_soulcalibur2`
(`group_vars/all/soulcalibur2.yml`).

- **Role:** `install_soulcalibur2` — `ansible-playbook install-soulcalibur2.yml`
  (or `site.yml --tags soulcalibur2`).
- **Upstream:** prebuilt `Soulcalibur2Recomp-linux-x86_64.tar.gz`, pinned by
  version + sha256. No build step.
- **Needs:** the user's own **USA (or EU) retail** Soulcalibur II Xbox disc image.

## Disc (user-supplied, like a ROM)

The game reads the owned Xbox disc image directly and validates its `Default.xbe`
itself — it accepts only the **USA retail** dump:

- `d7c2e1fc993350821e3f7e13cfd1c9d4ba6a7bf91011005bdd1f843899efb730` (as on the disc), or
- `7ce12851850ab46766f77c612b251afe7c8bd81f879e11b4836bdf766be542c6` (extract-xiso's media patch = "the program target").

An EU disc is also supported upstream. The staged dump at
`ROMS_FINAL/xbox/Soulcalibur II (USA)/Soulcalibur II (USA).iso` extracts to
`7ce12851…`, XBE cert region `0x01` (North America) — accepted. (A **Japanese**
disc, region `0x02`, is rejected — the recomp is of the USA binary; see the
parked note in the project memory.)

Only the small writable Xbox HDD partitions (saves/config, a few MB) land in the
storage dir — the ISO stays the data source, read in place.

## How it runs

The role deploys a launcher (`bin/soulcalibur2`) that runs the game binary
directly (no GUI launcher needed):

```sh
soulcalibur2 --disc <iso> --storage ~/.local/share/"Soulcalibur II" \
  --settings ~/.local/share/"Soulcalibur II"/settings.ini \
  --fullscreen --widescreen --skip-intro
```

(`--disc` requires an explicit `--storage`.) The GUI launcher
(`soulcalibur2-launcher`) ships in the tarball too, for building guests, online
matchmaking and remapping — run it directly if you want those.

## Graphics — native Wayland 4K/60 widescreen

`settings.ini` (`[features]`) is seeded with `resolution=6` (**8x**, a
5120×3840 / 6827×3840-widescreen render target supersampled far above the 4K
panel — the RTX's quality ceiling for this Xbox-era fighter) and `widescreen=1`
(the game's own 16:9). The game boots fullscreen; the launcher focuses `DP-1`
first. Verified: Arcade at **4K / 60 FPS**, widescreen, native Wayland on DP-1.

**`SDL_VIDEODRIVER=wayland`** is set by the launcher (the UltraTears lesson — see
[ultratears.md](ultratears.md)): the bundled SDL3 otherwise picks x11
(XWayland), where the Vulkan present throttles on this fractional-scale panel.

Shaders (CRT Royale/Guest/Lottes, scanlines, xBRZ, ScaleFX) are off by default
(`shader=0`) and switchable in the in-game menu (Esc / F1 / gamepad Back). The
resolution field maps `Original|2x|3x|4x|5x|6x|8x` → `0|1|2|3|4|5|6`.

## Guests (Spawn / Link / Heihachi)

**Spawn** is on the Xbox disc and always available. **Link** (from a GameCube SC2
disc) and **Heihachi** (from a PS2 SC2 disc) are optional: open the GUI
launcher's **Guest** page, point it at your disc, and it builds them once (a few
minutes), region matching the USA/EU base. This box's current GameCube SC2 is the
**Japanese** release and there is no PS2 SC2 dump, so only Spawn is set up by
default; add USA/EU GameCube + PS2 discs to enable the other two.

## Gamepad

8BitDo works natively through the bundled **SDL3**. The in-game menu is the Back
button; Start is Start. The launcher sets `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`.

## Saves & backups

Saves and config live in `~/.local/share/Soulcalibur II` (the Xbox HDD
partitions `partition1/TDATA`,`UDATA` plus `settings.ini`), registered as the
`soulcalibur2` set in `dg_save_sets`. The binary is re-extracted and the disc
re-read on a from-scratch rebuild; only this storage dir carries real state.

## Revert

```sh
ansible-playbook install-soulcalibur2.yml -e dg_sc2_revert=true
```

Removes the launcher, install dir and desktop entry. Saves/config under the
storage dir and the NAS disc are left untouched.
