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

import logging

from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla_server.logging import LoggingMixin
from argilla_server.security.authentication.claims import Claims
from argilla_server.security.authentication.oauth2.providers._base import OAuth2ClientProvider

_LOGGER = logging.getLogger("argilla.security.oauth2.providers.huggingface")


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    OIDC_ENDPOINT = "https://huggingface.co"
    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


_HF_PREFERRED_USERNAME = "preferred_username"


class HuggingfaceClientProvider(OAuth2ClientProvider, LoggingMixin):
    """Specialized HuggingFace OAuth2 provider."""

    claims = Claims(username=_HF_PREFERRED_USERNAME, first_name="name")
    backend_class = HuggingfaceOpenId
    name = "huggingface"
