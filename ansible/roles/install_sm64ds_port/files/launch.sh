#!/usr/bin/env bash
# ==============================================================================
# Universal Linux Launcher for SM64DS Port
# - Applies any staged launcher self-updates before starting Wine/Proton.
# - Automatically detects and uses the default Proton configured in Steam
#   (or any available Proton / system Wine as fallback).
# - Fully portable across any Linux distribution, Steam Deck / SteamOS, Flatpak Steam.
# ==============================================================================

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Apply any pending launcher update before launching
if [ -f "launcher_new.exe" ] || [ -f "launcher_update.flag" ]; then
    if command -v python3 >/dev/null 2>&1 && [ -f "extract_assets.py" ]; then
        python3 extract_assets.py --apply-updates 2>/dev/null || true
    fi
    if [ -f "launcher_new.exe" ]; then
        echo "[launcher] Applying staged update: launcher_new.exe -> SM64DSLauncher.exe"
        mv -f launcher_new.exe SM64DSLauncher.exe
        chmod +x SM64DSLauncher.exe 2>/dev/null || true
    fi
    rm -f launcher_update.flag 2>/dev/null || true
fi

# 1b. Ensure game assets are extracted (the Windows launcher uses PowerShell
#     for this, which does not work under Wine/Proton; the Python script is
#     the Linux-native equivalent and is safe to run every launch — it checks
#     whether assets are already current before doing any work).
if command -v python3 >/dev/null 2>&1 && [ -f "extract_assets.py" ]; then
    echo "[launcher] Checking game assets..."
    if ! python3 extract_assets.py --ensure-current; then
        echo "[launcher] Error: Asset extraction failed. Check the output above."
        echo "Make sure your .nds ROM file is in this folder or in 'PLACE YOUR ROM HERE'."
        exit 1
    fi
else
    echo "[launcher] Warning: python3 not found. Cannot verify game assets."
    echo "If this is the first run, install Python 3 and try again."
fi

# 2. Check if we are already being run inside an active Steam/Proton environment
if [ -n "$STEAM_COMPAT_DATA_PATH" ] && [ -n "$STEAM_COMPAT_CLIENT_INSTALL_PATH" ] && [ -n "$PROTON" ]; then
    echo "[launcher] Running inside active Steam/Proton environment..."
    mkdir -p "$STEAM_COMPAT_DATA_PATH"
    exec "$PROTON" run "$DIR/SM64DSLauncher.exe" "$@"
fi

