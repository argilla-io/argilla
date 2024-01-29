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

    token_expiration:
        The session token expiration . Default=7200 (2 hours)

    """

    secret_key: str = uuid4().hex
    algorithm: str = "HS256"

    token_expiration: int = 120 * 60

    @validator("token_expiration", always=True)
    def default_token_expiration(cls, v, values, **kwargs) -> int:
        if "token_expiration" in values:
            return v

        # This is a backwards compatibility hack to support the old env variable and
        # it will be removed in version 1.25.0. See https://github.com/argilla-io/argilla/issues/4542
        expiration_in_minutes = os.getenv("ARGILLA_LOCAL_AUTH_TOKEN_EXPIRATION_IN_MINUTES")
        if expiration_in_minutes is not None:
            return int(expiration_in_minutes) * 60

        return v

    class Config:
        env_prefix = "ARGILLA_AUTH_"

        fields = {
            # Support for old local auth env variables.
            # It will be removed in version 1.25.0 (See https://github.com/argilla-io/argilla/issues/4542)
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
