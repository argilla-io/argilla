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
from typing import Dict, Any, ClassVar, Type, Optional, Union, List, Tuple
from urllib.parse import urljoin

import httpx
from oauthlib.oauth2 import WebApplicationClient
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthException

from social_core.strategy import BaseStrategy
from starlette.requests import Request
from starlette.responses import RedirectResponse

from argilla_server.errors import future
from argilla_server.security.authentication.claims import Claims
from argilla_server.security.settings import settings


class Strategy(BaseStrategy):
    def request_data(self, merge=True) -> Dict[str, Any]:
        return {}

    def absolute_uri(self, path=None) -> str:
        return path

    def get_setting(self, name):
        return None


class OAuth2ClientProvider:
    """OAuth2 flow handler  of a certain provider."""

    OAUTH_STATE_COOKIE_NAME = "oauth2_state"
    OAUTH_STATE_COOKIE_MAX_AGE = 90

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
        self.scope = self.scope.split(" ") if self.scope else []
        self.redirect_uri = redirect_uri or self._environment_variable_for_property("redirect_uri")
        self.redirect_uri = self.redirect_uri or f"/oauth/{self.name}/callback"

        self._backend = self.backend_class(strategy=self.backend_strategy)
        self._authorization_endpoint = self._backend.authorization_url()
        self._token_endpoint = self._backend.access_token_url()

    @classmethod
    def from_dict(cls, provider: dict) -> "OAuth2ClientProvider":
        return cls(**provider)

    def new_oauth_client(self) -> WebApplicationClient:
        return WebApplicationClient(self.client_id)

    def get_redirect_uri(self, request: Request) -> str:
        url = urljoin(str(request.base_url), self.redirect_uri)
        return self._align_url_to_allow_http_redirect(url)

    def authorization_url(self, request: Request) -> Tuple[str, Optional[str]]:
        redirect_uri = self.get_redirect_uri(request)
        state = "".join([random.choice(string.ascii_letters) for _ in range(32)])

        oauth2_query_params = dict(state=state, scope=self.scope, redirect_uri=redirect_uri)
        oauth2_query_params.update(request.query_params)

        authorization_url = str(
            self.new_oauth_client().prepare_request_uri(self._authorization_endpoint, **oauth2_query_params)
        )

        return authorization_url, state

    def authorization_redirect(self, request: Request) -> RedirectResponse:
        url, state = self.authorization_url(request)
        response = RedirectResponse(url, 303)

        response.set_cookie(
            self._get_state_cookie_name(),
            value=state,
            secure=True,
            httponly=True,
            max_age=self.OAUTH_STATE_COOKIE_MAX_AGE,
            samesite="none",
        )

        return response

    def _get_state_cookie_name(self) -> str:
        return f"{self.name}_{self.OAUTH_STATE_COOKIE_NAME}"

    async def get_user_data(self, request: Request) -> dict:
        self._check_request_params(request)

        redirect_uri = self.get_redirect_uri(request)
        authorization_response = self._align_url_to_allow_http_redirect(str(request.url))

        oauth2_query_params = dict(redirect_url=redirect_uri)
        oauth2_query_params.update(request.query_params)

        return await self._fetch_user_data(authorization_response=authorization_response, **oauth2_query_params)

    def _check_request_params(self, request) -> None:
        if "code" not in request.query_params:
            raise ValueError("'code' parameter was not found in callback request")

        if "state" not in request.query_params:
            raise ValueError("'state' parameter was not found in callback request")

        state = request.cookies.get(self._get_state_cookie_name())
        if request.query_params.get("state") != state:
            raise ValueError("'state' parameter does not match")

    @staticmethod
    def _align_url_to_allow_http_redirect(url: str) -> str:
        """This method is used to align the URL to the HTTP/HTTPS scheme"""

        scheme = "http" if settings.oauth.allow_http_redirect else "https"
        return re.sub(r"^https?", scheme, url)

    def standardize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["provider"] = self.name
        data["scope"] = self.scope

        return data

    async def _fetch_user_data(self, authorization_response: str, **oauth_query_params) -> dict:
        oauth_client = self.new_oauth_client()
        token_url, headers, content = oauth_client.prepare_token_request(
            self._token_endpoint,
            authorization_response=authorization_response,
            **oauth_query_params,
        )

        headers.update({"Accept": "application/json"})
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient(auth=auth) as session:
            try:
                response = await session.post(token_url, headers=headers, content=content)
                oauth_client.parse_request_body_response(json.dumps(response.json()))

                return self.standardize(self._backend.user_data(oauth_client.access_token))
            except httpx.HTTPError as e:
                raise ValueError(str(e))
            except AuthException as e:
                raise future.AuthenticationError(str(e))

    def _environment_variable_for_property(self, property_name: str, default: str = None) -> str:
        env_var_name = f"OAUTH2_{self.name.upper()}_{property_name.upper()}"

        return os.getenv(env_var_name, default)
