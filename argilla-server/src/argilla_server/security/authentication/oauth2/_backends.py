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
from typing import Type, Dict, Any

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


def _load_backends():
    backends = [
        "argilla_server.security.authentication.oauth2._backends.HuggingfaceOpenId",
        "social_core.backends.github.GithubOAuth2",
        "social_core.backends.github.GithubOrganizationOAuth2",
        "social_core.backends.github.GithubTeamOAuth2",
        "social_core.backends.github_enterprise.GithubEnterpriseOAuth2",
        "social_core.backends.github_enterprise.GithubEnterpriseOrganizationOAuth2",
        "social_core.backends.github_enterprise.GithubEnterpriseTeamOAuth2",
        "social_core.backends.google.GoogleOAuth2",
        "social_core.backends.google_openidconnect.GoogleOpenIdConnect",
    ]
    return load_backends(backends, force_load=True)


_SUPPORTED_BACKENDS = _load_backends()


def get_supported_backend_by_name(name: str) -> Type[BaseOAuth2]:
    """Get a registered oauth provider by name. Raise a ValueError if provided not found."""

    if provider := _SUPPORTED_BACKENDS.get(name):
        return provider
    else:
        raise NotFoundError(f"Unsupported provider {name}. Supported providers are {_SUPPORTED_BACKENDS.keys()}")
