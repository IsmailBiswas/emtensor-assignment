from datetime import date
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> str:
    docker_path = Path("/app/data")
    if docker_path.is_dir():
        return str(docker_path)
    repo_data = Path(__file__).resolve().parents[3] / "data"
    return str(repo_data)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    app_name: str = "Flood Early-Warning Project Status"
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:13130",
        "http://frontend:80",
    ]
    data_dir: str = _default_data_dir()
    as_of_date: date = date(2026, 9, 15)

    @field_validator("as_of_date", mode="before")
    @classmethod
    def parse_as_of(cls, value: object) -> object:
        if isinstance(value, str) and value.strip():
            return date.fromisoformat(value.strip())
        return value


settings = Settings()
