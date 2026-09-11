# Atari

Four ES-DE systems on three libretro cores: **2600** (Stella), **7800**
(ProSystem), **Lynx** (Handy) and the **Atari 800 / 5200** pair, which
share the single `atari800` core. Nothing new is downloaded — all three
cores were already in `dg_retroarch_cores` and `retroarch_extras` has
been fetching them from the buildbot since that list was written. What
was missing was the ES-DE side: with no entry in `dg_esde_systems` the
frontend never showed a system for them, so the cores sat installed and
unreachable except by loading a ROM by hand from RetroArch's own menu.

The **Atari ST** has its own page, [atari-st.md](atari-st.md): it is
opt-in (`install-atari-st.yml`) and keeps its TOS image in an isolated
RetroArch system dir rather than the shared one described below, because
a TOS revision is a per-machine choice and not a fleet-wide BIOS.

## Systems

| ES-DE system | Core | ROM dir | Extensions | BIOS |
|---|---|---|---|---|
| `atari2600` | `stella` | `roms/atari2600` | `.a26 .bin .rom .zip .7z` | none |
| `atari5200` | `atari800` (wrapper) | `roms/atari5200` | `.a52 .bin .car .rom .zip .7z` | optional |
| `atari7800` | `prosystem` | `roms/atari7800` | `.a78 .bin .zip .7z` | optional |
| `atarilynx` | `handy` | `roms/atarilynx` | `.lnx .o .zip .7z` | optional |
| `atari800` | `atari800` (wrapper) | `roms/atari800` | `.atr .bas .bin .car .cas .dcm .xex .xfd .zip .7z` | optional |

All four sit in the light `roms/` tier alongside NES and SNES — Atari
ROMs are kilobytes, and none of the `roms_mid` / `roms_heavy` /
`roms_rare` reasons apply.

The ROM directories are **yours to create**, on the host, before a system
appears. `dg_emudeck_root` is bind-mounted into the box read-only
(`create_box`), so no role can make them for you — and ES-DE hides a
system whose directory is missing or empty, which is why adding four
systems to a box with no Atari ROMs changes nothing visible.

## The 5200 shares a core with the 8-bit line

One core, two machines. Which one `atari800_libretro.so` boots is set by
the **`atari800_system` core option** — `5200` for the console,
`800XL (64K)` for the computers — and that is a value the core reads once
at init. RetroArch has no CLI flag for core options, so a launcher cannot
pass it; the only lever is the core's `.opt` file.

`bin/retroarch-atari800` writes it immediately before every launch:

```sh
retroarch-atari800 /…/roms/atari5200/Star\ Raiders.a52   # → atari800_system = "5200"
retroarch-atari800 /…/roms/atari800/Boulder\ Dash.atr    # → atari800_system = "800XL (64K)"
```

**The direction that matters is 8-bit, not 5200.** Reading the core's
`libretro/libretro-core.c`, it already forces 5200 mode by itself when it
recognises a 5200 cart — by the `.a52` extension, or by CRC32 against a
built-in 5200 database for `.bin`/`.rom`. But that force is one-way:

```c
if (autorunCartridge == A5200_CART || strcmp(var.value, "5200") == 0)
```

turns 5200 mode **on** and never off. So once a 5200 session has left the
option at `5200`, the next `.atr` or `.xex` boots as a 5200 — silently,
with 16 KB of RAM and a 5200 joystick layout. Rewriting the option before
every launch is what prevents that. On the 5200 side the wrapper is a
fallback, covering carts whose CRC the core's database does not carry.

Same pre-launch enforcement the xemu wrapper uses for `surface_scale`,
and for the same reason — a value the emulator owns at runtime,
re-asserted by the launcher instead of fought over.

Selection is by the ROM's own directory, with `.a52` honoured as a
fallback for 5200 carts filed outside `roms/atari5200`. The 8-bit machine
type can be overridden with `DG_ATARI800_SYSTEM`; the core accepts
`400/800 (OS B)`, `800XL (64K)` (our default), `130XE (128K)`, `XEGS`,
`Modern XL/XE(320K CS)`, `(576K)` and `(1088K)`. `DG_ATARI800_PRINT_SYSTEM=1`
makes the wrapper print its decision and the `.opt` path it would write,
without launching anything:

```sh
DG_ATARI800_PRINT_SYSTEM=1 ~/bin/retroarch-atari800 /path/to/roms/atari5200/any.a52
```

The target is `config/Atari800/Atari800.opt` under `dg_retroarch_dir`.
RetroArch names that directory after the core's `library_name`, which
this core sets to `Atari800` (`info->library_name = "Atari800"`). The
wrapper still matches the directory case-insensitively first, so a future
upstream rename degrades to writing the wrong directory rather than
dropping the option without a trace.

## BIOS

`dg_retroarch_system_bios` lists the files, `link_storage` symlinks them
out of `dg_bios_root` into `dg_retroarch_system_dir`
(`~/.config/retroarch/system`), and a missing source warns and is skipped
— same contract as the xemu BIOS links, nothing hard-fails.

