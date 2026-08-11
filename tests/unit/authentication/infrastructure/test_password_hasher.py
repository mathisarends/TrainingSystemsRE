from training_system.features.authentication.infrastructure.password_hasher import (
    Pbkdf2PasswordHasher,
)


def test_verify_accepts_the_correct_password() -> None:
    hasher = Pbkdf2PasswordHasher()
    password_hash = hasher.hash(password="s3cret!!")

    assert hasher.verify(password="s3cret!!", password_hash=password_hash) is True


def test_verify_rejects_a_wrong_password() -> None:
    hasher = Pbkdf2PasswordHasher()
    password_hash = hasher.hash(password="s3cret!!")

    result = hasher.verify(password="wrong-password", password_hash=password_hash)
    assert result is False


def test_hash_is_salted_so_the_same_password_hashes_differently() -> None:
    hasher = Pbkdf2PasswordHasher()

    assert hasher.hash(password="s3cret!!") != hasher.hash(password="s3cret!!")


def test_verify_rejects_a_malformed_hash() -> None:
    hasher = Pbkdf2PasswordHasher()

    result = hasher.verify(password="s3cret!!", password_hash="not-a-valid-hash")
    assert result is False


def test_verify_rejects_a_hash_from_an_unsupported_algorithm() -> None:
    hasher = Pbkdf2PasswordHasher()

    assert (
        hasher.verify(password="s3cret!!", password_hash="md5$1$salt$digest") is False
    )
