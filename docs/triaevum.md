# TriAevum (OoT 3D AOT recomp) — `install_triaevum`

[TriAevum](https://github.com/coccofresco/TriAevum) is a native PC **AOT
recompilation of *The Legend of Zelda: Ocarina of Time 3D*** (the 3DS remake),
with a modern NRI/Vulkan renderer, cel/toon shading, real widescreen, 60/90 FPS
visual interpolation, a single-screen TopScreen HUD, and (the author's words)
"a lot of grass". Opt-in role; installed 2026-09-08 at `v0.6.0-alpha.1c`.

**It is a Windows-x64-only experimental alpha** — the project does not target
Linux. We run it under **Wine 11 + DXVK/vkd3d-proton** on the RTX. It works, but
it is early (upstream has only tested through the title/file-select on USA).

## The one thing that made it work

TriAevum's NRI backend enumerates the GPU via **DXGI/D3D12**, and Wine's
*built-in* vkd3d can't map the DXGI adapter to a Vulkan device — it crashes with
`d3d12_get_vk_physical_device: Could not find Vulkan physical device` then an
`EXCEPTION_BREAKPOINT`. Fix: drop **GE-Proton's DXVK (`dxgi`,`d3d11`) +
vkd3d-proton (`d3d12`,`d3d12core`)** DLLs into the prefix and override them
native (the launcher sets `WINEDLLOVERRIDES`). vkd3d-proton then enumerates the
RTX properly (SM 6.8, DXR, DX Ultimate) and the game renders. `VK_ICD` is pinned
to nvidia; the "AMD GPU 0x73df" in the log is only GE-Proton's cosmetic DXGI
vendor spoof — actual rendering is on the 5090.

## ROM — no decryption needed

Forge imports a **decrypted** `.cci`/`.3ds` and refuses encrypted partitions.
The box's OoT 3D dump (USA Rev 1, the one Azahar runs) is **already decrypted**
— it has plaintext `.code`/`IVFC`/`CTR-P-`; the NCCH "encrypted" flag is the
legacy-flag false positive the Forge docs describe (which is also why Azahar
runs it without keys). So no keys and no decrypt step are required.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-triaevum.yml        # or: site.yml --tags triaevum
ansible-playbook install-triaevum.yml -e dg_triaevum_revert=true   # remove launcher+prefix
```

The role downloads the hash-pinned Windows zip to the NAS, extracts it (without
clobbering the Forge-prepared `data/`), builds the Wine prefix, copies the
DXVK/vkd3d-proton DLLs, and deploys the launcher + Walker entry ("TriAevum -
Ocarina of Time 3D").

- **Play:** `bin/triaevum` (opens on DP-1; 8BitDo via SDL; F1 = settings,
  F2 = toggle added effects).
- **One-time setup (fresh install):** `triaevum setup` runs `TriAevumForge.exe`
  — select the decrypted OoT 3D `.cci`; it extracts → prepares → activates the
  bundled precompiled title and downloads the TopScreen texture pack (needs
  internet). Our NAS install already carries the prepared `data/`, so a normal
  rebuild plays immediately; only a from-scratch NAS wipe needs this step again.
- **Keep `data/`** — it holds saves, settings, and the locally prepared title.

## Custom textures (Azahar-compatible)

TriAevum advertises **Azahar-compatible custom textures and dumping** (the
`TriAevum.exe` carries a `CustomTextures` system, and the TopScreen pack is
itself a hash-named `data/mods/` entry). So Henrico Magnifico's OoT 3D 4K pack —
the same Azahar/Citra `tex1_WxH_<hash>` format we confirmed loads on Azahar —
should apply here too; wiring it in is a follow-up.

## Notes

- Bump `dg_triaevum_version` + `dg_triaevum_zip_sha256` to update (it's a rolling
  alpha; grab the new Windows-x64 zip's sha256).
- The DLLs come from the newest installed GE-Proton (`dg_triaevum_geproton_glob`).
- This overlaps OoT 3D on Azahar (which has the Henrico 4K pack); TriAevum is the
  faster, cel-shaded, widescreen take — but an unfinished alpha.
