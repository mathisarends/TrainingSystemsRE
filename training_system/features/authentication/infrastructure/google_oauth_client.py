from urllib.parse import urlencode

import httpx
from pydantic import ValidationError

from training_system.features.authentication.application.ports import (
    GoogleOAuthProvider,
)
from training_system.features.authentication.application.schemas import GoogleIdentity
from training_system.features.authentication.infrastructure.google_auth_settings import (  # noqa: E501
    GoogleAuthSettings,
)


class GoogleOAuthClient(GoogleOAuthProvider):
    def __init__(self, settings: GoogleAuthSettings) -> None:
        self._settings = settings

    def build_authorization_url(self, *, state: str) -> str:
        self._validate_configuration()

        normalized_state = state.strip()
        if not normalized_state:
            raise ValueError("OAuth state must not be empty")

        query = urlencode(
            {
                "client_id": self._settings.client_id,
                "redirect_uri": self._settings.redirect_uri,
                "response_type": "code",
                "scope": self._settings.scope,
                "state": normalized_state,
            }
        )
        return f"{self._settings.authorization_endpoint}?{query}"

    async def exchange_code_for_identity(
        self, *, authorization_code: str
    ) -> GoogleIdentity:
        self._validate_configuration()

        access_token = await self._exchange_code_for_access_token(
            authorization_code=authorization_code
        )
        return await self._fetch_identity(access_token=access_token)

    def _validate_configuration(self) -> None:
        if not self._settings.client_id:
            raise ValueError("Google client ID is not configured")
        if not self._settings.client_secret:
            raise ValueError("Google client secret is not configured")
        if not self._settings.redirect_uri:
            raise ValueError("Google redirect URI is not configured")

    async def _exchange_code_for_access_token(self, *, authorization_code: str) -> str:
        payload = {
            "code": authorization_code,
            "client_id": self._settings.client_id,
            "client_secret": self._settings.client_secret,
            "redirect_uri": self._settings.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._settings.token_endpoint,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            raise ValueError("Google token exchange failed")

        access_token = response.json().get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise ValueError("Google token response did not include access token")
        return access_token

    async def _fetch_identity(self, *, access_token: str) -> GoogleIdentity:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self._settings.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code >= 400:
            raise ValueError("Google user info request failed")

        try:
            return GoogleIdentity.model_validate(response.json())
        except ValidationError as exc:
            raise ValueError("Google user info payload is invalid") from exc
