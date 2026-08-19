#!/usr/bin/env python3
#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""
Search for a class in prommis, idaes, pyomo, and idaes_fi and return
the correct import statement.

Usage:
    python get_imports.py <class_name>

Examples:
    python get_imports.py LeachingTrain
    python get_imports.py FlowsheetBlock
    python get_imports.py FlowsheetRunner

This script is designed to be run directly by an agent in a compatible
Python environment. It does not ask the user to run anything manually.
"""

import contextlib
import importlib
import inspect
import io
import logging
import pkgutil
import sys
import warnings


warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)


PACKAGES_TO_SEARCH = ["prommis", "idaes", "pyomo", "idaes_fi"]


def import_quietly(module_name: str):
    """Import a module without exposing warnings or logging noise."""
    output = io.StringIO()
    logging.disable(logging.CRITICAL)

    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return importlib.import_module(module_name)
    finally:
        logging.disable(logging.CRITICAL)


def walk_modules_quietly(package_path, prefix):
    """Discover package modules without exposing import noise."""
    output = io.StringIO()
    logging.disable(logging.CRITICAL)

    try:
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
    finally:
        logging.disable(logging.CRITICAL)


def get_preferred_import(class_name: str, deep_module: str) -> str:
    """
    Return the shortest module path that exposes the requested class.

    Example:
    Arc is defined in pyomo.network.arc but is also available from
    pyomo.network, so the preferred import is:

        from pyomo.network import Arc
    """
    parts = deep_module.split(".")

    for index in range(len(parts) - 1, 0, -1):
        shorter_path = ".".join(parts[:index])

        try:
            module = import_quietly(shorter_path)

            if hasattr(module, class_name):
                obj = getattr(module, class_name)

                if inspect.isclass(obj) and obj.__name__ == class_name:
                    return f"from {shorter_path} import {class_name}"
        except Exception:
            continue

    return f"from {deep_module} import {class_name}"


def search_package(package_name: str, class_name: str) -> list[str]:
    """Search one installed package for the requested class."""
    matches = []

    try:
        package = import_quietly(package_name)
    except Exception:
        return []

    package_path = getattr(package, "__path__", None)

    if package_path is None:
        return []

    modules = walk_modules_quietly(
        package_path=package_path,
        prefix=package_name + ".",
    )

    for _, module_name, _ in modules:
        if ".tests." in module_name or module_name.endswith(".tests"):
            continue

        try:
            module = import_quietly(module_name)
        except Exception:
            continue

        try:
            if hasattr(module, class_name):
                obj = getattr(module, class_name)

                if inspect.isclass(obj) and obj.__module__ == module_name:
                    preferred = get_preferred_import(class_name, module_name)

                    if preferred not in matches:
                        matches.append(preferred)
        except Exception:
            continue

    return matches


def main():
    if len(sys.argv) < 2:
        print("Usage: python get_imports.py <class_name>")
        print("Example: python get_imports.py LeachingTrain")
        sys.exit(1)

    class_name = sys.argv[1]
    all_matches = []

    for package_name in PACKAGES_TO_SEARCH:
        matches = search_package(package_name, class_name)
        all_matches.extend(matches)

    seen = set()
    unique_matches = []

    for match in all_matches:
        if match not in seen:
            seen.add(match)
            unique_matches.append(match)

    if not unique_matches:
        print(f"No match found for '{class_name}'.")
        print("Check that:")
        print("  1. The class name is spelled correctly")
        print("  2. A compatible Python environment is active")
        print("  3. The required package is installed")
        sys.exit(1)

    if len(unique_matches) == 1:
        print("Found 1 match:")
        print()
        print(unique_matches[0])
    else:
        print(f"Found {len(unique_matches)} matches:")
        print()

        for index, match in enumerate(unique_matches, 1):
            print(f"  {index}. {match}")

    sys.exit(0)


if __name__ == "__main__":
    main()