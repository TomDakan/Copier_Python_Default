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

    # assert settings.py exists
    assert (project_path / "src" / "test_project" / "settings.py").exists()

    #parse pyproject.toml to check for dependencies
    content = (project_path / "pyproject.toml").read_text()
    toml_data = tomllib.loads(content)

    main_deps = toml_data.get("project", {}).get("dependencies", [])
    pdm_dev_deps_groups = toml_data.get("tool", {}).get("pdm", {}).get("dev-dependencies", {})
    dev_deps = pdm_dev_deps_groups.get("dev", []) # Assuming your default group is 'dev'
    commitizen_config = toml_data.get("tool", {}).get("commitizen", {})

    # Check pyproject.toml content for default dependencies
    assert "pydantic-settings" in main_deps

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
    #pdm_dev_deps_groups = toml_data.get("tool", {}).get("pdm", {}).get("dev-dependencies", {})
    #dev_deps = pdm_dev_deps_groups.get("dev", []) # Adjust "dev" if needed

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
        "badge_build": "build_badge",
        "badge_coverage": "coverage_badge",
        "badge_docs": "docs_badge",
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
    assert "build_badge" in readme_content
    assert "coverage_badge" in readme_content
    assert "docs_badge" in readme_content


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