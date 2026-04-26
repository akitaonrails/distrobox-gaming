# Installing PS4 PKGs into shadPS4

shadPS4's QtLauncher Manager does not expose an "Install Package" button
in this build, so PKG installs have to be driven from the CLI inside the
gaming distrobox. There are two CLI tools available; one of them is
broken on patch PKGs, and the working one has a layout quirk you need to
know about. This runbook captures the working pattern after the
**Driveclub v1.28**, **The Last Guardian v1.03**, and **GT Sport v1.69**
installs hardened it.

Originals live at `/mnt/terachad/Emulators/ROMS_FINAL/ps4/...` (NAS
archive, scene release dirs as-shipped). Installs land at
`/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA<id>/`, which is
configured as shadPS4's `General.install_dirs[0].path` in
`~/.local/share/shadPS4/config.json`.

## TL;DR

1. RAR-packaged release? Extract with `unrar x -o+ first.rar extracted/`
   to get the `.pkg` file. Skip if you already have a loose `.pkg`.
2. Base PKG → `shadpkg extract base.pkg roms_rare/ps4/CUSA<id>/`
   (use the writable NAS path; tool dumps files at the top of the
   output dir, no CUSA wrapper).
3. Patch PKG → `shadpkg extract patch.pkg /mnt/data/.../pkg-staging/`
   (stage on local NVMe; do **not** point at the live CUSA dir or
   `ps4-pkg-tool` will segfault and `shadpkg` will silently overwrite
   files in unspecified order).
4. Merge: `rsync -a pkg-staging/ roms_rare/ps4/CUSA<id>/`. Patch files
   add alongside base files (same filename → patch wins; different
   filename → both kept), `eboot.bin` gets replaced.
5. `rm -rf pkg-staging`.
6. Drop a per-game JSON config under
   `~/.local/share/shadPS4/custom_configs/CUSA<id>.json`, ideally seeded
   from `ansible/roles/seed_configs/templates/CUSA<id>.json.j2`.

## Tool inventory

```
distrobox enter gaming -- compgen -c | grep -iE "^(pkg|orbis|ps4|shad)"
```

Two relevant tools in the gaming box:

