# Model 2 / Model 3 arcade easy-settings cheat-sheet

These arcade boards store all operator settings in battery-backed NVRAM (there
are no config files). You change them from each game's in-game **Test/Service
menu**, then **exit properly so the values persist**. Universal rule on Sega
boards: **Difficulty and the game-specific life/time knobs live under
`GAME ASSIGNMENTS`; Free Play is always under `COIN ASSIGNMENTS`** (set
COIN/CREDIT SETTING to the "FREE PLAY" entry, often option #27 — never in Game
Assignments).

After tuning, run `ansible-playbook sync-arcade-nvram.yml` to push the NVRAM up
to the NAS seed sources so the settings survive a from-scratch rebuild (the
reverse NAS→box seed is one-time, marker-gated, in `seed_configs` /
`install_m2emulator`).

## How to enter the Test menu

- **Supermodel (Model 3):** press the mapped **Test** input (bind it in
  Supermodel's config; **Service** = move cursor, **Test** = change value).
  Navigate to `EXIT` and press Test to save — leaving any other way discards
  changes and the NVRAM reverts.
- **ElSemi's Model 2 Emulator:** **Test** = **F2**, **Service** = **F1** (also
  mappable to pad buttons). Service moves, Test changes, exit via the menu's
  EXIT line to save.
- Caveat: a few Model 2 titles (e.g. Gunblade NY, Sega Rally) have historically
  failed to persist test-menu changes across a cold restart under emulation —
  re-check that your settings stuck after relaunching.

---

# Model 3 (Supermodel)

### Daytona USA 2 (Battle on the Edge / Power Edition)
- **DIFFICULTY** → `EASY` (EASY / NORMAL / HARD / HARDEST).
- **GAME MODE** → `NORMAL (SPRINT)` for the shortest race; the MILE events have no time limit if you'd rather never time out.
- **MOTOR POWER** → weakest for a lighter wheel.
- **FREE PLAY** → ON. LINK ID = `SINGLE` for standalone.
- No lives/continues — time/checkpoint based, so EASY + SPRINT is the easy combo.

### Dirt Devils
- **DIFFICULTY** → `EASY` (default NORMAL).
- **TIME (CANYON/STADIUM/DESERT)** → longest per course.
- **STEERING FORCE** → lower from the 80% default.
- **FREE PLAY** → ON. COMMUNICATION MODE = standalone.

### Emergency Call Ambulance
- **DIFFICULTY** → `EASY` (verify labels).
- **TIME / TIME LIMIT / TIME EXTENSION** → most generous (key knob — countdown-to-hospital time-attack).
- **FREE PLAY** → ON.

### Sega Bass Fishing / Get Bass
- **DIFFICULTY** → `EASY` (verify).
- **TIME LIMIT** → longest (main easy lever).
- **FREE PLAY** → ON. Score-attack — difficulty/time govern how long you fish.

### Fighting Vipers 2
- **DIFFICULTY / LEVEL** → `EASIEST`.
- **TIME LIMIT** → longest / `INFINITE` if offered.
- **ROUNDS** → fewest (e.g. 1).
- **FREE PLAY** → ON (also unlimited continues).

### Harley-Davidson & L.A. Riders
- **DIFFICULTY** → `EASY`.
- **TIME / TIME EXTENSION** → most generous start + per-checkpoint extension.
- **STEERING FORCE** → lower.
- **FREE PLAY** → ON.

### L.A. Machineguns
- **DIFFICULTY** → `EASIEST`.
- **LIFE / LIFE GAUGE** → MAX; **DAMAGE per hit** → lowest if separate.
- **FREE PLAY** → ON (free continues).

### Le Mans 24
- **DIFFICULTY** → `EASY`.
- **TIME / TIME EXTENSION** → longest start + max time-per-lap.
- **STEERING / MOTOR FORCE** → lower.
- **FREE PLAY** → ON. LINK/CABINET = standalone.

### Lost World: Jurassic Park
- **GAME DIFFICULTY** → `VERY EASY` (VERY EASY … VERY HARD).
- **LIFE SETTING → INITIAL LIFE** → MAX and **MAX LIFE** → MAX.
- **FREE PLAY** → ON. Same gun-game layout as House of the Dead.

### Magical Truck Adventure
- **DIFFICULTY / RANK** → `EASY` / lowest.
- **LIFE / DAMAGE** → MAX / most forgiving.
- **FREE PLAY** → ON. Self-test: Left Start ×2 → Service → Left Start → Service → Test. Labels undocumented — verify.

### The Ocean Hunter
- **DIFFICULTY** → `EASIEST` / lowest.
- **LIFE / DAMAGE GAUGE** → MAX (drains from creature hits).
- **FREE PLAY** → ON.

