from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthenticationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATION_",
        env_file=".env",
        extra="ignore",
    )

    google_client_id: str = ""
    session_ttl_days: int = 30
    cookie_secure: bool = True
    cookie_name: str = "session_token"
