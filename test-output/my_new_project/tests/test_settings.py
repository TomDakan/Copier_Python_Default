from my_new_project.settings import settings

def test_settings():
    assert settings.app_name == "My New Project"
    assert settings.debug is True
