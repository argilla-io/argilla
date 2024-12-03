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
from typing import Type, Dict, Any, Optional, List

from social_core.backends.oauth import BaseOAuth2
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.backends.utils import load_backends
from social_core.strategy import BaseStrategy

from argilla_server.errors.future import NotFoundError


class Strategy(BaseStrategy):
    def request_data(self, merge=True) -> Dict[str, Any]:
        return {}

    def absolute_uri(self, path=None) -> str:
        return path

    def get_setting(self, name):
        return os.environ[name]


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    # OIDC configuration
    OIDC_ENDPOINT = "https://huggingface.co"

    DEFAULT_SCOPE = ["openid", "profile"]


class KeycloakOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "keycloak"

    def oidc_endpoint(self) -> str:
        value = super().oidc_endpoint()

        if value is None:
            from social_core.utils import setting_name

            name = setting_name("OIDC_ENDPOINT")
            raise ValueError(
                "oidc_endpoint needs to be set in the Keycloak configuration. "
                f"Please set the {name} environment variable."
            )

        return value

    def get_user_details(self, response: Dict[str, Any]) -> Dict[str, Any]:
        user = super().get_user_details(response)

        if role := self._extract_role(response):
            user["role"] = role

        if available_workspaces := self._extract_available_workspaces(response):
            user["available_workspaces"] = available_workspaces

        return user

    def _extract_role(self, response: Dict[str, Any]) -> Optional[str]:
        roles = self._read_realm_roles(response)

        for role in roles:
            if role.startswith("argilla_role:"):
                role = role.split(":")[1]
                return role

    def _extract_available_workspaces(self, response: Dict[str, Any]) -> List[str]:
        roles = self._read_realm_roles(response)

        workspaces = []
        for role in roles:
            if role.startswith("argilla_workspace:"):
                workspace = role.split(":")[1]
                workspaces.append(workspace)

        return workspaces

    @classmethod
    def _read_realm_roles(cls, response) -> List[str]:
        realm_access = response.get("realm_access") or {}
        return realm_access.get("roles") or []


_SUPPORTED_BACKENDS = {}


def load_supported_backends(extra_backends: list = None) -> Dict[str, Type[BaseOAuth2]]:
    global _SUPPORTED_BACKENDS

    backends = [
        "argilla_server.security.authentication.oauth2._backends.HuggingfaceOpenId",
        "argilla_server.security.authentication.oauth2._backends.KeycloakOpenId",
        "social_core.backends.github.GithubOAuth2",
        "social_core.backends.google.GoogleOAuth2",
    ]

    if extra_backends:
        backends.extend(extra_backends)

    _SUPPORTED_BACKENDS = load_backends(backends, force_load=True)

    for backend in _SUPPORTED_BACKENDS.values():
        if not issubclass(backend, BaseOAuth2):
            raise ValueError(
                f"Backend {backend} is not a supported OAuth2 backend. "
                "Please, make sure it is a subclass of BaseOAuth2."
            )

    return _SUPPORTED_BACKENDS


def get_supported_backend_by_name(name: str) -> Type[BaseOAuth2]:
    """Get a registered oauth provider by name. Raise a ValueError if provided not found."""
    global _SUPPORTED_BACKENDS

    if not _SUPPORTED_BACKENDS:
        _SUPPORTED_BACKENDS = load_supported_backends()

    if provider := _SUPPORTED_BACKENDS.get(name):
        return provider
    else:
        raise NotFoundError(f"Unsupported provider {name}. Supported providers are {_SUPPORTED_BACKENDS.keys()}")