### Scud Race (Sega Super GT) + Scud Race Plus
- **DIFFICULTY** → `EASY` / lowest (higher number = harder).
- **GAME MODE** → keep `GRAND PRIX / NORMAL`; avoid `ENDURANCE` (40–80 laps).
- In-game: BEGINNER course + AT transmission.
- **FREE PLAY** → ON. No lives — EASY widens checkpoint margins.

### Ski Champ
- **DIFFICULTY / RANK** → `EASY` / lowest.
- In-game: beginner/easy course.
- **FREE PLAY** → ON. Self-test: Blue, Green, Blue, Green, Service, Service. Verify labels.

### Spikeout + Spikeout Final Edition
- **DIFFICULTY** → `EASIEST`.
- **LIFE / PLAYER STOCK** → MAX; **ENERGY / VITALITY** → MAX if separate; **TIME** → LONGEST.
- **FREE PLAY** → ON (continue-heavy beat-'em-up).

### Sega Rally 2
- **DIFFICULTY** → lowest number ("greater number = higher difficulty").
- **GAME MODE** → keep `NORMAL`.
- In-game: AT transmission.
- **FREE PLAY** → COIN ASSIGNMENTS → coin setting #27 (FREE PLAY). Checkpoint racer, no lives.

### Star Wars Trilogy Arcade
- **GAME DIFFICULTY** → EASIEST (lower difficulty also gives more initial time).
- **FREE PLAY** → ON → makes the CONTINUE prompt free/unlimited (the practical "more lives").
- Life-gauge rail shooter; no separate lives/shields.

### Virtua Fighter 3tb
- **DIFFICULTY** → `EASY` (default NORMAL); raises energy-gauge favorability.
- **MATCH COUNT (1P)** → `1` (range 1–5, default 2); **MATCH COUNT (VS)** → `1`.
- **FREE PLAY** → ON. TIME LIMIT / RING OUT not exposed in VF3 — verify on 3tb.

### Virtual On: Oratorio Tangram
- **DIFFICULTY** → `EASIEST` (verify label).
- **TIME LIMIT** → LONGEST.
- **FREE PLAY** → ON (post-KO CONTINUE effectively unlimited). Energy/damage: verify.

### Virtua Striker 2 (VS2 / '98 / '99 / Ver.2000)
- **DIFFICULTY** → `EASY` (default NORMAL).
- **TIME SET** → `3'00"` (max; default 2'00").
- **V GOAL / G GOAL SYSTEM** → ON (extended/golden-goal instead of instant loss).
- **FREE PLAY** → ON. No lives; EASY + 3'00" is the easy setup.

---

# Model 2 (ElSemi Model 2 Emulator)

### Daytona USA
- **DIFFICULTY** → `EASY` (also governs checkpoint/time allowance).
- **GAME MODE (laps)** → `NORMAL (SPRINT)`. LINK = `SINGLE`.
- **FREE PLAY** → ON. No lives/continues.

### Desert Tank (Desert War)
- **DIFFICULTY** → `EASY` / `EASIEST` (verify).
- **Energy / damage / time** → most forgiving (labels verify in-menu).
- **FREE PLAY** → ON.

### Dead or Alive
- **DIFFICULTY** → `EASIEST` / `VERY EASY`.
- **ROUNDS TO WIN** → `1`; **TIME LIMIT** → longest / `NO LIMIT`; **DAMAGE LEVEL** → lowest if present.
- **FREE PLAY** → ON. Numbers verify-in-menu.

### Dynamite Baseball '97
- **COM / DIFFICULTY** → easiest; **INNINGS** → fewest; **TIME/COUNT** → generous.
- **FREE PLAY** → ON. Labels undocumented — verify.

### Dynamite Cop (Dynamite Deka 2)
- **GAME DIFFICULTY** → `LEVEL 1` (scale 1–8).
- **INITIAL VITALITY** → MAX; **INITIAL PLAYERS** → MAX.
- **FREE PLAY** → ON. *Confirmed from the leftover arcade test menu.*

### Fighting Vipers
- **DIFFICULTY** → `VERY EASY`; **ROUNDS TO WIN** → `1`; **TIME LIMIT** → `NO LIMIT` (10/20/30/60/NO LIMIT).
- **DAMAGE LEVEL** → lowest if exposed. **FREE PLAY** → ON. *Confirmed.*

### Gunblade NY
- **DIFFICULTY** → `EASIEST`; **LIFE** → MAX, damage lowest; **CONTINUE** → unlimited if toggle exists.
- In-game: `EASY` scenario. **FREE PLAY** → ON. *Persistence caveat — re-verify.*

### The House of the Dead
- **GAME DIFFICULTY** → `VERY EASY`.
- **LIFE SETTING** → INITIAL LIFE 4 / MAX LIFE 5 (interlocked).
- **FREE PLAY** → ON (continues effectively unlimited).

### Indy 500 (Sega)
- **DIFFICULTY** → `1 (EASIEST)`; **TIME** → LONGEST if listed.
- In-game: **AT**. **FREE PLAY** → ON.

### Last Bronx
- **DIFFICULTY** → `EASIEST (1)` of 1–4; **TIME LIMIT** → LONGEST/INFINITY.
- **NUMBER OF ROUNDS** → verify it's one-sided before lowering. **FREE PLAY** → ON.

### Manx TT Superbike
- **DIFFICULTY** → `EASY`; **TIME/EXTEND** → LONGEST if present.
- In-game: Laxey Coast (Novice) + AT. **FREE PLAY** → ON.

### Motor Raid
- **DIFFICULTY** → `EASY`; **LAPS** → fewest; **LIFE/DAMAGE** → life MAX / damage low if listed.
- **FREE PLAY** → ON.

### Over Rev
- **DIFFICULTY** → `EASY`; **TIME LIMIT** → LONGEST if present.
- In-game: **AT**. **FREE PLAY** → ON.

### Pilot Kids
- **DIFFICULTY** → `EASY / EASIEST`; **LIVES (plane stock)** → MAX; **EXTEND** → lowest threshold / `EVERY`.
- **CONTINUE** → unlimited via Free Play. **FREE PLAY** → ON.

### Rail Chase 2
- **DIFFICULTY** → `EASY`; **LIVES** → MAX; **LIFE DECREASE (1P & 2P)** → `SLOW/MINIMUM`; **TIMER / TIMER INCREMENT** → LONGEST.
- **FREE PLAY** → ON.

### Sonic Championship (Sonic the Fighters)
- **DIFFICULTY** → `EASIEST (1)`; **TIME LIMIT** → LONGEST/INFINITE.
- **NUMBER OF ROUNDS** → verify one-sided before changing. **FREE PLAY** → ON.

### Sega Water Ski (Waverunner GP)
- **GAME DIFFICULTY** → `EASY` (default NORMAL; adds start time + checkpoint bonus).
- In-game: NOVICE course. **FREE PLAY** → ON. Leave HANDICAP ON (linked play only).

### Sega Touring Car Championship
- **DIFFICULTY** → `EASY` (varies start time + checkpoint bonus).
- **GAME MODE (laps)** → `SHORT` (=1 lap; avoid GRAND PRIX=20).
- In-game: **AT**. **FREE PLAY** → ON.

### Ski Super G
- **INITIAL TIME** → max; **STAGE TIME** → max ("longer time = lower difficulty").
- **FREE PLAY** → ON (#27). No numeric DIFFICULTY — time is the difficulty.

### Sky Target
- **DIFFICULTY** → `EASIEST`; **DAMAGE / SHIELD** → most forgiving/max.
- **FREE PLAY** → ON. Country = USA for English. Verify labels.

### Sega Rally Championship
- **GAME DIFFICULTY** → `EASY` (more start time + more at each checkpoint).
- **GAME MODE (laps)** → `SHORT`.
- In-game: **AT**. **FREE PLAY** → ON. *Persistence caveat — re-verify.*

### Top Skater
- **GAME DIFFICULTY** → `1` (range 1–8, default 4).
- **FREE PLAY** → ON (#27). Time extended in-game via checkpoints/Time Bonus rings.

### Virtua Cop
- **DIFFICULTY** → EASIEST; **LIFE** → maximum (verify range).
- **FREE PLAY** → ON. Reload by shooting off-screen (no auto-reload in VC1 — verify).

### Virtua Cop 2
- **DIFFICULTY** → `EASY` (GAME SYSTEM); **LIFE** → `9` (max, 1–9); **RELOAD TYPE** → `AUTOMATIC`.
- **FREE PLAY** → ON; CREDIT TO START/CONTINUE = 1.

### Virtua Fighter 2
- **DIFFICULTY** → `EASY` (default NORMAL).
- **MATCH COUNT (1P)** → keep `2` (fewest; do not raise); **ENERGY MAX (1P)** → optionally raise above 160.
- **CONTINUE** → ON. **FREE PLAY** → ON. *Verified against the service manual.*

### Virtual On: Cyber Troopers
- **DIFFICULTY** → `EASY` (default NORMAL).
- **ROUND TIME LIMIT** → LONGEST if present; **ROUND COUNT** → don't raise; **ENERGY/HANDICAP** → bias to player if present.
- **CONTINUE** → ON. **FREE PLAY** → ON.

### Virtua Striker
- **DIFFICULTY / LEVEL** → `EASY`; **GAME TIME** → LONGEST.
- **CONTINUE** → ON. **FREE PLAY** → ON. Knockout tournament — no auto-advance on loss.
