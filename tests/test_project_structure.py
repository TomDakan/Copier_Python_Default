import tomllib
from pathlib import Path

from copier import run_copy


def test_defaults(root_path: str, tmp_path: Path, common_data: dict[str, str]) -> None:
    destination_path = tmp_path / "generated_project"
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
    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / "src" / "test_project").exists()
    assert (project_path / "src" / "test_project" / "__init__.py").exists()
    assert (project_path / ".pre-commit-config.yaml").exists()
    assert (project_path / "tests").exists()
    assert (project_path / "src" / "test_project" / "py.typed").exists()

    # assert settings.py exists
    assert (project_path / "src" / "test_project" / "settings.py").exists()

    # parse pyproject.toml to check for dependencies
    content = (project_path / "pyproject.toml").read_text()
    toml_data = tomllib.loads(content)

    main_deps = toml_data.get("project", {}).get("dependencies", [])
    pdm_dev_deps_groups = (
        toml_data.get("tool", {}).get("pdm", {}).get("dev-dependencies", {})
    )
    dev_deps = pdm_dev_deps_groups.get("dev", [])  # Assuming your default group is 'dev'
    commitizen_config = toml_data.get("tool", {}).get("commitizen", {})

    # Check that CLI dependencies are NOT present by default
    assert "typer" not in main_deps
    assert "typer" not in dev_deps
    assert "rich" not in main_deps
    assert "rich" not in dev_deps

    # Check that conventional commits dependencies ARE present by default
    assert "commitizen" in dev_deps

    # Check that strict development dependencies are NOT present by default
    assert "safety" not in dev_deps
    assert "bandit" not in dev_deps
    assert "python-semantic-release" not in dev_deps

    # Check that project scripts section is NOT present by default
    assert "scripts" not in toml_data.get("project", {})

    # Check that commitizen config IS present by default
    assert "commitizen" in toml_data.get("tool", {})
    assert "bump_message" in toml_data.get("tool", {}).get("commitizen", {})
    assert "tag_format" in commitizen_config
    assert commitizen_config.get("update_changelog_on_bump") is True
    assert commitizen_config.get("version_provider") == "pep621"

    # Check that changelog file IS defined by default
    assert "changelog_file = " in content

    # Check that strict pytest options are NOT present by default
    assert "--strict-config" not in content
    assert "--strict-markers" not in content
    assert "--typeguard-packages=" not in content


def test_task_runner_pdm(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify pdm scripts are generated and justfile is absent when task_runner is pdm."""
    destination_path = tmp_path / "generated_project_pdm"
    data = {
        **common_data,
        "task_runner": "pdm",
        "use_safety": False,  # Ensure safety is off for this default check
        "use_bandit": False,  # Ensure bandit is off
        "doc_hosting_provider": "None",  # Ensure docs RTD is off
    }
    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,  # Allow defaults for unspecified vars
        skip_tasks=True,
        unsafe=True,
    )
    project_path = destination_path / common_data["project_slug"]

    # Assert justfile is NOT created
    assert not (project_path / "justfile").exists()

    # Assert pyproject.toml exists and contains pdm scripts
    pyproject_path = project_path / "pyproject.toml"
    assert pyproject_path.exists()
    content = pyproject_path.read_text()
    toml_data = tomllib.loads(content)

    pdm_scripts = toml_data.get("tool", {}).get("pdm", {}).get("scripts", {})
    assert pdm_scripts, "[tool.pdm.scripts] section not found in pyproject.toml"

    # Check for core scripts
    assert "lint" in pdm_scripts
    assert "test" in pdm_scripts
    assert "format" in pdm_scripts
    assert "type-check" in pdm_scripts
    assert "qa" in pdm_scripts  # Check the composite script exists

    # Check that optional scripts are NOT present by default
    assert "safety-check" not in pdm_scripts
    assert "bandit-check" not in pdm_scripts
    assert (
        "export-docs-reqs" not in pdm_scripts
    )  # Assuming use_docs=False or RTD=False in common_data defaults
    assert "adr" not in pdm_scripts  # Assuming include_adr=False in common_data defaults

    # Check composite 'qa' script definition
    qa_script = pdm_scripts.get("qa", {})
    assert "composite" in qa_script
    assert isinstance(qa_script["composite"], list)
    # Check default composite members
    expected_qa_default = ["format-check", "lint", "type-check", "test"]
    assert all(item in qa_script["composite"] for item in expected_qa_default)
    assert len(qa_script["composite"]) == len(expected_qa_default)  # Ensure no extras


def test_task_runner_just(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify justfile is generated and pdm scripts are absent when task_runner is just."""
    destination_path = tmp_path / "generated_project_just"
    data = {
        **common_data,
        "task_runner": "just",
        "use_safety": False,  # Ensure safety is off for this default check
        "use_bandit": False,  # Ensure bandit is off
    }
    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,  # Allow defaults for unspecified vars
        skip_tasks=True,
        unsafe=True,
    )
    project_path = destination_path / common_data["project_slug"]

    # Assert justfile IS created
    justfile_path = project_path / "justfile"
    assert justfile_path.exists()
    justfile_content = justfile_path.read_text()

    # Assert pyproject.toml does NOT contain pdm scripts
    pyproject_path = project_path / "pyproject.toml"
    assert pyproject_path.exists()
    pyproject_content = pyproject_path.read_text()
    toml_data = tomllib.loads(pyproject_content)
    assert "scripts" not in toml_data.get("tool", {}).get("pdm", {}), (
        "[tool.pdm.scripts] section unexpectedly found in pyproject.toml"
    )

    # Check for core script definitions in justfile (simple string checks)
    assert "lint *args:" in justfile_content
    assert "test *args:" in justfile_content
    assert "format *args:" in justfile_content
    assert "type-check *args:" in justfile_content
    assert "qa:" in justfile_content  # Composite scripts end with a colon

    # Check that optional script definitions are NOT present by default
    assert "safety-check *args:" not in justfile_content
    assert "bandit-check *args:" not in justfile_content
    assert "export-docs-reqs *args:" not in justfile_content
    assert "adr *args:" not in justfile_content

    # Check composite 'qa' script definition (look for dependencies)
    # This assumes 'qa:' is the line defining the composite task
    qa_line = next(
        (line for line in justfile_content.splitlines() if line.startswith("qa:")), None
    )
    assert qa_line is not None, "'qa:' definition not found in justfile"
    assert "@just format-check" in justfile_content
    assert "@just lint" in justfile_content
    assert "@just type-check" in justfile_content
    assert "@just test" in justfile_content

    # Check that optional dependencies are NOT included in the file
    assert "@just safety-check" not in justfile_content
    assert "@just bandit-check" not in justfile_content


