from {{ cookiecutter.project_slug }}.settings import settings

def test_settings():
    assert settings.app_name == "{{ cookiecutter.project_name }}"
    assert settings.debug is True