# 3. Detect default Proton from Steam configuration via portable Python helper
RUN_INFO=""
if command -v python3 >/dev/null 2>&1; then
    RUN_INFO=$(python3 - << 'PYEOF'
import os, sys, re

def find_proton_info():
    home = os.path.expanduser("~")
    xdg_data = os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share"))
    
    steam_roots = [
        os.environ.get("STEAM_DIR", ""),
        os.path.join(xdg_data, "Steam"),
        os.path.join(home, ".steam", "steam"),
        os.path.join(home, ".steam", "root"),
        os.path.join(home, ".var", "app", "com.valvesoftware.Steam", "data", "Steam"),
        os.path.join(home, ".var", "app", "com.valvesoftware.Steam", ".local", "share", "Steam"),
    ]
    
    steam_dir = None
    for d in steam_roots:
        if d and os.path.isdir(d):
            steam_dir = d
            break

    default_tool_name = None
    library_folders = []
    
    if steam_dir:
        library_folders.append(steam_dir)
        # Parse default compat tool mapping from config.vdf
        config_vdf = os.path.join(steam_dir, "config", "config.vdf")
        if os.path.isfile(config_vdf):
            try:
                with open(config_vdf, "r", errors="ignore") as f:
                    content = f.read()
                m = re.search(r'\"CompatToolMapping\"[^\{]*\{[^}]*\"0\"[^\{]*\{[^}]*\"name\"\s*\"([^\"]+)\"', content, re.DOTALL)
                if m:
                    default_tool_name = m.group(1).strip()
            except Exception:
                pass
                
        # Parse libraryfolders.vdf
        for lib_sub in ["steamapps", "SteamApps"]:
            lib_vdf = os.path.join(steam_dir, lib_sub, "libraryfolders.vdf")
            if os.path.isfile(lib_vdf):
                try:
                    with open(lib_vdf, "r", errors="ignore") as f:
                        for line in f:
                            m = re.search(r'\"path\"\s*\"([^\"]+)\"', line)
                            if m:
                                p = m.group(1).replace("\\\\", "/")
                                if os.path.isdir(p):
                                    library_folders.append(p)
                except Exception:
                    pass

    # Compatibility tools search directories
    search_dirs = [
        "/usr/share/steam/compatibilitytools.d",
        "/usr/local/share/steam/compatibilitytools.d",
        "/usr/share/compatibilitytools.d",
        os.path.join(home, ".compatibilitytools.d"),
    ]
    for lib in set(library_folders):
        search_dirs.append(os.path.join(lib, "compatibilitytools.d"))
        search_dirs.append(os.path.join(lib, "steamapps", "common"))
        search_dirs.append(os.path.join(lib, "SteamApps", "common"))

    found_tools = {}
    for sdir in set(search_dirs):
        if os.path.isdir(sdir):
            try:
                for entry in os.listdir(sdir):
                    tool_dir = os.path.join(sdir, entry)
                    proton_bin = os.path.join(tool_dir, "proton")
                    if os.path.isfile(proton_bin) and os.access(proton_bin, os.X_OK):
                        found_tools[entry] = proton_bin
                        vdf = os.path.join(tool_dir, "compatibilitytool.vdf")
                        if os.path.isfile(vdf):
                            try:
                                with open(vdf, "r", errors="ignore") as vf:
                                    vm = re.search(r'\"display_name\"\s*\"([^\"]+)\"', vf.read())
                                    if vm:
                                        found_tools[vm.group(1).strip()] = proton_bin
                            except Exception:
                                pass
            except Exception:
                pass

    chosen_proton = None
    if default_tool_name:
        if default_tool_name in found_tools:
            chosen_proton = found_tools[default_tool_name]
        else:
            for k, v in found_tools.items():
                if k.lower() == default_tool_name.lower():
                    chosen_proton = v
                    break

    # Fallback to popular or available Protons
    if not chosen_proton and found_tools:
        priority = [
            "Proton-CachyOS Latest", "Proton-GE Latest", "GE-Proton",
            "Proton - Experimental", "Proton Experimental",
            "Proton 10.0", "Proton 9.0", "Proton 8.0"
        ]
        for name in priority:
            for k, v in found_tools.items():
                if name.lower() in k.lower():
                    chosen_proton = v
                    break
            if chosen_proton:
                break
        if not chosen_proton:
            chosen_proton = next(iter(found_tools.values()))

    print(f"{steam_dir or ''}|{chosen_proton or ''}|{default_tool_name or ''}")

find_proton_info()
PYEOF
)
fi

IFS="|" read -r DETECTED_STEAM_DIR DETECTED_PROTON_BIN DETECTED_TOOL_NAME <<< "$RUN_INFO"

if [ -n "$DETECTED_PROTON_BIN" ] && [ -x "$DETECTED_PROTON_BIN" ]; then
    echo "[launcher] Using Steam Proton: ${DETECTED_TOOL_NAME:-$(basename "$(dirname "$DETECTED_PROTON_BIN")")}"
    echo "[launcher] Binary: $DETECTED_PROTON_BIN"

    export STEAM_COMPAT_CLIENT_INSTALL_PATH="${STEAM_COMPAT_CLIENT_INSTALL_PATH:-$DETECTED_STEAM_DIR}"
    export STEAM_COMPAT_DATA_PATH="${STEAM_COMPAT_DATA_PATH:-$DIR/.compatdata}"
    export SteamAppId="${SteamAppId:-0}"
    export SteamGameId="${SteamGameId:-0}"
    
    mkdir -p "$STEAM_COMPAT_DATA_PATH"
    exec "$DETECTED_PROTON_BIN" run "$DIR/SM64DSLauncher.exe" "$@"
elif command -v wine >/dev/null 2>&1; then
    echo "[launcher] Proton not found, falling back to system Wine..."
    exec wine "$DIR/SM64DSLauncher.exe" "$@"
else
    echo "[launcher] Error: Neither Steam Proton nor Wine could be found on this system."
    echo "Please install Wine or Steam with Proton to run the game."
    exit 1
fi
