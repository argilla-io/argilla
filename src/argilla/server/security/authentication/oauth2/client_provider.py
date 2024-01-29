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

import json
import os
import random
import re
import string
from typing import Any, ClassVar, Dict, List, Optional, Type, Union
from urllib.parse import urljoin

import httpx
from fastapi import Request
from oauthlib.oauth2 import WebApplicationClient
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthException
from social_core.strategy import BaseStrategy
from starlette.responses import RedirectResponse

from argilla.server.security.authentication.claims import Claims
from argilla.server.security.authentication.oauth2.errors import (
    OAuth2AuthenticationError,
    OAuth2Error,
    OAuth2InvalidRequestError,
)
from argilla.server.security.settings import settings


class Strategy(BaseStrategy):
    def request_data(self, merge=True) -> Dict[str, Any]:
        return {}

    def absolute_uri(self, path=None) -> str:
        return path

    def get_setting(self, name):
        return None


class OAuth2ClientProvider:
    """OAuth2 flow handler  of a certain provider."""

    name: ClassVar[str]
    backend_class: ClassVar[Type[BaseOAuth2]]
    claims: ClassVar[Optional[Union[Claims, dict]]] = None
    backend_strategy: ClassVar[BaseStrategy] = Strategy()

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        scope: Optional[List[str]] = None,
        redirect_uri: str = None,
    ) -> None:
        self.client_id = client_id or self._environment_variable_for_property("client_id")
        self.client_secret = client_secret or self._environment_variable_for_property("client_secret")
        self.scope = scope or self._environment_variable_for_property("scope", "")
        self.redirect_uri = redirect_uri or self._environment_variable_for_property("redirect_uri")
        self.redirect_uri = self.redirect_uri or f"/oauth/{self.name}/callback"

        self._backend = self.backend_class(strategy=self.backend_strategy)
        self._authorization_endpoint = self._backend.authorization_url()
        self._token_endpoint = self._backend.access_token_url()
        self._state = None  # TODO !!!

    def _environment_variable_for_property(self, property_name: str, default: str = None) -> str:
        env_var_name = f"OAUTH2_{self.name.upper()}_{property_name.upper()}"

        return os.getenv(env_var_name, default)

    @classmethod
    def from_dict(cls, provider: dict) -> "OAuth2ClientProvider":
        return cls(**provider)

    def new_oauth_client(self) -> WebApplicationClient:
        return WebApplicationClient(self.client_id)

    def get_redirect_uri(self, request: Request) -> str:
        url = urljoin(str(request.base_url), self.redirect_uri)
        return self._align_url_to_allow_http_redirect(url)

    def authorization_url(self, request: Request) -> str:
        redirect_uri = self.get_redirect_uri(request)
        state = "".join([random.choice(string.ascii_letters) for _ in range(32)])

        oauth2_query_params = dict(state=state, scope=self.scope, redirect_uri=redirect_uri)
        oauth2_query_params.update(request.query_params)

        self._state = oauth2_query_params.get("state")
        return str(self.new_oauth_client().prepare_request_uri(self._authorization_endpoint, **oauth2_query_params))

    def authorization_redirect(self, request: Request) -> RedirectResponse:
        return RedirectResponse(self.authorization_url(request), 303)

    async def token_data(self, request: Request, **httpx_client_args) -> dict:
        if not request.query_params.get("code"):
            raise OAuth2InvalidRequestError(400, "'code' parameter was not found in callback request")

        if not request.query_params.get("state"):
            raise OAuth2InvalidRequestError(400, "'state' parameter was not found in callback request")

        # This will be skipped for the moment
        # if request.query_params.get("state") != self._state:
        # raise OAuth2InvalidRequestError(400, "'state' parameter does not match")

        redirect_uri = self.get_redirect_uri(request)
        authorization_response = self._align_url_to_allow_http_redirect(str(request.url))

        oauth2_query_params = dict(redirect_url=redirect_uri, authorization_response=authorization_response)
        oauth2_query_params.update(request.query_params)

        oauth_client = self.new_oauth_client()
        token_url, headers, content = oauth_client.prepare_token_request(self._token_endpoint, **oauth2_query_params)

        headers.update({"Accept": "application/json"})
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient(auth=auth, **httpx_client_args) as session:
            try:
                response = await session.post(token_url, headers=headers, content=content)
                oauth_client.parse_request_body_response(json.dumps(response.json()))

                return self.standardize(self._backend.user_data(oauth_client.access_token))
            except (OAuth2Error, httpx.HTTPError) as e:
                raise OAuth2InvalidRequestError(400, str(e))
            except (AuthException, Exception) as e:
                raise OAuth2AuthenticationError(401, str(e))

    @staticmethod
    def _align_url_to_allow_http_redirect(url: str) -> str:
        """This method is used to align the URL to the HTTP/HTTPS scheme"""

        scheme = "http" if settings.oauth2.allow_http_redirect else "https"
        return re.sub(r"^https?", scheme, url)

    def standardize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["provider"] = self.name
        data["scope"] = self.scope

        return data
