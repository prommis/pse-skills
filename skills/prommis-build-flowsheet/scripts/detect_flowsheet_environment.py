#!/usr/bin/env python3
#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""Find Python environments containing the modules required by a flowsheet.

The script checks the current Python and any supplied project interpreters
first. If none are compatible, it queries Conda once and checks the Python
executable in each reported environment.

It prints JSON to standard output. It does not create files, install packages,
activate environments, or modify configuration.

Examples:
    python detect_flowsheet_environment.py pyomo idaes idaes_fi
    python detect_flowsheet_environment.py pyomo idaes watertap idaes_fi
    python detect_flowsheet_environment.py pyomo idaes prommis idaes_fi
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


MODULE_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
)

PROBE_CODE = """
import importlib.util
import json
import sys

modules = json.loads(sys.argv[1])
missing = []

for module_name in modules:
    try:
        available = importlib.util.find_spec(module_name) is not None
    except Exception:
        available = False

    if not available:
        missing.append(module_name)

print(json.dumps({
    "python": sys.executable,
    "python_version": sys.version.split()[0],
    "missing_modules": missing,
}))
"""


def environment_python(environment: Path) -> Path:
    """Return the conventional Python executable inside an environment."""
    if os.name == "nt":
        return environment / "python.exe"
    return environment / "bin" / "python"


def normalize_python(value: str | Path) -> Path:
    """Normalize an interpreter path or environment directory."""
    path = Path(value).expanduser()

    if path.is_dir():
        path = environment_python(path)

    return path.resolve(strict=False)


def unique_candidates(candidates):
    """Remove duplicate interpreter paths while preserving order."""
    unique = []
    seen = set()

    for label, source, python in candidates:
        key = os.path.normcase(os.path.abspath(str(python)))
        if key in seen:
            continue

        seen.add(key)
        unique.append((label, source, python))

    return unique


def probe_candidate(candidate, modules, timeout):
    """Check whether one interpreter can locate every requested module."""
    label, source, python = candidate

    record = {
        "label": label,
        "source": source,
        "python": str(python),
    }

    if not python.is_file():
        record["error"] = "Python executable does not exist."
        return "failed", record

    creation_flags = 0
    if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        completed = subprocess.run(
            [
                str(python),
                "-c",
                PROBE_CODE,
                json.dumps(modules),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            creationflags=creation_flags,
        )
    except subprocess.TimeoutExpired:
        record["reason"] = "Environment check timed out."
        return "timed_out", record
    except OSError as error:
        record["error"] = str(error)
        return "failed", record

    if completed.returncode != 0:
        record["error"] = completed.stderr.strip() or "Environment check failed."
        return "failed", record

    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as error:
        record["error"] = f"Invalid environment-check output: {error}"
        return "failed", record

    record["python_version"] = payload.get("python_version")
    missing_modules = payload.get("missing_modules", [])

    if missing_modules:
        record["missing_modules"] = missing_modules
        return "missing", record

    return "compatible", record


def probe_candidates(candidates, modules, timeout, results):
    """Probe candidates concurrently."""
    if not candidates:
        return

    workers = min(16, len(candidates))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(probe_candidate, candidate, modules, timeout): candidate
            for candidate in candidates
        }

        for future in as_completed(futures):
            category, record = future.result()
            results[category].append(record)


def conda_candidates(timeout, results):
    """Query Conda once and return its environment interpreters."""
    conda = shutil.which("conda")

    if conda is None:
        results["notes"].append(
            "Conda was not found; only the current and supplied interpreters "
            "were checked."
        )
        return []

    try:
        completed = subprocess.run(
            [conda, "env", "list", "--json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        results["timed_out"].append(
            {
                "label": "Conda environment discovery",
                "source": "conda",
                "python": None,
                "reason": "Conda environment discovery timed out.",
            }
        )
        return []
    except OSError as error:
        results["failed"].append(
            {
                "label": "Conda environment discovery",
                "source": "conda",
                "python": None,
                "error": str(error),
            }
        )
        return []

    if completed.returncode != 0:
        results["failed"].append(
            {
                "label": "Conda environment discovery",
                "source": "conda",
                "python": None,
                "error": completed.stderr.strip() or "Conda query failed.",
            }
        )
        return []

    try:
        environment_paths = json.loads(completed.stdout).get("envs", [])
    except json.JSONDecodeError as error:
        results["failed"].append(
            {
                "label": "Conda environment discovery",
                "source": "conda",
                "python": None,
                "error": f"Conda returned invalid JSON: {error}",
            }
        )
        return []

    candidates = []

    for value in environment_paths:
        environment = Path(value).expanduser().resolve(strict=False)
        candidates.append(
            (
                f"conda:{environment.name}",
                "conda",
                environment_python(environment),
            )
        )

    return unique_candidates(candidates)


def build_parser():
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Find Python environments containing required modules."
    )
    parser.add_argument(
        "modules",
        nargs="+",
        help="Required top-level Python module names.",
    )
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        metavar="PYTHON",
        help="Optional project interpreter or environment directory.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Timeout for each environment check. Default: 5 seconds.",
    )
    return parser


def main(argv=None):
    """Run environment discovery and print the result as JSON."""
    arguments = build_parser().parse_args(argv)

    invalid_modules = [
        name for name in arguments.modules if not MODULE_PATTERN.fullmatch(name)
    ]
    if invalid_modules:
        raise SystemExit(f"Invalid module names: {invalid_modules}")

    modules = list(dict.fromkeys(arguments.modules))

    results = {
        "required_modules": modules,
        "searched_conda": False,
        "compatible": [],
        "missing": [],
        "failed": [],
        "timed_out": [],
        "notes": [],
    }

    primary_candidates = [
        ("current", "current", normalize_python(sys.executable))
    ]

    for index, value in enumerate(arguments.candidate, start=1):
        primary_candidates.append(
            (
                f"project-candidate-{index}",
                "project",
                normalize_python(value),
            )
        )

    primary_candidates = unique_candidates(primary_candidates)

    probe_candidates(
        primary_candidates,
        modules,
        arguments.timeout,
        results,
    )

    if not results["compatible"]:
        results["searched_conda"] = True
        discovered = conda_candidates(arguments.timeout, results)

        primary_paths = {
            os.path.normcase(os.path.abspath(str(candidate[2])))
            for candidate in primary_candidates
        }
        discovered = [
            candidate
            for candidate in discovered
            if os.path.normcase(os.path.abspath(str(candidate[2])))
            not in primary_paths
        ]

        probe_candidates(
            discovered,
            modules,
            arguments.timeout,
            results,
        )

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())