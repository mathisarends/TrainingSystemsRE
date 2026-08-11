from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    environment: str = "local"
    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def is_local(self) -> bool:
        return self.environment == "local"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        extra="ignore",
    )

    url: str = "postgresql+asyncpg://training:training@localhost:5432/training_systems"
