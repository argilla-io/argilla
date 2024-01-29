import os
from unittest import mock

from argilla.server.security.settings import Settings


def test_default_security_settings():
    settings = Settings()

    assert settings.algorithm == "HS256"
    assert settings.token_expiration == 86400
    assert len(settings.secret_key) == 32


def test_configure_algorithm():
    algorithm = "mock-algorithm"
    with mock.patch.dict(os.environ, {"ARGILLA_AUTH_ALGORITHM": algorithm}):
        settings = Settings()

        assert settings.algorithm == algorithm


def test_configure_token_expiration():
    token_expiration = 3600
    with mock.patch.dict(os.environ, {"ARGILLA_AUTH_TOKEN_EXPIRATION": str(token_expiration)}):
        settings = Settings()

        assert settings.token_expiration == token_expiration


def test_configure_secret_key():
    secret_key = "mock-secret-key"
    with mock.patch.dict(os.environ, {"ARGILLA_AUTH_SECRET_KEY": secret_key}):
        settings = Settings()

        assert settings.secret_key == secret_key


def test_configure_algorithm_with_old_env_name():
    algorithm = "old_mock-algorithm"
    with mock.patch.dict(os.environ, {"ARGILLA_LOCAL_AUTH_ALGORITHM": algorithm}):
        settings = Settings()

        assert settings.algorithm == algorithm

# TODO: remove this test when ARGILLA_LOCAL_AUTH_SECRET_KEY will be removed
def test_configure_secret_key_with_old_env_name():
    secret_key = "old_mock-secret-key"
    with mock.patch.dict(os.environ, {"ARGILLA_LOCAL_AUTH_SECRET_KEY": secret_key}):
        settings = Settings()

        assert settings.secret_key == secret_key


# TODO: remove this test when ARGILLA_LOCAL_AUTH_TOKEN_EXPIRATION_IN_MINUTES will be removed
def test_configure_token_expiration_in_minutes():
    token_expiration_in_minutes = 30
    with mock.patch.dict(
        os.environ, {"ARGILLA_LOCAL_AUTH_TOKEN_EXPIRATION_IN_MINUTES": str(token_expiration_in_minutes)}
    ):
        settings = Settings()

        assert settings.token_expiration == token_expiration_in_minutes * 60
