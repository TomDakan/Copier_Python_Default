import subprocess
import sys
from pathlib import Path

from copier import run_copy


def test_generated_project(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project and run its install, test, and lint commands.
    """
    destination_path = tmp_path
    run_copy(
        root_path,
        destination_path,
        data=common_data,
        vcs_ref="HEAD",
        defaults=True,
        skip_tasks=True,
        unsafe=True,
    )

    project_path = destination_path / common_data["project_slug"]

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=project_path, check=True, timeout=60)

    # --- Install Dependencies ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "install"],
            cwd=project_path,
            check=True,
            timeout=300,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        # Fallback if pdm is not installed as a module, but on the PATH
        subprocess.run(
            ["pdm", "install"],
            cwd=project_path,
            check=True,
            timeout=300,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    # --- Run Tests ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "run", "pytest"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print("\n--- [Inner Pytest STDOUT] ---")
        print(e.stdout)
        print("--- [Inner Pytest STDERR] ---")
        print(e.stderr)
        print("-------------------------------\n")
        # Re-raise the exception to ensure the outer test still fails
        raise

    # --- Run Linter Check ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "run", "ruff", "check", "."],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    # --- Run Formatter Check ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "run", "ruff", "format", ".", "--check"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            [sys.executable, "-m", "ruff", "format", ".", "--check"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )


def test_generated_project_with_security_features(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project with security features and run its security checks.
    """
    common_data["use_safety"] = True
    common_data["use_bandit"] = True
    destination_path = tmp_path / "generated_project_security"
    run_copy(
        root_path,
        destination_path,
        data=common_data,
        vcs_ref="HEAD",
        defaults=True,
        skip_tasks=True,
    )

    project_path = destination_path / common_data["project_slug"]

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=project_path, check=True, timeout=60)

    # --- Install Dependencies ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "install"],
            cwd=project_path,
            check=True,
            timeout=300,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            ["pdm", "install"],
            cwd=project_path,
            check=True,
            timeout=300,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    # --- Run Safety Check ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "run", "safety-check"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            [sys.executable, "-m", "safety", "check"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    # --- Run Bandit Check ---
    try:
        subprocess.run(
            [sys.executable, "-m", "pdm", "run", "bandit-check"],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:  # pragma: no cover
        subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "."],
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
