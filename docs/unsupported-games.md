# Unsupported / parked games

Games and game-mods we could **not** get working in this setup. The full trail
for each — environment, everything tried, the exact failure, and any untried
lever — lives in a **GitHub issue** (the issues are the primary record; these
rows are just the index). Contributions welcome if you crack one.

| Game / mod | Why it's unsupported | Issue |
|---|---|---|
| Sega Rally 2 (25th-Anniversary repack) | Wine dead-end — the game's own MGameD3D renderer null-derefs; D3D resources come back null and it walks a hollow table | [#3](https://github.com/akitaonrails/distrobox-gaming/issues/3) |
| Colin McRae Rally 2005 (PC/GOG) | Wine dead-end (page fault `0041DA27`); use the PS2/PCSX2 version | [#4](https://github.com/akitaonrails/distrobox-gaming/issues/4) |
| DiRT 3 Complete Edition | No working controller path under Wine (green-light HID fault); Proton crashes earlier | [#5](https://github.com/akitaonrails/distrobox-gaming/issues/5) |
| DiRT Rally | Native Feral Linux build segfaults; Windows RELOADED crack fights Proton `lsteamclient` | [#6](https://github.com/akitaonrails/distrobox-gaming/issues/6) |
| TeknoParrot (arcade) | Parked — Windows-loaders-under-Wine works but is an endless per-game tuning treadmill | [#7](https://github.com/akitaonrails/distrobox-gaming/issues/7) |
| Doom 64 RT (path-traced) | RTGL1 ray-tracing won't init under distrobox Wine; needs real Proton (RT/Vulkan plumbing) | [#8](https://github.com/akitaonrails/distrobox-gaming/issues/8) |
| Castlevania: SotN (SymphonyRecomp) | Crashes ~2s after you start the game; graphics data never loads (`packs=0`, `read outside data track`) | [#9](https://github.com/akitaonrails/distrobox-gaming/issues/9) |
| Spyro the Dragon (OpenPete) | Blocked on a disc-image hash mismatch — needs Redump #576 (`1e08ae8…`); the common dump doesn't match | [#10](https://github.com/akitaonrails/distrobox-gaming/issues/10) |
| Spider-Man Remastered / Miles Morales (mods) | Nexus mods need the Overstrike GUI (no loose-file loading) — no headless install | [#11](https://github.com/akitaonrails/distrobox-gaming/issues/11) |
| MGSV: The Phantom Pain (mods) | Nexus mods are `.mgsv` SnakeBite packages — GUI-only, no headless CLI | [#12](https://github.com/akitaonrails/distrobox-gaming/issues/12) |
| Batman: Arkham Asylum/City/Knight (mods) | Nexus mods use the TFC Installer / Advanced Launcher GUI — not headless-automatable | [#13](https://github.com/akitaonrails/distrobox-gaming/issues/13) |
| Sonic Mania — Megamix Mania (mod) | DLL character-mods don't run under Steam+Proton (SteamStub `verchk` hook never fires); data mods do | [#14](https://github.com/akitaonrails/distrobox-gaming/issues/14) |

Notes:
- These are **not** bugs in this repo's Ansible code — they're games the
  Wine/distrobox (or Steam+Proton) stack can't run, or mods that need an
  interactive Windows GUI installer.
- Several have **working alternatives** already in the repo (e.g. Sega Rally
  Revo / Sega Rally Championship HD for Sega Rally 2; PCSX2 for Colin McRae
  Rally 2005). See the linked issue.
