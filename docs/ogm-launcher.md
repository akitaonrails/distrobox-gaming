# ogm (omarchy-games-menu) integration

ogm (omarchy-games-menu) is a host-side game launcher (Rust CLI, expected on
`PATH`, typically `~/.local/bin/ogm`). It builds its game collection from the
desktop entries this repo exports to `~/.local/share/applications`
(`scripts/install-host-launchers.sh` installs exactly what ogm reads).

## Discovery: the `X-OGM-*` desktop keys (primary)

The rendered `.desktop` files carry their own ogm metadata as freedesktop
`X-*` extension keys in the `[Desktop Entry]` group. This is the primary
discovery mechanism — ogm lists an entry **only** when `X-OGM-Managed=true` is
present (a legacy filename glob — `gaming-*`, `pc-*`, `screamer*`,
`ridge-racer`, … — remains as a migration fallback). An entry that must never
appear in the menu sets `X-OGM-Managed=false` — the explicit opt-out that
excludes it even when the legacy glob would match (`gaming-steam` uses this;
in `dg_ogm_games` it is the one entry with `managed: false`).

```ini
[Desktop Entry]
Name=Zelda: Ocarina of Time - Ship of Harkinian (on gaming)
Exec=...
Categories=Game;
X-OGM-Managed=true
X-OGM-Category=port
X-OGM-GitHub=HarbourMasters/Shipwright
```

| Key | Required | Value |
|-----|----------|-------|
| `X-OGM-Managed` | yes | `true` — the marker; without it ogm ignores the entry |
| `X-OGM-Category` | yes | one of `port`, `decomp`, `recomp`, `fangame`, `wine`, `arcade`, `emulator`, `tool`, `custom` |
| `X-OGM-GitHub` | optional | `owner/repo` — enables release/update checks |
| `X-OGM-SGDBQuery` | optional | SteamGridDB search name for cover art |

### How the keys get there

The metadata lives in one place — `group_vars/all/ogm.yml` (`dg_ogm_games`),
keyed by desktop stem — and is **never** restated in the templates. Every
`*.desktop.j2` in the repo imports a shared macro and calls it with its own
rendered stem as the last line of the `[Desktop Entry]` group:

```jinja2
{% raw %}{% from 'ogm-desktop-entry.j2' import ogm_metadata with context -%}
[Desktop Entry]
... entry keys ...
{{ ogm_metadata('gaming-ship-of-harkinian') }}{% endraw %}
```

`ansible/templates/ogm-desktop-entry.j2` looks the stem up in `dg_ogm_games`
and emits the `X-OGM-*` block when it is registered, nothing otherwise. The
`with context` is required — an imported Jinja macro cannot see `dg_ogm_games`
without it. For looped templates the argument is an expression matching the
render's `dest` (e.g. `'pc-' ~ item.slug`, `'gaming-' ~ item.key ~ '-recomp'`,
`launcher.name`). **To add ogm to a new game: add its `dg_ogm_games` entry and
the two macro lines to its `*.desktop.j2` — no per-template metadata.**

`github` values in `dg_ogm_games` are always derived from the existing `dg_*`
vars that already record the upstream repo (asset URLs, release APIs, clone
URLs) — see the comments in `group_vars/all/ogm.yml`. Entries with no known
metadata (Steam) are simply absent from the list and get no marker.

## Fallback: the `catalog.d` fragment

For ogm builds that predate the `X-OGM-*` keys (or as a belt-and-braces
source), the opt-in `ogm_catalog` role renders a TOML fragment to
`~/.config/ogm/catalog.d/distrobox-gaming.toml` from the same `dg_ogm_games`
list. ogm merges `~/.config/ogm/catalog.d/*.toml` over its bundled catalog;
the `X-OGM-*` keys on the desktop entries take precedence on the ogm side.
Because both the keys and the fragment come from `dg_ogm_games`, they never
disagree.

```toml
[[game]]
id = "ship-of-harkinian"
desktop_id = "gaming-ship-of-harkinian"
category = "port"
github = "HarbourMasters/Shipwright"
```

## Running it

```sh
ansible-playbook site.yml --tags configure   # re-render desktop entries (X-OGM keys) + install
ansible-playbook site.yml --tags ogm         # also render the catalog.d fallback fragment + ogm scan
```

`--tags configure` (or `reset-configs.yml --tags desktop`) re-renders every
desktop entry, so the `X-OGM-*` keys refresh whenever `dg_ogm_games` changes.
Opt-in per-game roles render their own entries into the same
`config/desktop/rendered/` and install through the same script.

Defaults live in `group_vars/all/ogm.yml` and can be overridden in
`host_vars/localhost.yml`:

```yaml
dg_ogm_enabled: true
dg_ogm_catalog_path: "{{ ansible_env.HOME }}/.config/ogm/catalog.d/distrobox-gaming.toml"
```

## When ogm scans

`ogm scan` (idempotent, offline — re-reads desktop files and catalogs) runs
automatically:

- after `scripts/install-host-launchers.sh` refreshes the host menu entries
  (quiet no-op when ogm is not on `PATH`), and
- via a handler when the `ogm_catalog` role changes the rendered fragment.

`ogm refresh` (GitHub release checks + cover downloads) is network-heavy and
is deliberately never called from any install path — run it by hand when you
want fresh metadata/covers.
