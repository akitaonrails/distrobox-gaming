#!/usr/bin/env python3
"""Bind an 8BitDo (js0) to OpenBOR Player 1 by rewriting a Saves/<pak>.cfg.

OpenBOR defaults Player 1 to the KEYBOARD and Player 2 to joystick index 1, so a
single controller (index 0) is bound to nobody and the game ignores it. This
rewrites Player 1's 12-entry control keyset to the js0 codes.

OpenBOR keycodes (engine/sdl/control.h, joysticks.h): for joystick index i,
  button b -> 1 + i*64 + b
  hat h    -> hatfirst = 1 + i*64 + NumButtons + 2*NumAxes + 4*h ; Up,Right,Down,Left = +0,+1,+2,+3
The 8BitDo Ultimate 2 presents (via SDL) 11 buttons, 6 axes, 1 hat (dpad), std
XInput button order (0=A 1=B 2=X 3=Y 4=LB 5=RB 6=Back 7=Start). Override the
layout with env DG_OPENBOR_* if a different pad/mode is used.

Idempotent: only rewrites when Player 1 is still on the keyboard defaults
(so it never clobbers a user's own in-game rebind). Usage: openbor-bind-8bitdo.py <cfg>
"""
import struct, sys, os

NB = int(os.environ.get("DG_OPENBOR_NUMBUTTONS", "11"))
NA = int(os.environ.get("DG_OPENBOR_NUMAXES", "6"))
def joybtn(b): return 1 + b
hatfirst = 1 + NB + 2 * NA               # hat 0
HAT = {"UP": hatfirst, "RIGHT": hatfirst + 1, "DOWN": hatfirst + 2, "LEFT": hatfirst + 3}

# Player-1 cfg order: Up,Down,Left,Right, Fire1..Fire6, Start, Screenshot
NEW = [HAT["UP"], HAT["DOWN"], HAT["LEFT"], HAT["RIGHT"],
       joybtn(0), joybtn(1), joybtn(2), joybtn(3), joybtn(4), joybtn(5),  # A B X Y LB RB
       joybtn(7),                                                         # Start
       69]                                                                # Screenshot: keep kbd F12
# Keyboard default P1 keyset = SDL scancodes Up,Down,Left,Right (82,81,80,79)...
KBD_HEAD = struct.pack("<4I", 82, 81, 80, 79)

def main(path):
    if not os.path.isfile(path):
        print(f"openbor-bind: no cfg yet at {path} (created on first launch)"); return 0
    d = bytearray(open(path, "rb").read())
    if d.find(struct.pack("<4I", *NEW[:4])) >= 0:
        print("openbor-bind: already bound to 8BitDo — leaving as-is"); return 0
    off = d.find(KBD_HEAD)
    if off < 0:
        print("openbor-bind: P1 keyset not at keyboard defaults (custom binds?) — not touching"); return 0
    struct.pack_into("<12I", d, off, *NEW)
    open(path, "wb").write(d)
    print(f"openbor-bind: bound 8BitDo -> Player 1 in {os.path.basename(path)}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) if len(sys.argv) > 1 else (print("usage: openbor-bind-8bitdo.py <cfg>") or 2))
