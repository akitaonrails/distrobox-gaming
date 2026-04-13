#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

need_cmd distrobox
box_sudo_begin

pacman_list="$DG_PROJECT_ROOT/config/package-lists/pacman.txt"
aur_list="$DG_PROJECT_ROOT/config/package-lists/aur.txt"

log "Refreshing pacman package database"
in_box sudo pacman -Syu --noconfirm

log "Installing pacman packages"
packages="$(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' "$pacman_list")"
# shellcheck disable=SC2086
in_box sudo pacman -S --needed --noconfirm $packages

if ! in_box sh -lc 'command -v yay' >/dev/null 2>&1; then
  log "Installing yay-bin"
  in_box sh -lc 'tmp="$(mktemp -d)"; cd "$tmp"; git clone https://aur.archlinux.org/yay-bin.git; cd yay-bin; makepkg -si --noconfirm; rm -rf "$tmp"'
fi

log "Installing AUR emulator packages"
aur_packages="$(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d; /yay-bin/d' "$aur_list")"
# shellcheck disable=SC2086
in_box yay -S --needed --noconfirm --answerclean None --answerdiff None $aur_packages

log "Package bootstrap completed"
