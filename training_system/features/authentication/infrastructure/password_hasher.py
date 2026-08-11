import hashlib
import hmac
import secrets

from training_system.features.authentication.application.ports import PasswordHasher

_ALGORITHM = "sha256"
_ITERATIONS = 600_000
_SALT_BYTES = 16


class Pbkdf2PasswordHasher(PasswordHasher):
    def hash(self, *, password: str) -> str:
        salt = secrets.token_hex(_SALT_BYTES)
        digest = self._derive(password=password, salt=salt)
        return f"{_ALGORITHM}${_ITERATIONS}${salt}${digest}"

    def verify(self, *, password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations_raw, salt, expected_digest = password_hash.split("$")
        except ValueError:
            return False

        if algorithm != _ALGORITHM:
            return False

        digest = self._derive(
            password=password, salt=salt, iterations=int(iterations_raw)
        )
        return hmac.compare_digest(digest, expected_digest)

    def _derive(
        self, *, password: str, salt: str, iterations: int = _ITERATIONS
    ) -> str:
        return hashlib.pbkdf2_hmac(
            _ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), iterations
        ).hex()
