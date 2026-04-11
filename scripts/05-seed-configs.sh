#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

log "Installing wrapper scripts"
ensure_dir "$DG_BOX_HOME/bin"
cp -p "$DG_PROJECT_ROOT/config/wrappers/flycast-hires" "$DG_BOX_HOME/bin/flycast-hires"
chmod +x "$DG_BOX_HOME/bin/flycast-hires"

log "Applying PCSX2 controller hotkey"
pcsx2_ini="$DG_BOX_HOME/.config/PCSX2/inis/PCSX2.ini"
replace_or_add_ini_key "$pcsx2_ini" "UI" "ConfirmShutdown" "false"
replace_or_add_ini_key "$pcsx2_ini" "Hotkeys" "ShutdownVM" "SDL-0/Start & SDL-0/Back"

log "Applying DuckStation visual defaults"
duck_ini="$DG_BOX_HOME/.config/duckstation/settings.ini"
replace_or_add_ini_key "$duck_ini" "Main" "ConfirmPowerOff" "false"
replace_or_add_ini_key "$duck_ini" "Main" "SaveStateOnExit" "true"
replace_or_add_ini_key "$duck_ini" "Main" "StartFullscreen" "true"
replace_or_add_ini_key "$duck_ini" "BIOS" "SearchDirectory" "$DG_BIOS_ROOT"
replace_or_add_ini_key "$duck_ini" "GPU" "Renderer" "Vulkan"
replace_or_add_ini_key "$duck_ini" "GPU" "ResolutionScale" "8"
replace_or_add_ini_key "$duck_ini" "GPU" "PGXPEnable" "true"
replace_or_add_ini_key "$duck_ini" "GPU" "PGXPDepthBuffer" "true"
replace_or_add_ini_key "$duck_ini" "GPU" "PGXPPreserveProjFP" "true"
replace_or_add_ini_key "$duck_ini" "GPU" "PGXPVertexCache" "false"
replace_or_add_ini_key "$duck_ini" "GPU" "WidescreenHack" "true"
replace_or_add_ini_key "$duck_ini" "Display" "VSync" "true"
replace_or_add_ini_key "$duck_ini" "Display" "OptimalFramePacing" "true"

log "Applying Flycast known-good keys when config exists"
flycast_ini="$DG_BOX_HOME/.config/flycast/emu.cfg"
if [ -f "$flycast_ini" ]; then
  replace_or_add_ini_key "$flycast_ini" "config" "pvr.AutoSkipFrame" "0"
  replace_or_add_ini_key "$flycast_ini" "config" "pvr.rend" "4"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.DelayFrameSwapping" "no"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.DupeFrames" "yes"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.EmulateFramebuffer" "no"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.Resolution" "2880"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.WideScreen" "yes"
  replace_or_add_ini_key "$flycast_ini" "config" "rend.vsync" "yes"
else
  warn "Flycast config not found yet; wrapper will force the critical runtime settings"
fi

log "Installing shadPS4 Driveclub config and patch"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/custom_configs"
ensure_dir "$DG_BOX_HOME/.local/share/shadPS4/patches"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/CUSA00003.toml" "$DG_BOX_HOME/.local/share/shadPS4/custom_configs/$DG_SHADPS4_TITLE_ID.toml"
cp -p "$DG_PROJECT_ROOT/config/emulator-overrides/shadPS4/Driveclub.xml" "$DG_SHADPS4_PATCH_XML"

log "Config seeding completed"

