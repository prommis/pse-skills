#!/usr/bin/env python3
#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""
Find import statements for classes or functions in installed packages.

With no --package arguments, search the supported process-modeling package
families. Callers can provide one or more --package arguments to limit or
extend the search.

Usage:
    python get_imports.py SYMBOL
    python get_imports.py SYMBOL --package PACKAGE
    python get_imports.py SYMBOL --package PACKAGE --package PACKAGE
"""

from __future__ import annotations

import argparse
import contextlib
from functools import lru_cache
import importlib
import inspect
import io
import logging
import pkgutil
from collections.abc import Sequence
import warnings


DEFAULT_PACKAGE_ROOTS = (
    "prommis",
    "idaes",
    "watertap",
    "pyomo",
    "idaes_fi",
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


def is_supported_symbol(obj: object) -> bool:
    """Return whether an object is an importable class or function."""
    return inspect.isclass(obj) or inspect.isfunction(obj)


def get_preferred_import(
    symbol_name: str,
    defining_module: str,
    target_object: object,
) -> str:
    """Return the shortest parent module that exports the same object."""
    parts = defining_module.split(".")

    for length in range(1, len(parts) + 1):
        module_path = ".".join(parts[:length])

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
    """Return an import when a module defines the requested symbol."""
    try:
        module = import_quietly(module_name)
    except Exception:
        return None

    if not hasattr(module, symbol_name):
        return None

    obj = getattr(module, symbol_name)

    if not is_supported_symbol(obj):
        return None

    defining_module = getattr(obj, "__module__", None)

    if not defining_module or defining_module != module_name:
        return None

    return get_preferred_import(
        symbol_name=symbol_name,
        defining_module=defining_module,
        target_object=obj,
    )


def search_package(
    package_name: str,
    symbol_name: str,
) -> list[str]:
    """Search one installed package for a class or function."""
    try:
        package = import_quietly(package_name)
    except Exception:
        return []

    package_path = getattr(package, "__path__", None)

    if package_path is None:
        return []

    matches: list[str] = []

    root_match = inspect_module(package_name, symbol_name)
    if root_match is not None:
        matches.append(root_match)

    modules = walk_modules_quietly(
        package_path=package_path,
        prefix=package_name + ".",
    )

    for module_info in modules:
        module_name = module_info.name

        if "tests" in module_name.split("."):
            continue

        match = inspect_module(module_name, symbol_name)

        if match is not None and match not in matches:
            matches.append(match)

    return matches


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Find import paths for an installed class or function."
    )
    parser.add_argument(
        "symbol_name",
        help="Exact, case-sensitive class or function name to locate",
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
    symbol_name: str,
    packages: Sequence[str],
) -> list[str]:
    """Search package roots and return unique import statements."""
    matches: list[str] = []

    for package_name in packages:
        for match in search_package(package_name, symbol_name):
            if match not in matches:
                matches.append(match)

    return matches


def main(argv: Sequence[str] | None = None) -> int:
    """Run the import search."""
    args = build_parser().parse_args(argv)

    packages = args.packages or list(DEFAULT_PACKAGE_ROOTS)
    packages = list(dict.fromkeys(packages))

    matches = find_imports(
        symbol_name=args.symbol_name,
        packages=packages,
    )

    if not matches:
        print(f"No match found for '{args.symbol_name}'.")
        print("Searched package roots:")

        for package_name in packages:
            print(f"  - {package_name}")

        return 1

    if len(matches) == 1:
        print("Found 1 match:")
        print()
        print(matches[0])
        return 0

    print(f"Found {len(matches)} matches:")
    print()

    for index, match in enumerate(matches, start=1):
        print(f"  {index}. {match}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())