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
import os
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from argilla.server.pydantic_v1 import BaseSettings, validator


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

    secret_key: str = uuid4().hex
    algorithm: str = "HS256"

    token_expiration_in_minutes: int = 15
    token_expiration: int

    @validator("token_expiration", always=True)
    def set_token_expire_time(cls, v, values, **kwargs) -> int:
        if v is not None:
            return v
        return values["token_expiration_in_minutes"] * 60

    class Config:
        env_prefix = "ARGILLA_AUTH_"

        fields = {
            # Support for old local auth env variables
            "algorithm": {"env": ["ARGILLA_LOCAL_AUTH_ALGORITHM", f"{env_prefix}ALGORITHM"]},
            "secret_key": {"env": ["ARGILLA_LOCAL_AUTH_SECRET_KEY", f"{env_prefix}SECRET_KEY"]},
            "token_expiration_in_minutes": {
                "env": [
                    "ARGILLA_LOCAL_AUTH_TOKEN_EXPIRATION_IN_MINUTES",
                    f"{env_prefix}TOKEN_EXPIRATION_IN_MINUTES",
                ]
            },
        }


settings = Settings()
