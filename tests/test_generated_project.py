import subprocess
import sys
from pathlib import Path
from typing import List
import os  # <-- 1. Add this import

import pytest
from copier import run_copy


# Helper to determine the correct task execution command
def get_run_command(task_runner: str, command: List[str]) -> List[str]:
    """Prefixes a command list with the correct task runner executable."""
    if task_runner == "just":
        # Assumes 'just' is in the system PATH
        # 'just' passes extra arguments, so we combine them
        return ["just"] + command
    else:
        # Default to PDM
        # We run 'pdm run' followed by the command
        return [sys.executable, "-m", "pdm", "run"] + command


def test_generated_project(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project and run its install, test, and lint commands.
    """
    destination_path = tmp_path

    # Get the task runner choice, defaulting to 'pdm' if not specified
    task_runner = common_data.get("task_runner", "pdm")
    data = {**common_data, "task_runner": task_runner}

    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,
        skip_tasks=True,
        unsafe=True,
    )

    project_path = destination_path / common_data["project_slug"]

    # Initialize git repository (required for pre-commit and others)
    subprocess.run(["git", "init"], cwd=project_path, check=True, timeout=60)
    subprocess.run(["git", "add", "."], cwd=project_path, check=True, timeout=60)
    subprocess.run(
        ["git", "commit", "-m", "initial commit"],
        cwd=project_path,
        check=True,
        timeout=60,
        # Bypassing pre-commit hooks for the initial test setup
        env={**os.environ, "SKIP": "pre-commit-hooks"},  # <-- 2. Fixed: os.environ
    )

    # --- Install Dependencies (Always PDM) ---
    # The task runner (just) is for *running scripts*, PDM is the *dependency manager*.
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

    # --- Run Tests ---
    # Use the alias 'test' defined in copier.yaml
    test_command = get_run_command(task_runner, ["test"])
    try:
        subprocess.run(
            test_command,
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
        raise

    # --- Run Linter Check (using format-check alias) ---
    # We use 'format-check' as it's the non-modifying lint task
    format_check_command = get_run_command(task_runner, ["format-check"])
    try:
        subprocess.run(
            format_check_command,
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print(f"\n--- [Inner Ruff Format STDOUT] ({' '.join(format_check_command)}) ---")
        print(e.stdout)
        print(f"--- [Inner Ruff Format STDERR] ({' '.join(format_check_command)}) ---")
        print(e.stderr)
        print("--------------------------------------------------\n")
        raise

    # --- Run Lint Check (using ruff check directly, as 'lint' alias fixes) ---
    # This checks for issues 'format' doesn't, without auto-fixing
    lint_check_command = get_run_command(task_runner, ["ruff", "check", "."])
    try:
        subprocess.run(
            lint_check_command,
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print(f"\n--- [Inner Ruff Lint STDOUT] ({' '.join(lint_check_command)}) ---")
        print(e.stdout)
        print(f"--- [Inner Ruff Lint STDERR] ({' '.join(lint_check_command)}) ---")
        print(e.stderr)
        print("------------------------------------------------\n")
        raise


def test_generated_project_with_security_features(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project with security features and run its security checks.
    """
    task_runner = common_data.get("task_runner", "pdm")
    data = {
        **common_data,
        "task_runner": task_runner,
        "use_safety": True,
        "use_bandit": True,
    }
    destination_path = tmp_path / "generated_project_security"
    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,
        skip_tasks=True,
        unsafe=True,
    )

    project_path = destination_path / common_data["project_slug"]

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=project_path, check=True, timeout=60)
    subprocess.run(["git", "add", "."], cwd=project_path, check=True, timeout=60)
    subprocess.run(
        ["git", "commit", "-m", "initial commit"],
        cwd=project_path,
        check=True,
        timeout=60,
        env={**os.environ, "SKIP": "pre-commit-hooks"},  # <-- 2. Fixed: os.environ
    )

    # --- Install Dependencies (Always PDM) ---
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
    safety_command = get_run_command(task_runner, ["safety-check"])
    try:
        subprocess.run(
            safety_command,
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print(f"\n--- [Inner Safety STDOUT] ({' '.join(safety_command)}) ---")
        print(e.stdout)
        print(f"--- [Inner Safety STDERR] ({' '.join(safety_command)}) ---")
        print(e.stderr)
        print("------------------------------------------\n")
        raise

    # --- Run Bandit Check ---
    bandit_command = get_run_command(task_runner, ["bandit-check"])
    try:
        subprocess.run(
            bandit_command,
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print(f"\n--- [Inner Bandit STDOUT] ({' '.join(bandit_command)}) ---")
        print(e.stdout)
        print(f"--- [Inner Bandit STDERR] ({' '.join(bandit_command)}) ---")
        print(e.stderr)
        print("-------------------------------------------\n")
        raise
