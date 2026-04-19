# PS1 60 FPS patches on DuckStation

Most PS1-era racing games ran rendering at 30 FPS while physics/timers ran
at the 60 Hz NTSC vsync. Patches that double rendering to 60 FPS are
therefore usually safe — they don't desync the sim, just draw a frame for
every vsync instead of every other one.

## Colin McRae Rally 1 (SLUS-00431, USA)

**Fastest fix:** built-in developer cheat. Enter **`SILKYSMOOTH`** as the
driver name on a new profile. Game runs at 60 FPS natively. Draw distance
shortens slightly (roadside trees thin out) — cosmetic only, no physics
impact. First-party option, fully safe for daily play and speedruns.

No emulator-side configuration needed; works on any DuckStation version.

## Colin McRae Rally 2.0 (SLUS-01222, USA)

**Fix:** GameShark 60 FPS code, applied via DuckStation's built-in Cheat
Manager (Tools → Cheat Manager → pick CMR2 → Add → paste code as
"GameShark" type).

Source: [GameHacking.org CMR2 NTSC-U codes](https://gamehacking.org/game/88607)

Important per-game DuckStation settings:

- **Force NTSC Timings = OFF** (default) — leave it off. The 60 FPS code
  is tuned for native NTSC timing; forcing NTSC on an already-NTSC disc
  causes speed variance.
- **CPU Clock = default** (no overclock). Speedrun.com's CMR2 preset
  [confirms](https://www.speedrun.com/cmr2/forums/13zdt) default clock +
  Force NTSC Timings off as the correct combo for NTSC-U.

Not safe on PAL discs — use only with SLUS-01222 (NTSC-U).

Alternative: [CMR 2.1 fan romhack](https://www.romhacking.net/hacks/322/)
bundles the 60 FPS patch + other improvements as an IPS patch over the
original ROM. Avoid if you want to keep your ISO pristine.

## Why these are safe

Colin McRae Rally 1 and 2 were built on PlayStation SDK's standard
vsync-interrupt timing — game logic ticks on the 60 Hz IRQ from the GPU,
then renders every *other* tick to keep within the console's fillrate
budget. Doubling the render rate (either via `SILKYSMOOTH` or a GameShark
address patch) just removes the "skip every other vsync" gate. Physics
step count per second is unchanged.

Contrast with games that tie physics directly to frame count (e.g.
Gran Turismo series, Ridge Racer V on PS2): doubling render there
doubles physics too, which desyncs replays, AI, and save compatibility.

## References

- [SILKYSMOOTH cheat description (SuperCheats)](https://www.supercheats.com/playstation/colin-mcrae-rally/649/silkysmooth-60-fps-br-open/)
- [Speedrun.com CMR1 cheat codes guide](https://www.speedrun.com/cmr1/guides/tvw00)
- [Speedrun.com CMR2 DuckStation settings](https://www.speedrun.com/cmr2/forums/13zdt)
- [GameHacking.org CMR2 NTSC-U codes](https://gamehacking.org/game/88607)
- [romhacking.net CMR 2.1 fan hack](https://www.romhacking.net/hacks/322/)
