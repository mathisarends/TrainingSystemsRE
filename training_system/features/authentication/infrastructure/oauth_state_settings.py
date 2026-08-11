from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthStateSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OAUTH_STATE_",
        env_file=".env",
        extra="ignore",
    )

    ttl_seconds: int = 60 * 10
