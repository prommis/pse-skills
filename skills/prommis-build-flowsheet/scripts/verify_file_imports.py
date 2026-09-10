#!/usr/bin/env python3
#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""Verify imports in a generated Python flowsheet.

Usage:
    python verify_file_imports.py FILE MODULE SYMBOL [MODULE SYMBOL ...]

The target file is parsed but never executed, so this check cannot build or
solve a flowsheet as a side effect. Test and fixture imports are rejected
unless they were explicitly accepted.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from pathlib import Path
import sys
from typing import Sequence


TEST_ONLY_SEGMENTS = {
    "test",
    "tests",
    "testing",
    "fixture",
    "fixtures",
}


class ImportVerificationError(ValueError):
    """Raised when a file does not contain valid expected imports."""


def is_test_only_module(module_name: str) -> bool:
    """Return whether a module belongs to a test or fixture namespace."""
    return any(
        segment.lower() in TEST_ONLY_SEGMENTS
        or segment.lower().startswith("test_")
        for segment in module_name.split(".")
    )


def find_test_only_imports(tree: ast.Module) -> list[str]:
    """Return test or fixture module paths imported anywhere in the file."""
    found = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if is_test_only_module(node.module):
                found.add(node.module)

        elif isinstance(node, ast.Import):
            for imported_name in node.names:
                if is_test_only_module(imported_name.name):
                    found.add(imported_name.name)

    return sorted(found)


def verify_file_imports(
    file_path: str | Path,
    expected_imports: Sequence[tuple[str, str]],
    allow_test_only: bool = False,
) -> None:
    """Verify syntax, expected imports, and import provenance."""
    path = Path(file_path)

    if not path.is_file():
        raise ImportVerificationError(f"File not found: {path}")

    if not expected_imports:
        raise ImportVerificationError("At least one expected import is required.")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ImportVerificationError(
            f"File is not valid UTF-8: {path}"
        ) from error

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        location = (
            f"line {error.lineno}"
            if error.lineno is not None
            else "unknown line"
        )
        raise ImportVerificationError(
            f"Python syntax error in {path} at {location}: {error.msg}"
        ) from error

    test_only_imports = find_test_only_imports(tree)

    if test_only_imports and not allow_test_only:
        modules = ", ".join(test_only_imports)
        raise ImportVerificationError(
            f"test-only or fixture imports are not allowed: {modules}"
        )

    counts: Counter[tuple[str, str]] = Counter()

    for node in tree.body:
        if (
            not isinstance(node, ast.ImportFrom)
            or node.level != 0
            or node.module is None
        ):
            continue

        for imported_name in node.names:
            if imported_name.asname is None:
                counts[(node.module, imported_name.name)] += 1

    problems = []

    for module_name, symbol_name in expected_imports:
        count = counts[(module_name, symbol_name)]
        statement = f"from {module_name} import {symbol_name}"

        if count == 0:
            problems.append(f"missing: {statement}")
        elif count > 1:
            problems.append(
                f"duplicated {count} times: {statement}"
            )

    if problems:
        raise ImportVerificationError("; ".join(problems))


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Verify expected imports and reject test-only dependencies "
            "without executing the generated file."
        )
    )
    parser.add_argument(
        "file",
        help="Python file to inspect",
    )
    parser.add_argument(
        "expected",
        nargs="+",
        metavar="MODULE_OR_SYMBOL",
        help="One or more MODULE SYMBOL pairs",
    )
    parser.add_argument(
        "--allow-test-only",
        action="store_true",
        help=(
            "Allow test-only imports when the user explicitly accepted "
            "that dependency"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run import verification."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if len(args.expected) % 2:
        parser.error(
            "expected imports must be supplied as MODULE SYMBOL pairs"
        )

    expected_imports = list(
        zip(args.expected[::2], args.expected[1::2])
    )

    try:
        verify_file_imports(
            args.file,
            expected_imports,
            allow_test_only=args.allow_test_only,
        )
    except ImportVerificationError as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1

    print(f"Verified {len(expected_imports)} import(s) in {args.file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())