import base64
import hashlib
import hmac
import time

from fastapi import Request, Response

from training_system.settings import AppSettings


class OAuthStateCookies:
    """Signed, short-lived state cookie for an OAuth authorization flow.

    Generic over the cookie name so the same logic serves every provider.
    """

    def __init__(
        self,
        *,
        cookie_name: str,
        ttl_seconds: int,
        signing_secret: str,
        app_settings: AppSettings,
    ) -> None:
        self._cookie_name = cookie_name
        self._ttl_seconds = ttl_seconds
        self._signing_key = signing_secret.encode("utf-8")
        self._app_settings = app_settings

    def set(self, *, response: Response, state: str) -> None:
        normalized_state = state.strip()
        if not normalized_state:
            raise ValueError("OAuth state must not be empty")

        response.set_cookie(
            key=self._cookie_name,
            value=self._encode(state=normalized_state),
            httponly=True,
            secure=not self._app_settings.is_local,
            samesite="lax",
            path="/",
            max_age=self._ttl_seconds,
        )

    def read(self, *, request: Request) -> str | None:
        signed_state = request.cookies.get(self._cookie_name)
        if not signed_state:
            return None
        return self._decode(signed_state=signed_state)

    def clear(self, response: Response) -> None:
        response.delete_cookie(key=self._cookie_name, path="/")

    def _encode(self, *, state: str) -> str:
        issued_at = str(int(time.time()))
        signature = self._sign(issued_at=issued_at, state=state)
        return f"{issued_at}.{state}.{signature}"

    def _decode(self, *, signed_state: str) -> str | None:
        first = signed_state.find(".")
        last = signed_state.rfind(".")
        if first <= 0 or last <= first + 1 or last >= len(signed_state) - 1:
            return None

        issued_at = signed_state[:first]
        state = signed_state[first + 1 : last]
        received_signature = signed_state[last + 1 :]

        if not issued_at.isdigit() or not state:
            return None

        expected_signature = self._sign(issued_at=issued_at, state=state)
        if not hmac.compare_digest(expected_signature, received_signature):
            return None

        token_age = int(time.time()) - int(issued_at)
        if token_age < 0 or token_age > self._ttl_seconds:
            return None

        return state

    def _sign(self, *, issued_at: str, state: str) -> str:
        payload = f"{issued_at}.{state}".encode("utf-8")
        signature = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


class GoogleOAuthStateCookies(OAuthStateCookies):
    """OAuth state cookie for the Google login flow.

    Subclass exists purely for DI type discrimination.
    """
