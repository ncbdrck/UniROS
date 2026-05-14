#!/usr/bin/env python3
"""Syntax-check Python code blocks in the Sphinx documentation.

Walks ``docs/**/*.rst``, extracts every ``.. code-block:: python``
block, and runs ``compile()`` on the contents. Reports
``SyntaxError``\\s with the file path and the (approximate) line
number where the block starts.

This is syntax-only: blocks that reference missing names, ROS
modules, Gazebo, hardware, etc. are fine because we never execute
them.

Opt-out mechanism: pseudo-code or intentionally schematic snippets
should use ``.. code-block:: text`` (or any non-``python`` lexer)
so this checker ignores them.

Exit code: 0 on success (every Python block compiles), 1 on any
failure.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Iterator, NamedTuple


CODE_BLOCK_RE = re.compile(
    r"^(?P<indent>[ \t]*)\.\.\s+code-block::\s*python\s*$",
    re.MULTILINE,
)


class Block(NamedTuple):
    path: pathlib.Path
    start_line: int  # 1-indexed line where `.. code-block:: python` directive sits
    code: str       # dedented Python source


def _iter_python_blocks(path: pathlib.Path) -> Iterator[Block]:
    """Yield every ``.. code-block:: python`` block in ``path``."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)

    i = 0
    n = len(lines)
    while i < n:
        m = CODE_BLOCK_RE.match(lines[i])
        if not m:
            i += 1
            continue

        directive_indent = len(m.group("indent").expandtabs(4))
        start_line = i + 1  # 1-indexed
        i += 1

        # Skip directive options + the mandatory blank line.
        while i < n and lines[i].strip() != "" and lines[i].lstrip().startswith(":"):
            i += 1
        while i < n and lines[i].strip() == "":
            i += 1

        # Collect indented body lines. The first non-blank body line
        # establishes the body indent (must be > directive indent).
        body_lines: list[str] = []
        body_indent: int | None = None
        while i < n:
            line = lines[i]
            if line.strip() == "":
                # Blank line: belongs to the block if we're still in it;
                # we'll decide when we see the next non-blank.
                body_lines.append("")
                i += 1
                continue
            line_indent = len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip())
            if body_indent is None:
                if line_indent <= directive_indent:
                    # No body — directive with empty content.
                    break
                body_indent = line_indent
            if line_indent < body_indent:
                # Block ended.
                break
            body_lines.append(line.expandtabs(4)[body_indent:])
            i += 1

        # Trim trailing blank lines we accumulated past the block end.
        while body_lines and body_lines[-1] == "":
            body_lines.pop()

        if body_lines:
            yield Block(path=path, start_line=start_line, code="\n".join(body_lines) + "\n")


def check(docs_root: pathlib.Path) -> list[tuple[Block, SyntaxError]]:
    """Return list of (block, error) for blocks that fail to compile."""
    failures: list[tuple[Block, SyntaxError]] = []
    for rst_path in sorted(docs_root.rglob("*.rst")):
        for block in _iter_python_blocks(rst_path):
            try:
                compile(block.code, f"{block.path}:{block.start_line}", "exec")
            except SyntaxError as exc:
                failures.append((block, exc))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "docs_root",
        nargs="?",
        default="docs",
        help="Path to the docs/ directory (default: docs)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="List every block that was checked, not just failures.",
    )
    args = parser.parse_args(argv)

    docs_root = pathlib.Path(args.docs_root).resolve()
    if not docs_root.is_dir():
        print(f"error: docs root not found: {docs_root}", file=sys.stderr)
        return 2

    failures = check(docs_root)

    if args.verbose:
        # Re-walk to count and list (cheap; we'd rather keep check() pure).
        total = sum(1 for rst in docs_root.rglob("*.rst") for _ in _iter_python_blocks(rst))
        print(f"checked {total} Python code block(s) under {docs_root}", file=sys.stderr)

    if not failures:
        print("OK: every Python code block in the docs compiles cleanly.")
        return 0

    print(f"FAIL: {len(failures)} Python code block(s) failed to compile:\n", file=sys.stderr)
    for block, exc in failures:
        rel = block.path.relative_to(docs_root.parent) if block.path.is_relative_to(docs_root.parent) else block.path
        # SyntaxError's lineno is relative to the start of the block; map back to the file.
        file_lineno = block.start_line + (exc.lineno or 0)
        print(f"  {rel}:{file_lineno}: {exc.msg}", file=sys.stderr)
        if exc.text:
            print(f"      {exc.text.rstrip()}", file=sys.stderr)
            if exc.offset:
                print(f"      {' ' * (exc.offset - 1)}^", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
