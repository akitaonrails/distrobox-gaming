#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"

if [ -f "$DG_PROJECT_ROOT/config/distrobox-gaming.env" ]; then
  # shellcheck disable=SC1091
  . "$DG_PROJECT_ROOT/config/distrobox-gaming.env"
fi

: "${DG_BOX_NAME:=gaming}"
: "${DG_IMAGE:=archlinux:latest}"

: "${DG_HOST_UID:=$(id -u)}"
: "${DG_HOST_GID:=$(id -g)}"
: "${DG_HOST_USER:=$(id -un)}"
: "${DG_HOST_GROUP:=$(id -gn)}"

: "${DG_BOX_ROOT:=/mnt/data/distrobox/gaming}"
: "${DG_BOX_HOME:=$DG_BOX_ROOT}"

: "${DG_EMUDECK_ROOT:=/mnt/terachad/Emulators/EmuDeck}"
: "${DG_ROM_ROOT:=$DG_EMUDECK_ROOT/roms}"
: "${DG_ROM_HEAVY_ROOT:=$DG_EMUDECK_ROOT/roms_heavy}"
: "${DG_ROM_RARE_ROOT:=$DG_EMUDECK_ROOT/roms_rare}"
: "${DG_BIOS_ROOT:=$DG_EMUDECK_ROOT/Emulation/bios}"

: "${DG_PS4_ROM_ROOT:=$DG_ROM_RARE_ROOT/ps4}"
: "${DG_PS4_FIRMWARE_MODULES:=$DG_ROM_RARE_ROOT/ps4-firmware/11.00_sys_modules}"
: "${DG_SHADPS4_TITLE_ID:=CUSA00003}"
: "${DG_SHADPS4_PATCH_NAME:=Driveclub.xml}"
: "${DG_SHADPS4_PATCH_XML:=$DG_BOX_HOME/.local/share/shadPS4/patches/$DG_SHADPS4_PATCH_NAME}"

: "${DG_LEGACY_DOCS_ROOT:=/mnt/terachad/Documents/FrankMD/Linux}"
: "${DG_HOST_APPLICATIONS_DIR:=$HOME/.local/share/applications}"

export DG_PROJECT_ROOT DG_BOX_NAME DG_IMAGE
export DG_HOST_UID DG_HOST_GID DG_HOST_USER DG_HOST_GROUP
export DG_BOX_ROOT DG_BOX_HOME
export DG_EMUDECK_ROOT DG_ROM_ROOT DG_ROM_HEAVY_ROOT DG_ROM_RARE_ROOT DG_BIOS_ROOT
export DG_PS4_ROM_ROOT DG_PS4_FIRMWARE_MODULES DG_SHADPS4_TITLE_ID DG_SHADPS4_PATCH_NAME DG_SHADPS4_PATCH_XML
export DG_LEGACY_DOCS_ROOT DG_HOST_APPLICATIONS_DIR

