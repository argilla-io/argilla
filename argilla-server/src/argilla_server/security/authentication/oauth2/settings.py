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
from typing import List

import yaml

from argilla_server.security.authentication.oauth2.providers import get_provider_by_name, OAuth2ClientProvider

__all__ = ["OAuth2Settings"]


class AllowedWorkspace:
    def __init__(self, name: str):
        self.name = name


class OAuth2Settings:
    """
    OAuth2 settings model.

    Args:
        allow_http_redirect:
            Whether to allow HTTP scheme on redirect urls (for tests purposes).
        providers:
            List of OAuth2 providers.
        allowed_workspaces:
            List of allowed workspace names (workspace must be created before).
    """

    ALLOWED_WORKSPACES_KEY = "allowed_workspaces"
    PROVIDERS_KEY = "providers"

    def __init__(
        self,
        allow_http_redirect: bool = False,
        providers: List[OAuth2ClientProvider] = None,
        allowed_workspaces: List[AllowedWorkspace] = None,
        **kwargs,  # Ignore any other key
    ):
        self.allow_http_redirect = allow_http_redirect
        self.allowed_workspaces = allowed_workspaces or []
        self._providers = providers or []

        if self.allow_http_redirect:
            # See https://stackoverflow.com/questions/27785375/testing-flask-oauthlib-locally-without-https
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    @property
    def providers(self) -> dict:
        return {provider.name: provider for provider in self._providers}

    @classmethod
    def from_yaml(cls, yaml_file: str) -> "OAuth2Settings":
        """Creates an instance of OAuth2Settings from a YAML file."""

        with open(yaml_file) as f:
            return cls.from_dict(yaml.safe_load(f))

    @classmethod
    def from_dict(cls, settings: dict) -> "OAuth2Settings":
        """Creates an instance of OAuth2Settings from a dictionary."""

        settings[cls.PROVIDERS_KEY] = cls._build_providers(settings)
        settings[cls.ALLOWED_WORKSPACES_KEY] = cls._build_workspaces(settings)

        return cls(**settings)

    @classmethod
    def _build_workspaces(cls, settings: dict) -> List[AllowedWorkspace]:
        allowed_workspaces = settings.pop(cls.ALLOWED_WORKSPACES_KEY, None) or []
        return [AllowedWorkspace(**workspace) for workspace in allowed_workspaces]

    @classmethod
    def _build_providers(cls, settings: dict) -> List["OAuth2ClientProvider"]:
        providers = []

        for provider in settings.pop("providers", []):
            name = provider.pop("name")
            provider_class = get_provider_by_name(name)

            providers.append(provider_class.from_dict(provider))

        return providers
