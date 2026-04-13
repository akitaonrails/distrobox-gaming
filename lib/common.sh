#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"

log() {
  printf '%s\n' "==> $*"
}

warn() {
  printf '%s\n' "WARN: $*" >&2
}

die() {
  printf '%s\n' "ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

in_box() {
  distrobox-enter -n "$DG_BOX_NAME" -- "$@"
}

backup_once() {
  file="$1"
  [ -f "$file" ] || return 0
  [ -f "$file.dg-original" ] || cp -p "$file" "$file.dg-original"
}

ensure_dir() {
  mkdir -p "$1"
}

require_readable_dir() {
  [ -d "$1" ] || die "Directory does not exist: $1"
  [ -r "$1" ] || die "Directory is not readable: $1"
}

require_writable_dir() {
  ensure_dir "$1"
  [ -w "$1" ] || die "Directory is not writable: $1"
}

write_test() {
  dir="$1"
  require_writable_dir "$dir"
  tmp="$dir/.dg-write-test.$$"
  : > "$tmp" || die "Cannot write test file in: $dir"
  rm -f "$tmp"
}

render_template() {
  template="$1"
  output="$2"

  ensure_dir "$(dirname "$output")"
  sed \
    -e "s|@DG_BOX_NAME@|$DG_BOX_NAME|g" \
    -e "s|@DG_BOX_HOME@|$DG_BOX_HOME|g" \
    -e "s|@DG_SHADPS4_BIN@|$DG_SHADPS4_BIN|g" \
    -e "s|@DG_SHADPS4_QTLAUNCHER_BIN@|$DG_SHADPS4_QTLAUNCHER_BIN|g" \
    -e "s|@DG_SHADPS4_GAME_ARG@|$DG_SHADPS4_GAME_ARG|g" \
    -e "s|@DG_SHADPS4_PATCH_XML@|$DG_SHADPS4_PATCH_XML|g" \
    -e "s|@DG_XEMU_BOOTROM@|$DG_XEMU_BOOTROM|g" \
    -e "s|@DG_XEMU_FLASHROM@|$DG_XEMU_FLASHROM|g" \
    -e "s|@DG_XEMU_HDD@|$DG_XEMU_HDD|g" \
    "$template" > "$output"
}

install_desktop_symlink() {
  source_file="$1"
  target_file="$2"
  ensure_dir "$(dirname "$target_file")"
  ln -sfn "$source_file" "$target_file"
}

sudo_begin() {
  sudo -v || die "sudo authentication failed"
  (
    while true; do
      sudo -n true >/dev/null 2>&1 || exit 0
      sleep 60
    done
  ) &
  DG_SUDO_KEEPALIVE_PID=$!
  trap 'kill "$DG_SUDO_KEEPALIVE_PID" 2>/dev/null || true' EXIT INT TERM
}

box_sudo_begin() {
  ensure_box_sudo
  in_box sudo -n true || die "sudo inside distrobox '$DG_BOX_NAME' is not available"
  (
    while true; do
      in_box sudo -n true >/dev/null 2>&1 || exit 0
      sleep 60
    done
  ) &
  DG_BOX_SUDO_KEEPALIVE_PID=$!
  trap 'kill "$DG_BOX_SUDO_KEEPALIVE_PID" 2>/dev/null || true' EXIT INT TERM
}

replace_or_add_ini_key() {
  file="$1"
  section="$2"
  key="$3"
  value="$4"

  ensure_dir "$(dirname "$file")"
  [ -f "$file" ] || : > "$file"
  backup_once "$file"

  awk -v section="$section" -v key="$key" -v value="$value" '
    BEGIN { in_section = 0; seen_section = 0; wrote = 0 }
    $0 == "[" section "]" {
      if (seen_section && !wrote) {
        print key " = " value
        wrote = 1
      }
      in_section = 1
      seen_section = 1
      print
      next
    }
    /^\[/ {
      if (in_section && !wrote) {
        print key " = " value
        wrote = 1
      }
      in_section = 0
      print
      next
    }
    in_section && $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
      if (!wrote) {
        print key " = " value
        wrote = 1
      }
      next
    }
    { print }
    END {
      if (!seen_section) {
        print ""
        print "[" section "]"
        print key " = " value
      } else if (in_section && !wrote) {
        print key " = " value
      }
    }
  ' "$file" > "$file.tmp.$$"
  mv "$file.tmp.$$" "$file"
}

ensure_multilib() {
  log "Ensuring multilib is enabled inside $DG_BOX_NAME"
  in_box sudo sh -eu -c '
    pacman_conf=/etc/pacman.conf
    if grep -q "^\[multilib\]$" "$pacman_conf"; then
      exit 0
    fi

    tmp="$(mktemp)"
    awk "
      BEGIN { pending_options = 0 }
      /^\[options\]$/ { pending_options = 1; next }
      {
        if (pending_options && \$0 !~ /^[[:space:]]*$/) {
          print \"[options]\"
          pending_options = 0
        }
        print
      }
      END {
        if (pending_options) {
          print \"[options]\"
        }
      }
    " "$pacman_conf" > "$tmp"

    cat >> "$tmp" <<EOF

[multilib]
Include = /etc/pacman.d/mirrorlist
EOF
    mv "$tmp" "$pacman_conf"
  '
}

container_root_exec() {
  if command -v docker >/dev/null 2>&1; then
    docker exec -u root "$DG_BOX_NAME" "$@"
    return 0
  fi

  if command -v podman >/dev/null 2>&1; then
    podman exec -u root "$DG_BOX_NAME" "$@"
    return 0
  fi

  die "Could not find docker or podman to repair sudo inside $DG_BOX_NAME"
}

ensure_box_sudo() {
  if in_box sudo -n true >/dev/null 2>&1; then
    return 0
  fi

  log "Repairing sudo policy inside $DG_BOX_NAME"
  container_root_exec sh -eu -c '
    install -d -m 0755 /etc/sudoers.d
    cat > /etc/sudoers.d/zz-distrobox-gaming-nopasswd <<EOF
%wheel ALL=(ALL:ALL) NOPASSWD: ALL
EOF
    chmod 0440 /etc/sudoers.d/zz-distrobox-gaming-nopasswd
    if [ -d /etc/sudoers.d ]; then
      find /etc/sudoers.d -maxdepth 1 -type f -exec chmod 0440 {} +
    fi
  '

  in_box sudo -n true >/dev/null 2>&1 || die "sudo inside distrobox '$DG_BOX_NAME' is not available"
}
