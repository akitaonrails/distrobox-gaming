# TOTK dump extractor (for UltraTears)

A one-time recovery tool that produces the **pre-extracted `exefs/` + `romfs/`
dump** that [UltraTears](../../docs/ultratears.md) needs. UltraTears refuses
encrypted packages (`.xci`/`.nsp`/`.nca`) and reads no keys, so it will not do
this step itself — it only accepts the merged plain files.

You run this **once**, from your own copies of the game, to stage the dump the
`install_ultratears` role consumes. It is the UltraTears analogue of
`scripts/recover-smas-25th-rom.py`: the role verifies and builds from the
artifact, this tool reproduces the artifact if it is ever lost.

## Why LibHac (and not hactool)

The dump is the base RomFS **with the 1.4.3 update applied**. The update is a
BKTR (indirect / AES-CTR-EX) patch over the base. Applying it is something only
the full **.NET LibHac** does:

- `hactool` — even git master against SciresM's live repo — reports
  `Invalid BKTR layout!` on TOTK 1.4.3.
- the Rust ports (`nsw-rs/libhac`) do not implement BKTR at all.
- the usual LibHac GitHub mirrors are DMCA'd (Thealexbarney/LibHac 404,
  garoxas/LibHac blocked), **but LibHac 0.19.0 is on NuGet**
  (<https://www.nuget.org/packages/LibHac>), independent of GitHub — that is the
  path this tool uses.

## Prerequisites

- A .NET SDK (built/verified with **.NET 10**; any recent SDK LibHac 0.19.0
  supports works). On this box it is the mise-managed `dotnet`
  (`~/.local/share/mise/dotnet-root/dotnet`); nothing is added to the box
  package set for it.
- Your own `prod.keys` (e.g. `~/.local/share/eden/keys/prod.keys`).
- A `title.keys` holding the **encrypted** titlekey for the title, one line:

  ```
  0100f2c0115b68000000000000000010 = <32 hex: the encrypted titlekey>
  ```

  `rights_id = enc_titlekey`. The encrypted titlekey is at offset `0x180` of the
  game's ticket (`.tik`); LibHac decrypts it with the titlekek internally. Do
  **not** put the already-decrypted titlekey here.
- Your owned base XCI and the 1.4.3 update NSP.

TOTK title ids: base `0100F2C0115B6000`, update `0100F2C0115B6800`; update 1.4.3
is title version `v720896`.

## Run

```sh
cd scripts/totk-dump-extractor
dotnet run -c Release -- \
  "<base>.xci" \
  "<update-1.4.3>.nsp" \
  "$HOME/.local/share/eden/keys/prod.keys" \
  "$HOME/.switch/title.keys" \
  "<dump-out-dir>"
```

`<dump-out-dir>` is `dg_ut_dump_dir` from `group_vars/all/ultratears.yml`
(`.../roms_heavy/switch/UltraTears-TOTK-1.4.3-dump`). It writes `exefs/` (5
files) and `romfs/` (~304,243 files, ~16 GiB).

## Verify

```sh
# from the extracted UltraTears builder (tools/ultratears):
deps/python/bin/python3.14 tools/setup.py --check-dump "<dump-out-dir>"
# -> "<dir>: Tears of the Kingdom 1.4.3"
```

`--check-dump` confirms the dump cryptographically (SHA-256 of the code
modules), which is why the role pins no size-based checksum on the 19 GB tree.
