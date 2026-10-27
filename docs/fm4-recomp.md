# Forza Motorsport 4 Recompiled (blocked on the required dump)

Experimental static recompilation of the Xbox 360 **Forza Motorsport 4**
([Alexbeav/fm4-recomp](https://github.com/Alexbeav/fm4-recomp), ReXGlue,
v0.1.0-alpha.2). The role `install_fm4_recomp` /
`install-fm4-recomp.yml` installs the pinned Windows x64 player build and runs
it through **GE-Proton** — the validated graphics profile uses the D3D12 ROV
path, which needs vkd3d-proton; plain Wine's vkd3d is not sufficient (same
Proton arrangement as [Azimuth](azimuth-fh2.md)).

## Status: waiting for the Europe Game of the Year Disc 1 dump

The player validates the exact game build. It requires the complete extracted
**FM4 Europe Game of the Year Disc 1** (title ID `4D530910`, media ID
`42C67824`) with these XEX SHA-256s, asserted by the role:

| File | SHA-256 |
|---|---|
| `default.xex` | `b34dfb88978819cccda6dafd755e7139970a58fbf6707dfbcba06846857f52bd` |
| `XMediaFacade_default.xex` | `2e82a8d08a59e79f4d68e68b744c2872855bfdd583eb39ad0a9c54e5b3fa1492` |
| `SpeechFacade_default.xex` | `49d506a2f8556836943d8bab3a50b6cd3877524500509ef462fb6e9802f2f4bf` |

Checked on 2026-10-18 — **none of the local dumps match**:

- `ROMS_FINAL/xbox360/Forza Motorsport 4 (USA) (Disc 1)` — USA build, different
  XEX hashes (verified via the Project Forza Plus tree's `default.xex.vanilla`).
- `ROMS_FINAL/xbox360/Forza Motorsport 4 - Essentials Edition (World)` — fully
  extracted and hashed; all three XEXs differ.
- `Project Forza Plus/Forza Motorsport 4 (Europe) (v3).zip` — a *modded* PFP
  archive, not a stock dump.
- `ROMS_FINAL/ps4/Forza.Motorsport.4.PAL.XBOX360-COMPLEX/` — the **original**
  PAL release (NFO date 10-2011); unpacked and XEX-hashed 2026-10-18, all
  three hashes differ (`default.xex` `6a7e9ae5…`). Valid PAL original for
  Xenia, wrong build for the recomp.

To unblock: obtain **redump `Forza Motorsport 4 (Europe) (Rev 1) (Racing Game
of the Year Edition)`** — the 2012 GOTY re-release, NOT the 2011 "normal"
Europe original (Limited Edition Racing Bundle), not Essentials, not USA.
Disc 1 (Play Disc) is redump disc 88560 (media ID 42C67824 is in the mastering
ring): ISO SHA-1 `3002a984c00ba6ca179ca177a917900f0c2c16c5`, MD5
`90ff7a4c1cd7237bb455fc6aeb4081a6` (8,738,846,720 bytes). The matching
Disc 2 (Content Install Disc) is the same edition (redump disc 89490) —
prefer it over the local USA Disc 2 for the content packages. Extract Disc 1
with `extract-xiso -x` into `ROMS_FINAL/PC/FM4-Recomp-EU-GOTY` (or point
`dg_fm4_recomp_game_root` at it), then run the playbook. The role verifies the
three XEX hashes before touching anything else.

## Version support (checked 2026-10-27)

Upstream has **not** widened support: the repository has had no commits since
2026-10-15 (`v0.1.0-alpha.2`), `release-policy.json` still pins the same three
XEX SHA-256s, and `docs/PLAYING.md` still says *"Copy the contents of your own
extracted FM4 Europe Game of the Year Disc 1"*. So the requirement remains
**EU Game of the Year (Racing GOTY, Rev 1, title ID 4D530910, media ID
42C67824) Disc 1 only** — USA, Essentials/World, the 2011 PAL original and any
later pressing are all still rejected by hash.

## Layout once installed

- Player: `~/distrobox/gaming/tools/fm4-recomp/releases/0.1.0-alpha.2/`
  (pinned zip, sha256-verified; empty zip-shipped `game/`/`disc2-content/`
  are replaced by links).
- `game` → the extracted EU GOTY tree on the NAS (single source of truth).
- `user` → stable `~/.local/share/fm4-recomp` (saves/caches/profiles survive
  updates — keep it; also in the backups list).
- `disc2-content` → `ROMS_FINAL/PC/FM4-Recomp-disc2-content` when staged: the
  four marketplace-content packages extracted from a Disc 2. The game
  validates each package's STFS metadata (title ID + content type) and
  installs them on first startup (`fm4_auto_install_disc2_content = true`).
  The local Disc 2 is the **USA** pressing — whether its packages pass
  validation against the EU base is untested; the game skips invalid ones.

## Baseline and policy

The validated profile is **native 1x resolution, D3D12 ROV, full synchronous
resolve readback, default vblank rate** (`fm4.toml`) — upstream states higher
internal resolution and timing overrides are **not safe** in this alpha, and
heavy scenes run around **30 FPS by design** of the correctness path. Per the
repo's timing policy we do **not** force 4K/gamescope/uncapped modes here; this
is the documented exception to the usual 4K baseline. `mnk_mode = true`:
keyboard + mouse are the validated input (`Space` = A, `Escape` = Start);
gamepad support in this alpha is unverified — test the 8BitDo before
considering input done.

Known upstream issues: fresh profiles can cache blank car thumbnails, career
validated only through the Sportsman tier, stable 60 FPS not achieved.

## Verification status

Not yet launched here — blocked on the required dump (above). When it runs:
first boot to the title screen, confirm the D3D12 device through
GE-Proton/vkd3d-proton, then a controller check before calling input done.
