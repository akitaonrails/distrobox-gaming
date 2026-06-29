#!/usr/bin/env python3
"""Set INI-style options while preserving comments and unrelated settings."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^\s*\[\s*(?P<section>[^\]]+?)\s*\]\s*(?:[;#].*)?$")


def parse_assignment(raw: str) -> tuple[str, str, str]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError(f"missing '=' in assignment: {raw}")

    target, value = raw.split("=", 1)
    if "." not in target:
        raise argparse.ArgumentTypeError(
            f"assignment target must be SECTION.KEY: {raw}"
        )

    section, key = target.split(".", 1)
    section = section.strip()
    key = key.strip()
    if not section or not key:
        raise argparse.ArgumentTypeError(f"empty section or key in: {raw}")

    return section, key, value.strip()


def key_re(key: str) -> re.Pattern[str]:
    return re.compile(rf"^(?P<prefix>\s*{re.escape(key)}\s*=\s*)(?P<value>.*)$", re.I)


def find_section(lines: list[str], section: str) -> tuple[int, int] | None:
    start = -1
    for index, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if not match:
            continue

        if match.group("section").strip().lower() == section.lower():
            start = index
            continue

        if start != -1:
            return start, index

    if start != -1:
        return start, len(lines)
    return None


def set_option(lines: list[str], section: str, key: str, value: str) -> bool:
    changed = False
    section_bounds = find_section(lines, section)

    if section_bounds is None:
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.extend([f"[{section}]\n", f"{key} = {value}\n"])
        return True

    section_start, section_end = section_bounds
    pattern = key_re(key)

    for index in range(section_start + 1, section_end):
        match = pattern.match(lines[index])
        if not match:
            continue

        replacement = f"{match.group('prefix')}{value}\n"
        if lines[index] != replacement:
            lines[index] = replacement
            changed = True
        return changed

    insert_at = section_end
    lines.insert(insert_at, f"{key} = {value}\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--create", action="store_true")
    parser.add_argument(
        "--set",
        dest="assignments",
        action="append",
        type=parse_assignment,
        default=[],
        metavar="SECTION.KEY=VALUE",
    )
    args = parser.parse_args()

    if not args.assignments:
        parser.error("at least one --set assignment is required")

    if not args.file.exists():
        if not args.create:
            print(f"missing INI file: {args.file}", file=sys.stderr)
            return 1
        lines: list[str] = []
    else:
        lines = args.file.read_text(encoding="utf-8").splitlines(keepends=True)

    changed = False
    for section, key, value in args.assignments:
        changed = set_option(lines, section, key, value) or changed

    if changed:
        args.file.write_text("".join(lines), encoding="utf-8")

    print(f"changed: {str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
