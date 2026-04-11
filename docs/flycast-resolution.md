# Flycast Resolution

Flycast reads `rend.*` keys inside the `[config]` section of `emu.cfg`.
Do not create a separate `[rend]` section.

The important fix for low-resolution rendering was:

```ini
[config]
rend.EmulateFramebuffer = no
rend.Resolution = 2880
rend.WideScreen = yes
```

Full framebuffer emulation is a compatibility fallback. When enabled globally,
it can force low-resolution rendering and prevent upscaling/widescreen behavior.

The wrapper installed by this repo forces the critical runtime values:

```sh
$DG_BOX_HOME/bin/flycast-hires
```

It passes:

```sh
-config config:pvr.rend=4
-config config:rend.Resolution=2880
-config config:rend.EmulateFramebuffer=no
-config config:rend.WideScreen=yes
-config config:rend.DupeFrames=yes
-config config:rend.DelayFrameSwapping=no
-config config:pvr.AutoSkipFrame=0
```

Use absolute wrapper paths in ES-DE and desktop entries. `distrobox-enter` does
not load the interactive shell PATH used by your terminal.

