#!/usr/bin/env python3
#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""
Find import statements for public symbols in installed packages.

This includes classes, functions, and public module-level configuration
objects. Test and fixture namespaces are excluded.

With no --package arguments, search the supported process-modeling package
families. Callers can provide one or more --package arguments to limit or
extend the search.

Accepts one or more symbol names in a single call. Each installed package
root is walked only once per invocation, regardless of how many symbols are
requested, so multiple related lookups should be batched into one call
instead of one process per symbol.

Usage:
    python get_imports.py SYMBOL
    python get_imports.py SYMBOL_A SYMBOL_B SYMBOL_C
    python get_imports.py SYMBOL --package PACKAGE
    python get_imports.py SYMBOL --package PACKAGE --package PACKAGE
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import contextlib
from functools import lru_cache
import importlib
import inspect
import io
import logging
import pkgutil
import warnings


DEFAULT_PACKAGE_ROOTS = (
    "prommis",
    "idaes",
    "watertap",
    "pyomo",
    "idaes_fi",
)

TEST_ONLY_SEGMENTS = {
    "test",
    "tests",
    "testing",
    "fixture",
    "fixtures",
}


def is_test_only_module(module_name: str) -> bool:
    """Return whether a module belongs to a test or fixture namespace."""
    return any(
        segment.lower() in TEST_ONLY_SEGMENTS
        or segment.lower().startswith("test_")
        for segment in module_name.split(".")
    )


warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)


@lru_cache(maxsize=None)
def import_quietly(module_name: str):
    """Import a module while suppressing terminal output and warnings."""
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return importlib.import_module(module_name)


def walk_modules_quietly(package_path, prefix: str):
    """Discover modules below a package without exposing discovery noise."""
    output = io.StringIO()

    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return list(
                pkgutil.walk_packages(
                    path=package_path,
                    prefix=prefix,
                    onerror=lambda _name: None,
                )
            )


def get_preferred_import(
    symbol_name: str,
    defining_module: str,
    target_object: object,
) -> str:
    """Return the shortest parent module that exports the same object."""
    parts = defining_module.split(".")

    for length in range(1, len(parts) + 1):
        module_path = ".".join(parts[:length])

        if is_test_only_module(module_path):
            continue

        try:
            module = import_quietly(module_path)
        except Exception:
            continue

        if not hasattr(module, symbol_name):
            continue

        exported_object = getattr(module, symbol_name)

        if exported_object is target_object:
            return f"from {module_path} import {symbol_name}"

    return f"from {defining_module} import {symbol_name}"


def inspect_module(
    module_name: str,
    symbol_name: str,
) -> str | None:
    """Return an import when a module publicly exposes the requested symbol."""
    if is_test_only_module(module_name) or symbol_name.startswith("_"):
        return None

    try:
        module = import_quietly(module_name)
    except Exception:
        return None

    if not hasattr(module, symbol_name):
        return None

    obj = getattr(module, symbol_name)

    if inspect.ismodule(obj):
        return None

    if inspect.isclass(obj) or inspect.isfunction(obj):
        defining_module = getattr(obj, "__module__", None)

        if not defining_module or defining_module != module_name:
            return None

        return get_preferred_import(
            symbol_name=symbol_name,
            defining_module=defining_module,
            target_object=obj,
        )

    # Public module-level configuration objects are also importable.
    return f"from {module_name} import {symbol_name}"


def search_package(
    package_name: str,
    symbol_names: Sequence[str],
) -> dict[str, list[str]]:
    """Search one installed package for multiple public symbols in a single walk."""
    results: dict[str, list[str]] = {name: [] for name in symbol_names}

    try:
        package = import_quietly(package_name)
    except Exception:
        return results

    package_path = getattr(package, "__path__", None)

    if package_path is None:
        return results

    for symbol_name in symbol_names:
        root_match = inspect_module(package_name, symbol_name)
        if root_match is not None:
            results[symbol_name].append(root_match)

    modules = walk_modules_quietly(
        package_path=package_path,
        prefix=package_name + ".",
    )

    for module_info in modules:
        module_name = module_info.name

        if is_test_only_module(module_name):
            continue

        for symbol_name in symbol_names:
            match = inspect_module(module_name, symbol_name)
            if match is not None and match not in results[symbol_name]:
                results[symbol_name].append(match)

    return results


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Find import paths for one or more installed public symbols."
    )
    parser.add_argument(
        "symbol_names",
        nargs="+",
        help="One or more exact, case-sensitive public symbol names to locate",
    )
    parser.add_argument(
        "--package",
        dest="packages",
        action="append",
        help=(
            "Top-level package to search. Repeat to search multiple packages. "
            "When omitted, the supported process-modeling packages are searched."
        ),
    )
    return parser


def find_imports(
    symbol_names: Sequence[str],
    packages: Sequence[str],
) -> dict[str, list[str]]:
    """Search package roots and return unique import statements per symbol."""
    results: dict[str, list[str]] = {name: [] for name in symbol_names}

    for package_name in packages:
        package_matches = search_package(package_name, symbol_names)
        for symbol_name, matches in package_matches.items():
            for match in matches:
                if match not in results[symbol_name]:
                    results[symbol_name].append(match)

    return results


def main(argv: Sequence[str] | None = None) -> int:
    """Run the import search."""
    args = build_parser().parse_args(argv)

    packages = args.packages or list(DEFAULT_PACKAGE_ROOTS)
    packages = list(dict.fromkeys(packages))

    symbol_names = list(dict.fromkeys(args.symbol_names))

    results = find_imports(
        symbol_names=symbol_names,
        packages=packages,
    )

    exit_code = 0

    for symbol_name in symbol_names:
        matches = results[symbol_name]
        print(f"## {symbol_name}")

        if not matches:
            print(f"No match found for '{symbol_name}'.")
            exit_code = 1
        elif len(matches) == 1:
            print("Found 1 match:")
            print(matches[0])
        else:
            print(f"Found {len(matches)} matches:")
            for index, match in enumerate(matches, start=1):
                print(f"  {index}. {match}")

        print()

    if exit_code:
        print("Searched package roots:")
        for package_name in packages:
            print(f"  - {package_name}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())