| File | Used by | Needed? |
|---|---|---|
| `5200.ROM` | Atari 5200 | No — see AltirraOS below |
| `ATARIXL.ROM` | Atari 800, 800XL / 130XE | No — see AltirraOS below |
| `ATARIBAS.ROM` | Atari 800, built-in BASIC | No — see AltirraOS below |
| `ATARIOSA.ROM` / `ATARIOSB.ROM` | Atari 800, 400/800 OS revs A and B | No |
| `lynxboot.img` | Atari Lynx | No — the core HLEs the boot ROM |

Stella needs none. ProSystem takes an optional `7800 BIOS (U).rom`; it is
left out of the list because the filename varies by dump and the core
boots fine without it — add it to `dg_retroarch_system_bios` if your dump
uses a stable name.

None of these are redistributable, so source them yourself into
`dg_bios_root`, same as every other BIOS in
[setup-assets.md](setup-assets.md).

### None of it is actually required

The core **compiles in** Avery Lee's AltirraOS, a clean-room, freely
redistributable replacement for Atari's OS ROMs — `altirra_5200_os.c`,
`altirraos_800.c`, `altirraos_xl.c` and `altirra_basic.c` under
`atari800/src/roms/`. Selecting it is a core option, not a file:

| Option | Set to | Replaces |
|---|---|---|
| `atari800_os_5200` | `AltirraOS` | `5200.ROM` |
| `atari800_os_xl` | `AltirraOS` | `ATARIXL.ROM` |
| `atari800_os_800` | `AltirraOS` | `ATARIOSA/OSB.ROM` |
| `atari800_basic_version` | `Altirra BASIC` | `ATARIBAS.ROM` |

For the 5200 this is automatic: `bin/retroarch-atari800` writes
`atari800_os_5200 = "Original"` when `5200.ROM` is present in the system
dir and `"AltirraOS"` when it is not, so the console boots either way.
The 8-bit options are left to you — set them in RetroArch's core options
if you would rather not source the original ROMs. Compatibility is high
but not identical: a title that pokes at OS internals may behave
differently on the replacement.

The Lynx needs no file either. `handy` constructs
`new CSystem(..., bios_file, !bios_found, eeprom_file)` — the fifth
argument is `useEmu`, so when `lynxboot.img` is absent the core skips
loading it and high-level-emulates the boot ROM instead
(`CSystem::HLE_BIOS_FE00` and friends in `lynx/system.cpp`).

So **all four systems boot with no BIOS file at all.** The symlinks are
there for the case where you do own the dumps and would rather run the
original ROMs — `dg_retroarch_system_bios` picks them up when present and
warns and skips when not, which is why nothing here hard-fails.

## Applying

```sh
cd ansible
ansible-playbook site.yml --tags retroarch    # opt-in: fetches the cores
ansible-playbook site.yml --tags configure    # es_systems.xml + BIOS symlinks + wrapper
```

`--tags configure` is what regenerates `es_systems.xml`, creates the BIOS
symlinks and deploys `bin/retroarch-atari800`; `reset-configs.yml --tags
esde` regenerates only the XML. The `verify` role now stats the wrapper,
so a half-applied run fails loudly instead of producing four systems
whose launches do nothing.

Scraped art needs no extra step — the four systems go through
`configure_esde`'s `media-symlinks` task like every other entry, picking
up `<rom_dir>/media/` or `<rom_dir>/images/` if your art tree has them.

## Not covered

**Atari Jaguar** — no core. `libretro-virtualjaguar` has no Arch package
(see [distrobox-gaming-packages.md](distrobox-gaming-packages.md)) and is
not in `dg_retroarch_cores`; wiring it up means adding the core to that
list first.

The same orphaned-core situation still holds for the other cores this
repo downloads and never surfaces: `vice_x64` (C64), `puae` (Amiga),
`fmsx` / `bluemsx` (MSX), plus `o2em`, `opera`, `vecx`, `neocd` and the
`mednafen_*` set. Each is the same shape of fix as this one — an entry in
`dg_esde_systems`, and a BIOS line where the core needs one.

## Status

The wrapper's machine-type detection and `.opt` writing were exercised
against a scratch RetroArch tree: 5200-by-directory, 5200-by-extension,
8-bit default, `DG_ATARI800_SYSTEM` override, first-run creation of a
missing `config/Atari800/`, replacement rather than duplication of an
existing `atari800_system` line, unrelated core options left intact, and
no temp file left behind on repeat runs.

The core's `library_name`, the `atari800_system` option key, its accepted
machine values and the 5200 auto-detection were read from
[libretro-atari800](https://github.com/libretro/libretro-atari800)'s
`libretro/libretro-core.c` rather than assumed, and the ES-DE commands,
extensions and platform names come from ES-DE's own system definitions.

**The cores themselves have still not been launched on real hardware from
this change** — video, audio, controllers and BIOS compatibility want a
confirming run on the box.
