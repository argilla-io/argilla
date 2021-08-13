from pydantic import BaseSettings
from rubrix import DEFAULT_API_KEY


class Settings(BaseSettings):

    """
    Attributes
    ----------

    secret_key:
        The secret key used for signed the token data

    algorithm:
        Encryption algorithm for token data

    token_expiration_in_minutes:
        The session token expiration in minutes. Default=30000

    """

    secret_key: str = "secret"
    algorithm: str = "HS256"
    token_expiration_in_minutes: int = 30000
    token_api_url: str = "/api/security/token"

    default_apikey: str = DEFAULT_API_KEY
    default_password: str = (
        "$2y$12$MPcRR71ByqgSI8AaqgxrMeSdrD4BcxDIdYkr.ePQoKz7wsGK7SAca"  # 1234
    )
    users_db_file: str = ".users.yml"

    class Config:
        env_prefix = "RUBRIX_LOCAL_AUTH_"

        fields = {
            "secret_key": {"env": ["SECRET_KEY", f"{env_prefix}SECRET_KEY"]},
            "token_expiration_in_minutes": {
                "env": [
                    "TOKEN_EXPIRATION_IN_MINUTES",
                    f"{env_prefix}TOKEN_EXPIRATION_IN_MINUTES",
                ]
            },
        }


settings = Settings()
