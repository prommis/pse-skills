import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


def run_script(script: Path, *arguments: object, cwd: Path):
    return subprocess.run(
        [sys.executable, str(script), *(str(argument) for argument in arguments)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_installed_skill_contains_required_resources():
    required_paths = (
        "SKILL.md",
        "agents/openai.yaml",
        "assets/flowsheet_template.py",
        "scripts/create_flowsheet.py",
        "scripts/check_wrapper.py",
        "scripts/detect_flowsheet_environment.py",
        "scripts/get_imports.py",
        "scripts/verify_file_imports.py",
        "references/model-discovery.md",
        "references/wrapper-integrity.md",
        "references/recycle-building.md",
        "references/validation.md",
    )

    missing = [
        relative_path
        for relative_path in required_paths
        if not (SKILL_DIR / relative_path).is_file()
    ]

    assert not missing, f"Missing required skill resources: {missing}"


def test_installed_skill_can_create_and_check_a_flowsheet(tmp_path):
    installed_skill = tmp_path / "installed-skill"
    shutil.copytree(SKILL_DIR, installed_skill)

    output_file = tmp_path / "project" / "desalination_flowsheet.py"
    create_script = installed_skill / "scripts" / "create_flowsheet.py"
    check_script = installed_skill / "scripts" / "check_wrapper.py"
    canonical_template = installed_skill / "assets" / "flowsheet_template.py"

    create_result = run_script(
        create_script,
        output_file,
        cwd=tmp_path,
    )

    assert create_result.returncode == 0, create_result.stderr
    assert output_file.is_file()
    assert output_file.read_bytes() == canonical_template.read_bytes()

    check_result = run_script(
        check_script,
        output_file,
        cwd=tmp_path,
    )

    assert check_result.returncode == 0, (
        check_result.stdout + check_result.stderr
    )