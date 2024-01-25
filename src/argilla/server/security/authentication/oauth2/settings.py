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

from argilla.server.security.authentication.oauth2.client_provider import OAuth2ClientProvider
from argilla.server.security.authentication.oauth2.supported_providers import ALL_SUPPORTED_OAUTH2_PROVIDERS

__all__ = ["OAuth2Settings"]


class OAuth2Settings:
    class Workspace:
        def __init__(self, name: str):
            self.name = name

    def __init__(
        self,
        enabled: bool = True,
        allow_http: bool = False,
        providers: List["OAuth2ClientProvider"] = None,
        workspaces: List[Workspace] = None,
    ):
        self.enabled = enabled
        self.allow_http = allow_http
        self._providers = providers or []
        self.workspaces = workspaces or []

        if self.allow_http:
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

        settings["providers"] = cls._build_providers(settings)
        settings["workspaces"] = cls._build_workspaces(settings)

        return cls(**settings)

    @classmethod
    def _build_workspaces(cls, settings: dict) -> List[Workspace]:
        return [cls.Workspace(**workspace) for workspace in settings.pop("workspaces", [])]

    @classmethod
    def _build_providers(cls, settings: dict) -> List["OAuth2ClientProvider"]:
        providers = []

        for provider in settings.pop("providers", []):
            name = provider.pop("name")

            provider_class = ALL_SUPPORTED_OAUTH2_PROVIDERS.get(name)
            if not provider_class:
                raise ValueError(
                    f"Unsupported provider {name}. Supported providers are {ALL_SUPPORTED_OAUTH2_PROVIDERS.keys()}"
                )

            providers.append(provider_class.from_dict(provider))

        return providers
