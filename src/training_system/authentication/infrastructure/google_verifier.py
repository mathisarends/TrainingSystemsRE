from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from training_system.authentication.application.errors import AuthenticationFailed
from training_system.authentication.application.ports import (
    IdentityVerifier,
    VerifiedIdentity,
)
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)


class GoogleIdentityVerifier(IdentityVerifier):
    """Verifies a Google OIDC ID token against the configured client id."""

    def __init__(self, settings: AuthenticationSettings) -> None:
        self._settings = settings
        self._request = google_requests.Request()

    def verify(self, *, credential: str) -> VerifiedIdentity:
        claims = google_id_token.verify_oauth2_token(
            credential, self._request, self._settings.google_client_id
        )
        subject = claims.get("sub")
        email = claims.get("email")
        name = claims.get("name")
        if not subject or not email or not name:
            raise AuthenticationFailed
        return VerifiedIdentity(
            subject=subject,
            email=email,
            name=name,
            picture_url=claims.get("picture"),
        )
