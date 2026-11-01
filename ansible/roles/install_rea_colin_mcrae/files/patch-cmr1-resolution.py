#!/usr/bin/env python3
"""Select the 640x480 game slot that REA replaces with its configured 4K mode."""

import os
from pathlib import Path
import shutil
import sys
import tempfile


cfg = Path(sys.argv[1])
backup = Path(sys.argv[2])
data = bytearray(cfg.read_bytes())
if len(data) != 7712 or data[:8] != bytes.fromhex("34 12 65 87 be 94 b0 ab"):
    raise SystemExit(f"unexpected Colin McRae Rally config format: {cfg}")
if data[0x13] not in range(4):
    raise SystemExit(f"unexpected race resolution slot {data[0x13]} in {cfg}")
if data[0x13] == 2:
    print("already-640x480")
    raise SystemExit(0)

backup.parent.mkdir(parents=True, exist_ok=True)
if not backup.exists():
    shutil.copy2(cfg, backup)
data[0x13] = 2
with tempfile.NamedTemporaryFile(dir=cfg.parent, delete=False) as tmp:
    tmp.write(data)
    tmp_name = tmp.name
try:
    os.chmod(tmp_name, cfg.stat().st_mode & 0o777)
    os.replace(tmp_name, cfg)
except BaseException:
    Path(tmp_name).unlink(missing_ok=True)
    raise
print("patched-640x480")
