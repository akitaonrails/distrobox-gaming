# Offline Mario Maker user levels

> **Paths:** examples show this maintainer's defaults. Every root is a
> `dg_*` variable — see `ansible/host_vars/localhost.yml.example`.

## SMM2 (Switch / Eden) — WORKING

The opt-in `install_smm2_levels` role fills Coursebot's "My Courses"
(slots 0–59, full editor access) with the most-liked courses from
Nintendo's live SMM2 servers, mirrored by
[tgrcode.com MariOver](https://tgrcode.com/mm2/docs/):

```sh
ansible-playbook install-smm2-levels.yml     # or site.yml --tags smm2_levels
```

Pipeline:

1. `fetch-popular.py` queries `search_popular` (overall + each
   difficulty bucket, 100 each), dedupes, **filters out courses uploaded
   after `dg_smm2_levels_max_uploaded`** and takes the top
   `dg_smm2_levels_count` by likes. Downloads `level_data` (.bcd) and
   `level_thumbnail` (.jpg) per course.
2. `smm2-inject` (Rust, built on
   [Tarnadas/smmdb-lib](https://github.com/Tarnadas/smmdb-lib)) opens the
   Eden save, wraps each thumbnail through SMM2's encryption, registers
   each course in `save.dat`, and writes
   `course_data_XXX.bcd`/`course_thumb_XXX.btl`.

Requirements and caveats:

- **The game must have been launched once in Eden** so `save.dat`
  exists (title screen is enough — the save is created at boot).
- **Close Eden before injecting** (the role refuses otherwise).
- **Game version matters.** Course files refuse to load on game
  versions older than the one that saved them. This box has SMM2 EUR
  v1.0.1, so the default cutoff `dg_smm2_levels_max_uploaded:
  2019-10-01` (v1.1.0's release) keeps everything loadable. After
  updating the game to 3.x, set it to `""` and re-run for the
  unfiltered all-time top list.
- A pristine save backup is kept at `<save>.bak-pre-inject/` (created
  before the first injection, never overwritten).
- Injected metadata quirk: play stats/maker info come from the course
  file itself; everything plays fine offline.
- tgrcode 403s generic Python User-Agents — the fetch script sends a
  curl UA on purpose.
- The `manifest.json` next to the downloaded courses maps slot rank →
  course name/likes/style for reference.

## SMM1 (Wii U / Cemu) — PAUSED, sources archived here

The original plan (SMMDB + cemu-smmdb) is blocked: **smmdb.net is
unreachable** (TCP dead as of 2026-07-02; Wayback last saw it alive
2026-05-22 — it may return, check periodically). Nintendo's Wii U
servers are gone since April 2024, so SMMDB was the only turnkey
archive.

What survives, mapped for a future attempt:

- **Course payloads** live in the Wayback Machine (the 556 GB
  `super_mario_maker_courses_202105` WARC crawl is ingested there);
  fetchable per-course via
  `web.archive.org/web/<ts>if_/<original CloudFront URL>`.
- **Metadata API**: `https://api.bobac-analytics.com/smm1` (from
  [HerobrineTV/SMM1-Level-Downloader](https://github.com/HerobrineTV/SMM1-Level-Downloader))
  is alive (`/ping` → pong) and serves per-level metadata including the
  original course `url` — search endpoints `searchLevels` and
  `searchRandomLevels` only, no global top-by-stars endpoint.
- Course files are **ASH-compressed**; a Linux ASH decompressor is
  needed (that tool ships `ashextractor.exe`, Windows-only).
- Injection layer exists: the `cemu-smm` npm package (v4.x, Tarnadas)
  edits Cemu SMM1 saves; the save must first be created by launching
  SMM1 once in Cemu (never launched yet on this box — no mlc01).
- Quick-win alternative if wanted sooner: the GBAtemp "Super Mario
  Maker Save Collection" thread ships ready-made saves with all
  official event/staff courses preserved.

### Pipeline state (2026-07-02)

Everything is proven except the final payload fetch:

- SMM1 save created (`mlc01/usr/save/00050000/1018dd00/user/80000001`),
  8BitDo profile captured into `seed_configs/files/cemu/`.
- `cemu-smm@3.0.3` (last Node-compatible release) loads on Node 26;
  `save.addCourseFromFs(courseDir)` handles slot assignment, order
  table, and save.dat CRC. Installed under
  `<dg_box_home>/tools/smm1-levels/injector/`.
- `ashdec` built from NinjaCheetah/ASH0-tools (course payloads are
  ASH0-compressed).
- `sample-levels.py` samples the bobac metadata API and ranks by
  stars (no global top endpoint exists): 120 candidates at
  `tools/smm1-levels/candidates.json`, star range 86..6 —
  best-of-random, since the truly famous 10k-star levels can't be
  found without a sorted index.
- **Blocked on**: web.archive.org rate-limiting this IP (heavy probing
  burned the quota; bans appear to last hours). Next session: fetch
  one payload via `web.archive.org/web/2021if_/<candidate url>`,
  identify the post-ASH structure (single .cdt vs bundle), finish the
  course-folder assembly step, run `inject.js`.
- Also viable: Pretendo Network has SMM1 Course World partially
  revived and working in Cemu (2026) — live in-game browsing,
  complements offline injection.

## Layout

- Tools (box): `<dg_box_home>/tools/smm2-levels/` — fetch script,
  cargo project, downloaded `courses/`.
- Role: `ansible/roles/install_smm2_levels/`; vars in
  `ansible/group_vars/all/smm2_levels.yml`
  (`dg_smm2_eden_profile` is machine-specific).
