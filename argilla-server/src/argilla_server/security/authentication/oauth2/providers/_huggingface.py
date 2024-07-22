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
from typing import Union, Optional

from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla_server.enums import UserRole
from argilla_server.integrations.huggingface.spaces import HUGGINGFACE_SETTINGS
from argilla_server.logging import LoggingMixin
from argilla_server.security.authentication.claims import Claims
from argilla_server.security.authentication.oauth2.providers._base import OAuth2ClientProvider

_LOGGER = logging.getLogger("argilla.security.oauth2.providers.huggingface")


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    OIDC_ENDPOINT = "https://huggingface.co"
    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


_HF_PREFERRED_USERNAME = "preferred_username"


def is_space_author(userinfo: dict, space_author: str) -> bool:
    """Return True if the space author name is the userinfo username. Otherwise, False"""
    return space_author == userinfo.get(_HF_PREFERRED_USERNAME)


def find_org_from_userinfo(userinfo: dict, org_name: str) -> Optional[dict]:
    """Find the organization by name from the userinfo"""
    for org in userinfo.get("orgs") or []:
        if org_name == org.get(_HF_PREFERRED_USERNAME):
            return org


def get_user_role_by_org(org: dict) -> Union[UserRole, None]:
    """Return the computed UserRole from the role found in a organization (if any)"""
    _ROLE_IN_ORG = "roleInOrg"
    _ROLES_MAPPING = {"admin": UserRole.owner}

    if _ROLE_IN_ORG not in org:
        _LOGGER.warning(f"Cannot find the user role info in org {org}. Review granted permissions")
    else:
        return _ROLES_MAPPING.get(org[_ROLE_IN_ORG])


class HuggingfaceClientProvider(OAuth2ClientProvider, LoggingMixin):
    """Specialized HuggingFace OAuth2 provider."""

    @staticmethod
    def parse_role_from_user_info(user: dict) -> Union[str, None]:
        """Parse the Argilla user role from info provided as part of the user info"""
        space_author_name = HUGGINGFACE_SETTINGS.space_author_name

        if is_space_author(user, space_author_name):
            return UserRole.owner
        elif org := find_org_from_userinfo(user, space_author_name):
            return get_user_role_by_org(org)

    claims = Claims(username=_HF_PREFERRED_USERNAME, role=parse_role_from_user_info)
    backend_class = HuggingfaceOpenId
    name = "huggingface"
