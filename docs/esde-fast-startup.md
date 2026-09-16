# ES-DE fast startup (gamelist cache only)

ES-DE rescans every ROM directory on each launch to pick up added or removed
files. On a large NAS-backed library that scan is the pause you see before the
menu appears — but it's also what makes freshly-dropped ROMs show up, so it is
**on by default** here (`dg_esde_parse_gamelist_only: false`).

Setting `dg_esde_parse_gamelist_only: true` (in `group_vars/all/main.yml` or
`host_vars/localhost.yml`) opts into fast startup: it flips ES-DE's
**`ParseGamelistOnly`** setting on, so ES-DE loads the collection only from the
cached `gamelist.xml` files and skips the filesystem scan — the menu opens
almost instantly. `configure_esde` writes the one line into
`ES-DE/settings/es_settings.xml` (a flat, ES-DE-owned file, so it is edited in
place rather than templated); ES-DE keeps `SaveGamelistsMode=always`, so the
gamelists stay complete and this is safe once ES-DE has scanned at least once.

The trade-off — and why it's off by default: with the scan off, **newly added
ROMs do not appear** until the gamelists are regenerated (which is easy to
forget, and looks like "missing games"). Use `esde-rescan` after adding ROMs.

## Rescanning after you add or remove ROMs

Run the helper (inside the box, or via `distrobox enter gaming -- esde-rescan`):

```sh
esde-rescan
```

It launches ES-DE once with the scan re-enabled — the new games are found and
written into the gamelists — and restores fast startup automatically when you
quit ES-DE. (Refuses to run if ES-DE is already open; quit it first.)

Equivalent by hand, if you prefer ES-DE's own menu: **Main Menu → Other
Settings → “Only show ROMs from gamelist.xml files”** — turn it **off**, restart
ES-DE (it rescans and saves the gamelists), then turn it back **on**.

## Applying / changing the default

```sh
cd ansible
ansible-playbook reset-configs.yml --tags esde       # apply (edit while ES-DE is closed)
```

Edit while ES-DE is **closed** — ES-DE rewrites `es_settings.xml` on exit and
would otherwise clobber the change. To opt into fast startup, set
`dg_esde_parse_gamelist_only: true` in `host_vars/localhost.yml` and re-run the
same command.
