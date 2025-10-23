from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def root_path() -> str:
    return str(Path(__file__).parent.parent)


@pytest.fixture(scope="session")
def common_data() -> dict[str, str]:
    return {
        "project_name": "Test Project",
        "project_slug": "test-project",
        "module_name": "test_project",
        "project_description": "testing a python copier template",
        "repository_url": "https://github.com/TomDakan/Copier_Python3.13_Default",
        "author_name": "Tom Dakan",
        "author_email": "tomdakan@gmail.com",
        "license": "MIT",
        "python_version": "3.13",
    }
