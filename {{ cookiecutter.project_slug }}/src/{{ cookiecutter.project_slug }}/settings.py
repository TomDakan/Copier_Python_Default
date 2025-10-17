from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings

try:
    from dotenv import load_dotenv  # type: ignore
    _DOTENV_AVAILABLE = True
except Exception:
    _DOTENV_AVAILABLE = False

if _DOTENV_AVAILABLE:
    load_dotenv()

class Settings(BaseSettings):
    app_name: str = "{{ cookiecutter.project_name }}"
    debug: bool = True
    secret_key: Optional[SecretStr] = None
    redis_dsn: Optional[str] = None

    class Config:
        pass

settings = Settings()
