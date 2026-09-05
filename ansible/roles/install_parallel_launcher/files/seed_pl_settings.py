#!/usr/bin/env python3
"""Seed / enforce Parallel Launcher settings for this box.

Usage: seed_pl_settings.py <settings.cfg path>

Parallel Launcher writes ~/.config/parallel-launcher/settings.cfg itself (on
first launch and whenever the user changes options). This merges the box's
required values on top of whatever is there — creating the file with sane
defaults if it does not exist yet — and prints "changed" only when it actually
had to write, so the Ansible task stays idempotent.

Enforced: fullscreen on the RTX, the ParaLLEl-RDP Vulkan plugin (default_gfx
plugin = 1), the SDL input driver (for the 8BitDo), and no pause-on-focus-loss
(so a screenshot/focus change doesn't freeze the game). Everything else the user
sets in the launcher is preserved.
"""
import json
import os
import sys

# Values the box requires. Only these are forced; the launcher fills in and the
# user keeps everything else.
ENFORCE = {
    "fullscreen": True,
    "default_gfx_plugin": 1,     # 0=GLideN64, 1=ParaLLEl-RDP (what heavy hacks need)
    "input_driver": "sdl",       # 8BitDo via SDL2 GameController
    "pause_on_focus_loss": False,
}

# Baseline used only when the file does not exist yet, so a fresh box gets a
# complete, migration-safe config instead of a bare fragment.
DEFAULTS = {
    "visible_columns": 6,
    "parallel_upscaling": 0,
    "parallel_remove_borders": False,
    "parallel_antialiasing": True,
    "parallel_upscale_texrects": False,
    "gliden64_correct_depth_compare": True,
    "gliden64_emulate_framebuffer": True,
    "window_scale": 4,
    "enable_vsync": True,
    "hide_while_playing": False,
    "preferred_controller": None,
    "dark_mode": True,
    "patch_to_same_folder": True,
    "migration_state": 47,       # current schema — avoids a first-run migration reset
    "core_update_interval": 1,
    "discord_integration": False,
    "libretro_log_level": 1,
}


def main():
    path = sys.argv[1]
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = dict(DEFAULTS)

    before = json.dumps(data, sort_keys=True)
    data.update(ENFORCE)
    after = json.dumps(data, sort_keys=True)

    if before != after or not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
        print("changed")
    else:
        print("unchanged")


if __name__ == "__main__":
    main()
