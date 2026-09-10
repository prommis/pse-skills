#!/usr/bin/env python3
"""Statically validate the FlowsheetRunner structure in a generated file."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence


class WrapperValidationError(ValueError):
    """Raised when a generated flowsheet violates wrapper invariants."""


def _is_name_main_test(node: ast.expr) -> bool:
    """Return whether node represents ``__name__ == "__main__"``."""
    if not isinstance(node, ast.Compare) or len(node.ops) != 1:
        return False
    if not isinstance(node.ops[0], ast.Eq) or len(node.comparators) != 1:
        return False

    values = (node.left, node.comparators[0])
    has_name = any(isinstance(value, ast.Name) and value.id == "__name__" for value in values)
    has_main = any(
        isinstance(value, ast.Constant) and value.value == "__main__"
        for value in values
    )
    return has_name and has_main


def _is_flowsheet_runner_call(node: ast.AST) -> bool:
    """Return whether node calls a name ending in FlowsheetRunner."""
    if not isinstance(node, ast.Call):
        return False
    function = node.func
    if isinstance(function, ast.Name):
        return function.id == "FlowsheetRunner"
    return isinstance(function, ast.Attribute) and function.attr == "FlowsheetRunner"


def _literal_steps(call: ast.Call) -> list[str]:
    """Extract the explicit string sequence supplied as ``steps=``."""
    keyword = next((item for item in call.keywords if item.arg == "steps"), None)
    if keyword is None:
        raise WrapperValidationError(
            "FlowsheetRunner must declare an explicit steps=(...) sequence"
        )
    if not isinstance(keyword.value, (ast.Tuple, ast.List)):
        raise WrapperValidationError("FlowsheetRunner steps must be a literal tuple or list")

    steps: list[str] = []
    for item in keyword.value.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            raise WrapperValidationError("Every FlowsheetRunner step must be a string literal")
        steps.append(item.value)
    return steps


def _decorated_steps(
    tree: ast.Module, runner_name: str
) -> list[tuple[str, str]]:
    """Return ``(step_name, function_name)`` pairs for one runner."""
    result: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            function = decorator.func
            if not (
                isinstance(function, ast.Attribute)
                and function.attr == "step"
                and isinstance(function.value, ast.Name)
                and function.value.id == runner_name
            ):
                continue
            if (
                len(decorator.args) != 1
                or not isinstance(decorator.args[0], ast.Constant)
                or not isinstance(decorator.args[0].value, str)
            ):
                raise WrapperValidationError(
                    f"Decorator on {node.name} must use one literal step name"
                )
            result.append((decorator.args[0].value, node.name))
    return result


def _main_runs_runner(tree: ast.Module, runner_name: str) -> bool:
    """Return whether the main guard calls ``runner.run_steps()``."""
    for node in tree.body:
        if not isinstance(node, ast.If) or not _is_name_main_test(node.test):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            function = child.func
            if (
                isinstance(function, ast.Attribute)
                and function.attr == "run_steps"
                and isinstance(function.value, ast.Name)
                and function.value.id == runner_name
            ):
                return True
    return False


def valid_step_names() -> set[str]:
    """Read valid step names from the installed ``fi-steps`` command."""
    executable = shutil.which("fi-steps")
    if executable is None:
        raise WrapperValidationError(
            "fi-steps was not found in the selected runtime environment"
        )
    result = subprocess.run(
        [executable, "--format", "text"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise WrapperValidationError("fi-steps could not provide valid step names")
    names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if not names:
        raise WrapperValidationError("fi-steps returned no valid step names")
    return names


def validate_source(source: str, filename: str, allowed_steps: set[str]) -> None:
    """Validate syntax and wrapper invariants without executing the file."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as error:
        location = f"line {error.lineno}" if error.lineno else "unknown line"
        raise WrapperValidationError(
            f"Python syntax error at {location}: {error.msg}"
        ) from error

    runners: list[tuple[str, ast.Call]] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None or not _is_flowsheet_runner_call(value):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                runners.append((target.id, value))

    if len(runners) != 1:
        raise WrapperValidationError(
            f"Expected exactly one FlowsheetRunner assignment; found {len(runners)}"
        )

    runner_name, runner_call = runners[0]
    runner_steps = _literal_steps(runner_call)
    decorated = _decorated_steps(tree, runner_name)
    decorated_names = [step for step, _function in decorated]

    duplicate_runner = sorted(
        name for name, count in Counter(runner_steps).items() if count > 1
    )
    duplicate_decorated = sorted(
        name for name, count in Counter(decorated_names).items() if count > 1
    )
    if duplicate_runner:
        raise WrapperValidationError(
            "Duplicate runner steps: " + ", ".join(duplicate_runner)
        )
    if duplicate_decorated:
        raise WrapperValidationError(
            "Duplicate decorated steps: " + ", ".join(duplicate_decorated)
        )

    invalid = sorted(set(decorated_names) - allowed_steps)
    if invalid:
        raise WrapperValidationError("Invalid Inspector step names: " + ", ".join(invalid))

    missing_from_runner = sorted(set(decorated_names) - set(runner_steps))
    missing_decorator = sorted(set(runner_steps) - set(decorated_names))
    if missing_from_runner:
        raise WrapperValidationError(
            "Decorated steps missing from runner sequence: "
            + ", ".join(missing_from_runner)
        )
    if missing_decorator:
        raise WrapperValidationError(
            "Runner entries without decorated functions: "
            + ", ".join(missing_decorator)
        )

    if not _main_runs_runner(tree, runner_name):
        raise WrapperValidationError(
            f'__main__ guard must call {runner_name}.run_steps()'
        )


def validate_file(path: Path) -> None:
    """Validate one UTF-8 Python flowsheet file."""
    if not path.is_file():
        raise WrapperValidationError(f"File not found: {path}")
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise WrapperValidationError(f"File is not valid UTF-8: {path}") from error
    validate_source(source, str(path), valid_step_names())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Statically validate a generated FlowsheetRunner wrapper."
    )
    parser.add_argument("file", type=Path, help="Generated Python flowsheet")
    args = parser.parse_args(argv)

    try:
        validate_file(args.file)
    except WrapperValidationError as error:
        print(f"Wrapper validation failed: {error}", file=sys.stderr)
        return 1

    print(f"Wrapper validation passed: {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
