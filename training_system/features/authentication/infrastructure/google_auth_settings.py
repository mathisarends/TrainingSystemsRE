from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_",
        env_file=".env",
        extra="ignore",
    )

    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    authorization_endpoint: str = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint: str = "https://oauth2.googleapis.com/token"
    userinfo_endpoint: str = "https://openidconnect.googleapis.com/v1/userinfo"
    scope: str = "openid email profile"
    state_cookie_name: str = "google_oauth_state"
