#!/usr/bin/env python3
"""Force a Steam app to use a Proton compatibility tool in config.vdf."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


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


def find_mapping_block(lines: list[str]) -> tuple[int, int]:
    for idx, line in enumerate(lines):
        if line.strip() == '"CompatToolMapping"' and idx + 1 < len(lines) and lines[idx + 1].strip() == '{':
            return idx, find_matching_brace(lines, idx + 1)
    raise ValueError('could not find CompatToolMapping block in config.vdf')


def default_tool(lines: list[str], mapping_start: int, mapping_end: int) -> str:
    for idx in range(mapping_start + 2, mapping_end):
        if lines[idx].strip() != '"0"':
            continue
        end = find_matching_brace(lines, idx + 1)
        for line in lines[idx:end]:
            match = re.match(r'^\s*"name"\s+"([^"]+)"', line)
            if match:
                return match.group(1)
    raise ValueError('CompatToolMapping has no default "0" tool; pass --tool')


def set_mapping(lines: list[str], appid: str, tool: str, priority: str) -> bool:
    start, end = find_mapping_block(lines)
    block = [
        f'\t\t\t\t\t"{appid}"\n',
        '\t\t\t\t\t{\n',
        f'\t\t\t\t\t\t"name"\t\t"{tool}"\n',
        '\t\t\t\t\t\t"config"\t\t""\n',
        f'\t\t\t\t\t\t"priority"\t\t"{priority}"\n',
        '\t\t\t\t\t}\n',
    ]
    idx = start + 2
    while idx < end:
        if lines[idx].strip() == f'"{appid}"':
            close = find_matching_brace(lines, idx + 1)
            if lines[idx:close + 1] == block:
                return False
            lines[idx:close + 1] = block
            return True
        idx += 1
    lines[end:end] = block
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--tool', help='Compat tool name. Defaults to config.vdf app 0 mapping.')
    parser.add_argument('--priority', default='250')
    parser.add_argument('--appid', action='append', required=True)
    args = parser.parse_args()

    path = args.config.expanduser()
    lines = path.read_text().splitlines(keepends=True)
    start, end = find_mapping_block(lines)
    tool = args.tool or default_tool(lines, start, end)
    changed = False
    for appid in args.appid:
        changed = set_mapping(lines, appid, tool, args.priority) or changed
    if changed:
        backup = path.with_suffix(path.suffix + '.bak-dg-compat-tool')
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(''.join(lines))
    print(f'changed: {str(changed).lower()}')
    print(f'tool: {tool}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
