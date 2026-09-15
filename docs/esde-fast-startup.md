# ES-DE fast startup (gamelist cache only)

By default ES-DE rescans every ROM directory on each launch to pick up added or
removed files. On a large NAS-backed library that scan is the pause you see
before the menu appears.

`dg_esde_parse_gamelist_only: true` (in `group_vars/all/main.yml`) flips ES-DE's
**`ParseGamelistOnly`** setting on, so ES-DE loads the collection only from the
cached `gamelist.xml` files and skips the filesystem scan — the menu opens
almost instantly. `configure_esde` writes the one line into
`ES-DE/settings/es_settings.xml` (a flat, ES-DE-owned file, so it is edited in
place rather than templated); ES-DE keeps `SaveGamelistsMode=always`, so the
gamelists stay complete and this is safe once ES-DE has scanned at least once.

The trade-off: with the scan off, **newly added ROMs do not appear** until the
gamelists are regenerated.

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
would otherwise clobber the change. To keep the scan-on-every-launch behaviour,
set `dg_esde_parse_gamelist_only: false` in `host_vars/localhost.yml` and
re-run the same command.
