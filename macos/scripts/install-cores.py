#!/usr/bin/env python3
"""Install native macOS cores atomically; existing cores are kept unchanged."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import urllib.request
import zipfile

CORES = ('stella', 'genesis_plus_gx', 'mgba', 'gambatte', 'nestopia', 'snes9x', 'vice_x64sc')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        raise SystemExit('macOS required')
    arch = platform.machine()
    if arch not in ('arm64', 'x86_64'):
        raise SystemExit('Unsupported architecture: ' + arch)
    destination = Path.home() / 'Library/Application Support/distrobox-gaming/cores'
    if args.check:
        missing = [c for c in CORES if not (destination / (c + '_libretro.dylib')).is_file()]
        if missing:
            raise SystemExit('Missing cores: ' + ', '.join(missing))
        for core in CORES:
            if subprocess.run(['lipo', str(destination / (core + '_libretro.dylib')),
                               '-verify_arch', arch]).returncode:
                raise SystemExit(f'{core} is not a native {arch} core; delete it and reinstall.')
        print(f'All {len(CORES)} native cores are installed.')
        return
    destination.mkdir(parents=True, exist_ok=True)
    for core in CORES:
        name = core + '_libretro.dylib'
        target = destination / name
        if target.exists():
            print('Already installed:', core)
            continue
        url = f'https://buildbot.libretro.com/nightly/apple/osx/{arch}/latest/{name}.zip'
        with urllib.request.urlopen(url, timeout=120) as response:
            archive = response.read()
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            data = z.read(name)
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as f:
            temporary = Path(f.name)
            f.write(data)
        try:
            subprocess.run(['lipo', str(temporary), '-verify_arch', arch], check=True)
            temporary.chmod(0o755)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        (destination / (name + '.json')).write_text(json.dumps({
            'url': url, 'sha256': hashlib.sha256(data).hexdigest(), 'architecture': arch
        }, indent=2) + '\n')
        print('Installed:', core)

if __name__ == '__main__':
    main()
