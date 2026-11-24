#!/usr/bin/env python3
"""Read-only RAILGUN Markdown structure and relative-link audit.

Run from repository root:
    python3 -B RAILGUN/scripts/check_documentation.py
"""

import argparse
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"(?<!!)\[([^]\n]*)\]\(([^)\n]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def inventory(root, supplied=None):
    if supplied is not None:
        data = json.loads(supplied.read_text(encoding="utf-8"))
        return set(data.get("tracked_paths", []))
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Git tracked-file inventory unavailable")
    return {
        path.decode("utf-8")
        for path in result.stdout.split(b"\0") if path
    }


def audit(root, tracked):
    problems = []
    checked_links = 0
    checked_files = 0

    for path in sorted((root / "RAILGUN").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        checked_files += 1
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        if not text.endswith("\n"):
            problems.append(f"{rel}: missing final newline")

        if any(line.rstrip(" \t") != line for line in lines):
            problems.append(f"{rel}: trailing whitespace")

        headings = []
        in_fence = False
        fence_char = ""
        fence_len = 0
        visible_lines = []

        for n, line in enumerate(lines, 1):
            fence = FENCE.match(line)
            if fence:
                mark = fence.group(1)
                if not in_fence:
                    in_fence = True
                    fence_char = mark[0]
                    fence_len = len(mark)
                elif mark[0] == fence_char and len(mark) >= fence_len:
                    in_fence = False
                continue
            if in_fence:
                continue
            visible_lines.append(line)
            heading = HEADING.match(line)
            if heading:
                headings.append((n, len(heading.group(1))))

        if in_fence:
            problems.append(f"{rel}: unclosed fenced code block")
        if sum(level == 1 for _, level in headings) != 1:
            problems.append(f"{rel}: expected exactly one H1")
        for prev, curr in zip(headings, headings[1:]):
            if curr[1] > prev[1] + 1:
                problems.append(f"{rel}:{curr[0]}: heading-level jump")

        # Links in prose only; fenced examples are not navigation.
        visible = "\n".join(visible_lines)
        for match in LINK.finditer(visible):
            uri = match.group(2).split(" ")[0].strip("<>")
            if uri.startswith(("#", "http:", "https:", "mailto:", "data:")):
                continue
            uri = unquote(uri).split("#", 1)[0].split("?", 1)[0]
            if not uri:
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(rel), uri)
            )
            checked_links += 1
            if not (
                target in tracked
                or any(x.startswith(target.rstrip("/") + "/") for x in tracked)
            ):
                problems.append(f"{rel}: unresolved relative link {uri}")

    return problems, checked_files, checked_links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args()
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    tracked = inventory(root, args.inventory)
    problems, files, links = audit(root, tracked)
    print(f"RAILGUN_MARKDOWN_FILES: {files}")
    print(f"RELATIVE_LINKS_CHECKED: {links}")
    for problem in problems:
        print("FAIL:", problem)
    print("DOC_STYLE_CHECK:", "PASS" if not problems else "FAIL")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
