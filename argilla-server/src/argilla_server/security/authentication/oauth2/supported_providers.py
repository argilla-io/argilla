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
from typing import Union

from social_core.backends.github import GithubOAuth2
from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla_server.enums import UserRole
from argilla_server.logging import LoggingMixin
from argilla_server.security.authentication.claims import Claims
from argilla_server.security.authentication.oauth2.client_provider import OAuth2ClientProvider


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    OIDC_ENDPOINT = "https://huggingface.co"
    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


class GitHubClientProvider(OAuth2ClientProvider):
    claims = Claims(picture="avatar_url", identity=lambda user: f"{user.provider}:{user.id}", username="login")
    backend_class = GithubOAuth2
    name = "github"


# TODO: Move each provided to separate module
class HuggingfaceClientProvider(OAuth2ClientProvider, LoggingMixin):
    """Specialized HuggingFace OAuth2 provider."""

    _LOGGER = logging.getLogger("argilla.security.oauth2.huggingface")

    _PREFERRED_USERNAME = "preferred_username"
    _ROLE_IN_ORG = "roleInOrg"

    _ROLES_MAPPING = {"admin": UserRole.owner}

    @classmethod
    def _resolve_argilla_role(cls, user: dict) -> Union[str, None]:
        # TODO: Create module for huggingface integrations: argilla_server.huggingface.spaces (oauth,...)
        from argilla_server.api.schemas.v1.settings import HuggingfaceSettings

        space_author_name = HuggingfaceSettings().space_author_name
        if space_author_name == user[cls._PREFERRED_USERNAME]:
            return UserRole.owner

        org = None
        for org in user.get("orgs") or []:
            if space_author_name == org[cls._PREFERRED_USERNAME]:
                break

        if org:
            if cls._ROLE_IN_ORG not in org:
                cls._LOGGER.warning("Cannot find user role in org. Review permissions")
            return cls._ROLES_MAPPING.get(org[cls._ROLE_IN_ORG])

    claims = Claims(username=_PREFERRED_USERNAME, role=_resolve_argilla_role)
    backend_class = HuggingfaceOpenId
    name = "huggingface"


_providers = [GitHubClientProvider, HuggingfaceClientProvider]

ALL_SUPPORTED_OAUTH2_PROVIDERS = {provider_class.name: provider_class for provider_class in _providers}
