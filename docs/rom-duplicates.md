# Cross-platform ROM duplicates — cleanup list

Inventory of games present on **more than one system** across
`EmuDeck/{roms_heavy,roms_mid,roms_rare}` (68 titles), with a recommended
**keep** per title and the copies to **move to `ROMS_FINAL/<system>/`** (archive,
not delete). Goal: slim the active EmuDeck sets so ES-DE shows one good copy per
game. Everything lives on the same NAS (`/mnt/terachad/Emulators/`), so a move
is instant and reclaims no disk — it declutters the *active* library.

> **Nothing here has been moved.** This is a proposal for you to review/override.
> On your OK I'll generate a verified move script (reading exact filenames) — I
> won't run raw `mv`s off possibly-truncated paths.

## How the "keep" was chosen (override freely)

1. **HD remaster / remake / definitive / collection beats the original** (your
   preference).
2. **Superior + reliably-emulated platform.** Native fidelity roughly
   Xbox ≥ GameCube ≥ PS2 for 6th-gen multiplat — **but** original-Xbox
   emulation (**xemu**) is still immature, while Dolphin (GC/Wii), PCSX2 (PS2),
   RPCS3 (PS3) and Xenia (360) are mature. So where I recommend an Xbox copy I
   flag the GC/PS2 fallback in case it doesn't boot in xemu. ⚠ = judgement call.
3. **Console beats handheld** for the same game (keep console, move NDS/PSP).
4. **Arcade originals** (model2/naomi, ~10–30 MB) are tiny and accurate — keep
   alongside one console copy rather than moving.
5. **7th gen (PS3 ⇄ 360):** default to the copy that's the more complete edition;
   otherwise 360 (Xenia is the actively-used path here).

Legend: **KEEP** = stays in EmuDeck · **→ FINAL** = move to `ROMS_FINAL/<sys>/`.

## A. Remaster / remake / collection wins

| Title | KEEP | → FINAL | Note |
|---|---|---|---|
| Metroid Prime | switch *Remastered* | gc | keep **wii Trilogy** too — it's the only Prime 2 & 3 |
| Mario Kart 8 | switch *Deluxe* | wiiu | Deluxe = all DLC + more |
| New Super Mario Bros. U | switch *Deluxe* | wiiu | |
| Ocarina of Time | n3ds *OoT 3D* | — | n64 copy is the *Redux romhack* → **keep** (different thing) |
| Star Fox 64 | n3ds *64 3D* | n64 | ⚠ n64 original is 12 MB; keep it if you like the classic |
| Rayman Legends | switch *Definitive* | ps3, xbox360 | Definitive adds levels |
| Dead or Alive 2 | xbox *Ultimate* | dreamcast | Ultimate is the enhanced remake |
| Devil May Cry HD Collection | xbox360 | ps3 | both HD; 360 copy is smaller |
| GoldenEye 007 (2010) | xbox360 *Reloaded* | nds | n64 1997 = **different game**, keep |
| God of War Collection | ps3 | psvita | ⚠ Vita saves 16 GB if you want portable |
| Soul Calibur (1) | ps3 *2012 HD* | dreamcast | ⚠ DC original is arcade-perfect via Flycast — keep DC instead if you're a purist |
| Luigi's Mansion | ⚠ gc | n3ds | GC via Dolphin looks best; 3DS remake adds co-op/extra mansion — your call |
| Pikmin | gc | wiiu | GC/Dolphin highest-res; Wii U = *New Play Control* motion |
| Super Mario Galaxy 2 | wii | switch | Wii/Dolphin is the gold standard; the Switch rip emulates worse |
| Crazy Taxi | dreamcast | — | ⚠ keep psp *Fare Wars* too — it's CT1 **+** CT2 |

## B. 6th-gen multiplatform originals (Xbox / GC / PS2 / DC)

⚠ Xbox picks assume xemu runs them — if not, keep the GC/PS2 copy noted.

| Title | KEEP | → FINAL | Note |
|---|---|---|---|
| Splinter Cell (1) | xbox | gc | Xbox is the definitive version; ps3 Trilogy HD also has it |
| SC: Pandora Tomorrow | xbox | gc, ps3 | ps3 also in Trilogy HD |
| SC: Chaos Theory | xbox | gc | best-looking on Xbox; also in ps3 Trilogy HD |
| SC: Double Agent | xbox360 | gc, xbox, ps3 | 360 is the "version 1" definitive; GC/Xbox are the cut-down "v2" |
| Bloody Roar Extreme | xbox | gc | Xbox version runs higher-res |
| Burnout (1) | ⚠ gc | xbox | tiny GC via Dolphin; Xbox if xemu runs it |
| Burnout 3 Takedown | xbox | ps2 | Xbox = 720p-capable, best version |
| Burnout Revenge | xbox360 | ps2, xbox | 360 is the enhanced/last-gen-plus version |
| Colin McRae Rally 04 | xbox | ps2 | |
| Colin McRae Rally 2005 | xbox | ps2 | psp "2005 Plus" is a distinct edition — keep if wanted |
| Hitman: Blood Money | xbox360 | xbox | 360 is the superior release |
| Midnight Club 3 DUB Remix | ⚠ ps2 | xbox | both are "Remix"; PS2/PCSX2 more reliable than xemu |
| Psychonauts | xbox360 | xbox | 360 (BC) runs great in Xenia |
| Soulcalibur II | gc | ps2, xbox | ⚠ each has an exclusive guest (GC=Link, Xbox=Spawn, PS2=Heihachi) — keep your favourite |
| SSX Tricky | ⚠ xbox | ps2 | Xbox sharper; PS2/PCSX2 safer |
| 18 Wheeler | gc | ps2, dreamcast | GC smallest + Dolphin upscales |

