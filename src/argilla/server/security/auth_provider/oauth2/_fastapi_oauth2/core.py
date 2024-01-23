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
import random
import re
import string
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from oauthlib.oauth2 import OAuth2Error, WebApplicationClient
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthException
from social_core.strategy import BaseStrategy
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .claims import Claims
from .client import OAuth2Client
from .exceptions import OAuth2AuthenticationError, OAuth2InvalidRequestError


class OAuth2Strategy(BaseStrategy):
    """Dummy strategy for using the `BaseOAuth2.user_data` method."""

    def request_data(self, merge=True) -> Dict[str, Any]:
        return {}

    def absolute_uri(self, path=None) -> str:
        return path

    def get_setting(self, name) -> Any:
        """Mocked setting method."""

    @staticmethod
    def get_json(url, method="GET", *args, **kwargs) -> httpx.Response:
        return httpx.request(method, url, *args, **kwargs)


class OAuth2Core:
    """OAuth2 flow handler of a certain provider."""

    client_id: str = None
    client_secret: str = None
    scope: Optional[List[str]] = None
    claims: Optional[Claims] = None
    provider: str = None
    redirect_uri: str = None
    backend: BaseOAuth2 = None

    _oauth_client: Optional[WebApplicationClient] = None
    _authorization_endpoint: str = None
    _token_endpoint: str = None
    _state: str = None

    def __init__(self, client: OAuth2Client) -> None:
        self.client_id = client.client_id
        self.client_secret = client.client_secret
        self.scope = client.scope
        self.claims = client.claims
        self.provider = client.backend.name
        self.redirect_uri = client.redirect_uri
        self.backend = client.backend(OAuth2Strategy())
        self._authorization_endpoint = self.backend.authorization_url()
        self._token_endpoint = self.backend.access_token_url()
        self._oauth_client = WebApplicationClient(self.client_id)

    @property
    def access_token(self) -> str:
        return self._oauth_client.access_token

    def get_redirect_uri(self, request: Request) -> str:
        base_url = request.base_url.replace(scheme="http" if request.auth.http else "https")
        return urljoin(str(base_url), "/oauth2/%s/token" % self.provider)

    def authorization_url(self, request: Request) -> str:
        redirect_uri = self.get_redirect_uri(request)
        state = "".join([random.choice(string.ascii_letters) for _ in range(32)])

        oauth2_query_params = dict(state=state, scope=self.scope, redirect_uri=redirect_uri)
        oauth2_query_params.update(request.query_params)

        self._state = oauth2_query_params.get("state")

        return str(
            self._oauth_client.prepare_request_uri(
                self._authorization_endpoint,
                **oauth2_query_params,
            )
        )

    def authorization_redirect(self, request: Request) -> RedirectResponse:
        return RedirectResponse(self.authorization_url(request), 303)

    async def token_data(self, request: Request, **httpx_client_args) -> dict:
        if not request.query_params.get("code"):
            raise OAuth2InvalidRequestError(400, "'code' parameter was not found in callback request")
        if not request.query_params.get("state"):
            raise OAuth2InvalidRequestError(400, "'state' parameter was not found in callback request")
        if request.query_params.get("state") != self._state:
            raise OAuth2InvalidRequestError(400, "'state' parameter does not match")

        redirect_uri = self.get_redirect_uri(request)
        scheme = "http" if request.auth.http else "https"
        authorization_response = re.sub(r"^https?", scheme, str(request.url))

        oauth2_query_params = dict(redirect_url=redirect_uri, authorization_response=authorization_response)
        oauth2_query_params.update(request.query_params)

        token_url, headers, content = self._oauth_client.prepare_token_request(
            self._token_endpoint,
            **oauth2_query_params,
        )

        headers.update({"Accept": "application/json"})
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient(auth=auth, **httpx_client_args) as session:
            try:
                response = await session.post(token_url, headers=headers, content=content)
                self._oauth_client.parse_request_body_response(json.dumps(response.json()))
                return self.standardize(self.backend.user_data(self.access_token))
            except (OAuth2Error, httpx.HTTPError) as e:
                raise OAuth2InvalidRequestError(400, str(e))
            except (AuthException, Exception) as e:
                raise OAuth2AuthenticationError(401, str(e))

    async def token_redirect(self, request: Request, **kwargs) -> RedirectResponse:
        access_token = request.auth.jwt_create(await self.token_data(request, **kwargs))
        response = RedirectResponse(self.redirect_uri or request.base_url)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            max_age=request.auth.expires,
            expires=request.auth.expires,
            secure=not request.auth.http,
            httponly=True,
            samesite="none",
        )
        return response

    def standardize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["provider"] = self.provider
        data["scope"] = self.scope
        return data
