from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PushSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PUSH_",
        env_file=".env",
        extra="ignore",
    )

    vapid_public_key: str = ""
    vapid_private_key: SecretStr = SecretStr("")
    vapid_subject: str = "mailto:admin@example.com"
