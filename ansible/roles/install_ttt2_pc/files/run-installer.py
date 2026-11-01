#!/usr/bin/env python3
"""Run the TTT2 silent installer under a dedicated, reaped Proton process group."""

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def windows_path(path: Path) -> str:
    return "Z:" + str(path.resolve()).replace("/", "\\")


def stop_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    time.sleep(2)
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def prefix_processes(compatdata: Path, earliest: int = 0) -> list[int]:
    """Find processes in this dedicated prefix, including detached Wine services."""
    matches = []
    path = os.fsencode(str(compatdata))
    markers = {b"STEAM_COMPAT_DATA_PATH=" + path, b"WINEPREFIX=" + path + b"/pfx"}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            env = set((proc / "environ").read_bytes().split(b"\0"))
            if not env.intersection(markers):
                continue
            # stat fields after the closing parenthesis begin at field 3.
            started = int((proc / "stat").read_text().rsplit(")", 1)[1].split()[19])
        except (OSError, ValueError, IndexError):
            continue
        if started >= earliest:
            matches.append(int(proc.name))
    return matches


def stop_prefix_processes(compatdata: Path, earliest: int) -> list[int]:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in prefix_processes(compatdata, earliest):
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        time.sleep(2)
    return prefix_processes(compatdata, earliest)


def main() -> int:
    parser = argparse.ArgumentParser()
    for key in ("proton", "steam-root", "compatdata", "installer", "iso", "tu", "output", "log"):
        parser.add_argument("--" + key, required=True)
    args = parser.parse_args()
    proton = Path(args.proton)
    installer = Path(args.installer)
    iso = Path(args.iso)
    tu = Path(args.tu)
    output = Path(args.output)
    log = Path(args.log)
    for item in (proton, installer, iso, tu):
        if not item.is_file():
            parser.error(f"missing required file: {item}")
    compatdata = Path(args.compatdata).resolve()
    if prefix_processes(compatdata):
        parser.error(f"dedicated Proton prefix is already running: {compatdata}")
    started = int(Path(f"/proc/{os.getpid()}/stat").read_text().rsplit(")", 1)[1].split()[19])
    output.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        STEAM_COMPAT_CLIENT_INSTALL_PATH=args.steam_root,
        STEAM_COMPAT_DATA_PATH=args.compatdata,
        SteamAppId="0",
        SteamGameId="0",
        __NV_PRIME_RENDER_OFFLOAD="1",
        __GLX_VENDOR_LIBRARY_NAME="nvidia",
    )
    cmd = [str(proton), "waitforexitandrun", str(installer), "/silent", windows_path(iso), windows_path(tu), windows_path(output)]
    with log.open("w") as stream:
        stream.write(f"started={time.strftime('%Y-%m-%dT%H:%M:%S%z')} container=host process=proton\n")
        stream.flush()
        proc = subprocess.Popen(cmd, cwd=output.parent, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        stream.write(f"pid={proc.pid} parent={os.getpid()} pgid={proc.pid}\n")
        stream.flush()
        try:
            rc = proc.wait(timeout=3600)
        except subprocess.TimeoutExpired:
            stream.write("installer timed out after 3600 seconds\n")
            rc = 124
        finally:
            stop_group(proc.pid)
            proc.wait()
            remaining = stop_prefix_processes(compatdata, started)
            if remaining:
                stream.write(f"unreaped prefix processes={remaining}\n")
                rc = 125
        stream.write(f"exit={rc} finished={time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    if rc != 0:
        print(f"TTT2 installer failed (rc={rc}); inspect {log}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