def test_conditional_scripts_pdm(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify optional scripts (e.g., safety) appear in pdm config when enabled."""
    destination_path = tmp_path / "generated_project_pdm_safety"
    data = {
        **common_data,
        "task_runner": "pdm",
        "use_safety": True,  # Enable safety
        "use_bandit": False,  # Keep bandit off
    }
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
    content = (project_path / "pyproject.toml").read_text()
    toml_data = tomllib.loads(content)
    pdm_scripts = toml_data.get("tool", {}).get("pdm", {}).get("scripts", {})

    assert "safety-check" in pdm_scripts  # Should now be present
    assert "bandit-check" not in pdm_scripts  # Should still be absent

    # Check composite 'qa' script includes safety
    qa_script = pdm_scripts.get("qa", {})
    assert "safety-check" in qa_script.get("composite", [])
    assert "bandit-check" not in qa_script.get("composite", [])


def test_conditional_scripts_just(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify optional scripts (e.g., safety) appear in justfile when enabled."""
    destination_path = tmp_path / "generated_project_just_safety"
    data = {
        **common_data,
        "task_runner": "just",
        "use_safety": True,  # Enable safety
        "use_bandit": False,  # Keep bandit off
    }
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
    justfile_content = (project_path / "justfile").read_text()

    assert "safety-check *args:" in justfile_content  # Should now be present
    assert "bandit-check:" not in justfile_content  # Should still be absent

    # Check composite 'qa' script includes safety
    qa_line = next(
        (line for line in justfile_content.splitlines() if line.startswith("qa:")), None
    )
    assert qa_line is not None
    assert "@just safety-check" in justfile_content
    assert "@just bandit-check" not in justfile_content


def test_with_cli(root_path: str, tmp_path: Path, common_data: dict[str, str]) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "cli": True,
    }
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
    assert Path(project_path / "pyproject.toml").exists()

    # Parse pyproject.toml to check for CLI dependencies and scripts
    content = (project_path / "pyproject.toml").read_text()
    toml_data = tomllib.loads(content)

    # Get dependency lists
    main_deps = toml_data.get("project", {}).get("dependencies", [])
    # pdm_dev_deps_groups = toml_data.get("tool", {}).get("pdm", {}).get("dev-dependencies", {})
    # dev_deps = pdm_dev_deps_groups.get("dev", []) # Adjust "dev" if needed

    assert "typer[all]" in main_deps
    assert "rich" in main_deps

    project_scripts = toml_data.get("project", {}).get("scripts", {})
    assert project_scripts is not None

    # check script entry point
    script_name = common_data["project_slug"]
    module_path = common_data["module_name"]
    expected_entry = f"{module_path}.cli.__main__:app"
    assert project_scripts.get(script_name) == expected_entry

    assert (project_path / "src" / "test_project" / "cli").exists()
    assert (project_path / "src" / "test_project" / "cli" / "__main__.py").exists()

    (project_path / "tests" / "cli").mkdir(parents=True)
    (project_path / "tests" / "cli" / "test_cli.py").write_text(
        """from typer.testing import CliRunner

from test_project.cli.__main__ import app

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "Tom"])
    assert result.exit_code == 0
    assert "Hello, Tom!" in result.stdout
"""
    )


