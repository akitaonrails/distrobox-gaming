# Project Gotham Racing Recomp

[hk21x/pgr1-recomp](https://github.com/hk21x/pgr1-recomp) recompiles the
original Xbox release of Project Gotham Racing into a Windows executable, using
the same XboxXBERecomp SDK as [NightFire](nightfire-recomp.md). The port does
not include game data: the game's code is built on your own machine from your
own disc. The executable is a Windows binary; on this box it runs under Wine.
Our opt-in role stages the pinned build launcher, verifies the owned USA disc,
creates a dedicated Wine prefix with native `d3dcompiler_47` + DXVK, publishes
the menu entry, and checks the build completed.

## Owned game data

The current `dg_pgr1_iso` is `ROMS_FINAL/xbox-iso/Project Gotham Racing
(USA).iso`. Its SHA256 is
`7798dd31728676f342e7c17db1b3b336ce00cad0ab77138d46d561cfb712dd9b`. Inside that
image the title id is `4D530003` and `default.xbe`'s SHA-1 is
`0d55fff29ceb34ab4dfcfc4820e823d967ca1469` — the supported USA 1.0 release. The
image is a trimmed XISO, so the launcher accepts either the `.iso` or a folder
with the disc's files, and it re-checks `default.xbe`'s SHA-1 before building.
Other releases (Europe 1.0/1.1, and the untested Japanese/Asian discs) are not
this role's pin. On another machine, override `dg_pgr1_iso` and its ISO
checksum in host vars.

## Install and rebuild

```sh
cd ansible
ansible-playbook install-pgr1-recomp.yml
```

The upstream launcher is a Windows GUI. Choose your disc image (or the folder
with the disc's files) in its **Your game** section, review and accept the
Microsoft C++ libraries and Windows SDK terms, then press **Build**. The first
build downloads its Windows build toolchain (clang/LLVM, CMake, Ninja, Git) and
recompiles the game — expect a long run, several GB of downloads, all under
Wine. The role reports an explicit incomplete-build error until
`PGR1/play/PGR1.exe` exists; rerun it after the GUI build. Run `pgr1-recomp
build` to reopen the build launcher later. The game menu runs the compiled game
when it is present.

The launcher copies the disc into its `PGR1/play` tree and builds under `PGR1/`
beside it. It keeps saves and the profile in `play/hdd`, settings in
`play/pgr1.toml`, and logs in `play/logs`. The role seeds the settings file only
when absent. The save backup registers the title's `hdd/E/UDATA/4d530003`
directory, `hdd/display.bin`, and `pgr1.toml`; the copied disc, toolchain,
source checkout, shader cache, `hdd/Z` disc cache, and logs are reproducible and
excluded.

## Wine specifics (why the prefix carries extra DLLs)

Two issues, both already solved for the sibling NightFire role on this SDK:

- **Native `d3dcompiler_47`.** The game compiles its translated HLSL shaders at
  runtime through `D3DCompile`. Wine's built-in `d3dcompiler_47` routes to the
  vkd3d-shader HLSL compiler, which rejects the generated shaders (error
  `E5000`, *"syntax error … expecting ')' or ','"*) — the window renders black,
  then flickers with missing geometry. Microsoft's own compiler (what the
  upstream dev uses on Windows) accepts the same shaders. The role installs
  mozilla/fxc2's checksum-pinned vendored copy of Microsoft's real
  `d3dcompiler_47.dll` (x64 + x86) into the prefix and sets the native override.
- **DXVK.** WineD3D runs the D3D11 renderer far too slowly for the panel. The
  role pins DXVK v3.1.1 (dxgi + d3d11) for this prefix, translating D3D11 to
  Vulkan on the RTX.

## Graphics and input

`pgr1.toml` is seeded at the box ceiling: `renderer = "d3d11"`,
`display_mode = "fullscreen"` inside gamescope at 3840×2160, explicit `16:9`,
`msaa8`, 16× anisotropic, `sharpen = 50`, `render_percent = 100`, vsync on, and
`skip_intro = true`. The Xbox D3D output (640×480) is supersampled to 4K
(render scale ≈ 4.5×). The launcher opens the game through gamescope so it
lands fullscreen on the landscape 4K monitor (DP-1) instead of being tiled.

`skip_intro` matters on Wine: the `FMV\Intro.bik` intro movie's video freezes on
its first frame while its audio plays, so the game appears stuck on a static
image. Skipping it goes straight to the front end.

Gamepad: the game uses SDL/XInput with hot-plug ("no game controllers but Xbox
pads — one plugged in later is picked up"), and the prefix sets winebus
`Enable SDL` + `Map Controllers`. An 8BitDo in XInput mode is picked up as an
Xbox pad; the in-game controller settings bind it. Steering wheels get the raw
axis path upstream.
