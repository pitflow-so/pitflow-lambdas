import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
TERRAFORM_DIR = ROOT_DIR / "infra" / "terraform"
BUILD_DIR = TERRAFORM_DIR / ".build"
ARTIFACTS_DIR = TERRAFORM_DIR / "artifacts"


def main() -> None:
    clean_dir(BUILD_DIR)
    clean_dir(ARTIFACTS_DIR)

    build_layer()
    zip_directory(ROOT_DIR / "lambdas" / "auth" / "src", ARTIFACTS_DIR / "pitflow-auth.zip")
    zip_directory(ROOT_DIR / "lambdas" / "budget_form" / "src", ARTIFACTS_DIR / "pitflow-budget-form.zip")


def build_layer() -> None:
    layer_source_dir = ROOT_DIR / "layers" / "shared"
    layer_build_dir = BUILD_DIR / "layer"
    python_build_dir = layer_build_dir / "python"

    python_build_dir.mkdir(parents=True)

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(layer_source_dir / "requirements.txt"),
            "-t",
            str(python_build_dir),
        ]
    )

    shutil.copytree(
        layer_source_dir / "python" / "pitflow_shared",
        python_build_dir / "pitflow_shared",
    )

    zip_directory(layer_build_dir, ARTIFACTS_DIR / "pitflow-shared-layer.zip")


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def zip_directory(source_dir: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_dir))


if __name__ == "__main__":
    main()
