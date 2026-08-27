"""Tests for import discovery and verification helpers."""

import importlib
import importlib.util
from pathlib import Path
import sys

import pytest


SKILL_DIR = Path(__file__).resolve().parents[1]


def load_script(module_name: str, script_name: str):
    """Load one skill script as a Python module."""
    script_path = SKILL_DIR / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GET_IMPORTS = load_script(
    "prommis_build_get_imports",
    "get_imports.py",
)

VERIFY_IMPORTS = load_script(
    "prommis_build_verify_imports",
    "verify_file_imports.py",
)


def test_discovers_public_configuration_object(tmp_path, monkeypatch):
    """Public module-level configuration objects can be discovered."""
    module_name = "pse_skill_public_configuration"
    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text(
        'thermo_config = {"components": ["example"]}\n',
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    GET_IMPORTS.import_quietly.cache_clear()

    try:
        result = GET_IMPORTS.inspect_module(
            module_name,
            "thermo_config",
        )
    finally:
        sys.modules.pop(module_name, None)
        GET_IMPORTS.import_quietly.cache_clear()

    assert result == (
        f"from {module_name} import thermo_config"
    )


def test_import_discovery_identifies_test_namespaces():
    """Test and fixture namespaces are classified as unsupported."""
    assert GET_IMPORTS.is_test_only_module(
        "example.tests.property_package"
    )
    assert GET_IMPORTS.is_test_only_module(
        "example.fixtures.model"
    )
    assert not GET_IMPORTS.is_test_only_module(
        "example.models.property_package"
    )


def test_verifier_accepts_public_import(tmp_path):
    """A public expected import is accepted."""
    target = tmp_path / "flowsheet.py"
    target.write_text(
        "from example.models import PublicModel\n",
        encoding="utf-8",
    )

    VERIFY_IMPORTS.verify_file_imports(
        target,
        [("example.models", "PublicModel")],
    )


def test_verifier_rejects_test_only_import(tmp_path):
    """A test-only dependency is rejected by default."""
    target = tmp_path / "flowsheet.py"
    target.write_text(
        "from example.tests.models import TestModel\n",
        encoding="utf-8",
    )

    with pytest.raises(
        VERIFY_IMPORTS.ImportVerificationError,
        match="test-only or fixture imports are not allowed",
    ):
        VERIFY_IMPORTS.verify_file_imports(
            target,
            [("example.tests.models", "TestModel")],
        )


def test_verifier_allows_explicit_test_dependency(tmp_path):
    """An explicitly accepted test dependency can be allowed."""
    target = tmp_path / "flowsheet.py"
    target.write_text(
        "from example.tests.models import TestModel\n",
        encoding="utf-8",
    )

    VERIFY_IMPORTS.verify_file_imports(
        target,
        [("example.tests.models", "TestModel")],
        allow_test_only=True,
    )