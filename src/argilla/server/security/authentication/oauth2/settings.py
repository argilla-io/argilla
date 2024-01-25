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
from typing import List, Optional

from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla.server.security.authentication.oauth2.client_provider import OAuth2ClientProvider

__all__ = ["OAuth2Settings"]


class OAuth2Settings:
    def __init__(
        self,
        enabled: bool = True,
        allow_http: bool = False,
        providers: List["OAuth2ClientProvider"] = None,
    ):
        self.enabled = enabled
        self.allow_http = allow_http
        self._providers = providers or []

        if self.allow_http:
            # See https://stackoverflow.com/questions/27785375/testing-flask-oauthlib-locally-without-https
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    @property
    def providers(self) -> dict:
        return {provider.name: provider for provider in self._providers}

    @classmethod
    def defaults(cls) -> "OAuth2Settings":
        from dotenv import load_dotenv

        load_dotenv()
        return cls(providers=[HuggingfaceClientProvider()])


class HuggingfaceClientProvider(OAuth2ClientProvider):
    """Specialized HuggingFace OAuth2 provider."""

    class HuggingfaceOpenId(OpenIdConnectAuth):
        """Huggingface OpenID Connect authentication backend."""

        name = "huggingface"

        OIDC_ENDPOINT = "https://huggingface.co"
        AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
        ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

        def oidc_endpoint(self) -> str:
            return self.OIDC_ENDPOINT

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            name=self.HuggingfaceOpenId.name,
            backend_class=self.HuggingfaceOpenId,
            client_id=client_id or os.getenv("OAUTH2_HF_CLIENT_ID", client_id),
            client_secret=client_secret or os.getenv("OAUTH2_HF_CLIENT_SECRET", client_secret),
            redirect_uri=redirect_uri
            or os.getenv("OAUTH2_HF_REDIRECT_URI"),  # THis should be the same for all providers
            scope=["openid", "profile"],
            claims={"username": "preferred_username", "first_name": "name"},
        )
