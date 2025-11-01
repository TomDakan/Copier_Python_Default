import subprocess
import sys
from pathlib import Path
from typing import List
import os


import pytest
from copier import run_copy
import copier.errors


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
    data = {**common_data,
            "task_runner": task_runner,
            "initialize_git": True,
            "push_to_github": False,}

    try:
        run_copy(
            root_path,
            destination_path,
            data=data,
            vcs_ref="HEAD",
            defaults=True,
            skip_tasks=False,
            unsafe=True,
        )
    except copier.errors.TaskError as e:
        # This block catches the failure and prints the script's output
        print("\n--- [Copier TaskError STDOUT] ---")
        # Corrected: access e.stdout directly
        if e.stdout:
            # Output can be bytes or string, so we handle both
            print(e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout)
        
        print("--- [Copier TaskError STDERR] ---")
        # Corrected: access e.stderr directly
        if e.stderr:
            print(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
        
        print("----------------------------------\n")
        raise  # Re-raise the exception to ensure the test still fails

    project_path = destination_path / common_data["project_slug"]

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

@pytest.mark.integration
def test_generated_project_github_creation(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Tests the full project generation *including* GitHub repo creation.
    This test requires live network access and 'gh' CLI auth.
    """
    # Use a unique subdir for this test run
    destination_path = tmp_path / "github_test_project"

    # --- Setup: Define repo name for creation and deletion ---
    # NOTE: You may need to add "github_account" to your 'common_data' fixture
    # For now, we'll get it from common_data or default to your username
    github_user = common_data.get("github_account", "TomDakan")
    project_slug = common_data["project_slug"]
    repo_name = f"{github_user}/{project_slug}"

    data = {**common_data,
            "task_runner": common_data.get("task_runner", "pdm"),
            "initialize_git": True,
            "push_to_github": True,  # <-- ENABLED for this test
            "github_account": github_user,
           }

    try:
        # --- 1. Run Copier with tasks enabled ---
        run_copy(
            root_path,
            destination_path,
            data=data,
            vcs_ref="HEAD",
            defaults=True,
            skip_tasks=False, # This runs bootstrap.py
            unsafe=True,
        )

        # --- 2. (Optional) Assert the repo was created ---
        project_path = destination_path / project_slug
        result = subprocess.run(
            ["gh", "repo", "view", repo_name],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        print(f"\nSuccessfully created test repo: {repo_name}")

    finally:
        # --- 3. Teardown: Delete the repo regardless of success ---
        print(f"\n--- Tearing down: Deleting repo {repo_name} ---")
        # Use --yes to skip the interactive confirmation prompt
        delete_result = subprocess.run(
            ["gh", "repo", "delete", repo_name, "--yes"],
            capture_output=True,
            text=True,
        )
        if delete_result.returncode != 0:
            # This prints a warning but doesn't fail the test
            print(f"Warning: Failed to delete repo {repo_name}.")
            print(delete_result.stderr)
        else:
            print(f"Successfully deleted test repo: {repo_name}")

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