## C. 7th-gen multiplatform (PS3 ⇄ 360, ± Wii U / Vita)

| Title | KEEP | → FINAL | Note |
|---|---|---|---|
| Devil May Cry 4 | xbox360 | ps3 | parity; 360 smaller |
| Race Driver: GRID | xbox360 | ps3 | ps3 copy is a huge 16 GB |
| GRID 2 | xbox360 | ps3 | |
| Injustice: Gods Among Us | ps3 | wiiu | ⚠ neither is the "Ultimate Ed."; pick platform you emulate best |
| Psychonauts | (see B) | | |
| Rayman Legends | (see A) | | |
| Soulcalibur IV | xbox360 | ps3 | Xbox-exclusive Yoda vs PS3 Vader — ⚠ pick your Star Wars guest |
| Soulcalibur V | xbox360 | ps3 | |
| Ultra Street Fighter IV | xbox360 | ps3 | ps3 copy is 19 GB |
| Ultimate MvC3 | ps3 | psvita | keep console; Vita portable only |
| Street Fighter X Tekken | ps3 | psvita | |
| Dead or Alive 5 | ps3 *Ultimate* | psvita *Plus* | ⚠ different editions of DOA5 — Ultimate is the fuller one |
| Virtua Fighter 5 | xbox360 | ps3 | ⚠ 360=*Online*, ps3=vanilla; Online is the better version → keep 360 |
| Virtua Tennis 4 | ps3 | psvita | |
| Tekken Tag Tournament 2 | xbox360 | wiiu | Wii U = "Wii U Edition" gimmicks; 360 cleaner |
| Child of Light | wiiu | psvita | ⚠ both fine; keep platform you prefer |
| Star Wars Episode I Racer | switch | dreamcast | modern re-release vs DC port |
| Splinter Cell Blacklist | xbox360 | ps3, wiiu | 360 2-disc = full; keep one |
| WRC 3 | ps3 | psvita | |
| WRC 4 | xbox360 | ps3 | |
| WRC 5 | xbox360 | ps3, psvita | |
| WRC 1 | xbox360 | psp | |
| Sega Rally Revo | xbox360 | ps3 (×2 dumps), psp | ⚠ two ps3 dumps present — drop both |
| Hitman: Blood Money | (see B) | | |

## D. Console vs handheld / low-value dups (keep console, move the small one)

| Title | KEEP | → FINAL |
|---|---|---|
| Astro Boy: The Video Game | psp | nds |
| Burnout Legends | psp | nds *(or drop both — it's a handheld-only spin-off)* |
| Colin McRae DiRT 2 | *(handheld-only pair)* | ⚠ keep whichever; the real DiRT 2 is the PC/console game |
| Need for Speed: Most Wanted (2005) | gc *(or ps3)* | nds | ⚠ wiiu "Most Wanted U" & psp "5-1-0" are **different games** — keep |
| OutRun 2006 C2C | xbox | ps2, psp | Xbox is the best C2C version |

## E. Multi-gen ports of retro games (keep the best-emulated original)

| Title | KEEP | → FINAL | Note |
|---|---|---|---|
| Super Mario 64 | n64 | dreamcast | DC ".cdi" is a bootleg port |
| Mario Kart 64 | n64 | dreamcast | DC is a bootleg port |
| Hydro Thunder | dreamcast | n64 | DC is the superior arcade port |
| Rayman 2 | dreamcast | n64 | DC version is the definitive one |
| Daytona USA | model2 *(arcade)* | dreamcast | ⚠ keep DC too — it's *Championship Circuit Edition* (extra tracks) |
| Ikaruga | naomi *(arcade)* | gc, dreamcast | gc has extra modes — ⚠ keep gc if you want them |
| Road Rash | 3do | megacd | 3DO is the better CD version |
| Star Wars Rebel Assault | 3do | megacd | 3DO superior |

## F. Verify first — likely NOT the same game

| "Title" | Copies | Action |
|---|---|---|
| Shinobi | ps2 (2002) vs n3ds (2011) | **different games** — keep both |
| GoldenEye 007 | n64 (1997) vs 2010 remake line | different — handled in A |
| Need for Speed Most Wanted | 2005 vs "U" (2012) vs "5-1-0" (psp) | different — handled in D |

## Rough tally

If you accept the recommendations, **~55 copies** move to `ROMS_FINAL`
(mostly the redundant PS3/PS2/handheld/second-disc dumps), leaving one curated
copy per title in EmuDeck. The bulk of the decluttering is on the big 7th-gen
`roms_heavy/{ps3,xbox360}` sets.

## Next step

Tell me which recommendations to accept (or "all, with the ⚠ ones left as-is",
etc.) and I'll generate a reviewed `mv` script that:
- creates `ROMS_FINAL/<system>/` targets,
- moves each agreed copy (exact filenames, quoted),
- and leaves the kept copy untouched.
Then you run it (or I do, with confirmation).
