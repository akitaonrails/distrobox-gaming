/*
 * sensapi_mta_shim.c — proxy SensApi.dll that keeps a COM MTA alive.
 *
 * Why: some Windows games create COM objects (e.g. the WIC imaging factory for
 * texture loading) from plain worker threads that never call CoInitialize.
 * On Windows that works through the *implicit MTA*: as long as ANY thread in
 * the process holds a multithreaded apartment, uninitialised threads join it.
 * Real Windows always has one (the Win10 XInput1_4 / WinRT stack keeps an
 * MTA), but Wine's builtin DLLs don't, and if the game's main thread is STA
 * its own later CoInitializeEx(MTA) fails with RPC_E_CHANGED_MODE — so no MTA
 * ever exists and CoCreateInstance returns CO_E_NOTINITIALIZED, which the
 * game dereferences -> EXCEPTION_ACCESS_VIOLATION on launch.
 *
 * This DLL replaces SensApi.dll (one-function import: IsNetworkAlive) and, on
 * process attach, starts a thread that initialises an MTA and parks forever,
 * so the process always has an MTA for Wine's implicit-MTA lookup.
 * Load with WINEDLLOVERRIDES="sensapi=n,b" (native first).
 *
 * First user: Arcade Classics Anniversary Collection (Konami/M2, appid 1018000).
 * Build: x86_64-w64-mingw32-gcc -shared -O2 -o SensApi.dll sensapi_mta_shim.c \
 *        sensapi_mta_shim.def -lole32 -Wl,--kill-at
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <objbase.h>

#define NETWORK_ALIVE_LAN 0x00000001

static DWORD WINAPI mta_keepalive(LPVOID arg)
{
    (void)arg;
    /* COINIT_MULTITHREADED on a fresh thread creates the process MTA. */
    if (SUCCEEDED(CoInitializeEx(NULL, COINIT_MULTITHREADED)))
    {
        for (;;) Sleep(INFINITE);
    }
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH)
    {
        HANDLE t;
        DisableThreadLibraryCalls(inst);
        /* CreateThread is safe in DllMain; COM init happens on the new thread
         * (never call COM under the loader lock). */
        t = CreateThread(NULL, 0, mta_keepalive, NULL, 0, NULL);
        if (t) CloseHandle(t);
    }
    return TRUE;
}

/* Same answer Wine's builtin gives: the LAN is up. */
BOOL WINAPI IsNetworkAlive(LPDWORD flags)
{
    if (flags) *flags = NETWORK_ALIVE_LAN;
    return TRUE;
}
