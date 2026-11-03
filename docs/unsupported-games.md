# Unsupported / parked games

Games and game-mods we could **not** get working in this setup. The full trail
for each — environment, everything tried, the exact failure, and any untried
lever — lives in a **GitHub issue** (the issues are the primary record; these
rows are just the index). Contributions welcome if you crack one.

| Game / mod | Why it's unsupported | Issue |
|---|---|---|
| ~~Sega Rally 2~~ (25th-Anniversary repack) | ✅ RESOLVED 2026-10-30 with the original European PC release and [sr2-patcher](https://github.com/pairomaniac/sr2-patcher); the opt-in role installs and launches it on the RTX 5090. The Anniversary repack's modified executable remains incompatible. See [setup](sega-rally-2.md). | [#3](https://github.com/akitaonrails/distrobox-gaming/issues/3) |
| ~~Colin McRae Rally 2005 (PC/GOG)~~ | ✅ RESOLVED 2026-11-02 — the dead-end crash at `0041DA27` was the game loading its fonts through registry values its installer never got to write; the [REA launcher](rea-colin-mcrae-2005.md) writes them on every start and unpacks the GOG installer with innoextract. Runs natively at 4K via `install_rea_colin_mcrae_2005`. | [#4](https://github.com/akitaonrails/distrobox-gaming/issues/4) |
| DiRT 3 Complete Edition | Fix exists but needs the legit Steam copy (disable Steam Input + in-game V-Sync) — not owned, delisted/unpurchasable; repack's GFWL crash unfixable. ⛔ final 2026-10-03: stays parked | [#5](https://github.com/akitaonrails/distrobox-gaming/issues/5) |
| ~~DiRT Rally~~ | ✅ RESOLVED 2026-11-02 — the Windows-under-Proton path needed a legit Steam copy, but Feral's **native Linux port** sidesteps that; the [REA launcher](rea-dirt-rally.md) bundles the old scout libraries + the Ryzen-5000 crash shim and runs it at 4K via `install_rea_dirt_rally`. (Full in-box stage not yet re-driven here; upstream played it end to end on this config.) | [#6](https://github.com/akitaonrails/distrobox-gaming/issues/6) |
| TeknoParrot (arcade) | Parked — Windows-loaders-under-Wine works but is an endless per-game tuning treadmill. 🔴 re-checked 2026-10-03: no structural change | [#7](https://github.com/akitaonrails/distrobox-gaming/issues/7) |
| ~~Doom 64 RT (path-traced)~~ | ✅ RESOLVED 2026-10-17 — Retribution v1.5 and OGG music archives installed; native AppImage `check` confirms the game data is complete. Interactive play has not yet been verified; see [setup notes](doom64-rt.md). | [#8](https://github.com/akitaonrails/distrobox-gaming/issues/8) |
| ~~Castlevania: SotN (SymphonyRecomp)~~ | ✅ RESOLVED 2026-10-03 — our disc staging was malformed (missing `"(USA)"` in bin names per the 2026-09-27 README spec); fixed by symlinking the EmuDeck rip verbatim; boot-verified past the crash | [#9](https://github.com/akitaonrails/distrobox-gaming/issues/9) |
| Spyro the Dragon (OpenPete) | Blocked on a disc-image hash mismatch — needs Redump #576 (`1e08ae8…`); the common dump doesn't match. 🔴 re-checked 2026-10-03: unchanged (native Linux AppImage now exists for when the disc appears) | [#10](https://github.com/akitaonrails/distrobox-gaming/issues/10) |
| ~~Spider-Man Remastered / Miles Morales (mods)~~ | ✅ RESOLVED 2026-10-03 — park diagnosis was wrong: Overstrike has a headless CLI since v1.7.2 (2025-04); automated via `install_spiderman_mods` | [#11](https://github.com/akitaonrails/distrobox-gaming/issues/11) |
| ~~MGSV: The Phantom Pain (mods)~~ | ✅ RESOLVED 2026-10-03 — mgsv-mod-installer (headless SnakeBite) installed 4/5 mods via `install_mgsvtpp_mods`; 316 archive missing | [#12](https://github.com/akitaonrails/distrobox-gaming/issues/12) |
| Batman: Arkham Asylum/City/Knight (mods) | Nexus mods use the TFC Installer / Advanced Launcher GUI — not headless-automatable. 🔴 re-checked 2026-10-03: still GUI-only, but the manual GUI pass under Proton is now well-confirmed | [#13](https://github.com/akitaonrails/distrobox-gaming/issues/13) |
| Sonic Mania — Megamix Mania (mod) | DLL character-mods don't run under Steam+Proton (SteamStub `verchk` hook never fires); data mods do. 🔴 re-checked 2026-10-03 with v1.1.1: still the same Steam DLL mod; user decision: stays parked | [#14](https://github.com/akitaonrails/distrobox-gaming/issues/14) |
| Marvel Tōkon: Fighting Souls | EAC Linux/Proton module not enabled by the devs — "No anti-cheat module found for this platform"; dev-side toggle, no local workaround. 🔴 re-checked 2026-10-03: still blocked | [#15](https://github.com/akitaonrails/distrobox-gaming/issues/15) |

Notes:
- These are **not** bugs in this repo's Ansible code — they're games the
  Wine/distrobox (or Steam+Proton) stack can't run, or mods that need an
  interactive Windows GUI installer.
- Several have **working alternatives** already in the repo (e.g. Sega Rally
  Revo / Sega Rally Championship HD for Sega Rally 2). See the linked issue.
