import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import copier.errors
import pytest
from copier import run_copy


def force_rmtree_onerror(func: Any, path: Any, exc_info: Any) -> None:
    """
    Error handler for shutil.rmtree that tries to
    remove read-only flags and retry the failed operation.
    """
    # exc_info[0] is the exception type
    if exc_info[0] is PermissionError:
        try:
            # Make the file writable and retry
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            # Re-raise the original error if retry fails
            raise exc_info[1] from e
    else:
        # Re-raise any other error
        raise exc_info[1]


# Helper to determine the correct task execution command
def get_run_command(task_runner: str, command: list[str]) -> list[str]:
    """Prefixes a command list with the correct task runner executable."""
    if task_runner == "just":
        # Assumes 'just' is in the system PATH
        # 'just' passes extra arguments, so we combine them
        return ["just", *command]
    else:
        # Default to PDM
        # We run 'pdm run' followed by the command
        return [sys.executable, "-m", "pdm", "run", *command]


def test_generated_project(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project and run its install, test, and lint commands.
    """
    destination_path = tmp_path

    # Get the task runner choice, defaulting to 'pdm' if not specified
    task_runner = common_data.get("task_runner", "pdm")
    data = {
        **common_data,
        "task_runner": task_runner,
        "initialize_git": True,
        "push_to_github": False,
    }

    try:
        run_copy(
            root_path,
            destination_path,
            data=data,
            vcs_ref="HEAD",
            defaults=True,
            skip_tasks=True,
            unsafe=True,
        )
    except copier.errors.TaskError as e:
        print(e.stdout)
        print(e.stderr)
        print("------------------------------------------\n")
        raise

    project_path = destination_path / common_data["project_slug"]

    # --- Run Tests ---
    # Use the alias 'test' defined in copier.yaml
    test_command = get_run_command(task_runner, ["test"])
    try:
        try:
            subprocess.run(
                [sys.executable, "-m", "pdm", "install", "-G", ":all"],
                cwd=project_path,
                check=True,
                timeout=300,
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

        subprocess.run(
            test_command,
            cwd=project_path,
            check=True,
            timeout=120,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PDM_CONFIG_use_uv": "false"},
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

    data = {
        **common_data,
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
            skip_tasks=False,  # This runs bootstrap.py
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


def test_generated_project_with_bandit(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project with bandit and run its security check.
    """
    task_runner = common_data.get("task_runner", "pdm")
    data = {
        **common_data,
        "task_runner": task_runner,
        "use_bandit": True,
        "use_safety": False,
    }
    destination_path = tmp_path / "generated_project_bandit"
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
        env={**os.environ, "SKIP": "pre-commit-hooks"},
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
            env={**os.environ, "PDM_CONFIG_use_uv": "false"},
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
            env={**os.environ, "PDM_CONFIG_use_uv": "false"},
        )
    except subprocess.CalledProcessError as e:
        print("\n--- [Inner PDM Install STDOUT] ---")
        print(e.stdout)
        print("--- [Inner PDM Install STDERR] ---")
        print(e.stderr)
        print("-------------------------------------------\n")
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


