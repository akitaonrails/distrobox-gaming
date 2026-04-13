#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

need_cmd curl
need_cmd python

pick_qtlauncher_release() {
  qt_json="$(curl -fsSL "$DG_SHADPS4_QTLAUNCHER_RELEASES_API")"
  qt_info="$(
    printf '%s' "$qt_json" | DG_SHADPS4_QTLAUNCHER_RELEASE="$DG_SHADPS4_QTLAUNCHER_RELEASE" \
      DG_SHADPS4_QTLAUNCHER_ASSET_NAME="$DG_SHADPS4_QTLAUNCHER_ASSET_NAME" \
      python -c '
import json, os, sys
hint = os.environ.get("DG_SHADPS4_QTLAUNCHER_RELEASE", "")
asset_name = os.environ.get("DG_SHADPS4_QTLAUNCHER_ASSET_NAME", "")
data = json.load(sys.stdin)
release = None
for candidate in data:
    if candidate.get("draft"):
        continue
    tag = candidate.get("tag_name", "")
    name = candidate.get("name", "")
    if hint and hint not in tag and hint not in name:
        continue
    release = candidate
    break
if release is None:
    for candidate in data:
        if not candidate.get("draft"):
            release = candidate
            break
if release is None:
    raise SystemExit("Could not find a matching shadPS4 QtLauncher release")
assets = release.get("assets", [])
asset = None
for candidate in assets:
    name = candidate.get("name", "")
    lower = name.lower()
    if asset_name and name == asset_name:
        asset = candidate
        break
    if name.endswith(".zip") and "qtlauncher" in lower and "linux" in lower:
        asset = candidate
        break
    if name.endswith(".AppImage") and "qtlauncher" in lower:
        asset = candidate
        break
if asset is None:
    for candidate in assets:
        name = candidate.get("name", "")
        if name.endswith(".AppImage"):
            asset = candidate
            break
if asset is None:
    raise SystemExit("Could not find a QtLauncher AppImage asset")
tag = release["tag_name"]
suffix = tag.split("shadPS4QtLauncher-", 1)[1] if "shadPS4QtLauncher-" in tag else tag
print(tag)
print(asset["browser_download_url"])
print(asset["name"])
print(suffix)
'
  )"
  QT_TAG="$(printf '%s\n' "$qt_info" | sed -n '1p')"
  QT_URL="$(printf '%s\n' "$qt_info" | sed -n '2p')"
  QT_ASSET_NAME="$(printf '%s\n' "$qt_info" | sed -n '3p')"
  QT_RELEASE_SUFFIX="$(printf '%s\n' "$qt_info" | sed -n '4p')"
}

pick_shadps4_release() {
  shad_json="$(curl -fsSL "$DG_SHADPS4_RELEASES_API")"
  shad_info="$(
    printf '%s' "$shad_json" | DG_SHADPS4_CHANNEL="$DG_SHADPS4_CHANNEL" python -c '
import json, os, sys
channel = os.environ.get("DG_SHADPS4_CHANNEL", "").lower()
want_prerelease = channel.startswith("pre")
data = json.load(sys.stdin)
release = None
for candidate in data:
    if candidate.get("draft"):
        continue
    if bool(candidate.get("prerelease")) != want_prerelease:
        continue
    release = candidate
    break
if release is None:
    raise SystemExit("Could not find a matching shadPS4 release")
assets = release.get("assets", [])
asset = None
for candidate in assets:
    name = candidate.get("name", "")
    lower = name.lower()
    if name.endswith(".zip") and "linux" in lower and "sdl" in lower:
        asset = candidate
        break
    if name.endswith(".AppImage") and ("sdl" in lower or "linux" in lower):
        asset = candidate
        break
if asset is None:
    for candidate in assets:
        name = candidate.get("name", "")
        if name.endswith(".AppImage"):
            asset = candidate
            break
if asset is None:
    raise SystemExit("Could not find a shadPS4 AppImage asset")
display = "Pre-release (Nightly)" if release.get("prerelease") else "Stable"
published = release.get("published_at", "")
date = published[:10] if len(published) >= 10 else ""
codename = release.get("target_commitish") or release.get("tag_name", "")
print(release["tag_name"])
print(display)
print(date)
print(codename)
print(asset["browser_download_url"])
print(asset["name"])
print("1" if release.get("prerelease") else "0")
'
  )"
  SHADPS4_TAG="$(printf '%s\n' "$shad_info" | sed -n '1p')"
  SHADPS4_DISPLAY_NAME="$(printf '%s\n' "$shad_info" | sed -n '2p')"
  SHADPS4_DATE="$(printf '%s\n' "$shad_info" | sed -n '3p')"
  SHADPS4_CODENAME="$(printf '%s\n' "$shad_info" | sed -n '4p')"
  SHADPS4_URL="$(printf '%s\n' "$shad_info" | sed -n '5p')"
  SHADPS4_ASSET_NAME="$(printf '%s\n' "$shad_info" | sed -n '6p')"
  SHADPS4_TYPE="$(printf '%s\n' "$shad_info" | sed -n '7p')"
}

