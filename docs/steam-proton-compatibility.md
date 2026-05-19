# Steam Proton Compatibility Database

`data/steam-proton-compat.json` is the local compatibility database for the
Steam games installed in this distrobox setup. It is generated from Steam
`appmanifest_*.acf` files and enriched with ProtonDB summaries, Valve Steam Deck
compatibility data, and small curated overrides.

## Refreshing The Database

Run from the repo root and pass every Steam `steamapps` directory you want to
audit:

```sh
DG_STEAM_LIBRARY_ROOTS="$HOME/.local/share/Steam/steamapps:/path/to/external/steamapps" \
  scripts/build-steam-proton-db.py
```

The script writes `data/steam-proton-compat.json`. It does not change Steam
settings, launch options, compatdata, or installed games.

## How To Read Entries

`protondb` records the current ProtonDB summary tier and confidence. Treat it as
a compatibility signal, not as a launch recipe.

`steam_deck` records Valve's Deck and SteamOS categories from Steam's public
compatibility endpoint. This is useful when ProtonDB is sparse or old.

`compat_policy` is our repo policy for the next action:

```text
prefer_native_linux              Use the native Linux build first.
steam_default_proton             Try Steam's default/current Proton first.
steam_default_proton_low_confidence Likely compatible, but source confidence is sparse.
check_sources_before_testing    Read known_issues/source_notes first.
research_before_testing          Do not guess; find a source or test cleanly.
local_fix_recorded               A tested local fix is documented in overrides.
runtime_component                Steam runtime/Proton dependency, not a game.
```

To list games that need research before changing Steam launch options:

```sh
python - <<'PY'
import json
db = json.load(open("data/steam-proton-compat.json"))
for app in db["apps"]:
    if app["type"] == "game" and app["compat_policy"] != "steam_default_proton":
        print(app["app_id"], app["compat_policy"], app["name"])
PY
```

## Curated Overrides

Put human decisions in `data/steam-proton-overrides.json`, not in the generated
database. Only add launch options or Proton version pins when they have a source
or a successful local test. Include the source URL and explain whether it is a
current recommendation or only historical context.

Do not hardcode maintainer-specific mount paths in this database or its scripts.
Use `DG_STEAM_LIBRARY_ROOTS` for local library discovery.
