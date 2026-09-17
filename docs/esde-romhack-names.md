# De-colliding ROM-hack names in ES-DE

When ES-DE's scraper can't identify a ROM hack it drops the file in a
`no_match/` subfolder of that system's ROM dir. If you then match it by hand (or
let auto-match guess), ES-DE stamps the entry with the **base game's** name — so
several different hacks all show up as, e.g., `Super Mario World`, with no way to
tell them apart in the UI. The hack's real identity survives only in its
**filename**, which carries a marker like `(DINOSAUR LAND ROM HACK)` or a credit
like `[FastROM hack by Vitor Vilela v1.0]`.

The helper **`bin/esde-name-romhacks`** (deployed by `scripts_in_box`) sweeps
every `ES-DE/gamelists/*/gamelist.xml`, and for each game whose `<path>` is under
a `no_match/` dir with such a marker, **appends the marker to its `<name>`**:

| Filename | `<name>` before | `<name>` after |
|---|---|---|
| `Super Mario World (DINOSAUR LAND ROM HACK).sfc` | Super Mario World | Super Mario World (Dinosaur Land) |
| `Super Mario World (REMASTERED ROM HACK).sfc` | Super Mario World | Super Mario World (Remastered) |
| `...A Link to the Past (REDUX ROM HACK).sfc` | The Legend of Zelda : A Link to the Past | … (Redux) |
| `F-Zero (USA) [FastROM hack by Vitor Vilela v1.0].sfc` | F-Zero | F-Zero (FastROM Hack) |

Run it with **ES-DE closed** (ES-DE rewrites its gamelists on exit and would
clobber the edit), then reopen ES-DE:

```sh
distrobox enter gaming -- esde-name-romhacks
```

It is idempotent — a descriptor already present in the name is left alone — so
it is safe to re-run after each new scrape. Each changed gamelist is backed up
alongside as `gamelist.xml.bak`. Acronyms like `DX`/`NES` are preserved in case;
other words are title-cased.

## What it does *not* touch

- **Real duplicate ROMs / regional variants** (not hacks): e.g. the same game in
  the system root *and* under `no_match/`, or `Parodius (Europe).sfc` +
  `Parodius (Europe)_dup1.sfc`, or `Gradius Advance` / `Gradius Galaxies` /
  `Gradius Generation` (three regions, one scraped name). These show as duplicate
  names too, but the fix is to delete the redundant dump — a library cleanup, not
  a rename — so the helper leaves them alone.
- **Arcade clones** (Model 2/3 sets with sibling regions/revisions). Those are
  hidden via `configure_esde`'s arcade-gamelist clone-hiding, not renamed.

The gamelists themselves are scraper-generated state and are **not** tracked in
this repo; only the helper is. Re-run it whenever a re-scrape reintroduces the
collisions.
