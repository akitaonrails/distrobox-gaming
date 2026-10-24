#!/usr/bin/env python3
"""Extract the pinned NSIS payload and GS ZIP without backslash path leakage."""

import argparse
import pathlib
import shutil
import subprocess
import tempfile
import zipfile


def extract(installer: pathlib.Path, gs_zip: pathlib.Path, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gt4-recomp-", dir=destination.parent) as work:
        stage = pathlib.Path(work)
        subprocess.run(
            ["7z", "x", "-y", f"-o{stage}", str(installer), ".update-staging/*"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        payload = stage / ".update-staging"
        if not (payload / "game/gt4vulkan.exe").is_file():
            raise RuntimeError("NSIS archive lacks the expected game executable")
        gs_dir = payload / "game/gs"
        gs_dir.mkdir()
        with zipfile.ZipFile(gs_zip) as archive:
            for entry in archive.infolist():
                parts = pathlib.PurePosixPath(entry.filename.replace("\\", "/")).parts
                if len(parts) < 2 or parts[0] != gs_zip.stem or ".." in parts:
                    raise RuntimeError(f"Unexpected GS archive path: {entry.filename}")
                target = gs_dir.joinpath(*parts[1:])
                if entry.is_dir() or entry.filename.endswith(("/", "\\")):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(entry) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
        if not (gs_dir / "gt4-gs.exe").is_file():
            raise RuntimeError("GS archive lacks its executable")
        if destination.exists():
            raise RuntimeError(f"Install destination already exists: {destination}")
        payload.rename(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("installer", "gs_zip", "destination"):
        parser.add_argument(name, type=pathlib.Path)
    args = parser.parse_args()
    extract(args.installer, args.gs_zip, args.destination)
