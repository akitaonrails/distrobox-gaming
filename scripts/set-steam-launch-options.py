#!/usr/bin/env python3
"""Set Steam LaunchOptions entries in userdata/config/localconfig.vdf.

This is a tiny VDF text editor for Steam's user-local launch options. It edits
`UserLocalConfigStore/Software/Valve/Steam/apps`, preserving the rest of
localconfig.vdf verbatim.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


LAUNCH_RE = re.compile(r'^\t+"LaunchOptions"\s+".*"\s*$')


def escape_vdf(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def find_matching_brace(lines: list[str], open_index: int) -> int:
    depth = 0
    for idx in range(open_index, len(lines)):
        stripped = lines[idx].strip()
        if stripped == '{':
            depth += 1
        elif stripped == '}':
            depth -= 1
            if depth == 0:
                return idx
    raise ValueError(f"no matching closing brace for line {open_index + 1}")


def find_steam_apps_block(lines: list[str]) -> tuple[int, int]:
    """Find the canonical Software/Valve/Steam/apps block.

    Follow the parent keys: an empty or never-played library may have no
    LastPlayed or LaunchOptions fields, and other branches can have apps too.
    """
    child_start, end = 0, len(lines)
    for key in ('UserLocalConfigStore', 'Software', 'Valve', 'Steam', 'apps'):
        idx = child_start
        while idx + 1 < end:
            if lines[idx + 1].strip() != '{':
                idx += 1
                continue
            close = find_matching_brace(lines, idx + 1)
            if lines[idx].strip().lower() == f'"{key}"'.lower():
                child_start, end = idx + 2, close
                break
            # Skip this entire sibling, including any similarly named children.
            idx = close + 1
        else:
            raise ValueError('could not find Software/Valve/Steam/apps block in localconfig.vdf')
    return idx, end


def set_launch_option(lines: list[str], appid: str, option: str) -> bool:
    apps_start, apps_end = find_steam_apps_block(lines)
    escaped = escape_vdf(option)
    app_indent = '\t\t\t\t\t'
    prop_indent = '\t\t\t\t\t\t'
    launch_line = f'{prop_indent}"LaunchOptions"\t\t"{escaped}"\n'

    idx = apps_start + 2
    while idx < apps_end:
        match = re.match(r'^\t\t\t\t\t"(?P<appid>\d+)"\s*$', lines[idx].rstrip())
        if not match:
            idx += 1
            continue
        block_open = idx + 1
        block_end = find_matching_brace(lines, block_open)
        if match.group('appid') == appid:
            for line_idx in range(block_open + 1, block_end):
                if LAUNCH_RE.match(lines[line_idx].rstrip()):
                    if lines[line_idx] == launch_line:
                        return False
                    lines[line_idx] = launch_line
                    return True
            lines[block_end:block_end] = [launch_line]
            return True
        idx = block_end + 1

    lines[apps_end:apps_end] = [
        f'{app_indent}"{appid}"\n',
        f'{app_indent}{{\n',
        launch_line,
        f'{app_indent}}}\n',
    ]
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--localconfig', required=True, type=Path)
    parser.add_argument('--set', dest='sets', nargs=2, action='append', metavar=('APPID', 'LAUNCH_OPTIONS'), required=True)
    args = parser.parse_args()

    path = args.localconfig.expanduser()
    lines = path.read_text().splitlines(keepends=True)
    changed = False
    for appid, option in args.sets:
        changed = set_launch_option(lines, appid, option) or changed

    if changed:
        backup = path.with_suffix(path.suffix + '.bak-dg-metal-gear')
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(''.join(lines))
    print(f'changed: {str(changed).lower()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
