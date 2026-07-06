from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    storage_dir: Path = Path("storage")
    database_url: str = "postgresql+psycopg://codepilot:codepilot@localhost:5432/codepilot"
    redis_url: str = "redis://localhost:6379/0"
    deepseek_api_key: str | None = Field(default=None, validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias="DEEPSEEK_BASE_URL",
    )
    deepseek_model: str = Field(default="deepseek-chat", validation_alias="DEEPSEEK_MODEL")

    model_config = SettingsConfigDict(
        env_prefix="CODEPILOT_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
