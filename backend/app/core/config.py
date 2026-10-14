from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    app_name: str = "Flood Early-Warning Project Status"
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:13130",
        "http://frontend:80",
    ]
    data_dir: str = "/app/data"


settings = Settings()
