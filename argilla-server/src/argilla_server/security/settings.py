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

# from argilla_server.pydantic_v1 import BaseSettings, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from argilla_server.security.authentication.oauth2 import OAuth2Settings


class Settings(BaseSettings):
    """
    Attributes
    ----------

    secret_key:
        The secret key used for signed the token data

    algorithm:
        Encryption algorithm for token data

    token_expiration:
        The session token expiration . Default=86400 (1 day)

    oauth_cfg:
        The path to the oauth yaml configuration file. Default=.oauth.yaml

    """

    secret_key: str = uuid4().hex
    algorithm: str = "HS256"
    token_expiration: int = 24 * 60 * 60  # 1 day
    oauth_cfg: str = ".oauth.yaml"

    _oauth_settings: Optional["OAuth2Settings"] = None  # PrivateAttr(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._oauth_settings = None

    @property
    def oauth(self) -> "OAuth2Settings":
        """Return the oauth settings"""
        from argilla_server.security.authentication.oauth2.settings import OAuth2Settings

        if self._oauth_settings:
            return self._oauth_settings

        if not self._oauth_settings and os.path.exists(self.oauth_cfg):
            self._oauth_settings = OAuth2Settings.from_yaml(self.oauth_cfg)
        else:
            self._oauth_settings = OAuth2Settings(enabled=False)

        return self._oauth_settings

    model_config = SettingsConfigDict(env_prefix="ARGILLA_AUTH_")


settings = Settings()
