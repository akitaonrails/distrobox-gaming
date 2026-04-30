#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"

render_dir="${DG_DESKTOP_RENDER_DIR:-$project_root/config/desktop/rendered}"
apps_dir="${DG_HOST_APPLICATIONS_DIR:-$HOME/.local/share/applications}"

log() {
  printf '[host-launchers] %s\n' "$*"
}

desktop_exec() {
  sed -n 's/^Exec=//p' "$1" | head -n 1
}

desktop_box_name() {
  local exec_line="$1"
  sed -n 's/.*distrobox-enter -n \([^ ]*\) -- .*/\1/p' <<<"$exec_line"
}

desktop_box_command_tail() {
  local exec_line="$1"
  sed -n 's/.*distrobox-enter -n [^ ]* -- \(.*\)$/\1/p' <<<"$exec_line"
}

desktop_target_command() {
  local tail="$1"
  python - "$tail" <<'PY'
import shlex
import sys

parts = shlex.split(sys.argv[1])
if not parts:
    sys.exit(1)

while parts and parts[0] == "env":
    parts = parts[1:]
    while parts:
        if parts[0] == "-u" and len(parts) >= 2:
            parts = parts[2:]
            continue
        if parts[0].startswith("-"):
            parts = parts[1:]
            continue
        if "=" in parts[0] and not parts[0].startswith("/"):
            parts = parts[1:]
            continue
        break

if not parts:
    sys.exit(1)

print(parts[0])
PY
}

target_exists_in_box() {
  local box="$1"
  local target="$2"

  if [[ "$target" == /* ]]; then
    distrobox-enter -n "$box" -- test -e "$target" >/dev/null 2>&1
  else
    distrobox-enter -n "$box" -- sh -lc 'command -v "$1" >/dev/null 2>&1' sh "$target"
  fi
}

launcher_is_installable() {
  local desktop="$1"
  local exec_line box tail target

  exec_line="$(desktop_exec "$desktop")"
  if [[ -z "$exec_line" ]]; then
    log "skip $(basename "$desktop"): missing Exec"
    return 1
  fi

  box="$(desktop_box_name "$exec_line")"
  if [[ -z "$box" ]]; then
    return 0
  fi

  tail="$(desktop_box_command_tail "$exec_line")"
  if ! target="$(desktop_target_command "$tail")"; then
    log "skip $(basename "$desktop"): cannot parse Exec target"
    return 1
  fi

  if target_exists_in_box "$box" "$target"; then
    return 0
  fi

  log "skip $(basename "$desktop"): $target is not installed in box $box"
  return 1
}

install_desktop() {
  local src="$1"
  local dest="$apps_dir/$(basename "$src")"

  if [[ -f "$dest" ]] && cmp -s "$src" "$dest"; then
    log "ok $(basename "$src")"
    return 0
  fi

  install -Dm0644 "$src" "$dest"
  log "installed $(basename "$src")"
}

remove_desktop() {
  local src="$1"
  local dest="$apps_dir/$(basename "$src")"

  if [[ -e "$dest" || -L "$dest" ]]; then
    rm -f "$dest"
    log "removed stale $(basename "$src")"
  fi
}

main() {
  if [[ ! -d "$render_dir" ]]; then
    printf 'ERROR: rendered desktop directory missing: %s\n' "$render_dir" >&2
    printf 'Run: cd %s/ansible && ansible-playbook site.yml --tags desktop\n' "$project_root" >&2
    return 1
  fi

  mkdir -p "$apps_dir"
  if [[ ! -w "$apps_dir" ]]; then
    printf 'ERROR: host applications directory is not writable: %s\n' "$apps_dir" >&2
    return 1
  fi

  shopt -s nullglob
  local desktop
  for desktop in "$render_dir"/*.desktop; do
    if command -v desktop-file-validate >/dev/null 2>&1; then
      desktop-file-validate "$desktop"
    fi

    if launcher_is_installable "$desktop"; then
      install_desktop "$desktop"
    else
      remove_desktop "$desktop"
    fi
  done

  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$apps_dir" >/dev/null 2>&1 || true
  fi

  if [[ "${DG_SKIP_WALKER_RESTART:-0}" != "1" ]]; then
    pkill -f '/usr/bin/walker --gapplication-service' >/dev/null 2>&1 || true
  fi
  log "done"
}

main "$@"
