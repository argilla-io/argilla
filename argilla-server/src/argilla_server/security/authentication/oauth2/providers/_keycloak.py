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
from typing import Optional, List

from social_core.backends.keycloak import KeycloakOAuth2
from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla_server.logging import LoggingMixin
from argilla_server.security.authentication.claims import Claims
from argilla_server.security.authentication.oauth2.providers._base import OAuth2ClientProvider

_LOGGER = logging.getLogger("argilla.security.oauth2.providers.keycloak")

class KeycloakOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "keycloak"

    @staticmethod
    def from_oidc_endpoint(oidc_endpoint: str):
        KeycloakOpenId.OIDC_ENDPOINT = oidc_endpoint.rstrip('/')
        KeycloakOpenId.AUTHORIZATION_URL = f"{oidc_endpoint}/protocol/openid-connect/auth"
        KeycloakOpenId.ACCESS_TOKEN_URL = f"{oidc_endpoint}/protocol/openid-connect/token"

        return KeycloakOpenId
    
    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


class KeycloakClientProvider(OAuth2ClientProvider, LoggingMixin):
    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        scope: Optional[List[str]] = None,
        redirect_uri: str = None,
        oidc_endpoint: str = None,
    ):
        if oidc_endpoint is None:
            raise ValueError('oidc_endpoint needs to be set in the Keycloak configuration')
        
        self.oidc_endpoint = oidc_endpoint
        self.backend_class = KeycloakOpenId.from_oidc_endpoint(self.oidc_endpoint)
        print(self.backend_class.__dict__)
        super().__init__(
            client_id = client_id,
            client_secret=client_secret,
            scope = scope,
            redirect_uri= redirect_uri,
        )

    claims = Claims(
        identity=lambda user: f"{user.provider}:{user.id}",
        username="preferred_username",
        # TODO . 'given_name': 'xy', 'family_name': 'xy'
    )
    name = "keycloak"