install_qtlauncher_release() {
  pick_qtlauncher_release
  qt_release_root="$DG_SHADPS4_QTLAUNCHER_ROOT/releases/$QT_RELEASE_SUFFIX"
  qt_download="$DG_SHADPS4_QTLAUNCHER_ROOT/downloads/$QT_TAG-$QT_ASSET_NAME"

  ensure_dir "$DG_SHADPS4_QTLAUNCHER_ROOT/downloads"
  ensure_dir "$DG_SHADPS4_QTLAUNCHER_ROOT/releases"
  ensure_dir "$qt_release_root"

  if [ ! -f "$qt_download" ]; then
    log "Downloading shadPS4 QtLauncher $QT_TAG"
    curl -fL "$QT_URL" -o "$qt_download"
  fi

  if [ "${QT_ASSET_NAME##*.}" = "zip" ]; then
    if [ ! -f "$qt_release_root/shadPS4QtLauncher-qt.AppImage" ]; then
      unzip -oq "$qt_download" -d "$qt_release_root"
    fi
  elif [ ! -f "$qt_release_root/$QT_ASSET_NAME" ]; then
    cp -p "$qt_download" "$qt_release_root/$QT_ASSET_NAME"
  fi

  qt_release_asset="$(find "$qt_release_root" -maxdepth 2 -name 'shadPS4QtLauncher-qt.AppImage' -print | sed -n '1p')"
  [ -n "$qt_release_asset" ] || die "QtLauncher AppImage missing after unpacking $QT_ASSET_NAME"

  if [ ! -x "$qt_release_root/squashfs-root/AppRun" ]; then
    log "Extracting shadPS4 QtLauncher into $qt_release_root"
    chmod +x "$qt_release_asset"
    (
      cd "$qt_release_root"
      rm -rf squashfs-root
      "$qt_release_asset" --appimage-extract >/dev/null
    )
  fi

  ln -sfn "$qt_release_root/squashfs-root" "$DG_SHADPS4_QTLAUNCHER_ROOT/current"
}

install_managed_shadps4_build() {
  pick_shadps4_release
  ensure_dir "$DG_SHADPS4_VERSIONS_ROOT/$DG_SHADPS4_CHANNEL"

  shadps4_tag_file="$DG_SHADPS4_VERSIONS_ROOT/$DG_SHADPS4_CHANNEL/release.tag"
if [ ! -f "$shadps4_tag_file" ] || [ "$(cat "$shadps4_tag_file")" != "$SHADPS4_TAG" ]; then
    log "Downloading shadPS4 $SHADPS4_TAG"
    tmp_download="$DG_SHADPS4_MANAGED_BIN.download.$$"
    curl -fL "$SHADPS4_URL" -o "$tmp_download"
    if [ "${SHADPS4_ASSET_NAME##*.}" = "zip" ]; then
      tmp_extract_dir="$(mktemp -d "$DG_SHADPS4_VERSIONS_ROOT/$DG_SHADPS4_CHANNEL/.extract.XXXXXX")"
      unzip -oq "$tmp_download" -d "$tmp_extract_dir"
      extracted_appimage="$(find "$tmp_extract_dir" -maxdepth 2 -name 'Shadps4-sdl.AppImage' -print | sed -n '1p')"
      [ -n "$extracted_appimage" ] || die "Could not find Shadps4-sdl.AppImage inside $SHADPS4_ASSET_NAME"
      chmod +x "$extracted_appimage"
      mv "$extracted_appimage" "$DG_SHADPS4_MANAGED_BIN"
      rm -rf "$tmp_extract_dir"
      rm -f "$tmp_download"
    else
      chmod +x "$tmp_download"
      mv "$tmp_download" "$DG_SHADPS4_MANAGED_BIN"
    fi
    printf '%s\n' "$SHADPS4_TAG" > "$shadps4_tag_file"
  fi

  cat > "$DG_BOX_HOME/.local/share/shadPS4QtLauncher/versions.json" <<EOF
[
    {
        "codename": "$SHADPS4_CODENAME",
        "date": "$SHADPS4_DATE",
        "name": "$SHADPS4_DISPLAY_NAME",
        "path": "$DG_SHADPS4_MANAGED_BIN",
        "type": $SHADPS4_TYPE
    }
]
EOF
  printf '%s\n' "$SHADPS4_DISPLAY_NAME" > "$DG_SHADPS4_VERSIONS_ROOT/cache.version"

  if [ ! -f "$DG_BOX_HOME/.local/share/shadPS4QtLauncher/qt_ui.ini" ]; then
    cat > "$DG_BOX_HOME/.local/share/shadPS4QtLauncher/qt_ui.ini" <<EOF
[general_settings]
checkForUpdates=false
showChangeLog=false

[version_manager]
checkOnStartup=true
versionPath=$DG_SHADPS4_VERSIONS_ROOT
versionSelected=$DG_SHADPS4_MANAGED_BIN
EOF
  fi
}

