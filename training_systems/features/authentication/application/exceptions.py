class InvalidCredentialsException(Exception):
    """Login credentials (password or OAuth exchange) were rejected."""


class EmailAlreadyRegisteredException(Exception):
    """The email is already associated with a different auth identity."""


class SessionExpiredException(Exception):
    """A JWT was well-formed but has expired."""


class SessionInvalidException(Exception):
    """A JWT failed signature, type, or claim validation."""
