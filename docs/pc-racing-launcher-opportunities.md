# PC racing launcher opportunities

Research snapshot: 2026-11-01. This is a shortlist for future launcher work,
not a replacement for the installed-game instructions in [PC Racing Games](pc-racing.md).
The search covered GitHub projects, Lutris installer scripts, and game-specific
patch pages. “No launcher found” means none surfaced in that search; it does not
prove that none exists.

Update, 2026-11-05: this table is historical. REA launchers now cover CMR04,
Sega Rally Revo, DiRT 2007, CMR3, and OutRun 2006. Their current installation
notes and release inventory are in [external installers](external-installers.md).

| Priority | Game | Existing tool and its scope | Remaining setup problem |
| --- | --- | --- | --- |
| 1 | Colin McRae Rally 04 | [CMR04 Widescreen Fix](https://community.pcgamingwiki.com/files/file/2536-colin-mcrae-rally-04-widescreen-fix/) patches the aspect ratio. No modern setup launcher surfaced. | A reliable setup must coordinate the executable patch, 4K registry resolution, dgVoodoo, and controller mapping. The in-game graphics menu can overwrite the working resolution; see [our install notes](pc-racing.md#colin-mcrae-rally-04). |
| 2 | Sega Rally Revo | A [Lutris installer](https://lutris.net/games/install/37264/view) extracts one full-rip edition, sets language/registry values and a 60 FPS DXVK limit, then invokes the original settings launcher. Separate [frame pacing](https://github.com/Martijnsx/Sega-Rally-Revo-Frame-Pacing-Fix) and [stutter](https://github.com/stuken/SegaRallyRevoStutterFix) patches target specific executable builds. | The original settings launcher is troublesome under Wine. A new launcher could validate the game edition, manage graphics/input settings, and integrate compatible fixes with our Wine setup. Do not apply either binary patch without checking its supported executable hash and testing it. |
| 3 | Colin McRae: DiRT (2007) | [CMCR-DiRT-MTFix](https://github.com/xatornet/CMCR-DiRT-MTFix) addresses the modern CPU race-load crash. No installer covering the complete game/patch sequence surfaced. | Our installation needs an interactive base installer followed by four ordered patches, then the CPU fix, which resets graphics settings. See [our install notes](pc-racing.md#colin-mcrae-dirt-2007). |
| Lower | Colin McRae Rally 3 | [SilentPatch](https://github.com/CookiePLMonster/SilentPatchCMR3) adds widescreen, a 4K UI, and settings/input improvements. A [Lutris script](https://lutris.net/games/install/38283/view) installs the retail discs, update, executable patch, and SilentPatch. | Our Wine-specific Xidi and display setup remains useful, but the general installation problem is substantially covered. |
| Lower | OutRun 2006 | An [NSIS patch installer](https://github.com/stpettersens/or2006_c2c_patch) includes [OutRun2006Tweaks](https://github.com/emoose/OutRun2006Tweaks). | Its v0.6.1 release downloads the older tagged Tweaks build. Our role uses a newer CI build and manages Wine, DXVK, controller, and 4K settings. Extending the existing installer may be more useful than creating another one. |
| Lower | Colin McRae Rally 2.0 | [OpenCMR2](https://github.com/pablocpas/OpenCMR2) provides a native option. A [Lutris script](https://lutris.net/games/install/38236/view) installs the original PC game and SilentPatch. | Our original PC install still has Wine display and controller quirks, but a new launcher is less urgent while the native port is available. |

The strongest original-launcher candidate is **CMR04**. **Sega Rally Revo**
and **DiRT 2007** follow. Recheck upstream projects before starting work: the
available patches and their supported game builds can change.
