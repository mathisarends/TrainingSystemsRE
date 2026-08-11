from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtAlgorithm(StrEnum):
    HS256 = "HS256"
    RS256 = "RS256"


class CookieSameSite(StrEnum):
    STRICT = "strict"
    LAX = "lax"
    NONE = "none"


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATION_",
        env_file=".env",
        extra="ignore",
    )

    frontend_base_url: str = "http://localhost:5173"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: JwtAlgorithm = JwtAlgorithm.HS256
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    access_token_cookie_name: str = "access_token"
    refresh_token_cookie_name: str = "refresh_token"

    cookie_samesite_dev: CookieSameSite = CookieSameSite.LAX
    cookie_samesite_prod: CookieSameSite = CookieSameSite.STRICT
