# Wine COM-MTA keepalive shim (proxy `SensApi.dll`)

`install_mta_shim` (`site.yml --tags mta_shim` / `install-mta-shim.yml`) builds
a tiny proxy **`SensApi.dll`** with mingw-w64 inside the box and drops it into
listed game dirs (`dg_mta_shim_games`). Paired with the launch option
`WINEDLLOVERRIDES="sensapi=n,b"` (managed in `dg_steam_launch_options_by_appid`),
it fixes a class of **"crashes on launch under every Proton"** games.

## The bug it fixes

Some Windows games create COM objects — typically `CLSID_WICImagingFactory`
(Windows Imaging Component, for texture loading) — from **plain worker threads
that never call `CoInitialize`**. On Windows that works via the *implicit MTA*:
if any thread in the process holds a multithreaded apartment, uninitialised
threads join it, and real Windows always has one (the Win10 `XInput1_4`/WinRT
stack keeps an MTA alive). Under Wine the builtin DLLs hold no MTA, and if the
game's main thread initialised COM as **STA** its own later
`CoInitializeEx(MTA)` fails with `RPC_E_CHANGED_MODE` — so **no MTA ever
exists**. `CoCreateInstance` then returns `CO_E_NOTINITIALIZED`
(`err:ole:com_get_class_object apartment not initialised`), the game
dereferences the null factory, and dies with `EXCEPTION_ACCESS_VIOLATION`
seconds after launch. Wine's implicit-MTA lookup itself is correct
(`apartment_get_current_or_mta`) — it just needs an MTA to find.

## The fix

The game imports exactly one function from `SensApi.dll` (`IsNetworkAlive`).
The proxy exports it (returning "LAN alive", like Wine's builtin) and, on
process attach, starts a thread that calls `CoInitializeEx(NULL,
COINIT_MULTITHREADED)` and parks forever — so the process always has an MTA.
Source: `ansible/roles/install_mta_shim/files/sensapi_mta_shim.c`.

Diagnosing pointers (how this was found): run the exe with the prefix's Proton
wine and `WINEDEBUG=+seh,+ole,+pid`; look for `apartment not initialised`
immediately before a `c0000005`, and check the `CoInitializeEx` calls per
thread (`0x2` = STA, `0` = MTA) in the crashing **pid** — other Wine processes
(explorer, rpcss) also init COM and will confuse a pid-less trace.

## Games

| Game | appid | Notes |
|---|---|---|
| Arcade Classics Anniversary Collection | 1018000 | Crash at `AA_AC_ArcadeClassics.exe+0x10f71` creating the WIC factory. Verified fixed 2026-08-29 (renders on DP-1). Also needs `DXVK_FRAME_RATE=60` (M2 refresh-rate speed coupling). |

Adding a game: append to `dg_mta_shim_games` (name, appid, `game_dir`), add
`WINEDLLOVERRIDES="sensapi=n,b"` to its entry in `steam_launch_options.yml`,
run `install-mta-shim.yml` with Steam closed. Only games that actually import
`SensApi.dll` can use this proxy as-is; for others, proxy a different
one-function import the same way.
