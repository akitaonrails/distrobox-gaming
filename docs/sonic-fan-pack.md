# Sonic fan games: S3AIR, SMS Remake (Banjo-Kazooie moved to lighthouse.md)

Three installs from the 2026-09-04 batch (`docs/dkc-recomp.md` came the same
week — it's fan-port season).

## Sonic 3 A.I.R. (`install_sonic3air`)

[Eukaryot/sonic3air](https://github.com/Eukaryot/sonic3air) — "Angel Island
Revisited", the definitive Sonic 3 & Knuckles remaster on the Oxygen engine.
**Official native Linux build** (`sonic3air_game.tar.gz` from the stable GitHub
release, sha256-pinned, NAS-staged under `ROMS_FINAL/PC/sonic remake/`; the
`sonic3air_game.zip` downloaded from sonic3air.org is the *Windows* package).
**Requires the original Sonic 3 & Knuckles combined ROM** — the role stages the
box's standard 4 MiB dump (`Sonic and Knuckles & Sonic 3 (JUE) [!].bin`, sha1
`cfbf98c3…`) as `Sonic_Knuckles_wSonic3.bin` beside the binary; the game
verifies it and adopts it into `~/.local/share/Sonic3AIR/`. Verified: fullscreen
DP-1 on the RTX, log shows `Controller #1: "8BitDo Ultimate 2 Wireless
Controller"` (native). Launcher `bin/sonic3air`, Walker "Sonic 3 A.I.R.".
Mods go in `~/.local/share/Sonic3AIR/mods/`.

## Sonic SMS Remake (`install_sonic_sms_remake`)

[The Creative Araya's remake](https://sonic-sms-remake.blogspot.com/) of the
Master System Sonic 1 — 5 playable characters, no original data needed.
**GameMaker Windows exe, no Linux build exists** → wine-11.8 with the standard
recipe (UseEGL=N GLX pin, WineBus SDL for the 8BitDo), running inside a **4K
Wine virtual desktop**: its exclusive fullscreen otherwise renders in the
bottom-left corner of the panel (the Sega Rally Revo lesson; observed here
too). Source = the user's NAS zip (`v1-9-rev4_Sonic_SMS_Remake.zip`, single
exe inside). Launcher `bin/sonic-sms-remake`, Walker "Sonic SMS Remake".
Sonic 2 SMS and Sonic 3 SMS remakes exist on the same site — drop their zips
next to this one and clone the role data if wanted.

## Banjo-Kazooie

Moved to its own page — Banjo-Kazooie now runs on **Lighthouse**, HarbourMasters'
libultraship PC port (the old BanjoRecomp recompilation was replaced). See
[docs/lighthouse.md](lighthouse.md).
