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

from typing import Type

from argilla_server.errors.future import NotFoundError
from argilla_server.security.authentication.oauth2.providers._base import OAuth2ClientProvider
from argilla_server.security.authentication.oauth2.providers._github import GitHubClientProvider
from argilla_server.security.authentication.oauth2.providers._huggingface import HuggingfaceClientProvider

__all__ = [
    "OAuth2ClientProvider",
    "GitHubClientProvider",
    "HuggingfaceClientProvider",
    "get_provider_by_name",
]

_ALL_SUPPORTED_OAUTH2_PROVIDERS = {
    GitHubClientProvider.name: GitHubClientProvider,
    HuggingfaceClientProvider.name: HuggingfaceClientProvider,
}


def get_provider_by_name(name: str) -> Type["OAuth2ClientProvider"]:
    """Get a registered oauth provider by name. Raise a ValueError if provided not found."""
    if provider_class := _ALL_SUPPORTED_OAUTH2_PROVIDERS.get(name):
        return provider_class
    else:
        raise NotFoundError(
            f"Unsupported provider {name}. " f"Supported providers are {_ALL_SUPPORTED_OAUTH2_PROVIDERS.keys()}"
        )
