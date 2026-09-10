#####################################################################################################
# “PrOMMiS” was produced under the DOE Process Optimization and Modeling for Minerals Sustainability
# (“PrOMMiS”) initiative, and is copyright (c) 2023-2026 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory, et al. All rights reserved.
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license information.
#####################################################################################################

"""Tests for the canonical flowsheet creation helper."""

import ast
import importlib.util
from pathlib import Path

import pytest


SKILL_DIRECTORY = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIRECTORY / "scripts" / "create_flowsheet.py"

MODULE_SPEC = importlib.util.spec_from_file_location(
    "prommis_build_create_flowsheet",
    SCRIPT_PATH,
)

if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise ImportError(f"Unable to load flowsheet creation script: {SCRIPT_PATH}")

CREATE_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(CREATE_MODULE)

create_flowsheet = CREATE_MODULE.create_flowsheet
TEMPLATE_PATH = CREATE_MODULE.TEMPLATE_PATH


def test_create_flowsheet_copies_template_exactly(tmp_path):
    """The generated file must be an exact copy of the canonical template."""
    target = tmp_path / "new_directory" / "example_flowsheet.py"

    created = create_flowsheet(target)

    assert created == target.resolve()
    assert target.is_file()
    assert target.read_bytes() == TEMPLATE_PATH.read_bytes()


def test_create_flowsheet_requires_python_filename(tmp_path):
    """The target filename must use the .py extension."""
    target = tmp_path / "example_flowsheet.txt"

    with pytest.raises(ValueError, match=r"must end with \.py"):
        create_flowsheet(target)

    assert not target.exists()


def test_create_flowsheet_does_not_overwrite_by_default(tmp_path):
    """An existing file must remain unchanged unless replacement is requested."""
    target = tmp_path / "existing_flowsheet.py"
    original_content = "# Existing user content\n"
    target.write_text(original_content, encoding="utf-8")

    with pytest.raises(FileExistsError, match="already exists"):
        create_flowsheet(target)

    assert target.read_text(encoding="utf-8") == original_content


def test_create_flowsheet_can_replace_when_requested(tmp_path):
    """Explicit overwrite permission must replace the target with the template."""
    target = tmp_path / "existing_flowsheet.py"
    target.write_text("# Existing content\n", encoding="utf-8")

    created = create_flowsheet(target, overwrite=True)

    assert created == target.resolve()
    assert target.read_bytes() == TEMPLATE_PATH.read_bytes()

def test_template_activates_only_build():
    """Optional reusable phases must not impose a default execution order."""
    source = TEMPLATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions = set()
    decorated_steps = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        functions.add(node.name)

        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "step"
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
            ):
                decorated_steps.append(decorator.args[0].value)

    expected_helpers = {
        "set_solver",
        "set_operating_conditions",
        "set_scaling",
        "solve_initial",
        "set_autoscaling",
        "add_costing",
        "initialize_costing",
        "setup_optimization",
        "solve_optimization",
    }

    assert 'FS = FlowsheetRunner(steps=("build",))' in source
    assert decorated_steps == ["build"]
    assert expected_helpers <= functions