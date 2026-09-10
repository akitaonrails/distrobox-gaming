# Wave Race 64 Recompiled — `install_waverace_recomp`

[elliotttate/wave-race-64-recomp](https://github.com/elliotttate/wave-race-64-recomp)
is an **N64ModernRuntime + RT64 static recomp** PC port of Wave Race 64 (the same
stack as our GoldenEye/DK64/Banjo recomps). Opt-in role; installed 2026-09-10 at
`v0.4.0`.

## Why Wine (no native Linux build)

Upstream ships **Windows-x64 + macOS only**. The Linux source build is
undocumented (the docs cover Windows `clang-cl`/WSL and macOS Metal), and the
author states **RT64's Vulkan path was never tested** — so a native Linux build
is a high-risk, untested rabbit hole. The prebuilt **Windows** build, by
contrast, was author-smoke-tested on an **RTX 5090 with D3D12**, and we already
have the Wine + DXVK/vkd3d-proton path proven (TriAevum). So we run the Windows
build under **Wine 11**: RT64's D3D12 → GE-Proton's **vkd3d-proton** → the RTX
(`VK_ICD` pinned nvidia; the DXVK/vkd3d DLLs are dropped into the prefix and
overridden native). Verified: renders the attract demo in **16:9 widescreen** on
DP-1, presenting at 240 Hz with RT64 interpolation.

## ROM (required)

**Wave Race 64 (USA) (Rev A) / v1.1 only** — cart `WR`, region `E`, revision `1`,
header CRC `0x492F4B61 0x04E5146A`. Every other version (v1.0, JP, EU, Shindou)
is rejected. The box's dump `roms_mid/n64/Wave Race 64 (USA) (Rev A).n64` is
byte-swapped; the role converts it to a big-endian `.z64`, and the exe's
`--identify` confirms it. The recompiled binary is distributed prebuilt; the ROM
supplies only the original assets at runtime.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-waverace-recomp.yml     # or: site.yml --tags waverace_recomp
ansible-playbook install-waverace-recomp.yml -e dg_wr64_revert=true
```

The role downloads the hash-pinned Windows zip to the NAS, extracts it, converts
the ROM, builds the Wine prefix + installs the DXVK/vkd3d-proton DLLs, and
deploys `bin/waverace-recomp` + a Walker entry "Wave Race 64 · Recompiled".

**Launcher gotcha:** the launcher passes the ROM as a `Z:` path with **forward
slashes** (`Z:/mnt/…/Wave Race 64 (USA) (Rev A).z64`). Do NOT convert to
backslashes — a `\t`/`\n` in the path becomes a tab/newline and the exe falls
back to its ROM-picker GUI. Wine accepts forward slashes fine.

Gamepad is used if attached (8BitDo via SDL); on the keyboard, arrows = stick,
`X`=A, `C`=B, `Z`=Z, `Enter`=Start, `I/J/K/L`=C buttons. Graphics options are in
the in-game menu (Resolution Auto + Aspect Expand give the widescreen).
