"""Tests for the static generated-wrapper validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_wrapper.py"
SPEC = importlib.util.spec_from_file_location("check_wrapper", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECK_WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_WRAPPER)


VALID_SOURCE = '''
from idaes_fi.structfs.fsrunner import FlowsheetRunner

FS = FlowsheetRunner(steps=("build", "set_solver"))

@FS.step("build")
def build(context):
    pass

@FS.step("set_solver")
def set_solver(context):
    pass

def helper():
    pass

if __name__ == "__main__":
    FS.run_steps()
'''


class WrapperValidationTests(unittest.TestCase):
    def validate(self, source: str) -> None:
        CHECK_WRAPPER.validate_source(
            source,
            "generated.py",
            {"build", "set_solver"},
        )

    def test_accepts_consistent_wrapper(self):
        self.validate(VALID_SOURCE)

    def test_rejects_bare_runner(self):
        source = VALID_SOURCE.replace(
            'FlowsheetRunner(steps=("build", "set_solver"))',
            "FlowsheetRunner()",
        )
        with self.assertRaisesRegex(
            CHECK_WRAPPER.WrapperValidationError,
            "explicit steps",
        ):
            self.validate(source)

    def test_rejects_missing_decorated_step(self):
        source = VALID_SOURCE.replace(
            '(steps=("build", "set_solver"))',
            '(steps=("build",))',
        )
        with self.assertRaisesRegex(
            CHECK_WRAPPER.WrapperValidationError,
            "missing from runner",
        ):
            self.validate(source)

    def test_rejects_invalid_step_name(self):
        source = VALID_SOURCE.replace("set_solver", "made_up_step")
        with self.assertRaisesRegex(
            CHECK_WRAPPER.WrapperValidationError,
            "Invalid Inspector step",
        ):
            self.validate(source)

    def test_rejects_missing_main_call(self):
        source = VALID_SOURCE.replace("    FS.run_steps()", "    pass")
        with self.assertRaisesRegex(
            CHECK_WRAPPER.WrapperValidationError,
            "__main__ guard",
        ):
            self.validate(source)

if __name__ == "__main__":
    unittest.main()
