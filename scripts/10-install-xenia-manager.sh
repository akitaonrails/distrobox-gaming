#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

need_cmd distrobox
need_cmd curl
need_cmd unzip
need_cmd find
need_cmd awk
box_sudo_begin

install_pacman_list() {
  list_file="$1"
  packages="$(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' "$list_file")"
  [ -n "$packages" ] || return 0
  # shellcheck disable=SC2086
  in_box sudo pacman -Syu --needed --noconfirm $packages
}

fetch_xenia_manager_release() {
  if [ -n "$DG_XENIA_MANAGER_ZIP_URL" ]; then
    XENIA_MANAGER_TAG="manual"
    XENIA_MANAGER_ZIP_URL="$DG_XENIA_MANAGER_ZIP_URL"
    return 0
  fi

  release_json="$(curl -fsSL "$DG_XENIA_MANAGER_RELEASE_API")"
  XENIA_MANAGER_TAG="$(printf '%s\n' "$release_json" | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')"
  [ -n "$XENIA_MANAGER_TAG" ] || die "Could not determine the latest Xenia Manager release tag"

  XENIA_MANAGER_ZIP_URL="$(
    printf '%s\n' "$release_json" | awk '
      BEGIN { fallback = ""; found = 0 }
      /"name":[[:space:]]*"/ {
        name = $0
        sub(/^.*"name":[[:space:]]*"/, "", name)
        sub(/".*$/, "", name)
      }
      /"browser_download_url":[[:space:]]*"/ {
        url = $0
        sub(/^.*"browser_download_url":[[:space:]]*"/, "", url)
        sub(/".*$/, "", url)
        if (url ~ /\.zip$/ && fallback == "") {
          fallback = url
        }
        if (name ~ /[Ww]in/ && name ~ /x64/ && url ~ /\.zip$/) {
          print url
          found = 1
          exit
        }
      }
      END {
        if (!found && fallback != "") {
          print fallback
        }
      }
    '
  )"
  [ -n "$XENIA_MANAGER_ZIP_URL" ] || die "Could not determine the latest Xenia Manager ZIP asset"
}

wine_in_box() {
  in_box env \
    WINEPREFIX="$DG_XENIA_PREFIX" \
    WINEARCH=win64 \
    WINEDEBUG=-all \
    "$@"
}

run_windows_installer() {
  installer="$1"
  shift

  if wine_in_box wine "$installer" "$@"; then
    status=0
  else
    status=$?
  fi

  case "$status" in
    0|194)
      return 0
      ;;
    *)
      return "$status"
      ;;
  esac
}

ensure_dir "$DG_XENIA_PREFIX"
ensure_dir "$DG_XENIA_CACHE_DIR"
ensure_dir "$DG_XENIA_MANAGER_RELEASES_DIR"
ensure_dir "$DG_BOX_HOME/bin"

ensure_multilib
install_pacman_list "$DG_PROJECT_ROOT/config/package-lists/xenia-pacman.txt"

log "Initializing the Xenia Manager Wine prefix"
wine_in_box wineboot -u
wine_in_box wineserver -w

if [ -d "$DG_XENIA_GAME_DIR" ]; then
  log "Linking Xenia Manager G: drive to $DG_XENIA_GAME_DIR"
  ln -sfn "$DG_XENIA_GAME_DIR" "$DG_XENIA_PREFIX/dosdevices/g:"
else
  warn "Xbox 360 game directory missing: $DG_XENIA_GAME_DIR"
fi

dotnet_installer="$DG_XENIA_CACHE_DIR/windowsdesktop-runtime-win-x64.exe"
vcredist_installer="$DG_XENIA_CACHE_DIR/vc_redist.x64.exe"

log "Downloading .NET Desktop Runtime"
curl -fL "$DG_XENIA_DOTNET_URL" -o "$dotnet_installer"

log "Downloading Visual C++ Redistributable"
curl -fL "$DG_XENIA_VCREDIST_URL" -o "$vcredist_installer"

log "Installing or updating .NET Desktop Runtime inside the Xenia prefix"
run_windows_installer "Z:$dotnet_installer" /install /quiet /norestart
wine_in_box wineserver -w

log "Installing or updating Visual C++ Redistributable inside the Xenia prefix"
run_windows_installer "Z:$vcredist_installer" /install /quiet /norestart
wine_in_box wineserver -w

fetch_xenia_manager_release
release_dir="$DG_XENIA_MANAGER_RELEASES_DIR/$XENIA_MANAGER_TAG"
release_zip="$DG_XENIA_CACHE_DIR/$XENIA_MANAGER_TAG.zip"

if [ ! -f "$release_zip" ]; then
  log "Downloading Xenia Manager $XENIA_MANAGER_TAG"
  curl -fL "$XENIA_MANAGER_ZIP_URL" -o "$release_zip"
fi

if [ ! -d "$release_dir" ]; then
  tmp_dir="$(mktemp -d "$DG_XENIA_MANAGER_RELEASES_DIR/.extract.XXXXXX")"
  log "Extracting Xenia Manager into $release_dir"
  unzip -q "$release_zip" -d "$tmp_dir"
  mv "$tmp_dir" "$release_dir"
fi

manager_root="$(find "$release_dir" -name XeniaManager.exe -print | sed -n '1s#/XeniaManager.exe$##p')"
[ -n "$manager_root" ] || die "Xenia Manager executable not found after extracting $release_zip"
ln -sfn "$manager_root" "$DG_XENIA_MANAGER_CURRENT"

log "Writing Xenia Manager launcher wrapper"
cat > "$DG_XENIA_MANAGER_BIN" <<EOF
#!/usr/bin/env sh
set -eu
if [ ! -f "$DG_XENIA_MANAGER_EXE" ]; then
  printf '%s\n' "ERROR: Xenia Manager is not installed at $DG_XENIA_MANAGER_EXE" >&2
  printf '%s\n' "Run ./bin/dg xenia inside the repo to install or update it." >&2
  exit 1
fi
export WINEPREFIX="$DG_XENIA_PREFIX"
export WINEARCH=win64
export WINEDEBUG=-all
exec wine "$DG_XENIA_MANAGER_EXE" "\$@"
EOF
chmod +x "$DG_XENIA_MANAGER_BIN"

log "Refreshing desktop launchers"
"$DG_PROJECT_ROOT/scripts/06-export-desktop-apps.sh"

log "Xenia Manager setup completed"