def test_with_docker(root_path: str, tmp_path: Path, common_data: dict[str, str]) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "docker_support": True,
    }
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
    assert (project_path / "docker-compose.yml").exists()


def test_with_badges(root_path: str, tmp_path: Path, common_data: dict[str, str]) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "badges": True,
    }
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
    readme_content = (project_path / "README.md").read_text()
    assert "Build Status" in readme_content
    assert "Code Coverage" in readme_content
    assert "Documentation Status" in readme_content


def test_with_env_file(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "generate_env": True,
    }
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
    assert (project_path / ".env").exists()


def test_license_proprietary(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "license": "Proprietary",
    }
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
    license_content = (project_path / "LICENSE.md").read_text()
    assert "All Rights Reserved." in license_content


def test_license_apache(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "license": "Apache-2.0",
    }
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
    assert (project_path / "LICENSE.md").exists()
    license_content = (project_path / "LICENSE.md").read_text()
    assert "Apache License" in license_content


def test_different_python_version(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    destination_path = tmp_path / "generated_project"
    data = {
        **common_data,
        "python_version": "3.12",
    }
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
    pyproject_content = (project_path / "pyproject.toml").read_text()
    toml_data = tomllib.loads(pyproject_content)
    assert toml_data.get("project", {}).get("requires-python") == ">=3.12"


def test_with_typed_settings(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify that the typed-settings config is generated correctly."""
    destination_path = tmp_path / "generated_project_typed_settings"
    data = {
        **common_data,
        "config_library": "typed-settings",
    }
    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,  # Allow defaults for unspecified vars
        skip_tasks=True,
        unsafe=True,
    )
    project_path = destination_path / common_data["project_slug"]
    module_path_str = common_data["module_name"]

    # 1. Check that config.py exists
    config_file_path = project_path / "src" / module_path_str / "config.py"
    assert config_file_path.exists()

    # 2. Check that the content is correct for typed-settings
    config_content = config_file_path.read_text()
    assert "import typed_settings as ts" in config_content
    assert "@ts.settings" in config_content
    assert "pydantic_settings" not in config_content

    # 3. Check pyproject.toml for correct dependencies
    pyproject_path = project_path / "pyproject.toml"
    assert pyproject_path.exists()
    content = pyproject_path.read_text()
    toml_data = tomllib.loads(content)

    main_deps = toml_data.get("project", {}).get("dependencies", [])

    # 4. Check that typed-settings is a dependency
    assert "typed-settings" in main_deps

    # 5. Check that pydantic-settings is NOT a dependency
    assert "pydantic-settings" not in main_deps


def test_with_codecov(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify that the Codecov upload step is added to the CI workflow."""
    destination_path = tmp_path / "generated_project_codecov"
    data = {
        **common_data,
        "use_codecov": True,
    }
    run_copy(
        root_path,
        destination_path,
        data=data,
        vcs_ref="HEAD",
        defaults=True,  # Allow defaults for unspecified vars
        skip_tasks=True,
        unsafe=True,
    )
    project_path = destination_path / common_data["project_slug"]

    # 1. Check that the main CI workflow file exists
    ci_workflow_path = project_path / ".github" / "workflows" / "main.yaml"
    assert ci_workflow_path.exists()

    # 2. Check that the content includes the Codecov action
    ci_workflow_content = ci_workflow_path.read_text()
    assert "uses: codecov/codecov-action@v4" in ci_workflow_content
    assert "secrets.CODECOV_TOKEN" in ci_workflow_content


def test_with_detect_secrets(
    root_path: str, tmp_path: Path, common_data: dict[str, str]
) -> None:
    """Verify that the detect-secrets hook is added to pre-commit config."""
    destination_path = tmp_path / "generated_project_detect_secrets"
    data = {
        **common_data,
        "use_detect_secrets": True,
    }
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

    # 1. Check that the pre-commit config file exists
    pre_commit_path = project_path / ".pre-commit-config.yaml"
    assert pre_commit_path.exists()

    # 2. Check that the content includes the detect-secrets hook
    pre_commit_content = pre_commit_path.read_text()
    assert "repo: https://github.com/Yelp/detect-secrets" in pre_commit_content
    assert "id: detect-secrets" in pre_commit_content
    assert (
        "id: detect-secrets-baseline" in pre_commit_content
    )  # Check for the baseline hook
