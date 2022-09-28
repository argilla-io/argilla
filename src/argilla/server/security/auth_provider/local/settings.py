#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pydantic import BaseSettings

from argilla._constants import DEFAULT_API_KEY


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
        env_prefix = "ARGILLA_LOCAL_AUTH_"

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