| Tool | Path | Verdict |
|------|------|---------|
| `ps4-pkg-tool` | `/usr/bin/ps4-pkg-tool` (pacman-managed) | Works for **base** PKGs; **segfaults** (exit 139) on patch/update PKGs in any target dir. Auto-creates a `<output>/<CUSAID>/` subdirectory. |
| `shadpkg` | `/mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg` (locally built from <https://github.com/seregonwar/shadPKG>) | Works for **both** base and patch PKGs. Dumps files at the top of the output dir — **no CUSA subdirectory**. Use this. |

`shadpkg` is the canonical choice. `ps4-pkg-tool` is only useful as a
quick base-only fallback if `shadpkg` is unavailable.

Always run these inside the distrobox (`distrobox enter gaming -- …`) —
they were built against distrobox libs and may fail or misbehave on the
host. The NAS mounts (`/mnt/terachad/...`) and the bind-mounted box home
(`/mnt/data/distrobox/gaming/...`) are visible from both sides, so paths
in commands are stable across host and box.

## Why staging the patch matters

Both base and patch extractions write decrypted files to the output
directory. They **do not** know about each other:

- Pointing the patch at the populated CUSA dir directly makes
  `ps4-pkg-tool` segfault on first overwrite (consistently — even with a
  clean target the moment any sce_sys file collision happens).
- `shadpkg` happily writes into a populated dir but its overwrite
  semantics aren't documented. Trusting it to atomically merge multi-GB
  patch deltas onto a live game install is a recipe for a corrupt tree
  that's expensive to redo.

Stage the patch to a clean dir on local NVMe, then `rsync -a` into the
CUSA dir. The merge is now an explicit, dry-runnable step
(`rsync -an --itemize-changes`) you can verify before letting the writes
hit NAS.

`/mnt/data/distrobox/gaming/.cache/pkg-staging/` is a good staging
location: NVMe-fast, bind-mounted into the distrobox, easy to clean.

## Multi-volume scene archives (`.r00`, `.r01`, …)

Most PS4 release archives are RAR multi-volume sets:
`<release>.rar`, `<release>.r00`, `<release>.r01`, … Point `unrar` at
the first volume — it follows the chain automatically:

```
cd /mnt/terachad/Emulators/ROMS_FINAL/ps4/<release-dir>/
unrar x -o+ <release>.rar extracted/
```

Both `unrar` and `7z` are on the host and inside the box; either works.
After install, the multi-volume archive is redundant with the original
PKG; delete with a glob pattern that catches both extensions:

```
rm -f <release>.rar <release>.r[0-9][0-9]
```

Keep the `.nfo`, `.sfv`, `.jpg` (small, document the release) unless
you want a fully sterilised dir.

## The `app_param.sfo` gotcha (GT Sport-style backport repacks)

shadPS4 detects games by reading `<install>/sce_sys/param.sfo` for a
`TITLE_ID`. Most PKGs ship the file there. Some scene **backport** repacks
(in our library: `Gran.Turismo.Sport.incl.v1.69.PATCH.PS4-CUSA03220`,
labelled "v1.00 Base & v1.69 FW v5.05+ Backport Patch") instead ship a
top-level `app_param.sfo` and leave `sce_sys/` without a `param.sfo`.

After such a PKG is extracted, the game does **not** appear in shadPS4
because the title scanner finds no SFO. Symptom: install is on disk
(eboot, gtNN.vol, sce_sys/keystone, sce_sys/about/), but Manager shows
nothing.

Fix: copy the top-level SFO into the standard location.

```
cp roms_rare/ps4/CUSA<id>/app_param.sfo \
   roms_rare/ps4/CUSA<id>/sce_sys/param.sfo
```

Verify with the magic check + `TITLE_ID` field:

```
python3 -c '
import struct, sys
d = open(sys.argv[1],"rb").read()
m, ver, ko, do, n = struct.unpack("<4sIIII", d[:20])
print("magic:", m, "entries:", n)
for i in range(n):
    e = d[20+i*16:20+(i+1)*16]
    keyo, fmt, ulen, _, dataoff = struct.unpack("<HHIII", e)
    name = d[ko+keyo:].split(b"\x00",1)[0].decode()
    val = d[do+dataoff:do+dataoff+ulen].rstrip(b"\x00")
    print(" ", name, "=", val if fmt in (0x0204,0x0004) else int.from_bytes(val,"little"))
' roms_rare/ps4/CUSA<id>/sce_sys/param.sfo
```

A valid SFO begins with `\x00PSF` and lists `TITLE_ID`, `CONTENT_ID`,
`APP_VER`, `REGION`, etc. If `TITLE_ID` matches the directory name, the
install is discoverable.

A backport repack's SFO often pins `APP_VER=01.00` even when the patch
overlay is applied — cosmetic only, the eboot/data layer is the patched
one.

## Per-game config + Ansible template

After install, drop a per-game JSON under
`~/.local/share/shadPS4/custom_configs/CUSA<id>.json`. shadPS4 picks it
up at next scan. The minimal shape (matches what `seed_configs` deploys):

```json
{
  "General": { "neo_mode": false },
  "GPU": {
    "full_screen": true,
    "full_screen_mode": "Windowed",
    "window_width": 1920, "window_height": 1080,
    "internal_screen_width": 1920, "internal_screen_height": 1080,
    "patch_shaders": true,
    "readback_linear_images_enabled": false,
    "readbacks_mode": 0,
    "copy_gpu_buffers": false,
    "direct_memory_access_enabled": false,
    "vblank_frequency": 60
  },
  "Vulkan": {
    "gpu_id": 0,
    "vkvalidation_core_enabled": false,
    "vkvalidation_enabled": false,
    "vkvalidation_gpu_enabled": false,
    "vkvalidation_sync_enabled": false
  }
}
```

To make the config survive `reset-configs.yml`:

1. Add a `<title_id>.json.j2` template alongside the existing ones in
   `ansible/roles/seed_configs/templates/`.
2. Append an entry to `dg_shadps4_per_game_configs` in
   `ansible/group_vars/all/shadps4.yml`:
   ```yaml
   dg_shadps4_per_game_configs:
     - { title_id: CUSA00003, name: Driveclub }
     - { title_id: CUSA03745, name: The Last Guardian }
     - { title_id: CUSA03220, name: Gran Turismo Sport }
     - { title_id: CUSA<new>, name: <New Title> }
   ```
3. `seed_configs/tasks/shadps4.yml` loops over the list — no task edits
   needed for new titles.

## Worked examples

### The Last Guardian (CUSA03745, EU, v1.03)

```
cd /mnt/terachad/Emulators/ROMS_FINAL/ps4/The.Last.Guardian.PS4-DUPLEX/
unrar x -o+ duplex-the.last.guardian.rar extracted/

cd /mnt/terachad/Emulators/ROMS_FINAL/ps4/The_Last_Guardian_v1.03_PATCH_PS4-Playdox/
unrar x -o+ playdox-tlgv103.rar extracted/

distrobox enter gaming -- /mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg \
  extract /mnt/terachad/Emulators/ROMS_FINAL/ps4/The.Last.Guardian.PS4-DUPLEX/extracted/The.Last.Guardian.PS4-DUPLEX.pkg \
          /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03745/

mkdir -p /mnt/data/distrobox/gaming/.cache/pkg-staging
distrobox enter gaming -- /mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg \
  extract /mnt/terachad/Emulators/ROMS_FINAL/ps4/The_Last_Guardian_v1.03_PATCH_PS4-Playdox/extracted/EP9000-CUSA03745_00-LASTGUARDIANEU00-A0103-V0100.pkg \
          /mnt/data/distrobox/gaming/.cache/pkg-staging/

rsync -a /mnt/data/distrobox/gaming/.cache/pkg-staging/ \
         /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03745/
rm -rf /mnt/data/distrobox/gaming/.cache/pkg-staging
```

`sce_sys/param.sfo` came through cleanly from the base PKG, no
`app_param.sfo` workaround needed.

Per-game settings: `readbacks_mode=2` (Precise) and
`readback_linear_images_enabled=true`. shadPS4 0.10.0+ readbacks core
fixes climbing-on-Trico, the invisible spear, and barrel consumption;
**Precise** mode (read-protect, not just write-protect) is required.
Patch XML (`TheLastGuardian.xml`, covers CUSA03627/03745/04936/05152) is
auto-synced by shadPS4 into `~/.local/share/shadPS4/patches/shadPS4/`,
so no manual XML deploy needed.

### Gran Turismo Sport (CUSA03220, US, v1.00 + v1.69 backport)

```
# No RAR; the release dir already contains loose .pkg files.
mkdir -p /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03220

distrobox enter gaming -- /mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg \
  extract /mnt/terachad/Emulators/ROMS_FINAL/ps4/Gran.Turismo.Sport.incl.v1.69.PATCH.PS4-CUSA03220/Gran.Turismo.Sport.PS4-CUSA03220.pkg \
          /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03220/

mkdir -p /mnt/data/distrobox/gaming/.cache/pkg-staging
distrobox enter gaming -- /mnt/data/distrobox/gaming/tools/ShadPKG/build-cli/shadpkg \
  extract /mnt/terachad/Emulators/ROMS_FINAL/ps4/Gran.Turismo.Sport.incl.v1.69.PATCH.PS4-CUSA03220/Gran.Turismo.Sport.v1.69.PATCH.PS4-CUSA03220.pkg \
          /mnt/data/distrobox/gaming/.cache/pkg-staging/

rsync -a /mnt/data/distrobox/gaming/.cache/pkg-staging/ \
         /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03220/
rm -rf /mnt/data/distrobox/gaming/.cache/pkg-staging

# Backport-repack quirk: top-level app_param.sfo, no sce_sys/param.sfo
cp /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03220/app_param.sfo \
   /mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA03220/sce_sys/param.sfo
```

GT Sport **does not boot** on shadPS4 through 0.12.5 — known shader
recompiler bugs (`liverpool_to_vk.cpp StencilOp: Unreachable code`,
`vector_memory.cpp:197 Non immediate offset not supported`,
`spirv_emit_context.cpp:861` assertion). This install is on disk so
fresh nightlies can be tested without re-doing the install; the
per-game JSON ships safe defaults.

## Filesystem layout after a clean install

```
/mnt/terachad/Emulators/EmuDeck/roms_rare/ps4/CUSA<id>/
├── eboot.bin                         # patch-replaced if patch installed
├── sce_module/
├── sce_sys/
│   ├── param.sfo                     # required for Manager detection
│   └── ... (npbind.dat, keystone, about/, etc.)
└── <game data files>                  # .vol, .psarc, .ndx, .dat, etc.

/mnt/terachad/Emulators/ROMS_FINAL/ps4/<release-dir>/
└── extracted/<release>.pkg            # archive of the PKG, post-RAR-extract
```

The `extracted/<release>.pkg` files in `ROMS_FINAL` are kept as the
authoritative re-install source. Loose PKGs without RAR wrappers stay
in their release dir directly.

## NAS mount notes

By default the NAS share at `192.168.0.21:/volume1/TERACHAD/Emulators`
is mounted **read-only** on the host (`ro,nosuid,nodev,...`) as a safety
measure against accidental ROM deletion. PKG installs need write
access; the user has a known stack-mount remount-RW workflow for
maintenance windows. After install, the original `ro` mount remains
authoritative for runtime.

If a `cp`/`rsync`/`rm` returns "Read-only file system", check
`mount | grep terachad` — the latest mount entry wins, so an `rw`
remount may have been removed.

## See also

- [`docs/driveclub-shadps4.md`](driveclub-shadps4.md) — operational
  runbook for the Driveclub setup, including per-game settings rationale
  and the v1.28 cumulative-patch `param.sfo` issue (a sibling of the
  GT Sport `app_param.sfo` quirk).
- `~/Projects/shadPS4/docs/driveclub-v128-investigation.md` — fork
  investigation log; contains the deeper context on shadPS4 readbacks,
  tonemap behaviour, and per-game JSON keys.
- `ansible/roles/seed_configs/tasks/shadps4.yml` — the per-game config
  deployment loop; `seed_configs/templates/CUSA*.json.j2` for the
  per-title settings.