ensure_dir "$DG_BOX_HOME/.local/share/shadPS4QtLauncher"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4QtLauncher/game_data"

install_qtlauncher_release
install_managed_shadps4_build

log "Refreshing shadPS4 runtime directories"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/sys_modules"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/patches"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/custom_configs"
ensure_dir "$DG_BOX_HOME/.config/shadPS4/custom_configs"
ensure_dir "$DG_BOX_HOME/bin"

if [ -d "$DG_PS4_FIRMWARE_MODULES" ]; then
  log "Linking PS4 firmware modules from $DG_PS4_FIRMWARE_MODULES"
  find "$DG_PS4_FIRMWARE_MODULES" -maxdepth 1 -type f | while IFS= read -r src; do
    dst="$DG_BOX_HOME/.local/share/shadPS4/sys_modules/$(basename "$src")"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
      warn "Leaving existing non-symlink module in place: $dst"
      continue
    fi
    ln -sfn "$src" "$dst"
  done
else
  warn "PS4 firmware modules missing: $DG_PS4_FIRMWARE_MODULES"
fi

log "Seeding Driveclub shadPS4 config"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/CUSA00003.toml" \
  "$DG_BOX_HOME/.local/share/shadPS4/custom_configs/$DG_SHADPS4_TITLE_ID.toml"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/CUSA00003.toml" \
  "$DG_BOX_HOME/.config/shadPS4/custom_configs/$DG_SHADPS4_TITLE_ID.toml"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/Driveclub.xml" \
  "$DG_SHADPS4_PATCH_XML"

if [ -f "$DG_BOX_HOME/.local/share/shadPS4/config.toml" ]; then
  log "Mirroring shadPS4 global config into the XDG config path"
  cp -p "$DG_BOX_HOME/.local/share/shadPS4/config.toml" \
    "$DG_BOX_HOME/.config/shadPS4/config.toml"
fi

log "Refreshing shadPS4 wrappers"
cat > "$DG_SHADPS4_BIN" <<EOF
#!/usr/bin/env sh
set -eu
target="$DG_SHADPS4_MANAGED_BIN"
if [ ! -x "\$target" ]; then
  printf '%s\n' "ERROR: QtLauncher-managed shadPS4 build missing: \$target" >&2
  printf '%s\n' "Install or update the $DG_SHADPS4_CHANNEL build from shadPS4 QtLauncher first." >&2
  exit 1
fi
exec "\$target" "\$@"
EOF
chmod +x "$DG_SHADPS4_BIN"

cat > "$DG_SHADPS4_QTLAUNCHER_BIN" <<EOF
#!/usr/bin/env sh
set -eu
exec "$DG_SHADPS4_QTLAUNCHER_ROOT/current/AppRun" "\$@"
EOF
chmod +x "$DG_SHADPS4_QTLAUNCHER_BIN"

log "Linking shadPS4 command alias to the QtLauncher-managed wrapper"
ln -sfn "$DG_SHADPS4_BIN" "$DG_SHADPS4_CMD_ALIAS"

log "Refreshing desktop launchers from project templates"
"$DG_PROJECT_ROOT/scripts/06-export-desktop-apps.sh"

log "Regenerating ES-DE custom systems so the PS4 entry matches the extracted game layout"
"$DG_PROJECT_ROOT/scripts/07-configure-es-de.sh"

log "shadPS4 refresh completed"
