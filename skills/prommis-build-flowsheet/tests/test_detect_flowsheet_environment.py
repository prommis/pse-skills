#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "detect_flowsheet_environment.py"
)

MODULE_SPEC = importlib.util.spec_from_file_location(
    "prommis_build_environment_detector",
    SCRIPT,
)

if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise ImportError(f"Unable to load environment detector: {SCRIPT}")

DETECTOR_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(DETECTOR_MODULE)

def run_script(*arguments, env=None):
    """Run the environment detector using the current test interpreter."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(value) for value in arguments)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def read_result(completed):
    """Parse the script's JSON output."""
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_detects_compatible_current_python():
    completed = run_script("json")
    result = read_result(completed)

    assert result["searched_conda"] is False
    assert any(
        candidate["source"] == "current"
        for candidate in result["compatible"]
    )


def test_reports_missing_module_when_conda_is_unavailable():
    environment = os.environ.copy()
    environment["PATH"] = ""

    completed = run_script(
        "pse_skill_module_that_should_not_exist_91f21d",
        env=environment,
    )
    result = read_result(completed)

    assert result["searched_conda"] is True
    assert any(
        "pse_skill_module_that_should_not_exist_91f21d"
        in candidate.get("missing_modules", [])
        for candidate in result["missing"]
    )


def test_reports_invalid_project_candidate(tmp_path):
    missing_python = tmp_path / "missing-python"

    completed = run_script(
        "json",
        "--candidate",
        missing_python,
    )
    result = read_result(completed)

    assert any(
        candidate["source"] == "project"
        and candidate["python"] == str(missing_python.resolve())
        for candidate in result["failed"]
    )


def test_rejects_invalid_module_name():
    completed = run_script("not-a-valid-module-name")

    assert completed.returncode != 0
    assert "Invalid module names" in completed.stderr

def test_uses_separate_conda_discovery_timeout(monkeypatch):
    """Conda listing must not use the shorter Python-probe timeout."""
    observed = {}

    def fake_probe_candidates(candidates, modules, timeout, results):
        if candidates:
            results["missing"].append(
                {
                    "label": "current",
                    "source": "current",
                    "python": str(sys.executable),
                    "missing_modules": list(modules),
                }
            )

    def fake_conda_candidates(timeout, results):
        observed["timeout"] = timeout
        return []

    monkeypatch.setattr(
        DETECTOR_MODULE,
        "probe_candidates",
        fake_probe_candidates,
    )
    monkeypatch.setattr(
        DETECTOR_MODULE,
        "conda_candidates",
        fake_conda_candidates,
    )

    result = DETECTOR_MODULE.main(
        [
            "pse_skill_missing_test_module",
            "--timeout",
            "5",
            "--conda-timeout",
            "20",
        ]
    )

    assert result == 0
    assert observed["timeout"] == 20