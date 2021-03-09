from pydantic import BaseSettings


class SecuritySettings(BaseSettings):
    """
    Api security settings

    Attributes
    ----------

    secret_key:
        The secret key used for signed the token data

    algorithm:
        Encryption algorithm for token data

    token_expiration_in_minutes:
        The session token expiration in minutes. Default=30

    enable_security:
        If True, enables api security mechanisms. Default=False

    """

    secret_key = "secret"
    algorithm = "HS256"

    token_expiration_in_minutes = 30
    enable_security = False


settings = SecuritySettings()
