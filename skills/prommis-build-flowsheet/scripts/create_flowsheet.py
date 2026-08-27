"""Copy the canonical wrapped flowsheet template to a new file."""

import argparse
from pathlib import Path
import shutil


TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "flowsheet_template.py"
)


def create_flowsheet(target: Path, overwrite: bool = False) -> Path:
    """Create a flowsheet file from the canonical template."""
    target = target.resolve()

    if target.suffix.lower() != ".py":
        raise ValueError("The target filename must end with .py")

    if target.exists() and not overwrite:
        raise FileExistsError(
            f"{target} already exists. Use --force to replace it."
        )

    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(
            f"Canonical template not found: {TEMPLATE_PATH}"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE_PATH, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a wrapped IDAES/PrOMMiS/WaterTAP flowsheet."
    )
    parser.add_argument("target", type=Path, help="New .py flowsheet file")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the target if it already exists",
    )
    args = parser.parse_args()

    created = create_flowsheet(args.target, overwrite=args.force)
    print(f"Created flowsheet: {created}")


if __name__ == "__main__":
    main()