# @pytest.mark.skip(
#     reason="The 'safety' package does not yet support Python 3.13. Re-enable when it
#             does."
# )
def test_generated_project_with_safety(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Generate a project with safety and run its security check.
    """
    # Use a short, predictable path to avoid Windows MAX_PATH limit
    destination_path = Path("C:\\pytest-copier-test-safety")

    try:
        # --- 1. Setup Project ---
        task_runner = common_data.get("task_runner", "pdm")
        data = {
            **common_data,
            "task_runner": task_runner,
            "use_bandit": False,
            "use_safety": True,
        }

        # Clean up any previous failed runs, forcing deletion of .git files
        if destination_path.exists():
            shutil.rmtree(destination_path, onerror=force_rmtree_onerror)

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

        # --- 2. Initialize Git ---
        subprocess.run(["git", "init"], cwd=project_path, check=True, timeout=60)
        subprocess.run(["git", "add", "."], cwd=project_path, check=True, timeout=60)
        subprocess.run(
            ["git", "commit", "-m", "initial commit"],
            cwd=project_path,
            check=True,
            timeout=60,
            env={**os.environ, "SKIP": "pre-commit-hooks"},
        )

        # --- 3. Install Dependencies ---
        # We are intentionally letting this stream to stdout
        # by using capture_output=False for better debugging.
        try:
            subprocess.run(
                [sys.executable, "-m", "pdm", "install", "-vv"],
                cwd=project_path,
                check=True,
                timeout=300,
                capture_output=False,  # We want to see the output
                text=True,
                encoding="utf-8",
                # Removed env var to let PDM use default UV installer
            )
        except FileNotFoundError:  # pragma: no cover
            subprocess.run(
                ["pdm", "install", "-vv"],
                cwd=project_path,
                check=True,
                timeout=300,
                capture_output=False,
                text=True,
                encoding="utf-8",
                # Removed env var
            )
        except subprocess.CalledProcessError as e:
            print("\n--- [Inner PDM Install Failed] ---")
            # No stdout/stderr to print, as it streamed
            print(f"PDM install command failed with exit code {e.returncode}")
            print("-------------------------------------------\n")
            raise

        # --- 4. Run Safety Check ---
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

    finally:
        # --- 5. Cleanup ---
        # Ensure the test directory is removed on success or failure
        if destination_path.exists():
            print(f"\nCleaning up test directory: {destination_path}")
            shutil.rmtree(destination_path, onerror=force_rmtree_onerror)


def test_with_dependabot_automerge(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Tests that the dependabot.yml file is correctly generated with automerge.
    """
    # Test with automerge enabled
    data = {
        **common_data,
        "use_dependabot": True,
        "dependabot_automerge": True,
    }
    destination_path = tmp_path / "dependabot_automerge_true"
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
    dependabot_file = project_path / ".github" / "dependabot.yml"
    assert dependabot_file.is_file()
    with open(dependabot_file) as f:
        content = f.read()
        assert "automerge: true" in content

    # Test with dependabot disabled
    data = {
        **common_data,
        "use_dependabot": False,
    }
    destination_path = tmp_path / "dependabot_automerge_false"
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
    dependabot_file = project_path / ".github" / "dependabot.yml"
    assert not dependabot_file.exists()


def test_with_env_file(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Tests that the .env file is correctly generated.
    """
    # Test with .env file generation enabled
    data = {
        **common_data,
        "generate_env": True,
    }
    destination_path = tmp_path / "env_file_true"
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
    env_file = project_path / ".env"
    assert env_file.is_file()

    # Test with .env file generation disabled
    data = {
        **common_data,
        "generate_env": False,
    }
    destination_path = tmp_path / "env_file_false"
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
    env_file = project_path / ".env"
    assert not env_file.exists()


def test_with_adr_support(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Tests that the ADR files are correctly generated.
    """
    # Test with ADR support enabled
    data = {
        **common_data,
        "include_adr": True,
    }
    destination_path = tmp_path / "adr_support_true"
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
    adr_script = project_path / "scripts" / "new_adr.py"
    adr_template = project_path / "docs" / "adr" / "0000-template.md"
    assert adr_script.is_file()
    assert adr_template.is_file()

    # Test with ADR support disabled
    data = {
        **common_data,
        "include_adr": False,
    }
    destination_path = tmp_path / "adr_support_false"
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
    adr_script_path = project_path / "scripts"
    adr_script_file = adr_script_path / "new_adr.py"
    adr_docs_path = project_path / "docs" / "adr"
    assert not adr_script_file.exists()
    assert not adr_docs_path.exists()


def test_with_polish_files(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """
    Tests that the repository polish files are correctly generated.
    """
    # Test with polish files enabled
    data = {
        **common_data,
        "add_code_of_conduct": True,
        "add_security_md": True,
        "add_citation_cff": True,
    }
    destination_path = tmp_path / "polish_files_true"
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
    coc_file = project_path / "CODE_OF_CONDUCT.md"
    security_file = project_path / "SECURITY.md"
    citation_file = project_path / "CITATION.cff"
    assert coc_file.is_file()
    assert security_file.is_file()
    assert citation_file.is_file()

    # Test with polish files disabled
    data = {
        **common_data,
        "add_code_of_conduct": False,
        "add_security_md": False,
        "add_citation_cff": False,
    }
    destination_path = tmp_path / "polish_files_false"
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
    coc_file = project_path / "CODE_OF_CONDUCT.md"
    security_file = project_path / "SECURITY.md"
    citation_file = project_path / "CITATION.cff"
    assert not coc_file.exists()
    assert not security_file.exists()
    assert not citation_file.exists()
